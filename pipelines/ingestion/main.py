# pipelines/ingestion/main.py 

import os                # Used to access environment variables and system functions
import json              # Used to work with JSON data (convert to/from strings)
import time              # Provides time-related functions like sleeping or timestamps
import logging           # Used for logging messages (info, warnings, errors)
from datetime import datetime, timedelta  # Helps handle date and time operations
import boto3             # AWS SDK for Python (used to interact with S3)
import requests          # Library for making HTTP requests (to call APIs)

from dotenv import load_dotenv
load_dotenv()

# Configure basic logging setup so the script prints useful information while running
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Create a logger instance for this file

# Load AWS S3 bucket name from environment variable, or use default if not set
S3_BUCKET = os.getenv("S3_BUCKET", "your-s3-bucket")
# Define the folder (prefix) inside the S3 bucket where raw data will be stored
S3_PREFIX_RAW = os.getenv("S3_PREFIX_RAW", "raw")

# Configuration for all APIs we want to pull data from
# Each dictionary entry contains the name, base URL, auth token, and endpoint path
API_CONFIG = [
    {
        "name": "crm",  # First API: Customer Relationship Management system
        "base_url": os.getenv("CRM_API_URL"),  # API base URL (from environment variable)
        "token": os.getenv("CRM_API_TOKEN"),   # API access token (for authentication)
        "path": "/v1/customers"                # Specific endpoint path to fetch data
    },
    {
        "name": "billing",  # Second API: Billing or invoices system
        "base_url": os.getenv("BILLING_API_URL"),  # API base URL (from environment variable)
        "token": os.getenv("BILLING_API_TOKEN"),   # API access token (for authentication)
        "path": "/v1/invoices"                     # Endpoint path to get billing data
    },
]

# Create an S3 client so we can upload files directly to an AWS S3 bucket
s3 = boto3.client("s3")


# Define a function to fetch data from an API, retrying if it fails
def fetch_with_retry(url, headers, params=None, max_retries=5):
    # Try the request up to 'max_retries' times
    for attempt in range(1, max_retries + 1):
        # Make an HTTP GET request to the given API URL
        resp = requests.get(url, headers=headers, params=params or {}, timeout=30)
        # If the response is OK (HTTP 200), return the JSON data
        if resp.status_code == 200:
            return resp.json()
        # Otherwise, log a warning showing the status and attempt number
        logger.warning(
            "Request failed (status=%s, attempt=%s/%s)", 
            resp.status_code, attempt, max_retries
        )
        # Wait (sleep) before trying again — uses exponential backoff (2^attempt seconds)
        time.sleep(2 ** attempt)
    # If all retries fail, raise an error
    raise RuntimeError(f"Failed to fetch {url} after {max_retries} attempts")


# Define a function to figure out how far back in time to fetch data from
def get_checkpoint(api_name):
    # In a real system, this checkpoint (last successful run) might be stored in DynamoDB or SSM
    # For now, we read it from environment variable or default to the last 24 hours
    checkpoint = os.getenv(f"{api_name.upper()}_SINCE_HOURS", "24")
    # Return the datetime representing "now minus X hours"
    return datetime.utcnow() - timedelta(hours=int(checkpoint))


# Define a function to upload API data to S3 as a JSON file
def upload_to_s3(api_name, data):
    # Create an S3 object key (file path) using folder, API name, and current date/time
    key = f"{S3_PREFIX_RAW}/{api_name}/dt={datetime.utcnow().strftime('%Y-%m-%d')}/" \
          f"{int(time.time())}.json"
    # Upload the data to S3 as a JSON file
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(data).encode("utf-8")  # Convert JSON to bytes before upload
    )
    # Log success message showing where the file was saved
    logger.info("Uploaded %s records for %s to s3://%s/%s",
                len(data), api_name, S3_BUCKET, key)


# Main function that runs the whole pipeline
def run():
    # Loop through each API defined in our configuration
    for api in API_CONFIG:
        # Determine the time range (how far back to fetch data)
        since = get_checkpoint(api["name"])
        # Build the full API URL (base URL + endpoint path)
        url = f"{api['base_url']}{api['path']}"
        # Add the Authorization header for secure API access
        headers = {"Authorization": f"Bearer {api['token']}"}
        # Add query parameters (e.g., only fetch data updated since last run)
        params = {"updated_since": since.isoformat()}

        # Log what we’re about to fetch
        logger.info("Fetching %s data since %s", api["name"], since.isoformat())
        # Actually call the API and get the data
        data = fetch_with_retry(url, headers, params)
        # Save the data to S3
        upload_to_s3(api["name"], data)

    # Log once all APIs are done
    logger.info("Ingestion complete.")


# This ensures the script runs only if called directly (not imported as a module)
if __name__ == "__main__":
    run()


# Quick summary of what it does:

# Gets data from two APIs (CRM & billing).

# Retries automatically if something fails.

# Saves the data into AWS S3 as JSON files.

# Logs everything, so you know what’s happening.

# Designed to be automated in a cloud CI/CD setup (like GitLab).