// API Configuration
// Replace YOUR_API_GATEWAY_URL with the actual API Gateway URL from Terraform outputs
const API_CONFIG = {
    // Run 'terraform output api_gateway_invoke_url' in the tf/ directory to get this URL
    API_URL: 'https://0rhn8rbzd4.execute-api.ap-southeast-2.amazonaws.com/prod',
    STRIPE_PAYMENT_LINK: 'https://buy.stripe.com/8x2fZj1jz6RY0cx6TH9MY01'
};