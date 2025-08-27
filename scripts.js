// Import Perlin background functionality
import { initPerlinBackgrounds, handlePerlinResize } from './perlin-background.js';

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

// Initialize everything on load
window.addEventListener('load', async () => {
    // Load shared components first
    await Promise.all([
        loadComponent('header-component', 'components/header.html'),
        loadComponent('footer-component', 'components/footer.html')
    ]);
    
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
    
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.log('Chart.js not loaded, using fallback');
        drawFallbackChart();
        return;
    }
    
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

// Fallback chart function if Chart.js fails
function drawFallbackChart() {
    const canvas = document.getElementById('citizenDeveloperChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // High-DPI support
    const ratio = window.devicePixelRatio || 1;
    const displayWidth = 560;
    const displayHeight = 460;
    
    canvas.width = displayWidth * ratio;
    canvas.height = displayHeight * ratio;
    canvas.style.width = displayWidth + 'px';
    canvas.style.height = displayHeight + 'px';
    
    ctx.scale(ratio, ratio);
    
    const width = displayWidth;
    const height = displayHeight;
    
    // Clear canvas
    ctx.fillStyle = 'rgba(0,0,0,0.1)';
    ctx.fillRect(0, 0, width, height);
    
    // Chart data with months (2 per year)
    const data = [10, 8, 13, 16, 20, 25, 20, 22, 18, 32, 100];
    const labels = ['Aug 2020', 'Feb 2021', 'Aug 2021', 'Feb 2022', 'Aug 2022', 'Feb 2023', 'Aug 2023', 'Feb 2024', 'Aug 2024', 'May 2025', 'Aug 2025'];
    
    // Chart dimensions
    const margin = 60;
    const chartWidth = width - 2 * margin;
    const chartHeight = height - 2 * margin - 40;
    
    // Draw title
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 22px -apple-system, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('The Rise of Citizen Developers', width / 2, 35);
    
    // Draw subtitle
    ctx.fillStyle = '#999999';
    ctx.font = '12px -apple-system, sans-serif';
    ctx.fillText('Google Trends: "citizen developer" search popularity', width / 2, 55);
    
    // Calculate points
    const maxValue = Math.max(...data);
    const points = data.map((value, index) => ({
        x: margin + (index * chartWidth) / (data.length - 1),
        y: height - margin - 20 - (value / maxValue) * chartHeight
    }));
    
    // Draw grid lines
    ctx.strokeStyle = 'rgba(255,255,255,0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
        const y = height - margin - 20 - (i * chartHeight / 5);
        ctx.beginPath();
        ctx.moveTo(margin, y);
        ctx.lineTo(width - margin, y);
        ctx.stroke();
        
        // Y-axis labels
        ctx.fillStyle = '#cccccc';
        ctx.font = '12px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText((i * 20).toString(), margin - 10, y + 3);
    }
    
    // Draw area fill
    ctx.fillStyle = 'rgba(78, 255, 159, 0.1)';
    ctx.beginPath();
    ctx.moveTo(points[0].x, height - margin - 20);
    points.forEach(point => ctx.lineTo(point.x, point.y));
    ctx.lineTo(points[points.length - 1].x, height - margin - 20);
    ctx.closePath();
    ctx.fill();
    
    // Draw line
    ctx.strokeStyle = '#4eff9f';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.forEach(point => ctx.lineTo(point.x, point.y));
    ctx.stroke();
    
    // Draw points
    points.forEach((point, index) => {
        ctx.fillStyle = '#4eff9f';
        ctx.beginPath();
        ctx.arc(point.x, point.y, 4, 0, 2 * Math.PI);
        ctx.fill();
        
        // X-axis labels (stacked: month over year)
        ctx.fillStyle = '#cccccc';
        ctx.font = '11px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.textAlign = 'center';
        
        // Split label into month and year
        const [month, year] = labels[index].split(' ');
        
        // Draw month on top
        ctx.fillText(month, point.x, height - margin + 12);
        // Draw year below
        ctx.fillText(year, point.x, height - margin + 25);
    });
    
    // Draw axes
    ctx.strokeStyle = 'rgba(255,255,255,0.2)';
    ctx.lineWidth = 2;
    // Y-axis
    ctx.beginPath();
    ctx.moveTo(margin, margin);
    ctx.lineTo(margin, height - margin - 20);
    ctx.stroke();
    // X-axis
    ctx.beginPath();
    ctx.moveTo(margin, height - margin - 20);
    ctx.lineTo(width - margin, height - margin - 20);
    ctx.stroke();
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
    
    // Add real-time validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', clearFieldError);
    });
}

function handleFormSubmission(event) {
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
    
    // Simulate form submission (replace with actual submission logic)
    setTimeout(() => {
        showSuccessMessage();
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        
        // Log the registration data (replace with actual submission to server)
        console.log('Registration Data:', registrationData);
    }, 2000);
}

function validateForm(data) {
    const errors = [];
    
    // Required field validation
    if (!data.name) errors.push('Full name is required');
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

// Initialize registration form when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTerminalAnimations();
    initCourseTimelineAnimations();
    initRegistrationForm();
});

// Make functions globally available for inline event handlers
window.switchTab = switchTab;
window.toggleFAQ = toggleFAQ;