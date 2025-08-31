// Perlin Noise Flow Field Implementation
class PerlinNoise {
    constructor() {
        this.permutation = [];
        for (let i = 0; i < 256; i++) {
            this.permutation[i] = Math.floor(Math.random() * 256);
        }
        for (let i = 0; i < 256; i++) {
            this.permutation[256 + i] = this.permutation[i];
        }
    }
    
    fade(t) {
        return t * t * t * (t * (t * 6 - 15) + 10);
    }
    
    lerp(t, a, b) {
        return a + t * (b - a);
    }
    
    grad(hash, x, y) {
        const h = hash & 3;
        const u = h < 2 ? x : y;
        const v = h < 2 ? y : x;
        return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v);
    }
    
    noise(x, y) {
        const X = Math.floor(x) & 255;
        const Y = Math.floor(y) & 255;
        
        x -= Math.floor(x);
        y -= Math.floor(y);
        
        const u = this.fade(x);
        const v = this.fade(y);
        
        const a = this.permutation[X] + Y;
        const aa = this.permutation[a];
        const ab = this.permutation[a + 1];
        const b = this.permutation[X + 1] + Y;
        const ba = this.permutation[b];
        const bb = this.permutation[b + 1];
        
        return this.lerp(v, 
            this.lerp(u, this.grad(this.permutation[aa], x, y), 
                         this.grad(this.permutation[ba], x - 1, y)),
            this.lerp(u, this.grad(this.permutation[ab], x, y - 1),
                         this.grad(this.permutation[bb], x - 1, y - 1))
        );
    }
}

class GridAngle {
    constructor(x, y, r, angle) {
        this.x = x;
        this.y = y;
        this.r = r;
        this.angle = angle;
        this.vx = x + r * Math.cos(angle);
        this.vy = y + r * Math.sin(angle);
    }
}

class Particle {
    constructor(canvas, config = {}) {
        this.canvas = canvas;
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * 10;
        this.prevX = this.x;
        this.prevY = this.y;
        this.age = 0;
        this.maxAge = config.averageLifespan || (200 + Math.random() * 800); 
        if (config.colorProfile === 'red') {
            this.hue = Math.random() * 60; // Red/orange range: 0-60
        } else {
            this.hue = 90 + Math.random() * 60; // Green range: 90-150
        }
        
        this.speed = 0.5 + Math.random() * 2.5;
    }
    
    update(grid, spacing) {
        this.prevX = this.x;
        this.prevY = this.y;
        
        const gridX = Math.floor(this.x / spacing);
        const gridY = Math.floor(this.y / spacing);
        
        if (gridX >= 0 && gridX < grid.length && 
            gridY >= 0 && gridY < grid[0].length) {
            const angle = grid[gridX][gridY].angle;
            this.x += Math.cos(angle) * this.speed;
            this.y += Math.sin(angle) * this.speed;
            this.age++;
        } else {
            this.age = this.maxAge;
        }
    }
    
    draw(ctx) {
        if (this.age > 0) {
            const alpha = Math.max(0, 1 - this.age / this.maxAge) * 0.8;
            ctx.strokeStyle = `hsla(${this.hue}, 90%, 80%, ${alpha})`;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(this.prevX, this.prevY);
            ctx.lineTo(this.x, this.y);
            ctx.stroke();
        }
    }
    
    isDead() {
        return this.age >= this.maxAge || this.y > this.canvas.height;
    }
}

// Create flow field for each canvas
function createFlowField(canvasId, config = {}) {
    console.log(`Creating flow field for canvas: ${canvasId}`);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Default configuration
    const defaultConfig = {
        colorProfile: 'green', // 'green' or 'red'
        particleCount: window.innerWidth <= 768 ? 25 : 120,
        averageLifespan: 500
    };
    const finalConfig = { ...defaultConfig, ...config };
    
    const navContainer = document.querySelector('.nav-container');
    if (navContainer) {
        console.log(`Nav-container width before ${canvasId} sizing:`, navContainer.offsetWidth);
    }
    
    const ctx = canvas.getContext('2d');
    const rect = canvas.parentElement.getBoundingClientRect();
    
    console.log(`Setting ${canvasId} canvas dimensions:`, rect.width, 'x', rect.height);
    canvas.width = rect.width;
    canvas.height = rect.height;
    
    const navContainerAfter = document.querySelector('.nav-container');
    if (navContainerAfter) {
        console.log(`Nav-container width after ${canvasId} sizing:`, navContainerAfter.offsetWidth);
    }
    
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
    let particleLimit = finalConfig.particleCount;
    let frameCount = 0;
    let animationId = null;
    let isAnimating = false;
    
    function animate() {
        if (!isAnimating) return;
        
        frameCount++;
        
        if (frameCount % 2 === 0) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Add new particles
            if (particles.length < particleLimit) {
                const spawnCount = Math.min(3, particleLimit - particles.length);
                for (let i = 0; i < spawnCount; i++) {
                    particles.push(new Particle(canvas, finalConfig));
                }
            }
            
            // Update and draw particles
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].update(grid, spacing);
                particles[i].draw(ctx);
                
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
    
    // Return control functions
    return {
        start: function() {
            if (!isAnimating) {
                isAnimating = true;
                animate();
            }
        },
        stop: function() {
            isAnimating = false;
            if (animationId) {
                cancelAnimationFrame(animationId);
                animationId = null;
            }
        }
    };
}

// Store active canvas instances
const canvasInstances = new Map();

// Initialize all canvas elements with Intersection Observer
function initPerlinBackgrounds() {
    const canvasIds = ['heroCanvas', 'featuresCanvas', 'ctaCanvas'];
    
    // Create intersection observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const canvas = entry.target;
            const canvasId = canvas.id;
            
            if (entry.isIntersecting) {
                // Canvas is visible, start animation if not already running
                if (!canvasInstances.has(canvasId)) {
                    const instance = createFlowField(canvasId);
                    if (instance) {
                        canvasInstances.set(canvasId, instance);
                        instance.start();
                    }
                }
            }
            // Note: We don't stop animations once started, as requested
        });
    }, {
        threshold: 0.1, // Start when 10% of canvas is visible
        rootMargin: '50px 0px' // Start slightly before canvas enters viewport
    });
    
    // Observe all canvas elements
    canvasIds.forEach(id => {
        const canvas = document.getElementById(id);
        if (canvas) {
            observer.observe(canvas);
        }
    });
}

// Handle resize
function handlePerlinResize() {
    console.log('Handling Perlin resize');
    const navContainer = document.querySelector('.nav-container');
    if (navContainer) {
        console.log('Nav-container width before resize:', navContainer.offsetWidth);
    }
    
    const canvases = ['heroCanvas', 'featuresCanvas', 'ctaCanvas'];
    canvases.forEach(id => {
        const canvas = document.getElementById(id);
        if (canvas && canvas.parentElement) {
            const rect = canvas.parentElement.getBoundingClientRect();
            console.log(`Resizing ${id} to:`, rect.width, 'x', rect.height);
            canvas.width = rect.width;
            canvas.height = rect.height;
        }
    });
    
    const navContainerAfter = document.querySelector('.nav-container');
    if (navContainerAfter) {
        console.log('Nav-container width after resize:', navContainerAfter.offsetWidth);
    }
}

// Functions are available globally