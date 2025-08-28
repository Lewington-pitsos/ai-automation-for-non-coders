variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "course-registration"
}

variable "admin_email" {
  description = "Admin email for notifications"
  type        = string
  default     = "lewingtonpitsos@gmail.com"
}

variable "from_email" {
  description = "From email address"
  type        = string
  default     = "gday@fairdinkumsystems.com"
}

variable "stripe_webhook_secret" {
  description = "Stripe webhook secret"
  type        = string
  sensitive   = true
}