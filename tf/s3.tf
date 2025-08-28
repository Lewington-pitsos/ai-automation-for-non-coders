resource "aws_s3_bucket" "email_templates" {
  bucket = "${var.project_name}-email-templates-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name}-email-templates"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "email_templates" {
  bucket = aws_s3_bucket.email_templates.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "email_templates" {
  bucket = aws_s3_bucket.email_templates.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "email_templates" {
  bucket = aws_s3_bucket.email_templates.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}