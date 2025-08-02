// Design System JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Password toggle functionality
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('border-red-500');
                } else {
                    field.classList.remove('border-red-500');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Add loading states to buttons
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                this.disabled = true;
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
                
                // Re-enable after form submission (you can adjust this timing)
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = originalText;
                }, 3000);
            }
        });
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // Initialize tooltips
    const tooltipElements = document.querySelectorAll('[title]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const title = this.getAttribute('title');
            if (title) {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = title;
                tooltip.style.cssText = `
                    position: absolute;
                    background: var(--color-gray-900);
                    color: white;
                    padding: var(--space-2) var(--space-3);
                    border-radius: var(--radius-md);
                    font-size: var(--font-size-xs);
                    z-index: 1000;
                    pointer-events: none;
                    white-space: nowrap;
                `;
                
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
                
                this.addEventListener('mouseleave', function() {
                    tooltip.remove();
                }, { once: true });
            }
        });
    });
    
    // Add focus styles to interactive elements
    const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
    interactiveElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.classList.add('ring-2', 'ring-primary-500', 'ring-opacity-50');
        });
        
        element.addEventListener('blur', function() {
            this.classList.remove('ring-2', 'ring-primary-500', 'ring-opacity-50');
        });
    });
    
    // Initialize animations for elements with data-animate attribute
    const animatedElements = document.querySelectorAll('[data-animate]');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
    
    // Handle mobile menu toggle
    const mobileMenuToggle = document.querySelector('[data-mobile-menu-toggle]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            const isOpen = mobileMenu.classList.contains('hidden');
            if (isOpen) {
                mobileMenu.classList.remove('hidden');
                this.setAttribute('aria-expanded', 'true');
            } else {
                mobileMenu.classList.add('hidden');
                this.setAttribute('aria-expanded', 'false');
            }
        });
    }
    
    // Handle dropdown menus
    const dropdownToggles = document.querySelectorAll('[data-dropdown-toggle]');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = document.querySelector(this.getAttribute('data-dropdown-toggle'));
            if (dropdown) {
                const isOpen = !dropdown.classList.contains('hidden');
                
                // Close all other dropdowns
                document.querySelectorAll('[data-dropdown]').forEach(d => {
                    d.classList.add('hidden');
                });
                
                if (!isOpen) {
                    dropdown.classList.remove('hidden');
                }
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('[data-dropdown-toggle]') && !e.target.closest('[data-dropdown]')) {
            document.querySelectorAll('[data-dropdown]').forEach(dropdown => {
                dropdown.classList.add('hidden');
            });
        }
    });
    
    // Handle search functionality
    const searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(input => {
        let searchTimeout;
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Implement search functionality here
                console.log('Searching for:', this.value);
            }, 300);
        });
    });
    
    // Handle like/unlike functionality
    const likeButtons = document.querySelectorAll('[data-like]');
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const icon = this.querySelector('i');
            const isLiked = icon.classList.contains('fas');
            
            if (isLiked) {
                icon.classList.remove('fas', 'text-red-500');
                icon.classList.add('far', 'text-gray-400');
            } else {
                icon.classList.remove('far', 'text-gray-400');
                icon.classList.add('fas', 'text-red-500');
            }
            
            // You can add AJAX call here to update the like status
            console.log('Like toggled:', !isLiked);
        });
    });
    
    // Handle share functionality
    const shareButtons = document.querySelectorAll('[data-share]');
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-share');
            
            if (navigator.share) {
                navigator.share({
                    title: 'Check out this product on BuyRoll',
                    url: url
                });
            } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(url).then(() => {
                    // Show success message
                    const message = document.createElement('div');
                    message.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg z-50';
                    message.textContent = 'Link copied to clipboard!';
                    document.body.appendChild(message);
                    
                    setTimeout(() => {
                        message.remove();
                    }, 3000);
                });
            }
        });
    });
    
    // Initialize lazy loading for images
    const lazyImages = document.querySelectorAll('img[data-src]');
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
    
    lazyImages.forEach(img => {
        imageObserver.observe(img);
    });
    
    // Handle theme switching (if implemented)
    const themeToggle = document.querySelector('[data-theme-toggle]');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
    
    // Initialize theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    }
    
    console.log('Design System JavaScript loaded successfully!');
});