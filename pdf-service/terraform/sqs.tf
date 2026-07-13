# PDF Generation Dead Letter Queue (DLQ)
resource "aws_sqs_queue" "pdf_dlq" {
  name                      = "${var.environment}-pdf-generation-dlq"
  message_retention_seconds = 1209600 # 14 days
}

# Active PDF Generation Queue
resource "aws_sqs_queue" "pdf_queue" {
  name                      = "${var.environment}-pdf-generation-queue"
  visibility_timeout_seconds = 900 # 15 minutes (aligns with max Lambda execution time)
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.pdf_dlq.arn
    maxReceiveCount     = 3
  })
}
