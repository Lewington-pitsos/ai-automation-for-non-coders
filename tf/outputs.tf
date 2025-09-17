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

output "referral_events_table_name" {
  description = "Referral events DynamoDB table name"
  value       = aws_dynamodb_table.referral_events.name
}


output "stripe_webhook_url" {
  description = "Stripe webhook URL"
  value       = "https://${aws_api_gateway_rest_api.course_api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${var.environment}/stripe-webhook"
}