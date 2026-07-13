resource "aws_dynamodb_table" "pdf_jobs" {
  name         = "${var.environment}-pdf-generation-jobs"
  billing_mode = "PAY_PER_REQUEST" # Serverless on-demand billing
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true # Enable automatic expiry of metadata if needed (e.g. after 30 days)
  }

  tags = {
    Environment = var.environment
    Service     = "pdf-service"
  }
}
