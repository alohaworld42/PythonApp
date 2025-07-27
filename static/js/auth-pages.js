// BuyRoll Authentication Pages JavaScript

class AuthPages {
  constructor() {
    this.passwordStrengthRules = [
      { regex: /.{8,}/, message: 'At least 8 characters' },
      { regex: /[A-Z]/, message: 'One uppercase letter' },
      { regex: /[a-z]/, message: 'One lowercase letter' },
      { regex: /\d/, message: 'One number' },
      { regex: /[!@#$%^&*(),.?":{}|<>]/, message: 'One special character' }
    ];
    this.init();
  }

  init() {
    this.setupPasswordToggle();
    this.setupPasswordStrength();
    this.setupFormValidation();
    this.setupSocialLogin();
    this.setupTwoFactorAuth();
    this.setupFormSubmission();
    this.setupAnimations();
  }

  // Password Toggle Functionality
  setupPasswordToggle() {
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
      toggle.addEventListener('click', () => {
        const passwordInput = toggle.previousElementSibling;
        const isPassword = passwordInput.type === 'password';
        
        passwordInput.type = isPassword ? 'text' : 'password';
        toggle.innerHTML = isPassword ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
        
        // Update aria-label for accessibility
        toggle.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
      });
    });
  }

  // Password Strength Indicator
  setupPasswordStrength() {
    const passwordInputs = document.querySelectorAll('input[type="password"][data-strength]');
    
    passwordInputs.forEach(input => {
      input.addEventListener('input', () => {
        this.updatePasswordStrength(input);
      });
    });
  }

  updatePasswordStrength(input) {
    const password = input.value;
    const strengthContainer = input.parentNode.querySelector('.password-strength');
    
    if (!strengthContainer) return;

    const strengthBar = strengthContainer.querySelector('.password-strength-fill');
    const strengthText = strengthContainer.querySelector('.password-strength-text');
    const requirements = strengthContainer.querySelectorAll('.password-requirement');

    let score = 0;
    let metRequirements = 0;

    // Check each requirement
    this.passwordStrengthRules.forEach((rule, index) => {
      const requirement = requirements[index];
      const icon = requirement?.querySelector('.password-requirement-icon');
      
      if (rule.regex.test(password)) {
        score += 20;
        metRequirements++;
        if (requirement) {
          requirement.classList.add('met');
          if (icon) icon.innerHTML = '<i class="fas fa-check"></i>';
        }
      } else {
        if (requirement) {
          requirement.classList.remove('met');
          if (icon) icon.innerHTML = '<i class="fas fa-times"></i>';
        }
      }
    });

    // Update strength bar and text
    this.updateStrengthDisplay(strengthBar, strengthText, score, metRequirements);
  }

  updateStrengthDisplay(bar, text, score, metRequirements) {
    const strengthLevels = [
      { min: 0, max: 20, class: 'weak', text: 'Weak' },
      { min: 21, max: 40, class: 'fair', text: 'Fair' },
      { min: 41, max: 80, class: 'good', text: 'Good' },
      { min: 81, max: 100, class: 'strong', text: 'Strong' }
    ];

    const currentLevel = strengthLevels.find(level => score >= level.min && score <= level.max);
    
    if (currentLevel && bar && text) {
      // Remove all strength classes
      strengthLevels.forEach(level => bar.classList.remove(level.class));
      
      // Add current strength class
      bar.classList.add(currentLevel.class);
      text.textContent = `Password strength: ${currentLevel.text} (${metRequirements}/5 requirements met)`;
    }
  }

  // Form Validation
  setupFormValidation() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
      const inputs = form.querySelectorAll('.auth-form-input');
      
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
    const fieldType = field.type;
    const isRequired = field.hasAttribute('required');
    let isValid = true;
    let errorMessage = '';

    // Clear previous errors
    this.clearFieldError(field);

    // Required validation
    if (isRequired && !value) {
      isValid = false;
      errorMessage = 'This field is required';
    }

    // Email validation
    if (fieldType === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
      }
    }

    // Password validation
    if (fieldType === 'password' && value && field.dataset.validate) {
      if (value.length < 8) {
        isValid = false;
        errorMessage = 'Password must be at least 8 characters long';
      }
    }

    // Confirm password validation
    if (field.dataset.confirmPassword) {
      const originalPassword = document.querySelector(`#${field.dataset.confirmPassword}`);
      if (originalPassword && value !== originalPassword.value) {
        isValid = false;
        errorMessage = 'Passwords do not match';
      }
    }

    this.showFieldValidation(field, isValid, errorMessage);
    return isValid;
  }

  validateForm(form) {
    const inputs = form.querySelectorAll('.auth-form-input[required]');
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

  // Social Login
  setupSocialLogin() {
    const socialButtons = document.querySelectorAll('.social-login-button');
    
    socialButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const provider = button.dataset.provider;
        this.handleSocialLogin(provider, button);
      });
    });
  }

  handleSocialLogin(provider, button) {
    // Add loading state
    button.classList.add('loading');
    button.style.pointerEvents = 'none';
    
    // Simulate social login process
    setTimeout(() => {
      // In a real application, this would redirect to the OAuth provider
      console.log(`Initiating ${provider} login...`);
      
      // For demo purposes, show success message
      this.showNotification(`${provider} login initiated`, 'info');
      
      // Remove loading state
      button.classList.remove('loading');
      button.style.pointerEvents = 'auto';
    }, 1500);
  }

  // Two-Factor Authentication
  setupTwoFactorAuth() {
    const codeInputs = document.querySelectorAll('.verification-code-input');
    
    codeInputs.forEach((input, index) => {
      input.addEventListener('input', (e) => {
        const value = e.target.value;
        
        // Only allow numbers
        if (!/^\d$/.test(value)) {
          e.target.value = '';
          return;
        }

        // Move to next input
        if (value && index < codeInputs.length - 1) {
          codeInputs[index + 1].focus();
        }

        // Check if all inputs are filled
        this.checkVerificationCode(codeInputs);
      });

      input.addEventListener('keydown', (e) => {
        // Handle backspace
        if (e.key === 'Backspace' && !input.value && index > 0) {
          codeInputs[index - 1].focus();
        }
      });

      input.addEventListener('paste', (e) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text');
        const digits = pastedData.replace(/\D/g, '').slice(0, codeInputs.length);
        
        digits.split('').forEach((digit, i) => {
          if (codeInputs[i]) {
            codeInputs[i].value = digit;
          }
        });

        this.checkVerificationCode(codeInputs);
      });
    });
  }

  checkVerificationCode(inputs) {
    const code = Array.from(inputs).map(input => input.value).join('');
    
    if (code.length === inputs.length) {
      // Auto-submit when all digits are entered
      const form = inputs[0].closest('form');
      if (form) {
        this.submitVerificationCode(code, form);
      }
    }
  }

  submitVerificationCode(code, form) {
    const submitButton = form.querySelector('.auth-submit-button');
    
    if (submitButton) {
      submitButton.classList.add('loading');
      submitButton.disabled = true;
    }

    // Simulate verification
    setTimeout(() => {
      if (code === '123456') { // Demo code
        this.showNotification('Verification successful!', 'success');
        // Redirect or continue
      } else {
        this.showNotification('Invalid verification code', 'error');
        // Clear inputs
        form.querySelectorAll('.verification-code-input').forEach(input => {
          input.value = '';
        });
        form.querySelector('.verification-code-input').focus();
      }

      if (submitButton) {
        submitButton.classList.remove('loading');
        submitButton.disabled = false;
      }
    }, 2000);
  }

  // Form Submission
  setupFormSubmission() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleFormSubmission(form);
      });
    });
  }

  handleFormSubmission(form) {
    const submitButton = form.querySelector('.auth-submit-button');
    const formData = new FormData(form);
    
    // Add loading state
    if (submitButton) {
      submitButton.classList.add('loading');
      submitButton.disabled = true;
    }

    // Simulate form submission
    setTimeout(() => {
      const formType = form.dataset.formType || 'login';
      
      // Simulate success/error
      const isSuccess = Math.random() > 0.3; // 70% success rate for demo
      
      if (isSuccess) {
        this.showNotification(`${formType} successful!`, 'success');
        
        // Redirect after successful login/register
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1500);
      } else {
        this.showNotification(`${formType} failed. Please try again.`, 'error');
      }

      // Remove loading state
      if (submitButton) {
        submitButton.classList.remove('loading');
        submitButton.disabled = false;
      }
    }, 2000);
  }

  // Animations
  setupAnimations() {
    // Add entrance animations
    const authContainer = document.querySelector('.auth-container');
    if (authContainer) {
      authContainer.classList.add('auth-slide-in');
    }

    // Stagger form field animations
    const formGroups = document.querySelectorAll('.auth-form-group');
    formGroups.forEach((group, index) => {
      group.style.animationDelay = `${index * 0.1}s`;
      group.classList.add('auth-fade-in');
    });
  }

  // Utility Methods
  showNotification(message, type = 'info') {
    // Use the existing notification system from design-system.js
    if (window.buyrollDS && window.buyrollDS.showNotification) {
      window.buyrollDS.showNotification(message, type);
    } else {
      // Fallback notification
      alert(message);
    }
  }

  // Public API
  switchToLogin() {
    const registerForm = document.querySelector('[data-form-type="register"]');
    const loginForm = document.querySelector('[data-form-type="login"]');
    
    if (registerForm) registerForm.style.display = 'none';
    if (loginForm) loginForm.style.display = 'block';
  }

  switchToRegister() {
    const loginForm = document.querySelector('[data-form-type="login"]');
    const registerForm = document.querySelector('[data-form-type="register"]');
    
    if (loginForm) loginForm.style.display = 'none';
    if (registerForm) registerForm.style.display = 'block';
  }

  resetForm(formSelector) {
    const form = document.querySelector(formSelector);
    if (form) {
      form.reset();
      
      // Clear all validation errors
      form.querySelectorAll('.form-error').forEach(error => error.remove());
      form.querySelectorAll('.invalid').forEach(field => field.classList.remove('invalid'));
      
      // Reset password strength
      const strengthBars = form.querySelectorAll('.password-strength-fill');
      strengthBars.forEach(bar => {
        bar.className = 'password-strength-fill';
      });
    }
  }

  // Cleanup
  destroy() {
    // Remove event listeners if needed
    // This would be called when navigating away from auth pages
  }
}

// Initialize Auth Pages
document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.auth-page')) {
    window.authPages = new AuthPages();
  }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AuthPages;
}