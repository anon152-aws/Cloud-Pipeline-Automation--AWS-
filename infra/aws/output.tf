# --------------------------------------------------------
# TERRAFORM OUTPUTS
# --------------------------------------------------------
# Outputs show important values after Terraform applies.
# These values help you configure your .env file for your Python scripts.

# --------------------------------------------------------
# OUTPUT: S3 BUCKET NAME
# --------------------------------------------------------
output "data_lake_bucket" {
  description = "The name of the created S3 data lake bucket"
  value       = aws_s3_bucket.data_lake.bucket
}

# --------------------------------------------------------
# OUTPUT: PIPELINE USER ACCESS KEY ID
# --------------------------------------------------------
output "pipeline_user_access_key_id" {
  description = "Access key ID for the IAM user used by the data pipeline"
  value       = aws_iam_access_key.pipeline_user_key.id
  sensitive   = true          # Mark as sensitive so it won't show in plain text
}

# --------------------------------------------------------
# OUTPUT: PIPELINE USER SECRET ACCESS KEY
# --------------------------------------------------------
output "pipeline_user_secret_access_key" {
  description = "Secret access key for the IAM user used by the data pipeline"
  value       = aws_iam_access_key.pipeline_user_key.secret
  sensitive   = true          # Keep hidden for security
}
