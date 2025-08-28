data "archive_file" "registration_handler" {
  type        = "zip"
  output_path = "${path.module}/registration-handler.zip"
  source {
    content = templatefile("${path.module}/lambda/registration-handler.py", {
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
    content = templatefile("${path.module}/lambda/payment-webhook.py", {
      table_name = aws_dynamodb_table.course_registrations.name
      event_bus_name = aws_cloudwatch_event_bus.course_events.name
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
      EVENT_BUS_NAME = aws_cloudwatch_event_bus.course_events.name
      STRIPE_WEBHOOK_SECRET = var.stripe_webhook_secret
    }
  }

  tags = {
    Name        = "${var.project_name}-payment-webhook"
    Environment = var.environment
  }
}

data "archive_file" "send_user_email" {
  type        = "zip"
  output_path = "${path.module}/send-user-email.zip"
  source {
    content = templatefile("${path.module}/lambda/send-user-email.py", {
      from_email = var.from_email
      bucket_name = aws_s3_bucket.email_templates.bucket
    })
    filename = "lambda_function.py"
  }
}

resource "aws_lambda_function" "send_user_email" {
  filename         = data.archive_file.send_user_email.output_path
  function_name    = "${var.project_name}-send-user-email"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.send_user_email.output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      FROM_EMAIL = var.from_email
      BUCKET_NAME = aws_s3_bucket.email_templates.bucket
    }
  }

  tags = {
    Name        = "${var.project_name}-send-user-email"
    Environment = var.environment
  }
}

data "archive_file" "send_admin_email" {
  type        = "zip"
  output_path = "${path.module}/send-admin-email.zip"
  source {
    content = templatefile("${path.module}/lambda/send-admin-email.py", {
      from_email = var.from_email
      admin_email = var.admin_email
    })
    filename = "lambda_function.py"
  }
}

resource "aws_lambda_function" "send_admin_email" {
  filename         = data.archive_file.send_admin_email.output_path
  function_name    = "${var.project_name}-send-admin-email"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.send_admin_email.output_base64sha256
  runtime         = "python3.11"
  timeout         = 30

  environment {
    variables = {
      FROM_EMAIL = var.from_email
      ADMIN_EMAIL = var.admin_email
    }
  }

  tags = {
    Name        = "${var.project_name}-send-admin-email"
    Environment = var.environment
  }
}