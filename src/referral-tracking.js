// Referral tracking functionality for the book now page

// Function to extract referral parameter from URL
function getReferralCode() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('referral');
}

// Function to send referral event to backend
async function sendReferralEvent(eventName, referralCode) {
    try {
        // Wait for config to load if needed
        if (typeof configPromise !== 'undefined') {
            await configPromise;
        }
        
        // Build API URL
        const apiUrl = `${API_CONFIG.API_URL}/referral`
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event_name: eventName,
                referral_code: referralCode
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Referral event recorded:', result);
            return true;
        } else {
            console.error('Failed to record referral event:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Error sending referral event:', error);
        return false;
    }
}

// Function to handle book now button clicks with referral tracking
function handleBookNowClick(originalHref) {
    const referralCode = getReferralCode();
    
    if (referralCode) {
        // Send referral event before redirecting
        sendReferralEvent('booking_clicked', referralCode)
            .then(() => {
                // Redirect to the original booking link
                window.open(originalHref, '_blank');
            })
            .catch((error) => {
                console.error('Error tracking referral:', error);
                // Still redirect even if tracking fails
                window.open(originalHref, '_blank');
            });
    } else {
        // No referral code, just redirect normally
        window.open(originalHref, '_blank');
    }
}

// Initialize referral tracking when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Find the book now button on the book-meeting page
    const bookNowButton = document.querySelector('.calendar-button');
    
    if (bookNowButton) {
        // Store the original href
        const originalHref = bookNowButton.getAttribute('href');
        
        // Remove the href to prevent default navigation
        bookNowButton.removeAttribute('href');
        
        // Add click handler with referral tracking
        bookNowButton.addEventListener('click', function(event) {
            event.preventDefault();
            handleBookNowClick(originalHref);
        });
        
        // Make it still look clickable
        bookNowButton.style.cursor = 'pointer';
    }
});