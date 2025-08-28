// Frontend Performance Testing Suite
// This script measures various load time metrics and identifies bottlenecks

class PerformanceAnalyzer {
    constructor() {
        this.metrics = {
            navigation: {},
            resources: [],
            customTimings: {},
            renderMetrics: {},
            bottlenecks: []
        };
        
        // Start custom timing measurements
        this.startTime = performance.now();
        this.timingMarks = new Map();
        
        // Set up observers
        this.setupObservers();
        
        // Track when DOM is ready
        this.markTiming('dom-ready');
        
        console.log('🔍 Performance Analyzer initialized at', new Date().toISOString());
    }
    
    // Mark timing points
    markTiming(name, description = '') {
        const timestamp = performance.now();
        this.timingMarks.set(name, {
            timestamp,
            description,
            relativeTime: timestamp - this.startTime
        });
        console.log(`⏱️  ${name}: ${timestamp.toFixed(2)}ms (${(timestamp - this.startTime).toFixed(2)}ms from start)${description ? ' - ' + description : ''}`);
    }
    
    // Measure duration between two timing marks
    measureDuration(startMark, endMark) {
        const start = this.timingMarks.get(startMark);
        const end = this.timingMarks.get(endMark);
        
        if (start && end) {
            const duration = end.timestamp - start.timestamp;
            console.log(`📏 Duration ${startMark} → ${endMark}: ${duration.toFixed(2)}ms`);
            return duration;
        }
        return null;
    }
    
    // Setup performance observers
    setupObservers() {
        // Resource loading observer
        if ('PerformanceObserver' in window) {
            const resourceObserver = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    this.metrics.resources.push({
                        name: entry.name,
                        type: entry.initiatorType,
                        duration: entry.duration,
                        transferSize: entry.transferSize || 0,
                        startTime: entry.startTime
                    });
                    
                    // Log slow resources
                    if (entry.duration > 500) {
                        console.warn(`🐌 Slow resource (${entry.duration.toFixed(2)}ms):`, entry.name);
                        this.metrics.bottlenecks.push({
                            type: 'slow-resource',
                            resource: entry.name,
                            duration: entry.duration,
                            severity: entry.duration > 2000 ? 'high' : 'medium'
                        });
                    }
                });
            });
            resourceObserver.observe({entryTypes: ['resource']});
            
            // Paint observer for render metrics
            const paintObserver = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    this.metrics.renderMetrics[entry.name] = entry.startTime;
                    console.log(`🎨 ${entry.name}: ${entry.startTime.toFixed(2)}ms`);
                });
            });
            paintObserver.observe({entryTypes: ['paint']});
        }
    }
    
    // Test component loading performance
    async testComponentLoading() {
        console.log('\n📦 Testing component loading...');
        this.markTiming('component-load-start');
        
        try {
            const componentTests = [
                { id: 'header-component', path: 'components/header.html' },
                { id: 'footer-component', path: 'components/footer.html' }
            ];
            
            const loadPromises = componentTests.map(async (component) => {
                const startTime = performance.now();
                
                try {
                    const response = await fetch(component.path);
                    const html = await response.text();
                    const loadTime = performance.now() - startTime;
                    
                    console.log(`📄 ${component.path}: ${loadTime.toFixed(2)}ms`);
                    
                    return {
                        component: component.path,
                        loadTime,
                        size: html.length,
                        success: true
                    };
                } catch (error) {
                    console.error(`❌ Failed to load ${component.path}:`, error);
                    return {
                        component: component.path,
                        loadTime: performance.now() - startTime,
                        success: false,
                        error: error.message
                    };
                }
            });
            
            const results = await Promise.all(loadPromises);
            this.markTiming('component-load-end');
            
            // Analyze component load times
            results.forEach(result => {
                if (result.loadTime > 200) {
                    this.metrics.bottlenecks.push({
                        type: 'slow-component',
                        component: result.component,
                        duration: result.loadTime,
                        severity: result.loadTime > 1000 ? 'high' : 'medium'
                    });
                }
            });
            
            return results;
            
        } catch (error) {
            console.error('❌ Component loading test failed:', error);
            return null;
        }
    }
    
    // Test external resource loading
    testExternalResources() {
        console.log('\n🌐 Testing external resources...');
        
        const externalResources = [
            'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js'
        ];
        
        const resourcePromises = externalResources.map(url => {
            return new Promise((resolve) => {
                const startTime = performance.now();
                const script = document.createElement('script');
                
                script.onload = () => {
                    const loadTime = performance.now() - startTime;
                    console.log(`📚 ${url}: ${loadTime.toFixed(2)}ms`);
                    resolve({ url, loadTime, success: true });
                };
                
                script.onerror = () => {
                    const loadTime = performance.now() - startTime;
                    console.error(`❌ Failed to load ${url}: ${loadTime.toFixed(2)}ms`);
                    resolve({ url, loadTime, success: false });
                };
                
                script.src = url;
                // Don't actually append to avoid double-loading
            });
        });
        
        return Promise.all(resourcePromises);
    }
    
    // Test DOM performance
    testDOMPerformance() {
        console.log('\n🏗️  Testing DOM performance...');
        this.markTiming('dom-analysis-start');
        
        const domMetrics = {
            totalElements: document.querySelectorAll('*').length,
            totalImages: document.querySelectorAll('img').length,
            totalScripts: document.querySelectorAll('script').length,
            totalLinks: document.querySelectorAll('link').length,
            canvasElements: document.querySelectorAll('canvas').length,
            animatedElements: document.querySelectorAll('.persona-entry, .course-timeline-item, .terminal-line').length
        };
        
        console.log('📊 DOM Metrics:', domMetrics);
        
        // Test DOM query performance
        const queryStart = performance.now();
        for (let i = 0; i < 100; i++) {
            document.querySelectorAll('.course-timeline-item');
        }
        const queryTime = (performance.now() - queryStart) / 100;
        
        console.log(`🔍 Average DOM query time: ${queryTime.toFixed(3)}ms`);
        
        // Check for potential bottlenecks
        if (domMetrics.totalElements > 1000) {
            this.metrics.bottlenecks.push({
                type: 'large-dom',
                count: domMetrics.totalElements,
                severity: 'medium'
            });
        }
        
        if (domMetrics.canvasElements > 2) {
            this.metrics.bottlenecks.push({
                type: 'multiple-canvas',
                count: domMetrics.canvasElements,
                severity: 'medium'
            });
        }
        
        this.markTiming('dom-analysis-end');
        return domMetrics;
    }
    
    // Test animation performance
    testAnimationPerformance() {
        console.log('\n🎬 Testing animation systems...');
        this.markTiming('animation-test-start');
        
        const animationSystems = [
            'Perlin background animations',
            'Terminal animation system', 
            'Course timeline animations',
            'Chart.js animations'
        ];
        
        // Test frame rate during animations
        let frameCount = 0;
        let lastTime = performance.now();
        const frameTimes = [];
        
        const measureFrameRate = () => {
            const now = performance.now();
            const deltaTime = now - lastTime;
            frameTimes.push(deltaTime);
            lastTime = now;
            frameCount++;
            
            if (frameCount < 60) { // Test for 60 frames
                requestAnimationFrame(measureFrameRate);
            } else {
                const averageFrameTime = frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length;
                const fps = 1000 / averageFrameTime;
                
                console.log(`📺 Average frame time: ${averageFrameTime.toFixed(2)}ms`);
                console.log(`📺 Estimated FPS: ${fps.toFixed(1)}`);
                
                if (fps < 30) {
                    this.metrics.bottlenecks.push({
                        type: 'poor-animation-performance',
                        fps: fps,
                        severity: 'high'
                    });
                }
                
                this.markTiming('animation-test-end');
            }
        };
        
        requestAnimationFrame(measureFrameRate);
        
        return animationSystems;
    }
    
    // Analyze Navigation Timing API
    analyzeNavigationTiming() {
        console.log('\n🗺️  Analyzing navigation timing...');
        
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
            const timings = {
                'DNS Lookup': navigation.domainLookupEnd - navigation.domainLookupStart,
                'TCP Connection': navigation.connectEnd - navigation.connectStart,
                'TLS Setup': navigation.secureConnectionStart > 0 ? navigation.connectEnd - navigation.secureConnectionStart : 0,
                'Request Time': navigation.responseStart - navigation.requestStart,
                'Response Time': navigation.responseEnd - navigation.responseStart,
                'DOM Processing': navigation.domContentLoadedEventEnd - navigation.responseEnd,
                'Resource Loading': navigation.loadEventEnd - navigation.domContentLoadedEventEnd,
                'Total Load Time': navigation.loadEventEnd - navigation.navigationStart
            };
            
            console.log('⏰ Navigation Timings:');
            Object.entries(timings).forEach(([key, value]) => {
                console.log(`   ${key}: ${value.toFixed(2)}ms`);
                if (value > 1000 && key !== 'Total Load Time') {
                    this.metrics.bottlenecks.push({
                        type: 'slow-navigation-phase',
                        phase: key,
                        duration: value,
                        severity: value > 3000 ? 'high' : 'medium'
                    });
                }
            });
            
            this.metrics.navigation = timings;
        }
    }
    
    // Run comprehensive performance test
    async runFullPerformanceTest() {
        console.log('🚀 Starting comprehensive frontend performance test...');
        console.log('==========================================\n');
        
        // Navigation timing
        this.analyzeNavigationTiming();
        
        // DOM performance
        const domMetrics = this.testDOMPerformance();
        
        // Component loading
        const componentResults = await this.testComponentLoading();
        
        // External resources (commented out to avoid actual loading)
        // const resourceResults = await this.testExternalResources();
        
        // Animation performance
        this.testAnimationPerformance();
        
        // Wait a bit for all measurements to complete
        setTimeout(() => {
            this.generateReport();
        }, 2000);
    }
    
    // Generate comprehensive report
    generateReport() {
        console.log('\n📊 PERFORMANCE ANALYSIS REPORT');
        console.log('==========================================');
        
        // Summary of timing marks
        console.log('\n🏁 Key Timing Points:');
        Array.from(this.timingMarks.entries()).forEach(([name, data]) => {
            console.log(`   ${name}: ${data.relativeTime.toFixed(2)}ms`);
        });
        
        // Resource analysis
        if (this.metrics.resources.length > 0) {
            console.log('\n📦 Resource Load Analysis:');
            const slowResources = this.metrics.resources
                .filter(r => r.duration > 100)
                .sort((a, b) => b.duration - a.duration)
                .slice(0, 10);
            
            slowResources.forEach(resource => {
                console.log(`   ${resource.name}: ${resource.duration.toFixed(2)}ms (${resource.type})`);
            });
        }
        
        // Bottleneck summary
        if (this.metrics.bottlenecks.length > 0) {
            console.log('\n⚠️  IDENTIFIED BOTTLENECKS:');
            this.metrics.bottlenecks.forEach((bottleneck, index) => {
                const severity = bottleneck.severity === 'high' ? '🔴' : '🟡';
                console.log(`   ${severity} ${bottleneck.type}:`, bottleneck);
            });
        }
        
        // Recommendations
        this.generateRecommendations();
        
        // Paint timing
        if (Object.keys(this.metrics.renderMetrics).length > 0) {
            console.log('\n🎨 Render Metrics:');
            Object.entries(this.metrics.renderMetrics).forEach(([key, value]) => {
                console.log(`   ${key}: ${value.toFixed(2)}ms`);
            });
        }
        
        console.log('\n==========================================');
        console.log('Performance analysis complete! 🏁');
        
        return this.metrics;
    }
    
    // Generate specific recommendations
    generateRecommendations() {
        console.log('\n💡 PERFORMANCE RECOMMENDATIONS:');
        
        const recommendations = [];
        
        // Based on bottlenecks found
        this.metrics.bottlenecks.forEach(bottleneck => {
            switch (bottleneck.type) {
                case 'slow-resource':
                    recommendations.push(`🚀 Optimize or lazy-load: ${bottleneck.resource}`);
                    break;
                case 'slow-component':
                    recommendations.push(`📦 Consider inlining component: ${bottleneck.component}`);
                    break;
                case 'large-dom':
                    recommendations.push('🏗️  Consider virtualizing large DOM sections');
                    break;
                case 'multiple-canvas':
                    recommendations.push('🎨 Consider consolidating canvas animations');
                    break;
                case 'poor-animation-performance':
                    recommendations.push('⚡ Optimize animations, consider CSS transforms');
                    break;
            }
        });
        
        // General recommendations based on file analysis
        recommendations.push('📄 Consider preloading critical resources');
        recommendations.push('🎯 Implement progressive loading for non-critical features');
        recommendations.push('⚡ Use intersection observer for animations');
        recommendations.push('📦 Bundle and minify JavaScript files');
        
        recommendations.forEach((rec, index) => {
            console.log(`   ${index + 1}. ${rec}`);
        });
    }
    
    // Specific test for the 5-second delay issue
    investigateLoadDelay() {
        console.log('\n🔍 INVESTIGATING 5-SECOND DELAY ISSUE');
        console.log('==========================================');
        
        // Check for specific patterns that could cause delays
        const potentialCauses = [];
        
        // Check for setTimeout/setInterval calls in scripts
        const scripts = Array.from(document.querySelectorAll('script')).map(s => s.textContent || s.src);
        scripts.forEach(script => {
            if (script.includes('setTimeout') && script.includes('100')) {
                potentialCauses.push('Found setTimeout(100ms) in chart initialization - scripts.js:43');
            }
            if (script.includes('2000')) {
                potentialCauses.push('Found 2000ms delay in animation duration - scripts.js:122');
            }
        });
        
        // Check for async component loading
        if (document.getElementById('header-component') || document.getElementById('footer-component')) {
            potentialCauses.push('Async component loading may contribute to perceived delay');
        }
        
        // Check for heavy animations
        const canvases = document.querySelectorAll('canvas');
        if (canvases.length > 0) {
            potentialCauses.push(`${canvases.length} canvas elements with Perlin noise animations`);
        }
        
        // Check for large resources
        if (this.metrics.resources.some(r => r.duration > 2000)) {
            potentialCauses.push('Some resources taking >2 seconds to load');
        }
        
        console.log('🕵️  Potential causes of the 5-second delay:');
        potentialCauses.forEach((cause, index) => {
            console.log(`   ${index + 1}. ${cause}`);
        });
        
        return potentialCauses;
    }
}

// Initialize performance testing when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏃‍♂️ Starting frontend load time analysis...');
    
    const analyzer = new PerformanceAnalyzer();
    
    // Run tests after a short delay to let the page settle
    setTimeout(() => {
        analyzer.runFullPerformanceTest();
        
        // Investigate the specific 5-second delay
        setTimeout(() => {
            analyzer.investigateLoadDelay();
        }, 3000);
        
    }, 500);
});

// Export for manual testing
window.PerformanceAnalyzer = PerformanceAnalyzer;

console.log('📊 Performance testing script loaded. Check console for detailed metrics.');