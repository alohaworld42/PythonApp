// BuyRoll Form Validation & Feedback System

class FormValidator {
  constructor() {
    this.forms = new Map();
    this.autoSaveTimers = new Map();
    this.validationRules = this.getValidationRules();
    this.init();
  }

  init() {
    this.setupForms();
    this.setupAutoSave();
    this.setupPasswordStrength();
    this.setupFileValidation();
    this.setupFormAnalytics();
  }

  // Setup Forms
  setupForms() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
      this.initializeForm(form);
    });
  }

  initializeForm(form) {
    const formId = form.id || `form_${Date.now()}`;
    const formData = {
      element: form,
      fields: new Map(),
      isValid: false,
      submitAttempted: false
    };

    this.forms.set(formId, formData);

    // Setup form fields
    const fields = form.querySelectorAll('input, textarea, select');
    fields.forEach(field => {
      this.setupField(field, formData);
    });

    // Setup form submission
    form.addEventListener('submit', (e) => {
      this.handleFormSubmit(e, formData);
    });

    // Setup multi-step navigation
    this.setupMultiStep(form, formData);
  }

  setupField(field, formData) {
    const fieldName = field.name || field.id;
    const fieldData = {
      element: field,
      rules: this.parseValidationRules(field),
      isValid: false,
      isDirty: false,
      lastValue: field.value
    };

    formData.fields.set(fieldName, fieldData);

    // Real-time validation
    field.addEventListener('input', (e) => {
      this.handleFieldInput(e, fieldData, formData);
    });

    field.addEventListener('blur', (e) => {
      this.handleFieldBlur(e, fieldData, formData);
    });

    field.addEventListener('focus', (e) => {
      this.handleFieldFocus(e, fieldData);
    });

    // Initial validation for pre-filled fields
    if (field.value) {
      this.validateField(fieldData, formData);
    }
  }

  // Field Event Handlers
  handleFieldInput(event, fieldData, formData) {
    const field = fieldData.element;
    fieldData.isDirty = true;
    
    // Clear previous validation state
    this.clearFieldValidation(field);
    
    // Debounced validation
    clearTimeout(fieldData.validationTimer);
    fieldData.validationTimer = setTimeout(() => {
      this.validateField(fieldData, formData);
      this.updateFormValidation(formData);
      
      // Auto-save if enabled
      if (formData.element.dataset.autoSave === 'true') {
        this.triggerAutoSave(formData);
      }
    }, 300);

    // Special handling for password fields
    if (field.type === 'password') {
      this.updatePasswordStrength(field);
    }
  }

  handleFieldBlur(event, fieldData, formData) {
    if (fieldData.isDirty) {
      this.validateField(fieldData, formData);
      this.updateFormValidation(formData);
    }
  }

  handleFieldFocus(event, fieldData) {
    const field = fieldData.element;
    
    // Show help tooltip if available
    const tooltip = field.parentNode.querySelector('.form-tooltip-content');
    if (tooltip) {
      tooltip.style.opacity = '1';
      tooltip.style.visibility = 'visible';
    }
  }

  // Validation Logic
  validateField(fieldData, formData) {
    const field = fieldData.element;
    const value = field.value.trim();
    const rules = fieldData.rules;
    
    let isValid = true;
    let messages = [];

    // Required validation
    if (rules.required && !value) {
      isValid = false;
      messages.push({
        type: 'error',
        text: 'This field is required',
        icon: 'fas fa-exclamation-circle'
      });
    }

    if (value) {
      // Email validation
      if (rules.email && !this.isValidEmail(value)) {
        isValid = false;
        messages.push({
          type: 'error',
          text: 'Please enter a valid email address',
          icon: 'fas fa-exclamation-circle'
        });
      }

      // Min length validation
      if (rules.minLength && value.length < rules.minLength) {
        isValid = false;
        messages.push({
          type: 'error',
          text: `Minimum ${rules.minLength} characters required`,
          icon: 'fas fa-exclamation-circle'
        });
      }

      // Max length validation
      if (rules.maxLength && value.length > rules.maxLength) {
        isValid = false;
        messages.push({
          type: 'error',
          text: `Maximum ${rules.maxLength} characters allowed`,
          icon: 'fas fa-exclamation-circle'
        });
      }

      // Pattern validation
      if (rules.pattern && !new RegExp(rules.pattern).test(value)) {
        isValid = false;
        messages.push({
          type: 'error',
          text: rules.patternMessage || 'Invalid format',
          icon: 'fas fa-exclamation-circle'
        });
      }

      // Custom validation
      if (rules.custom) {
        const customResult = this.runCustomValidation(rules.custom, value, field);
        if (!customResult.isValid) {
          isValid = false;
          messages.push({
            type: 'error',
            text: customResult.message,
            icon: 'fas fa-exclamation-circle'
          });
        }
      }

      // Password confirmation
      if (rules.confirmPassword) {
        const passwordField = formData.element.querySelector(`[name="${rules.confirmPassword}"]`);
        if (passwordField && value !== passwordField.value) {
          isValid = false;
          messages.push({
            type: 'error',
            text: 'Passwords do not match',
            icon: 'fas fa-exclamation-circle'
          });
        }
      }
    }

    fieldData.isValid = isValid;
    this.updateFieldUI(field, isValid, messages);
    
    return { isValid, messages };
  }

  updateFieldUI(field, isValid, messages) {
    // Update field classes
    field.classList.remove('valid', 'invalid', 'warning');
    
    if (field.value.trim()) {
      field.classList.add(isValid ? 'valid' : 'invalid');
    }

    // Update ARIA attributes
    field.setAttribute('aria-invalid', !isValid);

    // Update validation icon
    const icon = field.parentNode.querySelector('.form-field-icon');
    if (icon) {
      icon.className = `form-field-icon ${isValid ? 'success' : 'error'}`;
      icon.innerHTML = isValid ? '<i class="fas fa-check"></i>' : '<i class="fas fa-times"></i>';
    }

    // Update validation messages
    this.updateValidationMessages(field, messages);
  }

  updateValidationMessages(field, messages) {
    const messageContainer = field.parentNode.querySelector('.form-message') || 
                           this.createMessageContainer(field.parentNode);

    if (messages.length > 0) {
      const message = messages[0]; // Show first message
      messageContainer.className = `form-message ${message.type} show`;
      messageContainer.innerHTML = `
        <i class="${message.icon} form-message-icon"></i>
        <span>${message.text}</span>
      `;
    } else {
      messageContainer.classList.remove('show');
    }
  }

  createMessageContainer(parent) {
    const container = document.createElement('div');
    container.className = 'form-message';
    parent.appendChild(container);
    return container;
  }

  // Form Validation
  updateFormValidation(formData) {
    let isFormValid = true;
    
    formData.fields.forEach(fieldData => {
      if (!fieldData.isValid) {
        isFormValid = false;
      }
    });

    formData.isValid = isFormValid;
    
    // Update submit button state
    const submitButton = formData.element.querySelector('[type="submit"]');
    if (submitButton) {
      submitButton.disabled = !isFormValid;
      submitButton.classList.toggle('btn-disabled', !isFormValid);
    }
  }

  // Form Submission
  handleFormSubmit(event, formData) {
    event.preventDefault();
    formData.submitAttempted = true;

    // Validate all fields
    let isFormValid = true;
    formData.fields.forEach(fieldData => {
      const result = this.validateField(fieldData, formData);
      if (!result.isValid) {
        isFormValid = false;
      }
    });

    if (isFormValid) {
      this.submitForm(formData);
    } else {
      this.showFormError(formData.element, 'Please correct the errors above');
      this.focusFirstInvalidField(formData);
    }
  }

  async submitForm(formData) {
    const form = formData.element;
    
    // Show loading state
    this.showFormLoading(form);

    try {
      const formDataObj = new FormData(form);
      const response = await fetch(form.action || window.location.href, {
        method: form.method || 'POST',
        body: formDataObj
      });

      if (response.ok) {
        this.showFormSuccess(form, 'Form submitted successfully!');
        this.trackFormSubmission(form, 'success');
      } else {
        throw new Error('Submission failed');
      }
    } catch (error) {
      this.showFormError(form, 'Submission failed. Please try again.');
      this.trackFormSubmission(form, 'error');
    } finally {
      this.hideFormLoading(form);
    }
  }

  // Auto-save Functionality
  setupAutoSave() {
    const autoSaveForms = document.querySelectorAll('form[data-auto-save="true"]');
    
    autoSaveForms.forEach(form => {
      const indicator = this.createAutoSaveIndicator(form);
      form.appendChild(indicator);
    });
  }

  createAutoSaveIndicator(form) {
    const indicator = document.createElement('div');
    indicator.className = 'auto-save-indicator';
    indicator.innerHTML = `
      <div class="auto-save-spinner" style="display: none;"></div>
      <i class="fas fa-check" style="display: none;"></i>
      <i class="fas fa-exclamation-triangle" style="display: none;"></i>
      <span class="auto-save-text">Auto-save enabled</span>
    `;
    return indicator;
  }

  triggerAutoSave(formData) {
    const form = formData.element;
    const formId = form.id;
    
    // Clear existing timer
    if (this.autoSaveTimers.has(formId)) {
      clearTimeout(this.autoSaveTimers.get(formId));
    }

    // Set new timer
    const timer = setTimeout(() => {
      this.performAutoSave(formData);
    }, 2000);

    this.autoSaveTimers.set(formId, timer);
  }

  async performAutoSave(formData) {
    const form = formData.element;
    const indicator = form.querySelector('.auto-save-indicator');
    
    if (!indicator) return;

    // Show saving state
    this.updateAutoSaveIndicator(indicator, 'saving', 'Saving...');

    try {
      const formDataObj = new FormData(form);
      const response = await fetch(form.dataset.autoSaveUrl || '/api/auto-save', {
        method: 'POST',
        body: formDataObj
      });

      if (response.ok) {
        this.updateAutoSaveIndicator(indicator, 'saved', 'Saved');
        setTimeout(() => {
          indicator.classList.remove('show');
        }, 2000);
      } else {
        throw new Error('Auto-save failed');
      }
    } catch (error) {
      this.updateAutoSaveIndicator(indicator, 'error', 'Save failed');
    }
  }

  updateAutoSaveIndicator(indicator, state, text) {
    const spinner = indicator.querySelector('.auto-save-spinner');
    const checkIcon = indicator.querySelector('.fa-check');
    const errorIcon = indicator.querySelector('.fa-exclamation-triangle');
    const textElement = indicator.querySelector('.auto-save-text');

    // Hide all icons
    spinner.style.display = 'none';
    checkIcon.style.display = 'none';
    errorIcon.style.display = 'none';

    // Update state
    indicator.className = `auto-save-indicator ${state} show`;
    textElement.textContent = text;

    // Show appropriate icon
    switch (state) {
      case 'saving':
        spinner.style.display = 'block';
        break;
      case 'saved':
        checkIcon.style.display = 'block';
        break;
      case 'error':
        errorIcon.style.display = 'block';
        break;
    }
  }

  // Password Strength
  setupPasswordStrength() {
    const passwordFields = document.querySelectorAll('input[type="password"][data-strength]');
    
    passwordFields.forEach(field => {
      this.createPasswordStrengthIndicator(field);
    });
  }

  createPasswordStrengthIndicator(field) {
    const container = document.createElement('div');
    container.className = 'password-strength';
    
    container.innerHTML = `
      <div class="validation-progress">
        <div class="validation-progress-bar">
          <div class="validation-progress-fill"></div>
        </div>
      </div>
      <ul class="password-requirements">
        <li class="password-requirement" data-rule="length">
          <div class="password-requirement-icon"></div>
          <span>At least 8 characters</span>
        </li>
        <li class="password-requirement" data-rule="uppercase">
          <div class="password-requirement-icon"></div>
          <span>One uppercase letter</span>
        </li>
        <li class="password-requirement" data-rule="lowercase">
          <div class="password-requirement-icon"></div>
          <span>One lowercase letter</span>
        </li>
        <li class="password-requirement" data-rule="number">
          <div class="password-requirement-icon"></div>
          <span>One number</span>
        </li>
        <li class="password-requirement" data-rule="special">
          <div class="password-requirement-icon"></div>
          <span>One special character</span>
        </li>
      </ul>
    `;

    field.parentNode.appendChild(container);
  }

  updatePasswordStrength(field) {
    const container = field.parentNode.querySelector('.password-strength');
    if (!container) return;

    const password = field.value;
    const requirements = container.querySelectorAll('.password-requirement');
    const progressFill = container.querySelector('.validation-progress-fill');

    let score = 0;
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    // Update requirements
    requirements.forEach(req => {
      const rule = req.dataset.rule;
      const isMet = checks[rule];
      
      req.classList.toggle('met', isMet);
      
      if (isMet) score++;
    });

    // Update progress bar
    const strength = this.getPasswordStrength(score);
    progressFill.className = `validation-progress-fill ${strength}`;
  }

  getPasswordStrength(score) {
    if (score <= 1) return 'weak';
    if (score <= 2) return 'fair';
    if (score <= 3) return 'good';
    return 'strong';
  }

  // Multi-step Forms
  setupMultiStep(form, formData) {
    const steps = form.querySelectorAll('.form-step-content');
    if (steps.length <= 1) return;

    formData.currentStep = 0;
    formData.totalSteps = steps.length;

    // Show first step
    this.showStep(formData, 0);

    // Setup navigation
    const nextButtons = form.querySelectorAll('.btn-next-step');
    const prevButtons = form.querySelectorAll('.btn-prev-step');

    nextButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.nextStep(formData);
      });
    });

    prevButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.prevStep(formData);
      });
    });
  }

  showStep(formData, stepIndex) {
    const form = formData.element;
    const steps = form.querySelectorAll('.form-step-content');
    const progressSteps = form.querySelectorAll('.form-step');

    // Hide all steps
    steps.forEach(step => step.style.display = 'none');
    
    // Show current step
    if (steps[stepIndex]) {
      steps[stepIndex].style.display = 'block';
    }

    // Update progress
    progressSteps.forEach((step, index) => {
      step.classList.remove('active', 'completed');
      
      if (index < stepIndex) {
        step.classList.add('completed');
      } else if (index === stepIndex) {
        step.classList.add('active');
      }
    });

    formData.currentStep = stepIndex;
  }

  nextStep(formData) {
    // Validate current step
    const currentStepValid = this.validateCurrentStep(formData);
    
    if (currentStepValid && formData.currentStep < formData.totalSteps - 1) {
      this.showStep(formData, formData.currentStep + 1);
    }
  }

  prevStep(formData) {
    if (formData.currentStep > 0) {
      this.showStep(formData, formData.currentStep - 1);
    }
  }

  validateCurrentStep(formData) {
    const form = formData.element;
    const currentStepElement = form.querySelectorAll('.form-step-content')[formData.currentStep];
    const stepFields = currentStepElement.querySelectorAll('input, textarea, select');
    
    let isStepValid = true;
    
    stepFields.forEach(field => {
      const fieldName = field.name || field.id;
      const fieldData = formData.fields.get(fieldName);
      
      if (fieldData) {
        const result = this.validateField(fieldData, formData);
        if (!result.isValid) {
          isStepValid = false;
        }
      }
    });

    return isStepValid;
  }

  // File Validation
  setupFileValidation() {
    const fileInputs = document.querySelectorAll('input[type="file"][data-validate]');
    
    fileInputs.forEach(input => {
      input.addEventListener('change', (e) => {
        this.validateFiles(e.target);
      });
    });
  }

  validateFiles(input) {
    const files = Array.from(input.files);
    const rules = this.parseValidationRules(input);
    const container = input.parentNode.querySelector('.file-upload-validation') || 
                     this.createFileValidationContainer(input.parentNode);

    let validationResults = [];

    files.forEach(file => {
      const result = this.validateFile(file, rules);
      validationResults.push(result);
    });

    this.updateFileValidationUI(container, validationResults);
  }

  validateFile(file, rules) {
    let isValid = true;
    let messages = [];

    // File size validation
    if (rules.maxSize && file.size > rules.maxSize) {
      isValid = false;
      messages.push({
        type: 'invalid',
        text: `File size exceeds ${this.formatFileSize(rules.maxSize)}`,
        icon: 'fas fa-times'
      });
    }

    // File type validation
    if (rules.allowedTypes && !rules.allowedTypes.includes(file.type)) {
      isValid = false;
      messages.push({
        type: 'invalid',
        text: `File type not allowed`,
        icon: 'fas fa-times'
      });
    }

    return { file, isValid, messages };
  }

  createFileValidationContainer(parent) {
    const container = document.createElement('div');
    container.className = 'file-upload-validation';
    parent.appendChild(container);
    return container;
  }

  updateFileValidationUI(container, results) {
    container.innerHTML = '';
    
    results.forEach(result => {
      const item = document.createElement('div');
      item.className = `file-validation-item ${result.isValid ? 'valid' : 'invalid'}`;
      
      const icon = result.isValid ? 'fas fa-check' : 'fas fa-times';
      const message = result.isValid ? 'Valid file' : result.messages[0]?.text || 'Invalid file';
      
      item.innerHTML = `
        <i class="${icon} file-validation-icon"></i>
        <span>${result.file.name}: ${message}</span>
      `;
      
      container.appendChild(item);
    });
  }

  // Form Analytics
  setupFormAnalytics() {
    const forms = document.querySelectorAll('form[data-analytics]');
    
    forms.forEach(form => {
      this.trackFormInteraction(form);
    });
  }

  trackFormInteraction(form) {
    const startTime = Date.now();
    let fieldInteractions = 0;
    
    const fields = form.querySelectorAll('input, textarea, select');
    fields.forEach(field => {
      field.addEventListener('focus', () => {
        fieldInteractions++;
      });
    });

    form.addEventListener('submit', () => {
      const completionTime = Date.now() - startTime;
      this.sendAnalytics({
        formId: form.id,
        completionTime,
        fieldInteractions,
        event: 'form_completed'
      });
    });
  }

  trackFormSubmission(form, status) {
    this.sendAnalytics({
      formId: form.id,
      status,
      event: 'form_submission'
    });
  }

  sendAnalytics(data) {
    // Send to analytics service
    if (typeof gtag !== 'undefined') {
      gtag('event', data.event, data);
    }
  }

  // UI State Management
  showFormLoading(form) {
    form.classList.add('form-submitting');
    
    const submitButton = form.querySelector('[type="submit"]');
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.dataset.originalText = submitButton.textContent;
      submitButton.textContent = 'Submitting...';
    }
  }

  hideFormLoading(form) {
    form.classList.remove('form-submitting');
    
    const submitButton = form.querySelector('[type="submit"]');
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = submitButton.dataset.originalText || 'Submit';
    }
  }

  showFormSuccess(form, message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'form-success';
    successDiv.innerHTML = `
      <div class="form-success-icon">
        <i class="fas fa-check-circle"></i>
      </div>
      <h3 class="form-success-title">Success!</h3>
      <p class="form-success-message">${message}</p>
    `;
    
    form.style.display = 'none';
    form.parentNode.insertBefore(successDiv, form);
  }

  showFormError(form, message) {
    let errorDiv = form.parentNode.querySelector('.form-error');
    
    if (!errorDiv) {
      errorDiv = document.createElement('div');
      errorDiv.className = 'form-error';
      form.parentNode.insertBefore(errorDiv, form);
    }
    
    errorDiv.innerHTML = `
      <div class="form-error-icon">
        <i class="fas fa-exclamation-circle"></i>
      </div>
      <h3 class="form-error-title">Error</h3>
      <p class="form-error-message">${message}</p>
    `;
  }

  focusFirstInvalidField(formData) {
    for (let [fieldName, fieldData] of formData.fields) {
      if (!fieldData.isValid) {
        fieldData.element.focus();
        break;
      }
    }
  }

  clearFieldValidation(field) {
    field.classList.remove('valid', 'invalid', 'warning');
    
    const message = field.parentNode.querySelector('.form-message');
    if (message) {
      message.classList.remove('show');
    }
  }

  // Validation Rules
  getValidationRules() {
    return {
      email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
      phone: (value) => /^\+?[\d\s\-\(\)]+$/.test(value),
      url: (value) => /^https?:\/\/.+/.test(value),
      creditCard: (value) => /^\d{4}\s?\d{4}\s?\d{4}\s?\d{4}$/.test(value)
    };
  }

  parseValidationRules(field) {
    const rules = {};
    
    if (field.required) rules.required = true;
    if (field.type === 'email') rules.email = true;
    if (field.minLength) rules.minLength = parseInt(field.minLength);
    if (field.maxLength) rules.maxLength = parseInt(field.maxLength);
    if (field.pattern) {
      rules.pattern = field.pattern;
      rules.patternMessage = field.dataset.patternMessage;
    }
    if (field.dataset.confirmPassword) {
      rules.confirmPassword = field.dataset.confirmPassword;
    }
    if (field.dataset.custom) {
      rules.custom = field.dataset.custom;
    }
    if (field.dataset.maxSize) {
      rules.maxSize = parseInt(field.dataset.maxSize);
    }
    if (field.dataset.allowedTypes) {
      rules.allowedTypes = field.dataset.allowedTypes.split(',');
    }
    
    return rules;
  }

  runCustomValidation(ruleName, value, field) {
    const customRules = {
      strongPassword: (value) => {
        const hasUpper = /[A-Z]/.test(value);
        const hasLower = /[a-z]/.test(value);
        const hasNumber = /\d/.test(value);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value);
        const isLongEnough = value.length >= 8;
        
        const isValid = hasUpper && hasLower && hasNumber && hasSpecial && isLongEnough;
        return {
          isValid,
          message: isValid ? '' : 'Password must contain uppercase, lowercase, number, and special character'
        };
      },
      
      uniqueUsername: async (value) => {
        // Simulate API call
        try {
          const response = await fetch(`/api/check-username?username=${value}`);
          const data = await response.json();
          return {
            isValid: data.available,
            message: data.available ? '' : 'Username is already taken'
          };
        } catch (error) {
          return {
            isValid: false,
            message: 'Unable to verify username availability'
          };
        }
      }
    };

    const rule = customRules[ruleName];
    if (rule) {
      return rule(value);
    }

    return { isValid: true, message: '' };
  }

  // Utility Methods
  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Public API
  validateForm(formId) {
    const formData = this.forms.get(formId);
    if (formData) {
      this.updateFormValidation(formData);
      return formData.isValid;
    }
    return false;
  }

  resetForm(formId) {
    const formData = this.forms.get(formId);
    if (formData) {
      formData.element.reset();
      formData.fields.forEach(fieldData => {
        this.clearFieldValidation(fieldData.element);
        fieldData.isValid = false;
        fieldData.isDirty = false;
      });
      this.updateFormValidation(formData);
    }
  }

  getFormData(formId) {
    const formData = this.forms.get(formId);
    if (formData) {
      return new FormData(formData.element);
    }
    return null;
  }
}

// Initialize Form Validator
document.addEventListener('DOMContentLoaded', () => {
  window.formValidator = new FormValidator();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FormValidator;
}