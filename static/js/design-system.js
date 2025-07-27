// BuyRoll Design System JavaScript

class BuyRollDesignSystem {
  constructor() {
    this.init();
  }

  init() {
    this.setupNavigation();
    this.setupModals();
    this.setupNotifications();
    this.setupFormValidation();
    this.setupScrollEffects();
    this.setupAccessibility();
  }

  // Navigation System
  setupNavigation() {
    const nav = document.querySelector('.nav');
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    // Mobile menu toggle
    if (navToggle && navMenu) {
      navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('show');
        navToggle.setAttribute('aria-expanded', 
          navToggle.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'
        );
      });

      // Close menu when clicking outside
      document.addEventListener('click', (e) => {
        if (!nav.contains(e.target)) {
          navMenu.classList.remove('show');
          navToggle.setAttribute('aria-expanded', 'false');
        }
      });

      // Close menu on escape key
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && navMenu.classList.contains('show')) {
          navMenu.classList.remove('show');
          navToggle.setAttribute('aria-expanded', 'false');
          navToggle.focus();
        }
      });
    }

    // Scroll effect for navigation
    if (nav) {
      let lastScrollY = window.scrollY;
      
      window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 100) {
          nav.classList.add('scrolled');
        } else {
          nav.classList.remove('scrolled');
        }

        // Hide/show nav on scroll
        if (currentScrollY > lastScrollY && currentScrollY > 200) {
          nav.style.transform = 'translateY(-100%)';
        } else {
          nav.style.transform = 'translateY(0)';
        }
        
        lastScrollY = currentScrollY;
      });
    }

    // Active link highlighting
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section[id]');

    if (navLinks.length && sections.length) {
      window.addEventListener('scroll', () => {
        let current = '';
        
        sections.forEach(section => {
          const sectionTop = section.offsetTop;
          const sectionHeight = section.clientHeight;
          
          if (window.scrollY >= sectionTop - 200) {
            current = section.getAttribute('id');
          }
        });

        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
          }
        });
      });
    }
  }

  // Modal System
  setupModals() {
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    const modalCloses = document.querySelectorAll('[data-modal-close]');
    const modals = document.querySelectorAll('.modal');

    modalTriggers.forEach(trigger => {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        const targetModal = document.querySelector(trigger.dataset.modalTarget);
        this.openModal(targetModal);
      });
    });

    modalCloses.forEach(close => {
      close.addEventListener('click', () => {
        const modal = close.closest('.modal');
        this.closeModal(modal);
      });
    });

    // Close modal on backdrop click
    modals.forEach(modal => {
      const backdrop = modal.querySelector('.modal-backdrop');
      if (backdrop) {
        backdrop.addEventListener('click', (e) => {
          if (e.target === backdrop) {
            this.closeModal(modal);
          }
        });
      }
    });

    // Close modal on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
          this.closeModal(openModal);
        }
      }
    });
  }

  openModal(modal) {
    if (!modal) return;
    
    modal.classList.add('show');
    const backdrop = modal.querySelector('.modal-backdrop');
    if (backdrop) backdrop.classList.add('show');
    
    document.body.style.overflow = 'hidden';
    
    // Focus management
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusableElements.length) {
      focusableElements[0].focus();
    }
  }

  closeModal(modal) {
    if (!modal) return;
    
    modal.classList.remove('show');
    const backdrop = modal.querySelector('.modal-backdrop');
    if (backdrop) backdrop.classList.remove('show');
    
    document.body.style.overflow = '';
  }

  // Notification System
  setupNotifications() {
    this.notificationContainer = this.createNotificationContainer();
  }

  createNotificationContainer() {
    let container = document.querySelector('.notification-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'notification-container';
      container.style.cssText = `
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1080;
        pointer-events: none;
      `;
      document.body.appendChild(container);
    }
    return container;
  }

  showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} show`;
    notification.style.pointerEvents = 'auto';
    
    const icon = this.getNotificationIcon(type);
    notification.innerHTML = `
      <div class="flex items-center gap-3">
        <span class="text-lg">${icon}</span>
        <span class="flex-1">${message}</span>
        <button class="notification-close text-gray-400 hover:text-black">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;

    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
      this.hideNotification(notification);
    });

    this.notificationContainer.appendChild(notification);

    // Auto-hide after duration
    if (duration > 0) {
      setTimeout(() => {
        this.hideNotification(notification);
      }, duration);
    }

    return notification;
  }

  hideNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }

  getNotificationIcon(type) {
    const icons = {
      success: '<i class="fas fa-check-circle text-success"></i>',
      error: '<i class="fas fa-exclamation-circle text-error"></i>',
      warning: '<i class="fas fa-exclamation-triangle text-warning"></i>',
      info: '<i class="fas fa-info-circle text-info"></i>'
    };
    return icons[type] || icons.info;
  }

  // Form Validation
  setupFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
      const inputs = form.querySelectorAll('input, textarea, select');
      
      inputs.forEach(input => {
        input.addEventListener('blur', () => this.validateField(input));
        input.addEventListener('input', () => this.clearFieldError(input));
      });

      form.addEventListener('submit', (e) => {
        if (!this.validateForm(form)) {
          e.preventDefault();
        }
      });
    });
  }

  validateField(field) {
    const value = field.value.trim();
    const rules = field.dataset.rules ? field.dataset.rules.split('|') : [];
    let isValid = true;
    let errorMessage = '';

    // Required validation
    if (rules.includes('required') && !value) {
      isValid = false;
      errorMessage = 'This field is required';
    }

    // Email validation
    if (rules.includes('email') && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
      }
    }

    // Min length validation
    const minLength = rules.find(rule => rule.startsWith('min:'));
    if (minLength && value) {
      const min = parseInt(minLength.split(':')[1]);
      if (value.length < min) {
        isValid = false;
        errorMessage = `Minimum ${min} characters required`;
      }
    }

    // Max length validation
    const maxLength = rules.find(rule => rule.startsWith('max:'));
    if (maxLength && value) {
      const max = parseInt(maxLength.split(':')[1]);
      if (value.length > max) {
        isValid = false;
        errorMessage = `Maximum ${max} characters allowed`;
      }
    }

    this.showFieldValidation(field, isValid, errorMessage);
    return isValid;
  }

  validateForm(form) {
    const inputs = form.querySelectorAll('input[data-rules], textarea[data-rules], select[data-rules]');
    let isFormValid = true;

    inputs.forEach(input => {
      if (!this.validateField(input)) {
        isFormValid = false;
      }
    });

    return isFormValid;
  }

  showFieldValidation(field, isValid, message) {
    const errorElement = field.parentNode.querySelector('.form-error');
    
    if (isValid) {
      field.classList.remove('invalid');
      if (errorElement) {
        errorElement.remove();
      }
    } else {
      field.classList.add('invalid');
      
      if (!errorElement) {
        const error = document.createElement('span');
        error.className = 'form-error';
        error.textContent = message;
        field.parentNode.appendChild(error);
      } else {
        errorElement.textContent = message;
      }
    }
  }

  clearFieldError(field) {
    field.classList.remove('invalid');
    const errorElement = field.parentNode.querySelector('.form-error');
    if (errorElement) {
      errorElement.remove();
    }
  }

  // Scroll Effects
  setupScrollEffects() {
    // Smooth scroll for anchor links
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

    // Intersection Observer for scroll animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Add fade-in animation
          if (entry.target.classList.contains('scroll-fade-in')) {
            entry.target.classList.add('in-view');
          }
          // Add slide animations
          if (entry.target.classList.contains('scroll-slide-left')) {
            entry.target.classList.add('in-view');
          }
          if (entry.target.classList.contains('scroll-slide-right')) {
            entry.target.classList.add('in-view');
          }
          // Add scale animation
          if (entry.target.classList.contains('scroll-scale-up')) {
            entry.target.classList.add('in-view');
          }
          // Generic animate-on-scroll
          if (entry.target.classList.contains('animate-on-scroll')) {
            entry.target.classList.add('animate-fade-in');
          }
        }
      });
    }, observerOptions);

    // Observe elements with scroll animation classes
    const scrollElements = document.querySelectorAll(
      '.animate-on-scroll, .scroll-fade-in, .scroll-slide-left, .scroll-slide-right, .scroll-scale-up'
    );
    scrollElements.forEach(el => observer.observe(el));

    // Parallax effect
    this.setupParallax();
    
    // Stagger animations
    this.setupStaggerAnimations();
  }

  setupParallax() {
    const parallaxElements = document.querySelectorAll('.parallax');
    
    if (parallaxElements.length) {
      window.addEventListener('scroll', this.throttle(() => {
        const scrolled = window.pageYOffset;
        
        parallaxElements.forEach(element => {
          const rate = scrolled * -0.5;
          element.style.transform = `translateY(${rate}px)`;
        });
      }, 16));
    }
  }

  setupStaggerAnimations() {
    const staggerGroups = document.querySelectorAll('[data-stagger]');
    
    staggerGroups.forEach(group => {
      const children = group.children;
      const delay = parseInt(group.dataset.stagger) || 100;
      
      Array.from(children).forEach((child, index) => {
        child.style.animationDelay = `${index * delay}ms`;
      });
    });
  }

  // Accessibility Features
  setupAccessibility() {
    // Skip link functionality
    const skipLink = document.querySelector('.skip-link');
    if (skipLink) {
      skipLink.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(skipLink.getAttribute('href'));
        if (target) {
          target.focus();
          target.scrollIntoView();
        }
      });
    }

    // Keyboard navigation for custom components
    this.setupKeyboardNavigation();
    
    // Focus management
    this.setupFocusManagement();
  }

  setupKeyboardNavigation() {
    // Tab navigation for custom dropdowns
    document.querySelectorAll('[role="button"]').forEach(button => {
      button.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          button.click();
        }
      });
    });
  }

  setupFocusManagement() {
    // Focus visible polyfill
    let hadKeyboardEvent = true;
    const keyboardThrottleTimeout = 100;

    const focusTriggersKeyboardModality = (e) => {
      if (e.metaKey || e.altKey || e.ctrlKey) {
        return false;
      }

      switch (e.key) {
        case 'Control':
        case 'Shift':
        case 'Meta':
        case 'Alt':
          return false;
        default:
          return true;
      }
    };

    const onKeyDown = (e) => {
      if (focusTriggersKeyboardModality(e)) {
        hadKeyboardEvent = true;
      }
    };

    const onPointerDown = () => {
      hadKeyboardEvent = false;
    };

    const onFocus = (e) => {
      if (hadKeyboardEvent || e.target.matches(':focus-visible')) {
        e.target.classList.add('focus-visible');
      }
    };

    const onBlur = (e) => {
      e.target.classList.remove('focus-visible');
    };

    document.addEventListener('keydown', onKeyDown, true);
    document.addEventListener('mousedown', onPointerDown, true);
    document.addEventListener('focus', onFocus, true);
    document.addEventListener('blur', onBlur, true);
  }

  // Utility Methods
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

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
}

// Initialize the design system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.buyrollDS = new BuyRollDesignSystem();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BuyRollDesignSystem;
}  // Adva
nced Layout Management
  setupAdvancedLayouts() {
    this.setupMasonryLayout();
    this.setupStickyElements();
    this.setupResponsiveGrids();
  }

  setupMasonryLayout() {
    const masonryContainers = document.querySelectorAll('.masonry');
    
    masonryContainers.forEach(container => {
      // Simple masonry implementation
      const resizeObserver = new ResizeObserver(() => {
        this.layoutMasonry(container);
      });
      
      resizeObserver.observe(container);
      
      // Initial layout
      setTimeout(() => this.layoutMasonry(container), 100);
    });
  }

  layoutMasonry(container) {
    const items = container.querySelectorAll('.masonry-item');
    const columnCount = parseInt(getComputedStyle(container).columnCount);
    
    if (columnCount === 1) return;
    
    const columnHeights = new Array(columnCount).fill(0);
    
    items.forEach(item => {
      const shortestColumn = columnHeights.indexOf(Math.min(...columnHeights));
      item.style.order = shortestColumn;
      columnHeights[shortestColumn] += item.offsetHeight;
    });
  }

  setupStickyElements() {
    const stickyElements = document.querySelectorAll('.sticky-header, .sticky-sidebar, .sticky-footer');
    
    stickyElements.forEach(element => {
      const observer = new IntersectionObserver(
        ([entry]) => {
          element.classList.toggle('is-stuck', !entry.isIntersecting);
        },
        { threshold: 1 }
      );
      
      observer.observe(element);
    });
  }

  setupResponsiveGrids() {
    const responsiveGrids = document.querySelectorAll('[data-responsive-grid]');
    
    responsiveGrids.forEach(grid => {
      const config = JSON.parse(grid.dataset.responsiveGrid);
      
      const updateGrid = () => {
        const width = window.innerWidth;
        let columns = config.default || 1;
        
        Object.keys(config).forEach(breakpoint => {
          if (breakpoint !== 'default' && width >= parseInt(breakpoint)) {
            columns = config[breakpoint];
          }
        });
        
        grid.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
      };
      
      updateGrid();
      window.addEventListener('resize', this.debounce(updateGrid, 250));
    });
  }

  // Theme Management
  setupThemeToggle() {
    const themeToggle = document.querySelector('[data-theme-toggle]');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: newTheme } }));
      });
    }
  }

  // Advanced Form Features
  setupAdvancedForms() {
    this.setupAutoSave();
    this.setupFormProgress();
    this.setupConditionalFields();
  }

  setupAutoSave() {
    const autoSaveForms = document.querySelectorAll('[data-auto-save]');
    
    autoSaveForms.forEach(form => {
      const inputs = form.querySelectorAll('input, textarea, select');
      const saveKey = form.dataset.autoSave;
      
      // Load saved data
      const savedData = localStorage.getItem(`autosave_${saveKey}`);
      if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(name => {
          const input = form.querySelector(`[name="${name}"]`);
          if (input) input.value = data[name];
        });
      }
      
      // Save on input
      inputs.forEach(input => {
        input.addEventListener('input', this.debounce(() => {
          const formData = new FormData(form);
          const data = Object.fromEntries(formData.entries());
          localStorage.setItem(`autosave_${saveKey}`, JSON.stringify(data));
        }, 1000));
      });
      
      // Clear on submit
      form.addEventListener('submit', () => {
        localStorage.removeItem(`autosave_${saveKey}`);
      });
    });
  }

  setupFormProgress() {
    const progressForms = document.querySelectorAll('[data-form-progress]');
    
    progressForms.forEach(form => {
      const progressBar = form.querySelector('.form-progress-bar');
      const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
      
      if (!progressBar) return;
      
      const updateProgress = () => {
        const filledInputs = Array.from(inputs).filter(input => input.value.trim() !== '');
        const progress = (filledInputs.length / inputs.length) * 100;
        progressBar.style.width = `${progress}%`;
      };
      
      inputs.forEach(input => {
        input.addEventListener('input', updateProgress);
      });
      
      updateProgress();
    });
  }

  setupConditionalFields() {
    const conditionalFields = document.querySelectorAll('[data-show-if]');
    
    conditionalFields.forEach(field => {
      const condition = field.dataset.showIf;
      const [targetName, expectedValue] = condition.split('=');
      const targetInput = document.querySelector(`[name="${targetName}"]`);
      
      if (!targetInput) return;
      
      const toggleField = () => {
        const shouldShow = targetInput.value === expectedValue;
        field.style.display = shouldShow ? 'block' : 'none';
        
        // Toggle required attribute
        const requiredInputs = field.querySelectorAll('[data-required-if]');
        requiredInputs.forEach(input => {
          input.required = shouldShow;
        });
      };
      
      targetInput.addEventListener('change', toggleField);
      toggleField(); // Initial check
    });
  }

  // Initialize all advanced features
  initAdvancedFeatures() {
    this.setupAdvancedLayouts();
    this.setupThemeToggle();
    this.setupAdvancedForms();
  }
}

// Update initialization to include advanced features
document.addEventListener('DOMContentLoaded', () => {
  window.buyrollDS = new BuyRollDesignSystem();
  window.buyrollDS.initAdvancedFeatures();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BuyRollDesignSystem;
}