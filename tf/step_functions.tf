resource "aws_sfn_state_machine" "registration_workflow" {
  name     = "${var.project_name}-registration-workflow"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = jsonencode({
    Comment = "Course registration email workflow"
    StartAt = "SendUserEmail"
    States = {
      SendUserEmail = {
        Type     = "Task"
        Resource = aws_lambda_function.send_user_email.arn
        Next     = "SendAdminEmail"
        Retry = [
          {
            ErrorEquals     = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts     = 6
            BackoffRate     = 2
          }
        ]
      }
      SendAdminEmail = {
        Type     = "Task"
        Resource = aws_lambda_function.send_admin_email.arn
        End      = true
        Retry = [
          {
            ErrorEquals     = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
            IntervalSeconds = 2
            MaxAttempts     = 6
            BackoffRate     = 2
          }
        ]
      }
    }
  })

  tags = {
    Name        = "${var.project_name}-registration-workflow"
    Environment = var.environment
  }
}