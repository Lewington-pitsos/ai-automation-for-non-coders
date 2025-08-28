resource "aws_dynamodb_table" "course_registrations" {
  name           = "course_registrations"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "registration_id"

  attribute {
    name = "registration_id"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }


  global_secondary_index {
    name            = "email-index"
    hash_key        = "email"
    projection_type = "ALL"
  }


  tags = {
    Name        = "${var.project_name}-registrations"
    Environment = var.environment
  }
}