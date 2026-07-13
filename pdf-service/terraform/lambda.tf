# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.environment}-pdf-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Attach basic execution policy for logging and VPC
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

# IAM Policy for S3, SQS, and DynamoDB access
resource "aws_iam_policy" "lambda_policy" {
  name        = "${var.environment}-pdf-lambda-policy"
  description = "IAM Policy for PDF generation lambda access to S3, SQS and DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.pdf_assets.arn,
          "${aws_s3_bucket.pdf_assets.arn}/*",
          aws_s3_bucket.pdf_archive.arn,
          "${aws_s3_bucket.pdf_archive.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.pdf_jobs.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.pdf_queue.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_permissions" {
  policy_arn = aws_iam_policy.lambda_policy.arn
  role       = aws_iam_role.lambda_role.name
}

# Container Image Configured Lambda
resource "aws_lambda_function" "pdf_generator" {
  function_name = "${var.environment}-pdf-generator-worker"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/pdf-service:latest"
  timeout       = 900 # 15 minutes
  memory_size   = 2048 # 2GB RAM (iText rendering can be memory-heavy)

  environment {
    variables = {
      ENVIRONMENT   = var.environment
      S3_ARCHIVE    = aws_s3_bucket.pdf_archive.id
      S3_ASSETS     = aws_s3_bucket.pdf_assets.id
      DYNAMODB_TABLE = aws_dynamodb_table.pdf_jobs.id
    }
  }
}

# Event Source Mapping (SQS to Lambda trigger)
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.pdf_queue.arn
  function_name    = aws_lambda_function.pdf_generator.arn
  batch_size       = 1 # Process one PDF job at a time to manage memory load
  enabled          = true
}
