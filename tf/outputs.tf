output "api_gateway_url" {
  description = "API Gateway URL"
  value       = "${aws_api_gateway_rest_api.course_api.execution_arn}/${var.environment}"
}

output "api_gateway_invoke_url" {
  description = "API Gateway invoke URL"
  value       = "https://${aws_api_gateway_rest_api.course_api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${var.environment}"
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.course_registrations.name
}


output "stripe_webhook_url" {
  description = "Stripe webhook URL"
  value       = "https://${aws_api_gateway_rest_api.course_api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${var.environment}/stripe-webhook"
}

output "ses_domain_verification_token" {
  value       = aws_ses_domain_identity.fairdinkumsystems.verification_token
  description = "Add this as a TXT record to _amazonses.fairdinkumsystems.com"
}

output "ses_domain_verification_instructions" {
  value = "To verify the domain for SES, add a TXT record with name '_amazonses' and value '${aws_ses_domain_identity.fairdinkumsystems.verification_token}' to your DNS"
  description = "Instructions for domain verification"
}