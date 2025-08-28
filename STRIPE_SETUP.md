# Stripe Payment Integration Setup Guide

## Overview
This system tracks course registrations and payments using:
1. Frontend registration form → API Gateway → Lambda → DynamoDB
2. Stripe Payment Link for payment processing
3. Stripe webhook → Lambda → DynamoDB update

## Setup Steps

### 1. Deploy Terraform Infrastructure
```bash
cd tf/
terraform init
terraform apply
```

### 2. Get Your API Gateway URL
```bash
terraform output api_gateway_invoke_url
```
Copy this URL - you'll need it for step 3.

### 3. Update Frontend Configuration
Edit `config.js` and replace `YOUR_API_GATEWAY_URL` with the actual URL from step 2:
```javascript
const API_CONFIG = {
    API_URL: 'https://xxxxx.execute-api.us-east-1.amazonaws.com/prod',
    STRIPE_PAYMENT_LINK: 'https://buy.stripe.com/8x2fZj1jz6RY0cx6TH9MY01'
};
```

### 4. Configure Stripe Webhook
1. Go to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Get your webhook URL:
   ```bash
   terraform output stripe_webhook_url
   ```
4. Enter the webhook URL in Stripe
5. Select event: `checkout.session.completed`
6. Copy the webhook signing secret

### 5. Set Stripe Secrets in Terraform
Create `tf/terraform.tfvars`:
```hcl
stripe_webhook_secret = "whsec_xxxxx"  # From step 4.6
```

### 6. Update Lambda Environment Variables
Re-run Terraform to apply the webhook secret:
```bash
cd tf/
terraform apply
```

## How It Works

### Registration Flow:
1. User fills out registration form
2. Frontend calls API Gateway `/register` endpoint
3. Lambda creates record in DynamoDB with `payment_status = "pending"`
4. Frontend redirects to Stripe Payment Link with pre-filled email

### Payment Flow:
1. User completes payment on Stripe
2. Stripe sends webhook to `/webhook/stripe` endpoint
3. Lambda matches payment to registration by email
4. Updates DynamoDB record: `payment_status = "paid"`
5. Triggers EventBridge event for email notifications

### Database Schema:
- **registration_id**: Unique identifier (primary key)
- **email**: User email (indexed for webhook matching)
- **name, phone, company, job_title**: User details
- **experience, referral_source**: Registration metadata
- **automation_interest**: User's automation goals
- **payment_status**: "pending" or "paid"
- **registration_date**: When registered
- **payment_date**: When paid
- **stripe_session_id**: Stripe checkout session ID
- **amount_paid**: Payment amount

## Testing

1. Submit a test registration
2. Check DynamoDB table for new record with `payment_status = "pending"`
3. Complete payment on Stripe (use test card: 4242 4242 4242 4242)
4. Verify DynamoDB record updates to `payment_status = "paid"`

## Monitoring

- CloudWatch Logs: Check Lambda function logs
- DynamoDB Console: View registration records
- Stripe Dashboard: Monitor payments and webhook deliveries

## Important Notes

- Emails are stored in lowercase for consistent matching
- Stripe Payment Links prefill the email but users can change it
- Make sure the email used for payment matches the registration email
- Consider implementing a fallback manual matching process for edge cases