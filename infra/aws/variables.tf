# --------------------------------------------------------
# TERRAFORM VARIABLES
# --------------------------------------------------------
# This file defines input variables for your Terraform configuration.
# Variables make your setup flexible — you can reuse this infrastructure
# in different environments (dev, prod) just by changing values.

# --------------------------------------------------------
# AWS REGION
# --------------------------------------------------------
variable "aws_region" {
  description = "AWS region to deploy resources (e.g., us-east-2)"
  type        = string
  default     = "us-east-2"   # Default region (Ohio)
}

# --------------------------------------------------------
# S3 BUCKET NAME
# --------------------------------------------------------
variable "bucket_name" {
  description = "Name of the S3 bucket to be created for data lake storage"
  type        = string
  default     = "cloud-data-pipeline-ramoneaws"   # Must be globally unique in AWS
}

# --------------------------------------------------------
# PROJECT NAME
# --------------------------------------------------------
variable "project_name" {
  description = "Project name used for tagging and naming resources"
  type        = string
  default     = "cloud-data-pipeline-automation"  # Used in IAM and tags
}

# --------------------------------------------------------
# OWNER
# --------------------------------------------------------
variable "owner" {
  description = "Owner of the infrastructure (for tagging and tracking)"
  type        = string
  default     = "ramone"     # Replace with your name or team name
}

# --------------------------------------------------------
# ENVIRONMENT TYPE
# --------------------------------------------------------
variable "environment" {
  description = "Environment tag to identify if this is dev, test, or prod"
  type        = string
  default     = "dev"        # Default to 'dev' for safe deployment
}
