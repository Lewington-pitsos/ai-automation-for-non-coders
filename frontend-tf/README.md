# Frontend Infrastructure

This Terraform configuration deploys a static website to AWS using S3, CloudFront, and Route53.

## Architecture

- **S3 Bucket**: Stores the static website files from `/src`
- **CloudFront**: CDN for global distribution with HTTPS
- **Route53**: DNS management for anyone-can-build.com
- **ACM**: SSL certificate for HTTPS

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. Terraform installed (>= 1.0)
3. Route53 hosted zone already exists for anyone-can-build.com

## Usage

1. Initialize Terraform:
   ```bash
   cd frontend-tf
   terraform init
   ```

2. Review the plan:
   ```bash
   terraform plan
   ```

3. Apply the configuration:
   ```bash
   terraform apply
   ```

4. The configuration will:
   - Create an S3 bucket for static hosting
   - Set up CloudFront distribution with SSL
   - Create DNS records pointing to CloudFront
   - Sync files from `/src` to S3

## Deployment

Files are automatically synced from `/src` to S3 during `terraform apply`. 

To manually sync files:
```bash
aws s3 sync ../src/ s3://anyone-can-build.com/ --delete
aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths '/*'
```

## Outputs

- `website_url`: The website URL
- `cloudfront_distribution_id`: CloudFront distribution ID
- `s3_bucket_name`: S3 bucket name

## Cost Considerations

- S3 storage: ~$0.023 per GB per month
- CloudFront: Pay per request and data transfer
- Route53: $0.50 per hosted zone per month
- ACM certificates: Free