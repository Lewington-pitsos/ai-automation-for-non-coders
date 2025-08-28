# Build Lambda packages with dependencies
resource "null_resource" "lambda_build" {
  triggers = {
    requirements = filemd5("../lambda/requirements.txt")
    payment_webhook = filemd5("../lambda/payment-webhook.py")
    registration_handler = filemd5("../lambda/registration-handler.py")
  }

  provisioner "local-exec" {
    command = "cd ../lambda && ./build_lambda_package.sh"
  }
}

# Registration Handler Lambda
resource "aws_lambda_function" "registration_handler" {
  filename         = "../lambda/registration-handler.zip"
  function_name    = "${var.project_name}-registration-handler"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("../lambda/registration-handler.zip")
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.course_registrations.name
    }
  }

  depends_on = [null_resource.lambda_build]

  tags = {
    Name        = "${var.project_name}-registration-handler"
    Environment = var.environment
  }
}

# Payment Webhook Lambda - needs Stripe library
resource "aws_lambda_function" "payment_webhook" {
  filename         = "../lambda/payment-webhook.zip"
  function_name    = "${var.project_name}-payment-webhook"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("../lambda/payment-webhook.zip")
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.course_registrations.name
      STRIPE_API_KEY = var.stripe_api_key
      STRIPE_WEBHOOK_SECRET = var.stripe_webhook_secret
      FROM_EMAIL = var.from_email
      ADMIN_EMAIL = var.admin_email
    }
  }

  depends_on = [null_resource.lambda_build]

  tags = {
    Name        = "${var.project_name}-payment-webhook"
    Environment = var.environment
  }
}

