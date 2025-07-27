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

    // Intersection Observer for animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in');
        }
      });
    }, observerOptions);

    // Observe elements with animation classes
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
      observer.observe(el);
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
}