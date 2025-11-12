== Cloud Data Pipeline Automation (AWS & Azure)
== Project Overview

Designed and implemented a fully automated, cloud-native ETL pipeline to ingest data from multiple REST APIs into a unified analytics layer across AWS and Azure.
The solution uses Python for extraction and transformation, Terraform for infrastructure-as-code, and GitLab CI/CD for automated testing, deployment, and scheduling.
Achieved ~30 % cost reduction by rightsizing compute, using serverless and spot-based workloads, and optimizing data storage and transfer patterns.
Improved reliability through centralized logging, retry logic, idempotent loads, and automated data-quality checks.

=High-Level Architecture

Data Flow

Sources: Multiple external APIs (CRM, Billing, Product, Usage)

Ingestion (Python):

Runs in a containerized job (AWS ECS Fargate / Lambda) triggered on a schedule

Fetches data from APIs with pagination, rate-limiting, exponential-backoff retries, and checkpointing (last successful timestamp)

Landing:

Raw JSON → AWS S3 (s3://data-lake/raw/...)

Transform:

Python jobs (or AWS Glue / Lambda) convert raw → cleaned Parquet

Normalize schemas, join across sources, add derived business metrics

Cross-Cloud Sync to Azure:

Curated S3 data replicated to Azure Blob Storage via scheduled sync (e.g., azcopy or Data Factory)

Analytics:

AWS Athena on S3 for internal analytics

Azure Synapse / SQL for downstream BI tools

Orchestration & CI/CD:

GitLab CI/CD

Runs tests & lint

Builds Docker image

Deploys infra (Terraform / Bicep)

Triggers pipeline updates

Monitoring & Reliability:

Centralized logs in CloudWatch / Azure Monitor

Alerting on failures, SLAs, and cost anomalies



=️ Setup & Installation

Follow these steps to run the project locally or in your own AWS account.

-1 Clone the repository
git clone https://github.com/<your-username>/cloud-data-pipeline-automation.git
cd cloud-data-pipeline-automation

-2 Create and activate a virtual environment
python -m venv venv
source venv/bin/activate    # Mac/Linux  
venv\Scripts\activate       # Windows

-3 Install dependencies
pip install -r requirements.txt

-4 Set up environment variables



Create a .env file in the project root:

AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_DEFAULT_REGION=us-east-2
S3_BUCKET=cloud-data-pipeline-ramoneaws
S3_PREFIX_RAW=raw
S3_PREFIX_CURATED=curated


 Add .env to your .gitignore — never push credentials to GitHub.

Deploy Infrastructure with Terraform

This creates your AWS S3 data-lake bucket and an IAM user for the pipeline.

cd infra/aws
terraform init
terraform apply


When finished, copy the Access Key and Secret Key outputs into your .env file.

To tear down resources and avoid charges:

terraform destroy

 Run the Data Pipeline

Ingestion (Extract → S3):

python pipelines/ingestion/main.py


Transformation (Raw → Curated Parquet):

python pipelines/transform/transform.py


You should now see files in:

s3://cloud-data-pipeline-ramoneaws/raw/...
s3://cloud-data-pipeline-ramoneaws/curated/...