# pipelines/transform/transform.py

import os                 # To work with environment variables and file paths
import json               # To load and handle JSON data
import logging            # For logging messages (info, warnings, errors)
import boto3              # AWS SDK for Python (used here to read/write S3 files)
import pyarrow as pa      # Library for in-memory columnar data (used before Parquet conversion)
import pyarrow.parquet as pq  # To write data into Parquet format files
from dotenv import load_dotenv
load_dotenv()
# Configure logging so the script prints useful info to the console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read environment variables or use default values if not set
S3_BUCKET = os.getenv("S3_BUCKET", "your-s3-bucket")          # The main S3 bucket name
S3_PREFIX_RAW = os.getenv("S3_PREFIX_RAW", "raw")             # Folder in S3 with raw JSON data
S3_PREFIX_CURATED = os.getenv("S3_PREFIX_CURATED", "curated") # Folder in S3 for processed data

# Create an S3 client to read and write data from AWS S3
s3 = boto3.client("s3")


# -----------------------------
# 1️⃣ List all raw files in S3
# -----------------------------
def list_raw_keys(api_name):
    # List all S3 objects under the path for this API's raw data
    resp = s3.list_objects_v2(
        Bucket=S3_BUCKET,
        Prefix=f"{S3_PREFIX_RAW}/{api_name}/"
    )
    # Return just the list of file keys (paths) from the response
    return [c["Key"] for c in resp.get("Contents", [])]


# -----------------------------
# 2️⃣ Load raw JSON data
# -----------------------------
def load_json_records(keys):
    records = []  # Empty list to store all records from all files
    for key in keys:
        # Download each raw file from S3
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        # Read and decode the file content as JSON
        payload = json.loads(obj["Body"].read())
        # Some APIs return a list of objects, others return a single object
        if isinstance(payload, list):
            records.extend(payload)  # Add all items to our list
        else:
            records.append(payload)  # Add single record
    return records  # Return the combined list of all records


# -----------------------------
# 3️⃣ Write transformed data to S3 as Parquet
# -----------------------------
def write_parquet(api_name, rows):
    # Convert list of Python dictionaries into an Arrow table
    table = pa.Table.from_pylist(rows)

    # Create an S3 object key (path) for where to save the new Parquet file
    # Example path: curated/crm/dt=2025-11-11/data.parquet
    key = f"{S3_PREFIX_CURATED}/{api_name}/dt={os.getenv('PROCESS_DATE', 'manual')}/data.parquet"

    # Create an in-memory buffer to hold the Parquet data
    buf = pa.BufferOutputStream()

    # Write the Arrow table into the buffer in Parquet format
    pq.write_table(table, buf)

    # Upload the Parquet file to S3
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=buf.getvalue().to_pybytes())

    # Log success message
    logger.info("Wrote curated parquet to s3://%s/%s", S3_BUCKET, key)


# -----------------------------
# 4️⃣ Main function - run transformations
# -----------------------------
def run():
    # Process each data source (crm and billing)
    for api_name in ["crm", "billing"]:
        # Step 1: List all raw JSON files for this API
        keys = list_raw_keys(api_name)
        if not keys:
            # If no raw files are found, skip to the next one
            logger.info("No raw keys for %s", api_name)
            continue

        # Step 2: Load and combine all raw records
        rows = load_json_records(keys)

        # Step 3: Normalize and clean up the data (make it consistent)
        # Add or rename fields depending on which API we're processing

        if api_name == "crm":
            # For CRM data, rename "id" → "customer_id"
            for r in rows:
                r["customer_id"] = r.get("id")

        if api_name == "billing":
            # For Billing data, convert "amount" (in cents) → "invoice_amount_usd" (in dollars)
            for r in rows:
                r["invoice_amount_usd"] = float(r.get("amount", 0)) / 100.0

        # Step 4: Save the cleaned data into curated S3 folder as Parquet
        write_parquet(api_name, rows)


# -----------------------------
# 5️⃣ Script entry point
# -----------------------------
# This means the script runs only when executed directly (not when imported)
if __name__ == "__main__":
    run()
