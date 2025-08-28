resource "aws_ses_email_identity" "from_email" {
  email = var.from_email
}

resource "aws_ses_email_identity" "admin_email" {
  email = var.admin_email
}

resource "aws_ses_configuration_set" "course_emails" {
  name = "${var.project_name}-emails"
}