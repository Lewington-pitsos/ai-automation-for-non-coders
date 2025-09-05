/**
 * Meta Conversions API Frontend Tracking Utilities
 * 
 * This file provides JavaScript utilities to send ViewContent events
 * to your Meta Conversions API Lambda function.
 */

// Configuration - Update these URLs based on your API Gateway endpoints
const META_API_CONFIG = {
    viewContentEndpoint: 'https://0rhn8rbzd4.execute-api.ap-southeast-2.amazonaws.com/prod/view-content',
    debug: false // Set to true for console logging
};

/**
 * Send a ViewContent event to Meta Conversions API
 * @param {Object} options - Event options
 * @param {string} options.contentName - Name of the content being viewed
 * @param {string} options.contentCategory - Category of the content
 * @param {string} options.userEmail - User's email (optional, for logged-in users)
 * @param {string} options.eventSourceUrl - URL of the page (defaults to current page)
 */
async function sendViewContentEvent(options = {}) {
    const {
        contentName = document.title,
        contentCategory = 'website',
        userEmail = null,
        eventSourceUrl = window.location.href
    } = options;

    try {
        const payload = {
            user_data: {
                client_user_agent: navigator.userAgent
            },
            event_source_url: eventSourceUrl,
            content_data: {
                content_name: contentName,
                content_category: contentCategory
            }
        };

        // Add email if provided
        if (userEmail) {
            payload.user_data.email = userEmail;
        }

        if (META_API_CONFIG.debug) {
            console.log('Sending ViewContent event:', payload);
        }

        const response = await fetch(META_API_CONFIG.viewContentEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            if (META_API_CONFIG.debug) {
                console.log('ViewContent event sent successfully:', result);
            }
            return result;
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error sending ViewContent event:', error);
        // Don't throw - we don't want tracking errors to break the user experience
    }
}

/**
 * Track key page views automatically
 */
function setupAutoTracking() {
    // Track landing page view
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        sendViewContentEvent({
            contentName: 'AI Automation Mastery - Home',
            contentCategory: 'landing_page'
        });
    }
    
    // Track registration page view
    if (window.location.pathname.includes('/register')) {
        sendViewContentEvent({
            contentName: 'Course Registration',
            contentCategory: 'registration_page'
        });
    }
    
    // Track contact page view
    if (window.location.pathname.includes('/contact')) {
        sendViewContentEvent({
            contentName: 'Contact Us',
            contentCategory: 'contact_page'
        });
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
window.MetaTracking = {
    sendViewContentEvent,
    trackPageView,
    setupAutoTracking
};