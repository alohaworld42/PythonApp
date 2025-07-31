/**
 * BuyRoll Main JavaScript
 * Handles core functionality and interactions
 */

class BuyRollApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupScrollEffects();
        this.setupSearchFunctionality();
        this.setupNotifications();
        this.setupProductInteractions();
    }

    setupEventListeners() {
        // DOM Content Loaded
        document.addEventListener('DOMContentLoaded', () => {
            this.onDOMReady();
        });

        // Window Load
        window.addEventListener('load', () => {
            this.onWindowLoad();
        });

        // Scroll Events
        window.addEventListener('scroll', this.throttle(() => {
            this.handleScroll();
        }, 16));

        // Resize Events
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }

    onDOMReady() {
        // Initialize loading states
        this.hideLoadingSpinners();
        
        // Setup form validation
        this.setupFormValidation();
        
        // Initialize tooltips
        this.initializeTooltips();
        
        // Setup keyboard navigation
        this.setupKeyboardNavigation();
    }

    onWindowLoad() {
        // Trigger scroll animations
        this.triggerScrollAnimations();
        
        // Preload critical images
        this.preloadImages();
        
        // Initialize lazy loading
        this.setupLazyLoading();
    }

    initializeComponents() {
        // Mobile menu toggle
        this.setupMobileMenu();
        
        // User dropdown menu
        this.setupUserMenu();
        
        // Search functionality
        this.setupSearch();
        
        // Product cards
        this.setupProductCards();
        
        // Newsletter form
        this.setupNewsletterForm();
    }

    setupMobileMenu() {
        const mobileMenuToggle = document.querySelector('[data-mobile-menu-toggle]');
        const mobileMenu = document.querySelector('[data-mobile-menu]');
        
        if (mobileMenuToggle && mobileMenu) {
            mobileMenuToggle.addEventListener('click', () => {
                const isOpen = mobileMenu.classList.contains('open');
                
                if (isOpen) {
                    this.closeMobileMenu();
                } else {
                    this.openMobileMenu();
                }
            });

            // Close on outside click
            document.addEventListener('click', (e) => {
                if (!mobileMenuToggle.contains(e.target) && !mobileMenu.contains(e.target)) {
                    this.closeMobileMenu();
                }
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeMobileMenu();
                }
            });
        }
    }

    openMobileMenu() {
        const mobileMenu = document.querySelector('[data-mobile-menu]');
        const mobileMenuToggle = document.querySelector('[data-mobile-menu-toggle]');
        
        if (mobileMenu) {
            mobileMenu.classList.add('open');
            document.body.classList.add('mobile-menu-open');
            
            // Update toggle icon
            if (mobileMenuToggle) {
                const icon = mobileMenuToggle.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-times text-lg';
                }
            }
        }
    }

    closeMobileMenu() {
        const mobileMenu = document.querySelector('[data-mobile-menu]');
        const mobileMenuToggle = document.querySelector('[data-mobile-menu-toggle]');
        
        if (mobileMenu) {
            mobileMenu.classList.remove('open');
            document.body.classList.remove('mobile-menu-open');
            
            // Update toggle icon
            if (mobileMenuToggle) {
                const icon = mobileMenuToggle.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-bars text-lg';
                }
            }
        }
    }

    setupUserMenu() {
        const userMenuToggle = document.querySelector('[data-user-menu-toggle]');
        const userMenu = document.querySelector('[data-user-menu]');
        
        if (userMenuToggle && userMenu) {
            userMenuToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                userMenu.classList.toggle('open');
            });

            // Close on outside click
            document.addEventListener('click', () => {
                userMenu.classList.remove('open');
            });
        }
    }

    setupSearchFunctionality() {
        const searchInputs = document.querySelectorAll('[data-search-input]');
        
        searchInputs.forEach(input => {
            input.addEventListener('input', this.debounce((e) => {
                this.handleSearch(e.target.value);
            }, 300));

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch(e.target.value);
                }
            });
        });
    }

    handleSearch(query) {
        if (query.length < 2) {
            this.clearSearchResults();
            return;
        }

        // Show loading state
        this.showSearchLoading();

        // Simulate API call (replace with actual search)
        setTimeout(() => {
            this.displaySearchResults(query);
        }, 500);
    }

    performSearch(query) {
        if (!query.trim()) return;
        
        // Redirect to search results page or filter current results
        console.log('Performing search for:', query);
        
        // Example: window.location.href = `/search?q=${encodeURIComponent(query)}`;
    }

    showSearchLoading() {
        const searchResults = document.querySelector('[data-search-results]');
        if (searchResults) {
            searchResults.innerHTML = '<div class="loading-container"><div class="loading-spinner"></div></div>';
            searchResults.classList.add('visible');
        }
    }

    displaySearchResults(query) {
        const searchResults = document.querySelector('[data-search-results]');
        if (!searchResults) return;

        // Mock search results (replace with actual data)
        const mockResults = [
            { title: 'Product 1', description: 'Description 1', url: '#' },
            { title: 'Product 2', description: 'Description 2', url: '#' }
        ].filter(item => 
            item.title.toLowerCase().includes(query.toLowerCase()) ||
            item.description.toLowerCase().includes(query.toLowerCase())
        );

        if (mockResults.length === 0) {
            searchResults.innerHTML = '<div class="no-results">No results found</div>';
        } else {
            const resultsHTML = mockResults.map(result => `
                <div class="search-result-item">
                    <h4>${result.title}</h4>
                    <p>${result.description}</p>
                    <a href="${result.url}">View Product</a>
                </div>
            `).join('');
            
            searchResults.innerHTML = resultsHTML;
        }
        
        searchResults.classList.add('visible');
    }

    clearSearchResults() {
        const searchResults = document.querySelector('[data-search-results]');
        if (searchResults) {
            searchResults.classList.remove('visible');
        }
    }

    setupProductCards() {
        const productCards = document.querySelectorAll('.product-card');
        
        productCards.forEach(card => {
            // Add hover effects
            card.addEventListener('mouseenter', () => {
                card.classList.add('hovered');
            });
            
            card.addEventListener('mouseleave', () => {
                card.classList.remove('hovered');
            });

            // Setup favorite buttons
            const favoriteBtn = card.querySelector('[data-favorite-btn]');
            if (favoriteBtn) {
                favoriteBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleFavorite(favoriteBtn);
                });
            }

            // Setup share buttons
            const shareBtn = card.querySelector('[data-share-btn]');
            if (shareBtn) {
                shareBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.shareProduct(card);
                });
            }
        });
    }

    toggleFavorite(btn) {
        const icon = btn.querySelector('i');
        const isFavorited = btn.classList.contains('favorited');
        
        if (isFavorited) {
            btn.classList.remove('favorited');
            icon.className = 'fas fa-heart';
            this.showNotification('Removed from favorites', 'info');
        } else {
            btn.classList.add('favorited');
            icon.className = 'fas fa-heart';
            btn.style.color = '#ef4444';
            this.showNotification('Added to favorites', 'success');
        }
    }

    shareProduct(card) {
        const title = card.querySelector('.product-card-title')?.textContent || 'Product';
        const url = window.location.href;
        
        if (navigator.share) {
            navigator.share({
                title: title,
                url: url
            }).catch(console.error);
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(url).then(() => {
                this.showNotification('Link copied to clipboard', 'success');
            }).catch(() => {
                this.showNotification('Failed to copy link', 'error');
            });
        }
    }

    setupScrollEffects() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        this.scrollObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements with scroll animation classes
        const animatedElements = document.querySelectorAll('.scroll-fade-in, .feature-card, .product-card');
        animatedElements.forEach(el => {
            this.scrollObserver.observe(el);
        });
    }

    handleScroll() {
        const scrollTop = window.pageYOffset;
        
        // Update navigation background
        this.updateNavigationBackground(scrollTop);
        
        // Update scroll progress
        this.updateScrollProgress();
        
        // Parallax effects
        this.updateParallaxEffects(scrollTop);
    }

    updateNavigationBackground(scrollTop) {
        const nav = document.querySelector('.nav');
        if (nav) {
            if (scrollTop > 50) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }
        }
    }

    updateScrollProgress() {
        const scrollProgress = document.querySelector('[data-scroll-progress]');
        if (scrollProgress) {
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrolled = (window.pageYOffset / scrollHeight) * 100;
            scrollProgress.style.width = `${scrolled}%`;
        }
    }

    updateParallaxEffects(scrollTop) {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        parallaxElements.forEach(element => {
            const speed = element.dataset.parallax || 0.5;
            const yPos = -(scrollTop * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }

    setupNotifications() {
        // Create notification container if it doesn't exist
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'info', duration = 3000) {
        const container = document.querySelector('.notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add close functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.removeNotification(notification);
        });

        // Add to container
        container.appendChild(notification);

        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Auto remove
        setTimeout(() => {
            this.removeNotification(notification);
        }, duration);
    }

    removeNotification(notification) {
        notification.classList.add('removing');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });

            // Real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
                
                input.addEventListener('input', () => {
                    this.clearFieldError(input);
                });
            });
        });
    }

    validateForm(form) {
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        let isValid = true;
        let errorMessage = '';

        // Required validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }

        // Email validation
        if (type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }

        // URL validation
        if (type === 'url' && value && !this.isValidURL(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid URL';
        }

        // Password validation
        if (type === 'password' && value && value.length < 8) {
            isValid = false;
            errorMessage = 'Password must be at least 8 characters long';
        }

        if (isValid) {
            this.clearFieldError(field);
        } else {
            this.showFieldError(field, errorMessage);
        }

        return isValid;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        field.classList.add('error');
        
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.textContent = message;
        
        field.parentNode.appendChild(errorElement);
    }

    clearFieldError(field) {
        field.classList.remove('error');
        
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidURL(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    setupNewsletterForm() {
        const newsletterForm = document.querySelector('[data-newsletter-form]');
        
        if (newsletterForm) {
            newsletterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleNewsletterSubmission(newsletterForm);
            });
        }
    }

    handleNewsletterSubmission(form) {
        const email = form.querySelector('input[type="email"]').value;
        
        if (!this.isValidEmail(email)) {
            this.showNotification('Please enter a valid email address', 'error');
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Subscribing...';
        submitBtn.disabled = true;

        // Simulate API call
        setTimeout(() => {
            this.showNotification('Successfully subscribed to newsletter!', 'success');
            form.reset();
            
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }, 1000);
    }

    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => {
            imageObserver.observe(img);
        });
    }

    preloadImages() {
        const criticalImages = document.querySelectorAll('img[data-preload]');
        
        criticalImages.forEach(img => {
            const imageUrl = img.src || img.dataset.src;
            if (imageUrl) {
                const preloadImg = new Image();
                preloadImg.src = imageUrl;
            }
        });
    }

    hideLoadingSpinners() {
        const spinners = document.querySelectorAll('.loading-spinner');
        spinners.forEach(spinner => {
            spinner.style.display = 'none';
        });
    }

    triggerScrollAnimations() {
        const animatedElements = document.querySelectorAll('.animate-fade-in');
        animatedElements.forEach((element, index) => {
            setTimeout(() => {
                element.classList.add('animate-in');
            }, index * 100);
        });
    }

    setupKeyboardNavigation() {
        // Tab navigation improvements
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    }

    initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target);
            });
            
            element.addEventListener('mouseleave', (e) => {
                this.hideTooltip(e.target);
            });
        });
    }

    showTooltip(element) {
        const tooltipText = element.dataset.tooltip;
        if (!tooltipText) return;

        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
        
        element._tooltip = tooltip;
    }

    hideTooltip(element) {
        if (element._tooltip) {
            element._tooltip.remove();
            delete element._tooltip;
        }
    }

    handleResize() {
        // Close mobile menu on resize to desktop
        if (window.innerWidth >= 768) {
            this.closeMobileMenu();
        }
        
        // Recalculate any position-dependent elements
        this.recalculatePositions();
    }

    recalculatePositions() {
        // Recalculate tooltip positions, modal positions, etc.
        const tooltips = document.querySelectorAll('.tooltip');
        tooltips.forEach(tooltip => tooltip.remove());
    }

    // Utility functions
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
}

// Initialize the app
const buyRollApp = new BuyRollApp();

// Export for use in other modules
window.BuyRollApp = BuyRollApp;