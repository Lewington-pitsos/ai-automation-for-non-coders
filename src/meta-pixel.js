// Meta Pixel Implementation
// This file handles all Meta Pixel tracking functionality

// Meta Pixel Configuration
const META_PIXEL_ID = '1316281149823688'; // Your Meta Pixel ID
const META_TEST_EVENT_CODE = null; // Set this to your test event code when testing

// Initialize Meta Pixel
function initMetaPixel() {
    // Meta Pixel base code
    !function(f,b,e,v,n,t,s)
    {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
    n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t,s)}(window, document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    
    fbq('init', META_PIXEL_ID);
    
    // Track PageView event
    fbq('track', 'PageView');
    
    // Track ViewContent event for the main page
    const currentPage = window.location.pathname;
    if (currentPage === '/' || currentPage === '/index.html' || currentPage === '') {
        trackViewContent({
            content_name: 'AI Automation Mastery Course',
            content_category: 'Course Landing Page',
            content_type: 'product',
            value: 612.00,
            currency: 'USD'
        });
    }
}

// Helper function to hash user data for privacy (Meta does this automatically)
function hashUserData(data) {
    if (!data) return null;
    // Clean and normalize the data - Meta will hash it automatically
    return data.toLowerCase().trim().replace(/\s+/g, '');
}

// Track ViewContent Event
function trackViewContent(params = {}) {
    const eventData = {
        content_name: params.content_name || 'Unknown Page',
        content_category: params.content_category || 'Website',
        content_type: params.content_type || 'page',
        value: params.value || 0,
        currency: params.currency || 'USD'
    };
    
    // Send via Pixel (Meta handles hashing automatically)
    fbq('track', 'ViewContent', eventData);
    
    console.log('Meta Pixel: ViewContent tracked', eventData);
}

// Track Contact Event
function trackContactEvent(contactData) {
    const eventData = {
        content_name: 'Contact Form Submission',
        content_category: 'Lead Generation',
        value: 0,
        currency: 'USD'
    };
    
    // Advanced matching - Meta will hash this data automatically
    const userData = {
        em: contactData.email?.toLowerCase().trim(),
        ph: contactData.mobile?.replace(/[^0-9]/g, ''), // Remove non-digits
        fn: contactData.name?.split(' ')[0]?.toLowerCase(),
        ln: contactData.name?.split(' ').slice(1).join(' ')?.toLowerCase()
    };
    
    // Send via Pixel with user data for better matching
    fbq('track', 'Contact', eventData, userData);
    
    console.log('Meta Pixel: Contact tracked', eventData, userData);
}

// Track CompleteRegistration Event
function trackCompleteRegistration(registrationData) {
    const eventData = {
        content_name: 'AI Automation Course Registration',
        status: true,
        value: 612.00,
        currency: 'USD',
        predicted_ltv: 612.00
    };
    
    // Advanced matching - Meta will hash this data automatically
    const userData = {
        em: registrationData.email?.toLowerCase().trim(),
        ph: registrationData.phone?.replace(/[^0-9]/g, ''), // Remove non-digits
        fn: registrationData.firstName?.toLowerCase().trim(),
        ln: registrationData.lastName?.toLowerCase().trim()
    };
    
    // Send via Pixel with user data for better matching
    fbq('track', 'CompleteRegistration', eventData, userData);
    
    console.log('Meta Pixel: CompleteRegistration tracked', eventData, userData);
}

// Track custom events if needed
function trackCustomEvent(eventName, params = {}) {
    fbq('trackCustom', eventName, params);
    console.log('Meta Pixel: Custom event tracked', eventName, params);
}

// Export functions for use in other scripts
if (typeof window !== 'undefined') {
    window.MetaPixel = {
        init: initMetaPixel,
        trackViewContent,
        trackContactEvent,
        trackCompleteRegistration,
        trackCustomEvent
    };
}