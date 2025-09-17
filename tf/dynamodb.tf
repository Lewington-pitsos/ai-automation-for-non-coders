resource "aws_dynamodb_table" "course_registrations" {
  name           = "course_registrations"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "course_id"
  range_key      = "email"

  attribute {
    name = "course_id"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }

  attribute {
    name = "registration_id"
    type = "S"
  }

  global_secondary_index {
    name            = "registration-id-index"
    hash_key        = "registration_id"
    projection_type = "ALL"
  }

  tags = {
    Name        = "${var.project_name}-registrations"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "referral_events" {
  name           = "referral_events"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "event_id"

  attribute {
    name = "event_id"
    type = "S"
  }

  attribute {
    name = "referral_code"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  global_secondary_index {
    name            = "referral-code-index"
    hash_key        = "referral_code"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  tags = {
    Name        = "${var.project_name}-referral-events"
    Environment = var.environment
  }
}