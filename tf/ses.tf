resource "aws_ses_email_identity" "from_email" {
  email = var.from_email
}

resource "aws_ses_email_identity" "admin_email" {
  email = var.admin_email
}

# Domain identity for fairdinkumsystems.com 
# This allows sending from ANY email @fairdinkumsystems.com without individual verification
resource "aws_ses_domain_identity" "fairdinkumsystems" {
  domain = "fairdinkumsystems.com"
}

# Domain verification record - you'll need to add this TXT record to your DNS
resource "aws_ses_domain_identity_verification" "fairdinkumsystems" {
  domain = aws_ses_domain_identity.fairdinkumsystems.id
  
  depends_on = [aws_ses_domain_identity.fairdinkumsystems]
}

resource "aws_ses_configuration_set" "course_emails" {
  name = "${var.project_name}-emails"
}