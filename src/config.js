// API Configuration
// Initialize with defaults
let API_CONFIG = {
    API_URL: '',
    STRIPE_PAYMENT_LINK: 'https://buy.stripe.com/14AaEZe6l0tA2kF3Hv9MY00',
    COURSE_ID: '01_ai_automation_for_non_coders', // Default course ID
    isLoaded: false
};

// Load terraform outputs dynamically
async function loadConfig() {
    let response = await fetch('./terraform-outputs.json');
    const terraformOutputs = await response.json();
    API_CONFIG.API_URL = terraformOutputs.api_gateway_invoke_url.value;
    API_CONFIG.isLoaded = true;

}

// Load config on initialization and export promise
const configPromise = loadConfig();