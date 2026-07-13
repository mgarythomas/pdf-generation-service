variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Target AWS Region"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Deployment environment (e.g. dev, staging, prod)"
}
