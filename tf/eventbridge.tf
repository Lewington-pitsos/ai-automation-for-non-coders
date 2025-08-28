resource "aws_cloudwatch_event_bus" "course_events" {
  name = "${var.project_name}-events"

  tags = {
    Name        = "${var.project_name}-events"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_rule" "payment_success" {
  name           = "${var.project_name}-payment-success"
  description    = "Rule for successful payment events"
  event_bus_name = aws_cloudwatch_event_bus.course_events.name

  event_pattern = jsonencode({
    source      = ["course.registration"]
    detail-type = ["Payment Successful"]
  })

  tags = {
    Name        = "${var.project_name}-payment-success"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "payment_success_target" {
  rule           = aws_cloudwatch_event_rule.payment_success.name
  target_id      = "PaymentSuccessTarget"
  arn            = aws_sfn_state_machine.registration_workflow.arn
  event_bus_name = aws_cloudwatch_event_bus.course_events.name
  role_arn       = aws_iam_role.eventbridge_role.arn
}

resource "aws_iam_role" "eventbridge_role" {
  name = "${var.project_name}-eventbridge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-eventbridge-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "eventbridge_step_functions" {
  name = "${var.project_name}-eventbridge-step-functions"
  role = aws_iam_role.eventbridge_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution"
        ]
        Resource = aws_sfn_state_machine.registration_workflow.arn
      }
    ]
  })
}