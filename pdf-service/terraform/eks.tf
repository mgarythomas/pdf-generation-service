# =========================================================================
# EKS Service Account IAM Role (IRSA) for PDF Workers
# =========================================================================

resource "aws_iam_role" "eks_pod_role" {
  name = "${var.environment}-eks-pdf-pod-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456789012:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/EXAMPLE"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            # Binds to the specific Kubernetes namespace and service account name
            "oidc.eks.us-east-1.amazonaws.com/id/EXAMPLE:sub" = "system:serviceaccount:pdf-services:pdf-worker-sa"
          }
        }
      }
    ]
  })
}

# Reuse the Lambda policy for EKS since permissions (S3, SQS, DynamoDB) are identical
resource "aws_iam_role_policy_attachment" "eks_pod_permissions" {
  policy_arn = aws_iam_policy.lambda_policy.arn
  role       = aws_iam_role.eks_pod_role.name
}

# Output EKS Role ARN for Helm / K8s Deployment YAML manifests
output "eks_pod_role_arn" {
  value       = aws_iam_role.eks_pod_role.arn
  description = "IAM Role ARN to annotate the Kubernetes ServiceAccount with."
}
