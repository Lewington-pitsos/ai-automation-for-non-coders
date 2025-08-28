// Perlin background functionality is loaded from perlin-background.js

// Load shared components
async function loadComponent(elementId, componentPath) {
    try {
        const response = await fetch(componentPath);
        if (!response.ok) throw new Error(`Failed to load ${componentPath}`);
        const html = await response.text();
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = html;
        }
    } catch (error) {
        console.error(`Error loading component ${componentPath}:`, error);
    }
}

// Fix footer link cursors after dynamic loading
function fixFooterCursors() {
    const footerLinks = document.querySelectorAll('.footer-links a');
    footerLinks.forEach(link => {
        link.style.cursor = 'pointer';
        // Force override any inherited cursor styles
        link.style.setProperty('cursor', 'pointer', 'important');
    });
}

// Initialize everything on load
window.addEventListener('load', async () => {
    // Load shared components first
    await Promise.all([
        loadComponent('header-component', 'components/header.html'),
        loadComponent('footer-component', 'components/footer.html')
    ]);
    
    // Fix footer link cursors after components are loaded
    fixFooterCursors();
    
    // Initialize Perlin backgrounds
    initPerlinBackgrounds();
    
    // Initialize chart with a small delay to ensure Chart.js is loaded
    setTimeout(() => {
        initChart();
    }, 100);
});

// Handle resize for Perlin backgrounds  
window.addEventListener('resize', () => {
    handlePerlinResize();
});

// Chart initialization function
function initChart() {
    const canvas = document.getElementById('citizenDeveloperChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [
                ['Aug', '2020'], ['Feb', '2021'], ['Aug', '2021'], ['Feb', '2022'], 
                ['Aug', '2022'], ['Feb', '2023'], ['Aug', '2023'], ['Feb', '2024'], 
                ['Aug', '2024'], ['May', '2025'], ['Aug', '2025']
            ],
            datasets: [{
                label: 'Search Interest',
                data: [10, 8, 13, 16, 20, 25, 20, 22, 18, 32, 100],
                borderColor: '#4eff9f',
                backgroundColor: 'rgba(78, 255, 159, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.3,
                pointBackgroundColor: '#4eff9f',
                pointBorderColor: '#4eff9f',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'The Rise of Citizen Developers',
                    color: '#ffffff',
                    font: { size: 22, weight: '600' },
                    padding: 20
                },
                subtitle: {
                    display: true,
                    text: 'Google Trends: "citizen developer" search popularity',
                    color: '#999999',
                    font: { size: 12 },
                    padding: 10
                },
                legend: { display: false }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Time Period', color: '#999999' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { 
                        color: '#cccccc',
                        maxRotation: 0,
                        minRotation: 0,
                        font: { size: 11 }
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 105,
                    title: { display: true, text: 'Search Interest (0-100)', color: '#999999' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#cccccc', stepSize: 20, font: { size: 12 } }
                }
            },
            animation: { duration: 2000, easing: 'easeInOutQuart' }
        }
    });
}

// Tab switching functionality
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName + '-content').classList.add('active');
    
    // Activate corresponding button
    event.target.classList.add('active');
}

// FAQ Accordion functionality
function toggleFAQ(header) {
    const faqItem = header.parentElement;
    const isActive = faqItem.classList.contains('active');
    
    // Close all other FAQ items
    document.querySelectorAll('.faq-item.active').forEach(item => {
        if (item !== faqItem) {
            item.classList.remove('active');
        }
    });
    
    // Toggle current item
    if (isActive) {
        faqItem.classList.remove('active');
    } else {
        faqItem.classList.add('active');
    }
}

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Terminal Section Animation System
function initTerminalAnimations() {
    const terminalContainer = document.querySelector('.terminal-container');
    const terminalLines = document.querySelectorAll('.terminal-line');
    const personaEntries = document.querySelectorAll('.persona-entry');
    
    if (!terminalContainer || terminalLines.length === 0) {
        return;
    }

    let animationTriggered = false;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !animationTriggered) {
                animationTriggered = true;
                startTerminalAnimation();
            }
        });
    }, {
        threshold: 0.5,
        rootMargin: '-100px 0px'
    });

    observer.observe(terminalContainer);

    function startTerminalAnimation() {
        // Animate terminal lines with staggered delays
        terminalLines.forEach((line, index) => {
            const delay = parseInt(line.dataset.delay) || 0;
            
            setTimeout(() => {
                line.classList.add('visible');
            }, delay);
        });

        // Animate persona entries separately
        personaEntries.forEach((entry, index) => {
            const delay = parseInt(entry.dataset.delay) || 0;
            
            setTimeout(() => {
                entry.classList.add('visible');
            }, delay);
        });
    }
}

// Course Timeline Animation System (same as persona but for course timeline)
function initCourseTimelineAnimations() {
    const courseContainer = document.querySelector('.course-timeline-container');
    const courseLine = document.querySelector('.course-timeline-line');
    const courseItems = document.querySelectorAll('.course-timeline-item');
    
    if (!courseContainer || !courseLine || courseItems.length === 0) {
        return;
    }

    let animationTriggered = false;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !animationTriggered) {
                animationTriggered = true;
                startCourseAnimation();
            }
        });
    }, {
        threshold: 0.2,
        rootMargin: '-50px 0px'
    });

    observer.observe(courseContainer);

    function startCourseAnimation() {
        // Animate the timeline line first
        courseLine.classList.add('animate');
        
        // Animate each course item with progressive delays
        courseItems.forEach((item, index) => {
            const delay = parseInt(item.dataset.delay) || (index * 200);
            
            setTimeout(() => {
                item.classList.add('animate');
                
                // Add pulse animation to marker after item appears
                setTimeout(() => {
                    const marker = item.querySelector('.course-timeline-marker');
                    if (marker) {
                        marker.classList.add('pulse');
                        
                        // Remove pulse after 4 seconds
                        setTimeout(() => {
                            marker.classList.remove('pulse');
                        }, 4000);
                    }
                }, 600);
                
            }, delay + 300); // Extra delay to let line animation start
        });
    }
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTerminalAnimations();
    initCourseTimelineAnimations();
});

// Registration Form Handling
function initRegistrationForm() {
    const form = document.getElementById('registrationForm');
    if (!form) return;
    
    form.addEventListener('submit', handleFormSubmission);
    
    // Get submit button and make it disabled initially
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.classList.add('disabled');
    }
    
    // Add real-time validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', function(event) {
            clearFieldError(event);
            checkFormValidity();
        });
        field.addEventListener('change', checkFormValidity);
    });
    
    // Initial form validity check
    checkFormValidity();
}

function checkFormValidity() {
    const form = document.getElementById('registrationForm');
    if (!form) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (!submitButton) return;
    
    // Get all required fields
    const firstName = form.querySelector('#firstName');
    const lastName = form.querySelector('#lastName');
    const email = form.querySelector('#email');
    const phone = form.querySelector('#phone');
    const experience = form.querySelector('#experience');
    const referralSource = form.querySelector('#referralSource');
    const termsCheckbox = form.querySelector('#terms');
    
    // Check if all required fields are filled and terms are checked
    const isValid = firstName.value.trim() !== '' &&
                   lastName.value.trim() !== '' &&
                   email.value.trim() !== '' &&
                   phone.value.trim() !== '' &&
                   experience.value !== '' &&
                   referralSource.value !== '' &&
                   termsCheckbox.checked;
    
    // Enable/disable button based on validity
    if (isValid) {
        submitButton.disabled = false;
        submitButton.classList.remove('disabled');
    } else {
        submitButton.disabled = true;
        submitButton.classList.add('disabled');
    }
}

async function handleFormSubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Convert form data to object
    const registrationData = {};
    for (let [key, value] of formData.entries()) {
        registrationData[key] = value.trim();
    }
    
    // Validate form
    if (!validateForm(registrationData)) {
        return;
    }
    
    // Disable submit button and show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'PROCESSING...';
    
    // Wait for config to load if needed
    if (typeof configPromise !== 'undefined') {
        await configPromise;
    }
    
    // Call registration API first
    const apiUrl = typeof API_CONFIG !== 'undefined' && API_CONFIG.API_URL 
        ? `${API_CONFIG.API_URL}/register`
        : 'https://YOUR_API_GATEWAY_URL/prod/register';
    
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: registrationData.email,
            name: `${registrationData.firstName} ${registrationData.lastName}`,
            phone: registrationData.phone,
            company: registrationData.company || '',
            job_title: registrationData.jobTitle || '',
            experience: registrationData.experience,
            referral_source: registrationData.referralSource,
            automation_interest: registrationData.automationInterest || ''
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.registration_id) {
            // Store registration ID for later use
            sessionStorage.setItem('registrationId', data.registration_id);
            sessionStorage.setItem('registrationData', JSON.stringify(registrationData));
            
            // Append registration_id and email to Stripe URL as client reference
            const stripeUrl = typeof API_CONFIG !== 'undefined' && API_CONFIG.STRIPE_PAYMENT_LINK
            const email = encodeURIComponent(registrationData.email);
            // Note: Payment Links don't support custom parameters, but we can use prefilled email
            window.location.href = `${stripeUrl}?prefilled_email=${email}`;
        } else {
            throw new Error('Registration failed');
        }
    })
    .catch(error => {
        console.error('Registration error:', error);
        showErrorMessages(['Registration failed. Please try again or contact support.']);
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
}

function validateForm(data) {
    const errors = [];
    
    // Required field validation
    if (!data.firstName) errors.push('First name is required');
    if (!data.lastName) errors.push('Last name is required');
    if (!data.email) errors.push('Email address is required');
    if (!data.phone) errors.push('Phone number is required');
    if (!data.experience) errors.push('Coding experience level is required');
    if (!data.referralSource) errors.push('Please tell us how you heard about us');
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (data.email && !emailRegex.test(data.email)) {
        errors.push('Please enter a valid email address');
    }
    
    // Phone validation (basic)
    const phoneRegex = /^[\+]?[\d\s\-\(\)]{10,}$/;
    if (data.phone && !phoneRegex.test(data.phone)) {
        errors.push('Please enter a valid phone number');
    }
    
    if (errors.length > 0) {
        showFormErrors(errors);
        return false;
    }
    
    clearFormErrors();
    return true;
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    // Remove any existing error styling
    clearFieldError(event);
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    // Specific field validations
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    if (field.type === 'tel' && value) {
        const phoneRegex = /^[\+]?[\d\s\-\(\)]{10,}$/;
        if (!phoneRegex.test(value)) {
            showFieldError(field, 'Please enter a valid phone number');
            return false;
        }
    }
    
    return true;
}

function showFieldError(field, message) {
    field.style.borderColor = '#ff4444';
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#ff4444';
    errorDiv.style.fontSize = '12px';
    errorDiv.style.marginTop = '4px';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(event) {
    const field = event.target;
    field.style.borderColor = '';
    
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function showFormErrors(errors) {
    // Remove existing error container
    const existingErrors = document.querySelector('.form-errors');
    if (existingErrors) {
        existingErrors.remove();
    }
    
    // Create error container
    const errorContainer = document.createElement('div');
    errorContainer.className = 'form-errors';
    errorContainer.style.cssText = `
        background: rgba(255, 68, 68, 0.1);
        border: 1px solid #ff4444;
        color: #ff4444;
        padding: 16px;
        margin-bottom: 24px;
        font-size: 14px;
    `;
    
    const errorList = document.createElement('ul');
    errorList.style.margin = '0';
    errorList.style.paddingLeft = '20px';
    
    errors.forEach(error => {
        const li = document.createElement('li');
        li.textContent = error;
        li.style.marginBottom = '4px';
        errorList.appendChild(li);
    });
    
    errorContainer.appendChild(errorList);
    
    // Insert at the top of the form
    const form = document.getElementById('registrationForm');
    form.insertBefore(errorContainer, form.firstChild);
    
    // Scroll to errors
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function clearFormErrors() {
    const errorContainer = document.querySelector('.form-errors');
    if (errorContainer) {
        errorContainer.remove();
    }
}

function showSuccessMessage() {
    // Remove existing success message
    const existingSuccess = document.querySelector('.form-success');
    if (existingSuccess) {
        existingSuccess.remove();
    }
    
    // Create success message
    const successContainer = document.createElement('div');
    successContainer.className = 'form-success';
    successContainer.style.cssText = `
        background: rgba(78, 255, 159, 0.1);
        border: 1px solid #4eff9f;
        color: #4eff9f;
        padding: 24px;
        margin-bottom: 24px;
        text-align: center;
        font-size: 16px;
        font-weight: 600;
    `;
    
    successContainer.innerHTML = `
        <div style="font-size: 24px; margin-bottom: 8px;">✓</div>
        <div>Registration Successful!</div>
        <div style="font-size: 14px; margin-top: 8px; font-weight: normal; color: #ccc;">
            We'll be in touch soon with payment details and course information.
        </div>
    `;
    
    // Insert at the top of the form
    const form = document.getElementById('registrationForm');
    form.insertBefore(successContainer, form.firstChild);
    
    // Scroll to success message
    successContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (successContainer.parentNode) {
            successContainer.remove();
        }
    }, 10000);
}

// Contact Form Handling
function initContactForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    
    form.addEventListener('submit', handleContactFormSubmission);
    
    // Get submit button and make it disabled initially
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.classList.add('disabled');
    }
    
    // Add real-time validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', function(event) {
            clearFieldError(event);
            checkContactFormValidity();
        });
        field.addEventListener('change', checkContactFormValidity);
    });
    
    // Initial form validity check
    checkContactFormValidity();
}

function checkContactFormValidity() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (!submitButton) return;
    
    // Get all required fields
    const name = form.querySelector('#name');
    const email = form.querySelector('#email');
    const message = form.querySelector('#message');
    
    // Check if all required fields are filled
    const isValid = name.value.trim() !== '' &&
                   email.value.trim() !== '' &&
                   message.value.trim() !== '';
    
    // Enable/disable button based on validity
    if (isValid) {
        submitButton.disabled = false;
        submitButton.classList.remove('disabled');
    } else {
        submitButton.disabled = true;
        submitButton.classList.add('disabled');
    }
}

function handleContactFormSubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Convert form data to object
    const contactData = {};
    for (let [key, value] of formData.entries()) {
        contactData[key] = value.trim();
    }
    
    // Validate form
    if (!validateContactForm(contactData)) {
        return;
    }
    
    // Disable submit button and show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'SENDING...';
    
    // Simulate form submission (replace with actual submission logic)
    setTimeout(() => {
        showContactSuccessMessage();
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        
        // Log the contact data (replace with actual submission to server)
        console.log('Contact Data:', contactData);
        
        // Reset form after successful submission
        form.reset();
        checkContactFormValidity();
    }, 2000);
}

function validateContactForm(data) {
    const errors = [];
    
    // Required field validation
    if (!data.name) errors.push('Name is required');
    if (!data.email) errors.push('Email address is required');
    if (!data.message) errors.push('Message is required');
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (data.email && !emailRegex.test(data.email)) {
        errors.push('Please enter a valid email address');
    }
    
    if (errors.length > 0) {
        showFormErrors(errors);
        return false;
    }
    
    clearFormErrors();
    return true;
}

function showContactSuccessMessage() {
    // Remove existing success message
    const existingSuccess = document.querySelector('.form-success');
    if (existingSuccess) {
        existingSuccess.remove();
    }
    
    // Create success message
    const successContainer = document.createElement('div');
    successContainer.className = 'form-success';
    successContainer.style.cssText = `
        background: rgba(78, 255, 159, 0.1);
        border: 1px solid #4eff9f;
        color: #4eff9f;
        padding: 24px;
        margin-bottom: 24px;
        text-align: center;
        font-size: 16px;
        font-weight: 600;
    `;
    
    successContainer.innerHTML = `
        <div style="font-size: 24px; margin-bottom: 8px;">✓</div>
        <div>Message Sent Successfully!</div>
        <div style="font-size: 14px; margin-top: 8px; font-weight: normal; color: #ccc;">
            We'll get back to you as soon as possible.
        </div>
    `;
    
    // Insert at the top of the form
    const form = document.getElementById('contactForm');
    form.insertBefore(successContainer, form.firstChild);
    
    // Scroll to success message
    successContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (successContainer.parentNode) {
            successContainer.remove();
        }
    }, 10000);
}

// Initialize registration form when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTerminalAnimations();
    initCourseTimelineAnimations();
    initRegistrationForm();
    initContactForm();
});

// Make functions globally available for inline event handlers
window.switchTab = switchTab;
window.toggleFAQ = toggleFAQ;