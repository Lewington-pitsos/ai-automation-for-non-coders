// API Configuration
// Load terraform outputs dynamically
const terraformOutputs = require('./terraform-outputs.json');

const API_CONFIG = {
    // API_URL is loaded from terraform-outputs.json
    API_URL: terraformOutputs.api_gateway_invoke_url.value,
    STRIPE_PAYMENT_LINK: 'https://buy.stripe.com/8x2fZj1jz6RY0cx6TH9MY01'
};