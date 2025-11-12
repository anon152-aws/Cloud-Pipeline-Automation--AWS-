# --------------------------------------------------------
# TERRAFORM CONFIGURATION BLOCK
# --------------------------------------------------------
terraform {
  required_version = ">= 1.5.0"        # Minimum Terraform version required

  required_providers {                # Define the cloud provider plugins to use
    aws = {                           # AWS provider configuration
      source  = "hashicorp/aws"       # Use official AWS provider from HashiCorp
      version = "~> 5.0"              # Allow any compatible version within 5.x
    }
  }
}

# --------------------------------------------------------
# AWS PROVIDER CONFIGURATION
# --------------------------------------------------------
provider "aws" {
  region = var.aws_region             # AWS region (from variables.tf) e.g., us-east-2
}

# --------------------------------------------------------
# S3 BUCKET (DATA LAKE)
# --------------------------------------------------------
resource "aws_s3_bucket" "data_lake" {
  bucket = var.bucket_name            # Bucket name passed via variable (must be unique globally)

  tags = {                            # Tagging resources for tracking and cost management
    Project = var.project_name        # Tag with project name (from variables.tf)
    Owner   = var.owner               # Tag with owner name (useful for team projects)
    Env     = var.environment         # Tag environment type (dev, test, prod)
  }
}

# --------------------------------------------------------
# BLOCK ALL PUBLIC ACCESS TO THE BUCKET (SECURITY BEST PRACTICE)
# --------------------------------------------------------
resource "aws_s3_bucket_public_access_block" "data_lake_block" {
  bucket = aws_s3_bucket.data_lake.id  # Apply security rules to the created S3 bucket

  block_public_acls       = true       # Disable public ACLs
  block_public_policy     = true       # Prevent public bucket policies
  ignore_public_acls      = true       # Ignore public ACLs that may already exist
  restrict_public_buckets = true       # Fully restrict all public access
}

# --------------------------------------------------------
# IAM USER (FOR THE DATA PIPELINE)
# --------------------------------------------------------
resource "aws_iam_user" "pipeline_user" {
  name = "${var.project_name}-user"    # IAM username pattern: projectname-user

  tags = {                             # Add tags for easy identification in IAM console
    Project = var.project_name
  }
}

# --------------------------------------------------------
# IAM POLICY DOCUMENT (PERMISSIONS FOR S3)
# --------------------------------------------------------
data "aws_iam_policy_document" "pipeline_user_policy_doc" {
  # Permission: allow listing the S3 bucket
  statement {
    effect = "Allow"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.data_lake.arn
    ]
  }

  # Permission: allow uploading and downloading objects from this bucket
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.data_lake.arn}/*"
    ]
  }
}

# --------------------------------------------------------
# IAM POLICY (APPLY THE ABOVE PERMISSIONS)
# --------------------------------------------------------
resource "aws_iam_policy" "pipeline_user_policy" {
  name        = "${var.project_name}-s3-access"    # Name of the custom IAM policy
  description = "Minimal S3 access for data pipeline user"
  policy      = data.aws_iam_policy_document.pipeline_user_policy_doc.json
}

# --------------------------------------------------------
# ATTACH POLICY TO PIPELINE USER
# --------------------------------------------------------
resource "aws_iam_user_policy_attachment" "pipeline_user_attach" {
  user       = aws_iam_user.pipeline_user.name     # Attach to the IAM user created above
  policy_arn = aws_iam_policy.pipeline_user_policy.arn
}

# --------------------------------------------------------
# ACCESS KEYS (PROGRAMMATIC ACCESS FOR THE PIPELINE USER)
# --------------------------------------------------------
resource "aws_iam_access_key" "pipeline_user_key" {
  user = aws_iam_user.pipeline_user.name           # Generate AWS access/secret keys for the pipeline user
}
