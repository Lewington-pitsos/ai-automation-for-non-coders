# Course Registration Infrastructure

This Terraform configuration creates the AWS infrastructure for a course registration system with Stripe payment processing and automated email workflows.

## Architecture Components

- **API Gateway**: REST API with endpoints for registration and Stripe webhooks
- **Lambda Functions**: Handle registration, payment webhooks, and email sending
- **DynamoDB**: Stores course registration data
- **SES**: Sends automated emails to users and admin
- **Step Functions**: Orchestrates email sending workflow
- **EventBridge**: Event-driven architecture for payment processing
- **S3**: Stores email templates

## Deployment

1. Copy `terraform.tfvars.example` to `terraform.tfvars` and update the values:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` with your actual values:
   - Update email addresses
   - Add your Stripe webhook secret
   - Adjust region if needed

3. Initialize and deploy:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

## Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- SES email addresses verified in AWS
- Stripe account with webhook configured

## Important Notes

- The SES email addresses need to be verified before emails can be sent
- The Stripe webhook secret should be obtained from your Stripe dashboard
- Lambda functions include retry logic and error handling
- All resources are tagged for easy identification

## Outputs

After deployment, Terraform will output:
- API Gateway URL for frontend integration
- Stripe webhook URL for Stripe configuration
- DynamoDB table name
- S3 bucket name for email templates