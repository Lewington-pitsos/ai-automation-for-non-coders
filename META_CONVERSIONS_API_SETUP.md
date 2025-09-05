# Meta Conversions API Implementation

This document describes the Meta Conversions API integration implemented for your website.

## Overview

The Meta Conversions API allows you to send conversion events directly from your server to Facebook/Meta for better tracking and attribution. This implementation includes:

- ✅ **CompleteRegistration** events (when users register for courses)
- ✅ **Contact** events (when users submit contact forms)
- ✅ **Purchase** events (when users complete payments)
- ✅ **ViewContent** events (when users visit important pages)

## Files Created/Modified

### New Files
- `lambda/meta_conversions_api.py` - Core Conversions API integration
- `lambda/view-content-handler.py` - Lambda handler for ViewContent events
- `lambda/test_meta_conversions.py` - Test suite for the implementation
- `src/meta-tracking.js` - Frontend tracking utilities

### Modified Files
- `lambda/registration-handler.py` - Added CompleteRegistration tracking
- `lambda/contact-handler.py` - Added Contact tracking
- `lambda/payment-webhook.py` - Added Purchase tracking
- `lambda/requirements.txt` - Added requests dependency
- `lambda/build_lambda_package.sh` - Updated to include meta_conversions_api.py in all packages
- `tf/lambda.tf` - Added view-content-handler function and Meta environment variables
- `tf/api_gateway.tf` - Added view-content endpoint configuration
- `tf/variables.tf` - Added meta_access_token variable

## Configuration

### Environment Variables

You need to set these environment variables on your Lambda functions:

```bash
META_PIXEL_ID=1232612085335834
META_ACCESS_TOKEN=xxx
```

### Lambda Functions That Need These Variables
- `registration-handler`
- `contact-handler`
- `payment-webhook`
- `view-content-handler` (new)

## Event Tracking

### Automatic Events

These events are sent automatically when users interact with your backend:

1. **CompleteRegistration**: Sent when a user successfully registers for a course
2. **Contact**: Sent when a user submits a contact form
3. **Purchase**: Sent when a payment webhook confirms a successful purchase

### Manual ViewContent Tracking

For ViewContent events, you need to include the tracking script in your HTML pages.

#### Add to your HTML pages:

```html
<script src="meta-tracking.js"></script>
```

#### Manual tracking example:

```javascript
// Track specific content views
MetaTracking.sendViewContentEvent({
    contentName: 'Course Overview',
    contentCategory: 'education',
    userEmail: 'user@example.com' // Optional, only if user is logged in
});
```

## Event Deduplication

The implementation includes event deduplication using unique event IDs:

- **CompleteRegistration**: Uses `registration_{registration_id}`
- **Contact**: Uses `contact_{email}_{timestamp}`
- **Purchase**: Uses `purchase_{registration_id}` 
- **ViewContent**: Uses auto-generated UUID

## Privacy & Security

- All user data (email, phone) is automatically hashed using SHA-256 before sending
- No sensitive data is logged in plain text
- Client User Agent is passed through without hashing as required by Meta

## Testing

Run the test suite to validate the implementation:

```bash
cd lambda
python test_meta_conversions.py
```

## Deployment Steps

1. **Build and Deploy Lambda Functions**:
   ```bash
   cd lambda
   # Build all Lambda packages (includes meta_conversions_api.py automatically)
   ./build_lambda_package.sh
   
   # Then deploy via Terraform
   cd ../tf
   terraform apply
   ```

2. **Set Environment Variables**:
   - The `META_PIXEL_ID` is hardcoded as `1232612085335834` in the Terraform configuration
   - Add your `meta_access_token` to `tf/terraform.tfvars`:
     ```
     meta_access_token = "xxx"
     ```

3. **Deploy Frontend Tracking**:
   - Include `meta-tracking.js` in your website
   - Update the `viewContentEndpoint` in `meta-tracking.js` with your actual API Gateway URL

4. **Create API Gateway Endpoint** (for ViewContent):
   - Create a new Lambda function with `view-content-handler.py`
   - Set up API Gateway endpoint
   - Update the endpoint URL in `meta-tracking.js`

## Monitoring

Check CloudWatch logs for these messages:

- ✅ `Meta Conversions API {EventName} event sent successfully`
- ⚠️ `Failed to send Meta Conversions API {EventName} event`
- ❌ `Error sending Meta Conversions API {EventName} event`

## Event Data Structure

### CompleteRegistration
```json
{
  "event_name": "CompleteRegistration",
  "event_time": 1692345678,
  "action_source": "website",
  "user_data": {
    "em": ["hashed_email"],
    "ph": ["hashed_phone"],
    "client_user_agent": "Mozilla/5.0..."
  },
  "event_id": "registration_abc123"
}
```

### Contact
```json
{
  "event_name": "Contact",
  "event_time": 1692345678,
  "action_source": "website",
  "user_data": {
    "em": ["hashed_email"],
    "ph": ["hashed_phone"],
    "client_user_agent": "Mozilla/5.0..."
  },
  "event_id": "contact_user@example.com_1692345678"
}
```

### Purchase
```json
{
  "event_name": "Purchase",
  "event_time": 1692345678,
  "action_source": "website",
  "user_data": {
    "em": ["hashed_email"],
    "ph": ["hashed_phone"]
  },
  "custom_data": {
    "currency": "USD",
    "value": 299.99
  },
  "event_id": "purchase_abc123"
}
```

### ViewContent
```json
{
  "event_name": "ViewContent",
  "event_time": 1692345678,
  "action_source": "website",
  "user_data": {
    "client_user_agent": "Mozilla/5.0..."
  },
  "custom_data": {
    "content_name": "Course Landing Page",
    "content_category": "education"
  },
  "event_id": "uuid-generated-id"
}
```

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure `META_PIXEL_ID` and `META_ACCESS_TOKEN` are set on Lambda functions

2. **"Invalid signature"** 
   - Check that your access token is correct and hasn't expired

3. **"No events received"**
   - Verify your Pixel ID is correct
   - Check Meta Events Manager for event delivery

4. **Import errors in Lambda**
   - Ensure `meta_conversions_api.py` is deployed with other Lambda functions
   - Check that `requests` library is included in deployment package

### Testing Individual Events

You can test individual event types using the Lambda test console:

```json
{
  "event_type": "CompleteRegistration",
  "user_data": {
    "email": "test@example.com",
    "phone": "+1234567890",
    "client_user_agent": "Mozilla/5.0 Test"
  },
  "event_source_url": "https://yoursite.com/register"
}
```

## Meta Business Manager

After deployment, monitor your events in:
- Meta Events Manager → Data Sources → Your Pixel
- Check for event match quality, deduplication rate, and data freshness metrics

## Support

If you encounter issues:
1. Check CloudWatch logs for detailed error messages
2. Use the test script to validate your integration
3. Verify environment variables are set correctly
4. Check Meta Events Manager for event delivery status