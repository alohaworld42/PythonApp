/**
 * Advanced Features for BuyRoll
 * Enhanced functionality and interactions
 */

class AdvancedFeatures {
    constructor() {
        this.init();
    }

    init() {
        this.setupDarkMode();
        this.setupAdvancedSearch();
        this.setupRealTimeFeatures();
        this.setupPWAFeatures();
        this.setupAdvancedAnimations();
        this.setupPerformanceMonitoring();
        this.setupAccessibilityEnhancements();
        this.setupAdvancedInteractions();
    }

    // Dark Mode Implementation
    setupDarkMode() {
        const themeToggle = this.createThemeToggle();
        const savedTheme = localStorage.getItem('theme') || 'auto';
        
        this.applyTheme(savedTheme);
        this.setupThemeToggleEvents(themeToggle);
        this.watchSystemTheme();
    }

    createThemeToggle() {
        const themeToggle = document.createElement('button');
        themeToggle.className = 'theme-toggle';
        themeToggle.setAttribute('aria-label', 'Toggle dark mode');
        themeToggle.innerHTML = `
            <div class="theme-toggle-indicator">
                <i class="fas fa-sun sun-icon"></i>
                <i class="fas fa-moon moon-icon"></i>
            </div>
        `;

        // Add to navigation
        const navActions = document.querySelector('.nav .flex.items-center.space-x-4');
        if (navActions) {
            navActions.insertBefore(themeToggle, navActions.firstChild);
        }

        return themeToggle;
    }

    applyTheme(theme) {
        const root = document.documentElement;
        
        if (theme === 'dark') {
            root.setAttribute('data-theme', 'dark');
        } else if (theme === 'light') {
            root.setAttribute('data-theme', 'light');
        } else {
            // Auto mode - follow system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            root.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
        }
        
        localStorage.setItem('theme', theme);
    }

    setupThemeToggleEvents(themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            this.applyTheme(newTheme);
            
            // Add ripple effect
            this.addRippleEffect(themeToggle);
        });
    }

    watchSystemTheme() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'auto') {
                this.applyTheme('auto');
            }
        });
    }

    // Advanced Search with Filters
    setupAdvancedSearch() {
        this.createAdvancedSearchModal();
        this.setupSearchFilters();
        this.setupSearchHistory();
        this.setupSearchSuggestions();
    }

    createAdvancedSearchModal() {
        const modal = document.createElement('div');
        modal.className = 'search-modal';
        modal.innerHTML = `
            <div class="search-modal-backdrop"></div>
            <div class="search-modal-content">
                <div class="search-modal-header">
                    <h3>Advanced Search</h3>
                    <button class="search-modal-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="search-modal-body">
                    <div class="search-input-container">
                        <input type="text" class="advanced-search-input" placeholder="Search products, brands, categories...">
                        <button class="search-voice-btn" title="Voice Search">
                            <i class="fas fa-microphone"></i>
                        </button>
                    </div>
                    
                    <div class="search-filters">
                        <div class="filter-group">
                            <label>Category</label>
                            <select class="filter-category">
                                <option value="">All Categories</option>
                                <option value="electronics">Electronics</option>
                                <option value="clothing">Clothing</option>
                                <option value="home">Home & Garden</option>
                                <option value="sports">Sports</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label>Price Range</label>
                            <div class="price-range-slider">
                                <input type="range" class="price-min" min="0" max="1000" value="0">
                                <input type="range" class="price-max" min="0" max="1000" value="1000">
                                <div class="price-display">
                                    <span class="price-min-display">$0</span> - 
                                    <span class="price-max-display">$1000</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="filter-group">
                            <label>Rating</label>
                            <div class="rating-filter">
                                <button class="rating-btn" data-rating="5">
                                    <i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i>
                                    & up
                                </button>
                                <button class="rating-btn" data-rating="4">
                                    <i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="far fa-star"></i>
                                    & up
                                </button>
                                <button class="rating-btn" data-rating="3">
                                    <i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="far fa-star"></i><i class="far fa-star"></i>
                                    & up
                                </button>
                            </div>
                        </div>
                        
                        <div class="filter-group">
                            <label>Sort By</label>
                            <select class="filter-sort">
                                <option value="relevance">Relevance</option>
                                <option value="price-low">Price: Low to High</option>
                                <option value="price-high">Price: High to Low</option>
                                <option value="rating">Customer Rating</option>
                                <option value="newest">Newest First</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="search-suggestions">
                        <h4>Popular Searches</h4>
                        <div class="suggestion-tags">
                            <button class="suggestion-tag">wireless headphones</button>
                            <button class="suggestion-tag">smart watch</button>
                            <button class="suggestion-tag">laptop stand</button>
                            <button class="suggestion-tag">coffee maker</button>
                        </div>
                    </div>
                    
                    <div class="search-history">
                        <h4>Recent Searches</h4>
                        <div class="history-list"></div>
                    </div>
                </div>
                
                <div class="search-modal-footer">
                    <button class="btn btn-outline search-clear">Clear All</button>
                    <button class="btn btn-primary search-apply">Search</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        this.setupSearchModalEvents(modal);
    }

    setupSearchModalEvents(modal) {
        const backdrop = modal.querySelector('.search-modal-backdrop');
        const closeBtn = modal.querySelector('.search-modal-close');
        const clearBtn = modal.querySelector('.search-clear');
        const applyBtn = modal.querySelector('.search-apply');
        
        // Open modal when clicking search input
        document.querySelectorAll('[data-search-input]').forEach(input => {
            input.addEventListener('focus', () => {
                modal.classList.add('active');
                document.body.classList.add('modal-open');
            });
        });
        
        // Close modal
        [backdrop, closeBtn].forEach(element => {
            element.addEventListener('click', () => {
                modal.classList.remove('active');
                document.body.classList.remove('modal-open');
            });
        });
        
        // Clear filters
        clearBtn.addEventListener('click', () => {
            this.clearSearchFilters(modal);
        });
        
        // Apply search
        applyBtn.addEventListener('click', () => {
            this.performAdvancedSearch(modal);
        });
    }

    // Real-time Features
    setupRealTimeFeatures() {
        this.setupLiveNotifications();
        this.setupRealTimeUpdates();
        this.setupCollaborativeFeatures();
    }

    setupLiveNotifications() {
        // Simulate real-time notifications
        setInterval(() => {
            if (Math.random() > 0.7) {
                this.showLiveNotification();
            }
        }, 30000); // Every 30 seconds
    }

    showLiveNotification() {
        const notifications = [
            { type: 'info', message: 'New product added by @sarah_m', icon: 'fas fa-plus' },
            { type: 'success', message: 'Your product got 5 new likes!', icon: 'fas fa-heart' },
            { type: 'info', message: '@john_doe shared your product', icon: 'fas fa-share' },
            { type: 'warning', message: 'Price drop alert on Wireless Headphones', icon: 'fas fa-tag' }
        ];
        
        const notification = notifications[Math.floor(Math.random() * notifications.length)];
        
        if (window.BuyRollApp) {
            const app = new window.BuyRollApp();
            app.showNotification(notification.message, notification.type, 5000);
        }
    }

    // PWA Features
    setupPWAFeatures() {
        this.registerServiceWorker();
        this.setupInstallPrompt();
        this.setupOfflineSupport();
        this.setupPushNotifications();
    }

    registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/sw.js')
                .then(registration => {
                    console.log('SW registered:', registration);
                })
                .catch(error => {
                    console.log('SW registration failed:', error);
                });
        }
    }

    setupInstallPrompt() {
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            this.showInstallButton(deferredPrompt);
        });
    }

    showInstallButton(deferredPrompt) {
        const installBtn = document.createElement('button');
        installBtn.className = 'fab install-btn';
        installBtn.innerHTML = '<i class="fas fa-download"></i>';
        installBtn.title = 'Install BuyRoll App';
        
        installBtn.addEventListener('click', () => {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                }
                deferredPrompt = null;
                installBtn.remove();
            });
        });
        
        document.body.appendChild(installBtn);
    }

    // Advanced Animations
    setupAdvancedAnimations() {
        this.setupScrollAnimations();
        this.setupParallaxEffects();
        this.setupMorphingElements();
        this.setupParticleEffects();
    }

    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, observerOptions);

        // Observe elements for scroll animations
        document.querySelectorAll('.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right').forEach(el => {
            observer.observe(el);
        });
    }

    setupParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        window.addEventListener('scroll', this.throttle(() => {
            const scrollTop = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = parseFloat(element.dataset.parallax) || 0.5;
                const yPos = -(scrollTop * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        }, 16));
    }

    setupMorphingElements() {
        document.querySelectorAll('.morphing-icon').forEach(icon => {
            icon.addEventListener('click', () => {
                icon.classList.toggle('active');
            });
        });
    }

    setupParticleEffects() {
        const heroSection = document.querySelector('.hero');
        if (heroSection) {
            this.createParticleBackground(heroSection);
        }
    }

    createParticleBackground(container) {
        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'particles-bg';
        
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 5) + 's';
            particlesContainer.appendChild(particle);
        }
        
        container.appendChild(particlesContainer);
    }

    // Performance Monitoring
    setupPerformanceMonitoring() {
        this.monitorPageLoad();
        this.monitorUserInteractions();
        this.setupLazyLoading();
        this.optimizeImages();
    }

    monitorPageLoad() {
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
            
            console.log(`Page load time: ${loadTime}ms`);
            
            // Send to analytics if needed
            if (loadTime > 3000) {
                console.warn('Slow page load detected');
            }
        });
    }

    monitorUserInteractions() {
        let interactionCount = 0;
        
        ['click', 'scroll', 'keydown'].forEach(eventType => {
            document.addEventListener(eventType, () => {
                interactionCount++;
            });
        });
        
        // Report interaction data periodically
        setInterval(() => {
            if (interactionCount > 0) {
                console.log(`User interactions in last minute: ${interactionCount}`);
                interactionCount = 0;
            }
        }, 60000);
    }

    // Accessibility Enhancements
    setupAccessibilityEnhancements() {
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.setupFocusManagement();
        this.setupColorContrastAdjustment();
    }

    setupKeyboardNavigation() {
        // Enhanced keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Escape key closes modals
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
            
            // Tab navigation improvements
            if (e.key === 'Tab') {
                this.highlightFocusableElements();
            }
        });
    }

    setupScreenReaderSupport() {
        // Add ARIA live regions for dynamic content
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'live-region';
        document.body.appendChild(liveRegion);
    }

    announceToScreenReader(message) {
        const liveRegion = document.getElementById('live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    }

    // Advanced Interactions
    setupAdvancedInteractions() {
        this.setupGestureSupport();
        this.setupVoiceCommands();
        this.setupSmartSuggestions();
        this.setupContextualMenus();
    }

    setupGestureSupport() {
        // Touch gesture support for mobile
        let startX, startY, endX, endY;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            this.handleGesture(startX, startY, endX, endY);
        });
    }

    handleGesture(startX, startY, endX, endY) {
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const minSwipeDistance = 50;
        
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
            if (deltaX > 0) {
                // Swipe right
                this.handleSwipeRight();
            } else {
                // Swipe left
                this.handleSwipeLeft();
            }
        }
    }

    setupVoiceCommands() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onresult = (event) => {
                const command = event.results[0][0].transcript.toLowerCase();
                this.processVoiceCommand(command);
            };
            
            // Add voice search button functionality
            document.querySelectorAll('.search-voice-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    recognition.start();
                    btn.classList.add('listening');
                });
            });
            
            recognition.onend = () => {
                document.querySelectorAll('.search-voice-btn').forEach(btn => {
                    btn.classList.remove('listening');
                });
            };
        }
    }

    processVoiceCommand(command) {
        if (command.includes('search for')) {
            const query = command.replace('search for', '').trim();
            this.performSearch(query);
        } else if (command.includes('go to dashboard')) {
            window.location.href = '/dashboard';
        } else if (command.includes('dark mode')) {
            this.applyTheme('dark');
        } else if (command.includes('light mode')) {
            this.applyTheme('light');
        }
    }

    // Utility Functions
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    debounce(func, wait, immediate) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    }

    addRippleEffect(element) {
        const ripple = document.createElement('div');
        ripple.className = 'ripple-effect';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    closeAllModals() {
        document.querySelectorAll('.modal, .search-modal').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.classList.remove('modal-open');
    }

    highlightFocusableElements() {
        document.body.classList.add('keyboard-navigation');
    }

    performSearch(query) {
        console.log('Performing search for:', query);
        // Implement actual search functionality
    }

    handleSwipeRight() {
        // Handle swipe right gesture
        console.log('Swipe right detected');
    }

    handleSwipeLeft() {
        // Handle swipe left gesture
        console.log('Swipe left detected');
    }
}

// Initialize advanced features
document.addEventListener('DOMContentLoaded', () => {
    window.advancedFeatures = new AdvancedFeatures();
});

// Export for use in other modules
window.AdvancedFeatures = AdvancedFeatures;