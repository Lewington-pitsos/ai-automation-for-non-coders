data "archive_file" "registration_handler" {
  type        = "zip"
  output_path = "${path.module}/registration-handler.zip"
  source {
    content = templatefile("../lambda/registration-handler.py", {
      table_name = aws_dynamodb_table.course_registrations.name
    })
    filename = "lambda_function.py"
  }
}

resource "aws_lambda_function" "registration_handler" {
  filename         = data.archive_file.registration_handler.output_path
  function_name    = "${var.project_name}-registration-handler"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.registration_handler.output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.course_registrations.name
    }
  }

  tags = {
    Name        = "${var.project_name}-registration-handler"
    Environment = var.environment
  }
}

data "archive_file" "payment_webhook" {
  type        = "zip"
  output_path = "${path.module}/payment-webhook.zip"
  source {
    content = templatefile("../lambda/payment-webhook.py", {
      table_name = aws_dynamodb_table.course_registrations.name
      from_email = var.from_email
      admin_email = var.admin_email
    })
    filename = "lambda_function.py"
  }
}

resource "aws_lambda_function" "payment_webhook" {
  filename         = data.archive_file.payment_webhook.output_path
  function_name    = "${var.project_name}-payment-webhook"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.payment_webhook.output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.course_registrations.name
      STRIPE_WEBHOOK_SECRET = var.stripe_webhook_secret
      FROM_EMAIL = var.from_email
      ADMIN_EMAIL = var.admin_email
    }
  }

  tags = {
    Name        = "${var.project_name}-payment-webhook"
    Environment = var.environment
  }
}

