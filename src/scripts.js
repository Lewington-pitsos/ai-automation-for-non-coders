// Perlin background functionality is loaded from perlin-background.js
// Chart functionality is loaded from chart.js

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

// Generic form validation function
function checkGenericFormValidity(formId, fieldSelectors, extraValidations = null) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (!submitButton) return;
    
    // Get all required fields and check validity
    let isValid = true;
    
    for (const selector of fieldSelectors) {
        const field = form.querySelector(selector);
        if (!field) {
            isValid = false;
            break;
        }
        
        if (field.type === 'checkbox') {
            if (!field.checked) {
                isValid = false;
                break;
            }
        } else {
            if (field.value.trim() === '' || field.value === '') {
                isValid = false;
                break;
            }
        }
    }
    
    // Run any extra validations
    if (isValid && extraValidations) {
        isValid = extraValidations(form);
    }
    
    // Enable/disable button based on validity
    if (isValid) {
        submitButton.disabled = false;
        submitButton.classList.remove('disabled');
    } else {
        submitButton.disabled = true;
        submitButton.classList.add('disabled');
    }
}

// Generic form initialization function
function initGenericForm(formId, submitHandler, validityChecker, useFieldValidation = true) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', submitHandler);
    
    // Get submit button and make it disabled initially
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.classList.add('disabled');
    }
    
    // Add real-time validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (useFieldValidation) {
            field.addEventListener('blur', validateField);
        }
        field.addEventListener('input', function(event) {
            if (useFieldValidation) {
                clearFieldError(event);
            }
            validityChecker();
        });
        field.addEventListener('change', validityChecker);
    });
    
    // Initial form validity check
    validityChecker();
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
    
    
    // Initialize Perlin backgrounds - DISABLED FOR TESTING
    initPerlinBackgrounds();
});

window.addEventListener('resize', () => {
    handlePerlinResize();
});

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

// Persona Cards Animation System
function initPersonaCards() {
    const cardsContainer = document.querySelector('.persona-cards-container');
    const cards = document.querySelectorAll('.persona-card');
    
    if (!cardsContainer || cards.length === 0) {
        return;
    }

    let animationTriggered = false;

    // Intersection observer for initial animation
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !animationTriggered) {
                animationTriggered = true;
                animateCardsIn();
            }
        });
    }, {
        threshold: 0.3,
        rootMargin: '-50px 0px'
    });

    observer.observe(cardsContainer);

    function animateCardsIn() {
        cards.forEach((card) => {
            const delay = parseInt(card.dataset.delay) || 0;
            setTimeout(() => {
                card.classList.add('visible');
            }, delay);
        });
    }

    // Mouse movement for spotlight effect and 3D tilt
    cards.forEach(card => {
        const spotlight = card.querySelector('.card-spotlight');
        
        card.addEventListener('mouseenter', (e) => {
            // Slide the card to the right on hover
            if (!card.classList.contains('selected')) {
                card.style.transform = 'translateX(20px)';
            } else {
                // If selected, maintain the position but prepare for 3D
                card.style.transform = 'translateX(20px)';
            }
        });
        
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Always move spotlight to cursor position
            spotlight.style.left = x + 'px';
            spotlight.style.top = y + 'px';
        });
        
        card.addEventListener('mouseleave', () => {
            if (card.classList.contains('selected')) {
                card.style.transform = 'translateX(20px)';
            } else {
                card.style.transform = '';
            }
        });
    });
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
        threshold: window.innerWidth <= 768 ? 0.05 : 0.2,
        rootMargin: window.innerWidth <= 768 ? '100px 0px' : '-50px 0px'
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
    initPersonaCards();
    initCourseTimelineAnimations();
});




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


// Application Form Handling
function initApplicationForm() {
    const config = {
        endpoint: 'livestream', // Use livestream endpoint but with application type
        loadingText: 'SUBMITTING APPLICATION...',
        validationFn: (data) => {
            // Add registration_type to data
            data.registration_type = 'application';
            
            // Combine firstName and lastName into name
            if (data.firstName || data.lastName) {
                data.name = `${data.firstName || ''} ${data.lastName || ''}`.trim();
            }
            
            // Validate required fields
            const requiredFields = ['name', 'email', 'phone', 'company', 'jobTitle', 'timeCommitment', 'automationInterest', 'automationBarriers'];
            for (const field of requiredFields) {
                if (!data[field]) {
                    return { isValid: false, error: `Please fill in all required fields` };
                }
            }
            
            // Validate attendance checkbox
            if (!data.attendance) {
                return { isValid: false, error: 'You must confirm you can attend both in person sessions' };
            }
            
            // Validate consent checkbox
            if (!data.contactConsent) {
                return { isValid: false, error: 'You must consent to being contacted about this course' };
            }
            
            // Validate terms checkbox
            if (!data.terms) {
                return { isValid: false, error: 'You must agree to the terms and conditions' };
            }
            
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(data.email)) {
                return { isValid: false, error: 'Please enter a valid email address' };
            }
            
            return { isValid: true };
        },
        successMessage: 'Thanks for taking the time to apply, we take all applications seriously and will respond within 48 hours',
        errorMessage: 'There was an error submitting your application. Please try again later or contact us directly.',
        validityChecker: checkApplicationFormValidity
    };
    initGenericForm('applicationForm', (event) => handleGenericFormSubmission(event, config), checkApplicationFormValidity, true);
}

function checkApplicationFormValidity() {
    checkGenericFormValidity('applicationForm', [
        '#firstName[required]',
        '#lastName[required]', 
        '#email[required]',
        '#phone[required]',
        '#company[required]',
        '#jobTitle[required]',
        '#timeCommitment[required]',
        '#automationInterest[required]',
        '#automationBarriers[required]',
        '#attendance[required]',
        '#contactConsent[required]',
        '#terms[required]'
    ]);
}

// Livestream Form Handling
function initLivestreamForm() {
    const config = {
        endpoint: 'livestream',
        loadingText: 'SIGNING UP...',
        validationFn: validateLivestreamFormData,
        successMessage: 'You\'re registered for the livestream!<br>Check your email for confirmation and access details.',
        errorMessage: 'There was an error processing your livestream registration, please try again in 24 hours or reach out to louka on <a href="https://www.linkedin.com/in/louka-ewington-pitsos-2a92b21a0/" target="_blank" style="color: #4eff9f;">linkedin</a>',
        validityChecker: checkLivestreamFormValidity
    };
    initGenericForm('livestreamForm', (event) => handleGenericFormSubmission(event, config), checkLivestreamFormValidity, true);
}

function checkLivestreamFormValidity() {
    const form = document.getElementById('livestreamForm');
    if (!form) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (!submitButton) return;
    
    // Get form data to validate
    const formData = new FormData(form);
    const livestreamData = {};
    for (let [key, value] of formData.entries()) {
        livestreamData[key] = value.trim();
    }
    
    // Use the same validation logic as form submission
    const validationResult = validateLivestreamFormData(livestreamData);
    const isValid = validationResult.isValid;
    
    // Enable/disable button based on validity
    if (isValid) {
        submitButton.disabled = false;
        submitButton.classList.remove('disabled');
    } else {
        submitButton.disabled = true;
        submitButton.classList.add('disabled');
    }
}

function validateLivestreamFormData(data) {
    if (!data.name || !data.email) {
        return { isValid: false, error: 'Please fill in all required fields' };
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
        return { isValid: false, error: 'Please enter a valid email address' };
    }
    return { isValid: true };
}

function showGenericSuccessMessage(message) {
    // Get toast container
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    // Clear any existing toasts
    toastContainer.innerHTML = '';
    
    // Show container
    toastContainer.classList.add('active');
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    // Create Perlin noise canvas
    const canvas = document.createElement('canvas');
    canvas.className = 'toast-perlin-bg';
    toast.appendChild(canvas);
    
    // Add content
    const content = document.createElement('div');
    content.className = 'toast-content';
    content.innerHTML = `
        <div class="toast-corner top-left"></div>
        <div class="toast-corner top-right"></div>
        <div class="toast-corner bottom-left"></div>
        <div class="toast-corner bottom-right"></div>
        <div class="toast-message">
            ${message}
        </div>
        <button class="toast-dismiss">DISMISS</button>
    `;
    toast.appendChild(content);
    
    // Add to container with animation
    toastContainer.appendChild(toast);
    
    // Initialize Perlin noise animation with green particles
    initToastPerlinNoise(canvas, { colorProfile: 'green' });
    
    // Dismiss function
    const dismissToast = () => {
        // Add slide out animation
        toast.style.animation = 'toastSlideOut 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards';
        
        // Re-enable scroll
        document.body.style.overflow = '';
        
        // Hide container after animation
        setTimeout(() => {
            toastContainer.classList.remove('active');
            toastContainer.innerHTML = '';
        }, 500);
    };
    
    // Add dismiss button handler
    const dismissButton = toast.querySelector('.toast-dismiss');
    dismissButton.addEventListener('click', dismissToast);
    
    // Auto-dismiss after 10 seconds
    setTimeout(dismissToast, 10000);
    
    // Disable scroll on body while toast is active
    document.body.style.overflow = 'hidden';
}


function showGenericErrorMessage(message) {
    // Get toast container
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    // Clear any existing toasts
    toastContainer.innerHTML = '';
    
    // Show container
    toastContainer.classList.add('active');
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    // Create Perlin noise canvas
    const canvas = document.createElement('canvas');
    canvas.className = 'toast-perlin-bg';
    toast.appendChild(canvas);
    
    // Add content
    const content = document.createElement('div');
    content.className = 'toast-content';
    content.innerHTML = `
        <div class="toast-corner top-left"></div>
        <div class="toast-corner top-right"></div>
        <div class="toast-corner bottom-left"></div>
        <div class="toast-corner bottom-right"></div>
        <div class="toast-message">
            ${message}
        </div>
        <button class="toast-dismiss">DISMISS</button>
    `;
    toast.appendChild(content);
    
    // Add to container with animation
    toastContainer.appendChild(toast);
    
    // Initialize Perlin noise animation with red particles
    initToastPerlinNoise(canvas, { colorProfile: 'red' });
    
    // Dismiss function
    const dismissToast = () => {
        // Add slide out animation
        toast.style.animation = 'toastSlideOut 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards';
        
        // Re-enable scroll
        document.body.style.overflow = '';
        
        // Hide container after animation
        setTimeout(() => {
            toastContainer.classList.remove('active');
            toastContainer.innerHTML = '';
        }, 500);
    };
    
    // Add dismiss button handler
    const dismissButton = toast.querySelector('.toast-dismiss');
    dismissButton.addEventListener('click', dismissToast);
    
    // Auto-dismiss after 10 seconds
    setTimeout(dismissToast, 10000);
    
    // Disable scroll on body while toast is active
    document.body.style.overflow = 'hidden';
}



// Contact Form Handling
function initContactForm() {
    const config = {
        endpoint: 'contact',
        loadingText: 'SENDING...',
        validationFn: validateContactFormData,
        successMessage: 'Your message has been received by our team.<br>We will respond ASAP, thanks for reaching out.',
        errorMessage: 'There was an error processing your query, please try again in 24 hours or reach out to louka on <a href="https://www.linkedin.com/in/louka-ewington-pitsos-2a92b21a0/" target="_blank" style="color: #4eff9f;">linkedin</a>',
        validityChecker: checkContactFormValidity
    };
    initGenericForm('contactForm', (event) => handleGenericFormSubmission(event, config), checkContactFormValidity, true);
}

function checkContactFormValidity() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (!submitButton) return;
    
    // Get form data to validate
    const formData = new FormData(form);
    const contactData = {};
    for (let [key, value] of formData.entries()) {
        contactData[key] = value.trim();
    }
    
    // Use the same validation logic as form submission
    const validationResult = validateContactFormData(contactData);
    const isValid = validationResult.isValid;
    
    // Enable/disable button based on validity
    if (isValid) {
        submitButton.disabled = false;
        submitButton.classList.remove('disabled');
    } else {
        submitButton.disabled = true;
        submitButton.classList.add('disabled');
    }
}

function validateContactFormData(data) {
    // Required field validation
    if (!data.name || !data.email || !data.mobile || !data.message) {
        return { isValid: false, error: 'Please fill in all required fields' };
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
        return { isValid: false, error: 'Please enter a valid email address' };
    }
    
    // Phone validation - allow various formats
    const phoneRegex = /^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,4}$/;
    if (!phoneRegex.test(data.mobile.replace(/\s/g, ''))) {
        return { isValid: false, error: 'Please enter a valid mobile phone number' };
    }
    
    return { isValid: true };
}

// Generic form submission handler
async function handleGenericFormSubmission(event, config) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Convert form data to object
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value.trim();
    }
    
    // Validate form
    const validation = config.validationFn(data);
    if (!validation.isValid) {
        showGenericErrorMessage(validation.error);
        return;
    }
    
    // Disable submit button and show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = config.loadingText;
    
    try {
        // Wait for config to load if needed
        if (typeof configPromise !== 'undefined') {
            await configPromise;
        }
        
        // Build API URL
        const apiUrl = typeof API_CONFIG !== 'undefined' && API_CONFIG.API_URL 
            ? `${API_CONFIG.API_URL}/${config.endpoint}`
            : `https://YOUR_API_GATEWAY_URL/prod/${config.endpoint}`;
        
        // Send form data to Lambda
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            // Show success toast
            showGenericSuccessMessage(config.successMessage);
            
            // Reset form after successful submission
            form.reset();
            config.validityChecker();
        } else {
            // Handle error responses
            console.log('Error response status:', response.status);
            
            let errorMessage = config.errorMessage;
            
            // Try to get error message from response
            try {
                const errorResult = await response.json();
                if (errorResult.error) {
                    errorMessage = errorResult.error;
                }
            } catch (jsonError) {
                console.log('Could not parse error response JSON');
            }
            
            showGenericErrorMessage(errorMessage);
        }
    } catch (error) {
        console.error(`${config.endpoint} form error:`, error);
        // Show generic error message
        showGenericErrorMessage(config.errorMessage);
    } finally {
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    }
}


// Initialize Perlin noise for toast background using existing system
function initToastPerlinNoise(canvas, config = {}) {
    // Give the canvas a temporary ID
    const tempId = 'toastPerlinCanvas';
    canvas.id = tempId;
    
    // Set canvas size - extend height above and below popup for invisible particle areas
    const rect = canvas.parentElement.getBoundingClientRect();
    const exitBuffer = 5; // Extra height below popup
    canvas.width = rect.width;
    canvas.height = rect.height + exitBuffer;
    
    // Position canvas so the extra height is above the visible popup
    canvas.style.position = 'absolute';
    canvas.style.top = `-1px`;
    canvas.style.left = '0';
    
    // Use the existing createFlowField function but modify it for toast
    const ctx = canvas.getContext('2d');
    const spacing = 15;
    const rez = 0.1;
    const grid = [];
    const perlin = new PerlinNoise();
    
    // Create grid
    const radius = spacing / 2;
    for (let x = 0; x < canvas.width - radius; x += spacing) {
        const row = [];
        for (let y = 0; y < canvas.height - radius; y += spacing) {
            const noiseValue = (perlin.noise(x * rez, y * rez) + 1) * 0.5;
            const angle = noiseValue * Math.PI * 2;
            const biasedAngle = angle * 0.5;
            row.push(new GridAngle(x, y, radius, biasedAngle));
        }
        grid.push(row);
    }
    
    let particles = [];
    let particleLimit = 45; // Fewer particles for smaller toast
    let frameCount = 0;
    let animationId = null;
    let isAnimating = true;
    
    function animate() {
        if (!isAnimating) return;
        
        frameCount++;
        
        if (frameCount % 2 === 0) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Add new particles - spawn them in the buffer area above visible popup
            if (particles.length < particleLimit) {
                const spawnCount = Math.min(2, particleLimit - particles.length);
                for (let i = 0; i < spawnCount; i++) {
                    const particle = new Particle(canvas, config);
                    // Override spawn position to be in the buffer area above visible popup
                    particle.y = 0; // Spawn in buffer area above popup
                    particles.push(particle);
                }
            }
            
            // Update and draw particles
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].update(grid, spacing);
                particles[i].draw(ctx);
                
                // Check if particle is dead - use actual visible popup height for bottom boundary
                if (particles[i].isDead()) {
                    particles.splice(i, 1);
                }
            }
        }
        
        animationId = requestAnimationFrame(animate);
    }
    
    // Clear canvas initially
    ctx.fillStyle = 'rgba(0, 0, 0, 0)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Start animation
    animate();
    
    // Clean up when toast is removed
    const observer = new MutationObserver(() => {
        if (!document.contains(canvas)) {
            isAnimating = false;
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
            observer.disconnect();
        }
    });
    observer.observe(canvas.parentElement.parentElement, { childList: true });
}


// Animate numbers in the course details section
function animateNumbers() {
    const statNumbers = document.querySelectorAll('.stat-number');
    const totalNumber = document.querySelector('.total-number');
    
    // Set up intersection observer to trigger animation when section comes into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Animate stat numbers
                statNumbers.forEach((numberEl, index) => {
                    const targetNumber = parseInt(numberEl.textContent);
                    numberEl.textContent = '0';
                    
                    setTimeout(() => {
                        animateCounter(numberEl, 0, targetNumber, 1000);
                    }, index * 200);
                });
                
                // Animate total number
                if (totalNumber) {
                    setTimeout(() => {
                        animateCounter(totalNumber, 0, 14.5, 1500, true);
                    }, 600);
                }
                
                observer.disconnect();
            }
        });
    }, { threshold: 0.3 });
    
    const courseDetails = document.querySelector('.sessions-highlight');
    if (courseDetails) {
        observer.observe(courseDetails);
    }
}

function animateCounter(element, start, end, duration, isDecimal = false) {
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * easeOut;
        
        if (isDecimal) {
            element.textContent = current.toFixed(1);
        } else {
            element.textContent = Math.floor(current);
        }
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = isDecimal ? end.toFixed(1) : end;
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Stagger animation for detail cards
function initDetailCardAnimations() {
    const cards = document.querySelectorAll('.detail-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Initialize Feature Cards Animation System
function initFeatureCards() {
    const featureItems = document.querySelectorAll('.feature-item');
    
    if (featureItems.length === 0) {
        return;
    }

    let animationTriggered = false;

    // Intersection observer for initial animation
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !animationTriggered) {
                animationTriggered = true;
                animateFeatureCardsIn();
            }
        });
    }, {
        threshold: 0.2,
        rootMargin: '-50px 0px'
    });

    // Observe the features section
    const featuresSection = document.querySelector('.features-grid');
    if (featuresSection) {
        observer.observe(featuresSection);
    }

    function animateFeatureCardsIn() {
        featureItems.forEach((card, index) => {
            const delay = index * 200; // Stagger the animations
            setTimeout(() => {
                card.classList.add('visible');
            }, delay);
        });
    }
}


// Initialize forms when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Audio hover functionality for CTA buttons
    const hoverAudio = new Audio('assets/audio/621849__welvynzportersamples__slow-building-synth-riser-uplifter.wav');
    hoverAudio.volume = 0.2;
    hoverAudio.loop = false;
    hoverAudio.preload = 'auto';
    
    // Ensure audio is loaded
    hoverAudio.load();
    
    // Track if audio context is unlocked
    let audioUnlocked = false;
    
    // Function to unlock audio on user interaction
    const unlockAudio = () => {
        if (!audioUnlocked) {
            // Create a temporary silent audio to unlock the context
            const silentAudio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+DyvmwhBjiS1/LNeSsFJHfH8N+PQAoUXrTp66hVFApGn+Dyvmw=');
            silentAudio.volume = 0.01;
            silentAudio.play().then(() => {
                audioUnlocked = true;
                silentAudio.pause();
                // Now preload the actual audio
                hoverAudio.load();
            }).catch(() => {
                // Still locked, will try again on next interaction
            });
        }
    };
    
    // Try to unlock on any click or key press (more reliable than mousemove)
    document.addEventListener('click', unlockAudio);
    document.addEventListener('keydown', unlockAudio);
    document.addEventListener('touchstart', unlockAudio);
    
    const ctaButtons = document.querySelectorAll('.cta-button');
    
    ctaButtons.forEach(button => {
        let shakeInterval;
        let shakeStartTime;
        let isShaking = false;
        
        // Store original transition
        const originalTransition = window.getComputedStyle(button).transition;
        
        // Skip effects for buttons with no-effects class
        const skipEffects = button.classList.contains('no-effects');
        
        button.addEventListener('mouseenter', function() {
            if (skipEffects) return;
            
            // Only play audio if unlocked
            if (audioUnlocked) {
                // Stop and reset audio before playing
                hoverAudio.pause();
                hoverAudio.currentTime = 0;
                
                // Play with promise handling
                const playPromise = hoverAudio.play();
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        // Silently fail - audio might still be loading
                    });
                }
            } else {
                // Try to unlock audio context on hover
                unlockAudio();
            }
            
            // Disable transitions for shaking
            button.style.transition = 'none';
            
            // Start shaking animation
            shakeStartTime = Date.now();
            shakeInterval = setInterval(() => {
                const elapsed = (Date.now() - shakeStartTime) / 1000;
                
                // Stop shaking at 23.5 seconds
                if (elapsed >= 23.5) {
                    clearInterval(shakeInterval);
                    button.style.setProperty('transform', '', '');
                    return;
                }
                
                // Exponential buildup: starts slow, gets intense near the end
                // Using power function for more dramatic buildup
                const progress = elapsed / 23.5; // 0 to 1 over 23.5 seconds
                const intensity = Math.pow(progress, 2.5) * 30; // Exponential growth up to 30px
                
                const x = (Math.random() - 0.5) * intensity;
                const y = (Math.random() - 0.5) * intensity;
                const rotation = (Math.random() - 0.5) * intensity * 0.5; // Less rotation
                
                button.style.setProperty('transform', `translate(${x}px, ${y}px) rotate(${rotation}deg)`, 'important');
            }, 20);
        });
        
        button.addEventListener('mouseleave', function() {
            if (skipEffects) return;
            
            hoverAudio.pause();
            hoverAudio.currentTime = 0;
            
            // Stop shaking and reset
            clearInterval(shakeInterval);
            button.style.setProperty('transform', '', '');
            button.style.transition = originalTransition;
        });
    });
    
    initPersonaCards();
    initCourseTimelineAnimations();
    initFeatureCards();
    initApplicationForm();
    initContactForm();
    initLivestreamForm();
    animateNumbers();
    initDetailCardAnimations();
});

// Make functions globally available for inline event handlers
window.toggleFAQ = toggleFAQ;




function initRegistrationForm() {
    initGenericForm('registrationForm', handleFormSubmission, checkFormValidity, true);
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
    
    // Check if this is an auto-fill registration (has applicant_id)
    const applicantId = form.getAttribute('data-applicant-id');
    if (applicantId) {
        registrationData.applicant_id = applicantId;
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
    const apiUrl = `${API_CONFIG.API_URL}/register`;
    
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
            referral_source: 'applied',
            automation_interest: registrationData.automationInterest || '',
            dietary_requirements: 'none',
            course_id: API_CONFIG.COURSE_ID || '01_ai_automation_for_non_coders',
            ...(registrationData.applicant_id && { applicant_id: registrationData.applicant_id })
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw data;
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.registration_id) {
            
            // Store registration ID for later use
            sessionStorage.setItem('registrationId', data.registration_id);
            sessionStorage.setItem('registrationData', JSON.stringify(registrationData));
            
            // Append registration_id and email to Stripe URL
            const stripeUrl = typeof API_CONFIG !== 'undefined' && API_CONFIG.STRIPE_PAYMENT_LINK
            const email = encodeURIComponent(registrationData.email);
            // Pass registration_id as client_reference_id and prefill email
            window.location.href = `${stripeUrl}?client_reference_id=${data.registration_id}&prefilled_email=${email}`;
        } else {
            throw new Error('Registration failed');
        }
    })
    .catch(error => {
        console.error('Registration error:', error);
        
        // Check for specific error types
        if (error.error === 'email_already_registered') {
            showFormErrors(['This email has already been registered for this course. Please use a different email address or contact support if you need assistance.']);
        } else {
            showFormErrors(['Registration failed. Please try again or contact support.']);
        }
        
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
    if (!data.company) errors.push('Company is required');
    if (!data.jobTitle) errors.push('Job title is required');
    
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