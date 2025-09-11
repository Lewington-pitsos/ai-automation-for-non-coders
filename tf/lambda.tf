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
      META_PIXEL_ID = "1232612085335834"
      META_ACCESS_TOKEN = var.meta_access_token
    }
  }

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
      META_PIXEL_ID = "1232612085335834"
      META_ACCESS_TOKEN = var.meta_access_token
    }
  }

  tags = {
    Name        = "${var.project_name}-payment-webhook"
    Environment = var.environment
  }
}

# Contact Form Handler Lambda
resource "aws_lambda_function" "contact_handler" {
  filename         = "../lambda/contact-handler.zip"
  function_name    = "${var.project_name}-contact-handler"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("../lambda/contact-handler.zip")
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      CONTACT_FORM_EMAIL = var.contact_form_email
      ADMIN_EMAIL = var.admin_email
      META_PIXEL_ID = "1232612085335834"
      META_ACCESS_TOKEN = var.meta_access_token
    }
  }

  tags = {
    Name        = "${var.project_name}-contact-handler"
    Environment = var.environment
  }
}

# Application Handler Lambda
resource "aws_lambda_function" "application_handler" {
  filename         = "../lambda/application_handler.zip"
  function_name    = "${var.project_name}-application-handler"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("../lambda/application_handler.zip")
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.course_registrations.name
      CONTACT_FORM_EMAIL = var.contact_form_email
      ADMIN_EMAIL = var.admin_email
      META_PIXEL_ID = "1232612085335834"
      META_ACCESS_TOKEN = var.meta_access_token
    }
  }

  tags = {
    Name        = "${var.project_name}-application-handler"
    Environment = var.environment
  }
}


