// Modern Interactions for BuyRoll Social E-commerce

class BuyRollInteractions {
    constructor() {
        this.init();
    }

    init() {
        this.setupScrollAnimations();
        this.setupProductCards();
        this.setupSearchFunctionality();
        this.setupThemeToggle();
        this.setupLoadingStates();
        this.setupTooltips();
        this.setupModals();
        this.setupInfiniteScroll();
        this.setupLazyLoading();
        this.setupSmoothScrolling();
    }

    // Scroll Animations
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe all elements with scroll-fade-in class
        document.querySelectorAll('.scroll-fade-in').forEach(el => {
            observer.observe(el);
        });

        // Stagger animations for product grids
        document.querySelectorAll('.product-card').forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
        });
    }

    // Product Card Interactions
    setupProductCards() {
        document.querySelectorAll('.product-card').forEach(card => {
            // Hover effects
            card.addEventListener('mouseenter', () => {
                card.classList.add('hover-lift');
            });

            card.addEventListener('mouseleave', () => {
                card.classList.remove('hover-lift');
            });

            // Quick view functionality
            const quickViewBtn = card.querySelector('[data-quick-view]');
            if (quickViewBtn) {
                quickViewBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.showQuickView(card.dataset.productId);
                });
            }

            // Like functionality
            const likeBtn = card.querySelector('[data-like]');
            if (likeBtn) {
                likeBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleLike(likeBtn);
                });
            }

            // Share functionality
            const shareBtn = card.querySelector('[data-share]');
            if (shareBtn) {
                shareBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.shareProduct(shareBtn);
                });
            }
        });
    }

    // Search Functionality
    setupSearchFunctionality() {
        const searchInput = document.querySelector('[data-search-input]');
        const searchResults = document.querySelector('[data-search-results]');

        if (searchInput && searchResults) {
            let searchTimeout;

            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();

                if (query.length < 2) {
                    searchResults.style.display = 'none';
                    return;
                }

                searchTimeout = setTimeout(() => {
                    this.performSearch(query, searchResults);
                }, 300);
            });

            // Close search results when clicking outside
            document.addEventListener('click', (e) => {
                if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                    searchResults.style.display = 'none';
                }
            });
        }
    }

    // Theme Toggle
    setupThemeToggle() {
        const themeToggle = document.querySelector('[data-theme-toggle]');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // Update toggle icon
                const icon = themeToggle.querySelector('i');
                if (icon) {
                    icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
                }
            });

            // Load saved theme
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        }
    }

    // Loading States
    setupLoadingStates() {
        // Show loading state for buttons
        document.querySelectorAll('[data-loading]').forEach(button => {
            button.addEventListener('click', () => {
                this.showButtonLoading(button);
            });
        });

        // Show loading state for forms
        document.querySelectorAll('form[data-loading]').forEach(form => {
            form.addEventListener('submit', () => {
                this.showFormLoading(form);
            });
        });
    }

    // Tooltips
    setupTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip-modern';
            tooltip.textContent = element.dataset.tooltip;
            document.body.appendChild(tooltip);

            element.addEventListener('mouseenter', (e) => {
                const rect = element.getBoundingClientRect();
                tooltip.style.left = rect.left + rect.width / 2 + 'px';
                tooltip.style.top = rect.top - 10 + 'px';
                tooltip.style.opacity = '1';
            });

            element.addEventListener('mouseleave', () => {
                tooltip.style.opacity = '0';
            });
        });
    }

    // Modals
    setupModals() {
        document.querySelectorAll('[data-modal]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modal;
                this.showModal(modalId);
            });
        });

        // Close modals
        document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                this.closeModal(closeBtn.closest('.modal'));
            });
        });

        // Close modal on backdrop click
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            backdrop.addEventListener('click', (e) => {
                if (e.target === backdrop) {
                    this.closeModal(backdrop.querySelector('.modal'));
                }
            });
        });
    }

    // Infinite Scroll
    setupInfiniteScroll() {
        let isLoading = false;
        let page = 1;

        const loadMoreObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !isLoading) {
                    this.loadMoreProducts(page);
                    page++;
                }
            });
        });

        const loadMoreTrigger = document.querySelector('[data-load-more]');
        if (loadMoreTrigger) {
            loadMoreObserver.observe(loadMoreTrigger);
        }
    }

    // Lazy Loading
    setupLazyLoading() {
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

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Smooth Scrolling
    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Helper Methods
    showQuickView(productId) {
        // Implementation for quick view modal
        console.log('Showing quick view for product:', productId);
    }

    toggleLike(button) {
        const icon = button.querySelector('i');
        const isLiked = button.classList.contains('liked');
        
        if (isLiked) {
            button.classList.remove('liked');
            icon.className = 'far fa-heart';
        } else {
            button.classList.add('liked');
            icon.className = 'fas fa-heart';
        }

        // Add animation
        button.classList.add('animate-pulse');
        setTimeout(() => {
            button.classList.remove('animate-pulse');
        }, 300);
    }

    shareProduct(button) {
        // Implementation for sharing functionality
        console.log('Sharing product');
        
        // Add animation
        button.classList.add('animate-pulse-glow');
        setTimeout(() => {
            button.classList.remove('animate-pulse-glow');
        }, 2000);
    }

    async performSearch(query, resultsContainer) {
        try {
            // Simulate API call
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.displaySearchResults(data, resultsContainer);
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    displaySearchResults(results, container) {
        container.innerHTML = '';
        
        if (results.length === 0) {
            container.innerHTML = '<div class="p-4 text-gray-500">No results found</div>';
        } else {
            results.forEach(result => {
                const item = document.createElement('div');
                item.className = 'p-3 hover:bg-gray-50 cursor-pointer';
                item.innerHTML = `
                    <div class="flex items-center space-x-3">
                        <img src="${result.image}" alt="${result.title}" class="w-10 h-10 rounded-lg object-cover">
                        <div>
                            <div class="font-medium text-gray-900">${result.title}</div>
                            <div class="text-sm text-gray-500">$${result.price}</div>
                        </div>
                    </div>
                `;
                container.appendChild(item);
            });
        }
        
        container.style.display = 'block';
    }

    showButtonLoading(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
        button.disabled = true;
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 2000);
    }

    showFormLoading(form) {
        const submitBtn = form.querySelector('[type="submit"]');
        if (submitBtn) {
            this.showButtonLoading(submitBtn);
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    async loadMoreProducts(page) {
        try {
            // Simulate API call
            const response = await fetch(`/api/products?page=${page}`);
            const data = await response.json();
            
            if (data.products.length > 0) {
                this.appendProducts(data.products);
            }
        } catch (error) {
            console.error('Load more error:', error);
        }
    }

    appendProducts(products) {
        const container = document.querySelector('.product-grid');
        if (container) {
            products.forEach(product => {
                const productCard = this.createProductCard(product);
                container.appendChild(productCard);
            });
        }
    }

    createProductCard(product) {
        const card = document.createElement('div');
        card.className = 'product-card scroll-fade-in';
        card.innerHTML = `
            <div class="product-image-container">
                <img src="${product.image}" alt="${product.title}" class="product-card-image">
                <div class="product-overlay">
                    <div class="flex items-center justify-center space-x-2">
                        <button class="product-action-btn" data-like>
                            <i class="far fa-heart"></i>
                        </button>
                        <button class="product-action-btn" data-share>
                            <i class="fas fa-share"></i>
                        </button>
                        <button class="product-action-btn" data-quick-view data-product-id="${product.id}">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>
            </div>
            <div class="product-card-content">
                <h3 class="product-card-title">${product.title}</h3>
                <p class="product-description">${product.description}</p>
                <div class="product-price">
                    <span class="current-price">$${product.price}</span>
                </div>
            </div>
        `;
        
        return card;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BuyRollInteractions();
});

// Export for use in other modules
window.BuyRollInteractions = BuyRollInteractions; 