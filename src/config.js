// API Configuration
// Initialize with defaults
let API_CONFIG = {
    API_URL: '',
    STRIPE_PAYMENT_LINK: 'https://buy.stripe.com/8x2fZj1jz6RY0cx6TH9MY01',
    isLoaded: false
};

// Load terraform outputs dynamically
async function loadConfig() {
    try {
        const response = await fetch('/assets/terraform-outputs.json');
        const terraformOutputs = await response.json();
        API_CONFIG.API_URL = terraformOutputs.api_gateway_invoke_url.value;
        API_CONFIG.isLoaded = true;
    } catch (error) {
        console.error('Failed to load terraform outputs:', error);
        API_CONFIG.isLoaded = true; // Mark as loaded even on error to prevent infinite waiting
    }
}

// Load config on initialization and export promise
const configPromise = loadConfig();