resource "aws_ses_email_identity" "from_email" {
  email = var.from_email

  tags = {
    Name        = "${var.project_name}-from-email"
    Environment = var.environment
  }
}

resource "aws_ses_email_identity" "admin_email" {
  email = var.admin_email

  tags = {
    Name        = "${var.project_name}-admin-email"
    Environment = var.environment
  }
}

resource "aws_ses_configuration_set" "course_emails" {
  name = "${var.project_name}-emails"

  tags = {
    Name        = "${var.project_name}-emails"
    Environment = var.environment
  }
}