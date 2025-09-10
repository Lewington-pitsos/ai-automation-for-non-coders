/**
 * Meta Conversions API Frontend Tracking Utilities
 * 
 * This file provides JavaScript utilities to send ViewContent events
 * to your Meta Conversions API Lambda function.
 */

// Configuration - API endpoints for Meta Conversions API
// Note: ViewContent endpoint removed since we don't track anonymous page views
const META_API_CONFIG = {
    debug: false // Set to true for console logging
};

/**
 * ViewContent tracking via Conversions API has been removed.
 * For page view tracking, use Meta Pixel (fbq) instead:
 * 
 * Example:
 * fbq('track', 'ViewContent', {
 *     content_name: 'Page Title',
 *     content_category: 'page_category'
 * });
 * 
 * This function is kept for backwards compatibility but does nothing.
 * @deprecated Use Meta Pixel for ViewContent tracking
 */
function sendViewContentEvent(options = {}) {
    if (META_API_CONFIG.debug) {
        console.warn('sendViewContentEvent is deprecated. Use Meta Pixel (fbq) for page view tracking.');
    }
    // Function disabled - use Meta Pixel instead
    return Promise.resolve({ message: 'ViewContent tracking disabled - use Meta Pixel instead' });
}

/**
 * Track key page views automatically
 * Note: ViewContent tracking via Conversions API requires user email/phone,
 * so automatic page view tracking has been disabled for anonymous users.
 * Use Meta Pixel for anonymous page view tracking instead.
 */
function setupAutoTracking() {
    // Automatic ViewContent tracking disabled - requires user email for Conversions API
    // Use Meta Pixel (fbq) for anonymous page view tracking instead
    
    if (META_API_CONFIG.debug) {
        console.log('Auto-tracking disabled for anonymous users. Use sendViewContentEvent manually with userEmail for logged-in users.');
    }
}

/**
 * Track ViewContent with delay to ensure page is fully loaded
 */
function trackPageView(delay = 1000) {
    setTimeout(() => {
        setupAutoTracking();
    }, delay);
}

// Automatically track page views when the script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => trackPageView());
} else {
    trackPageView();
}

// Export functions for manual use
// Note: ViewContent tracking has been removed - use Meta Pixel instead
window.MetaTracking = {
    sendViewContentEvent, // Deprecated - does nothing
    trackPageView,
    setupAutoTracking
};