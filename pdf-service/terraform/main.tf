terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # backend "s3" {} # Configured externally in GitLab CI
}

provider "aws" {
  region = var.aws_region
}

# =========================================================================
# S3 Buckets
# =========================================================================

# S3 Bucket for Templates and Assets (Fonts, ICC Profiles)
resource "aws_s3_bucket" "pdf_assets" {
  bucket        = "${var.environment}-pdf-generation-assets"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "assets_versioning" {
  bucket = aws_s3_bucket.pdf_assets.id
  rule {
    status = "Enabled"
  }
}

# S3 Bucket for Storing Generated PDFs
resource "aws_s3_bucket" "pdf_archive" {
  bucket        = "${var.environment}-pdf-generation-archive"
  force_destroy = false
}

resource "aws_s3_bucket_lifecycle_configuration" "archive_lifecycle" {
  bucket = aws_s3_bucket.pdf_archive.id

  rule {
    id     = "archive-old-pdfs"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
