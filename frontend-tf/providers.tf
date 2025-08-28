terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

# Default provider for most resources
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "anyone-can-build"
      ManagedBy   = "terraform"
      Environment = var.environment
    }
  }
}

# Provider for ACM certificate (must be in us-east-1 for CloudFront)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
  
  default_tags {
    tags = {
      Project     = "anyone-can-build"
      ManagedBy   = "terraform"
      Environment = var.environment
    }
  }
}