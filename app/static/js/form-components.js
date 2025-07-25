/**
 * BuyRoll Form Components
 * Enhanced form validation system with input field components and multi-step functionality
 */

class FormValidator {
    constructor(form, options = {}) {
        this.form = form;
        this.options = {
            validateOnBlur: true,
            validateOnInput: false,
            showSuccessStates: true,
            customValidators: {},
            ...options
        };
        
        this.fields = new Map();
        this.isValid = false;
        this.currentStep = 0;
        this.totalSteps = 1;
        
        this.init();
    }
    
    init() {
        this.setupFields();
        this.setupEventListeners();
        this.setupMultiStep();
        this.setupSubmissionHandling();
    }
    
    setupFields() {
        const inputs = this.form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            const fieldConfig = {
                element: input,
                validators: this.getValidators(input),
                isValid: false,
                isDirty: false,
                errorMessage: '',
                successMessage: ''
            };
            
            this.fields.set(input.name || input.id, fieldConfig);
            this.enhanceInputField(input);
        });
    }
    
    enhanceInputField(input) {
        const container = input.closest('.form-field') || this.createFieldContainer(input);
        
        // Add floating label if not exists
        if (!container.querySelector('.floating-label')) {
            this.addFloatingLabel(container, input);
        }
        
        // Add validation states
        this.addValidationStates(container, input);
        
        // Add input enhancements
        this.addInputEnhancements(container, input);
    }
    
    createFieldContainer(input) {
        const container = document.createElement('div');
        container.className = 'form-field relative mb-4';
        
        input.parentNode.insertBefore(container, input);
        container.appendChild(input);
        
        return container;
    }
    
    addFloatingLabel(container, input) {
        const existingLabel = container.querySelector('label');
        const labelText = existingLabel ? existingLabel.textContent : input.placeholder || input.name;
        
        if (existingLabel) {
            existingLabel.remove();
        }
        
        const label = document.createElement('label');
        label.className = 'floating-label absolute left-3 transition-all duration-200 pointer-events-none';
        label.setAttribute('for', input.id || input.name);
        label.textContent = labelText;
        
        // Position label based on input state
        this.updateLabelPosition(label, input);
        
        container.appendChild(label);
        
        // Update label position on focus/blur
        input.addEventListener('focus', () => this.updateLabelPosition(label, input, true));
        input.addEventListener('blur', () => this.updateLabelPosition(label, input, false));
        input.addEventListener('input', () => this.updateLabelPosition(label, input));
    }
    
    updateLabelPosition(label, input, isFocused = null) {
        const hasValue = input.value.length > 0;
        const shouldFloat = hasValue || isFocused === true || input === document.activeElement;
        
        if (shouldFloat) {
            label.className = 'floating-label absolute left-3 -top-2 text-xs bg-white px-1 text-green-700 transition-all duration-200 pointer-events-none';
        } else {
            label.className = 'floating-label absolute left-3 top-3 text-gray-500 transition-all duration-200 pointer-events-none';
        }
    }
    
    addValidationStates(container, input) {
        // Add validation message container
        const messageContainer = document.createElement('div');
        messageContainer.className = 'validation-message mt-1 text-sm transition-all duration-200';
        container.appendChild(messageContainer);
        
        // Add validation icons
        const iconContainer = document.createElement('div');
        iconContainer.className = 'validation-icon absolute right-3 top-3 transition-all duration-200';
        container.appendChild(iconContainer);
        
        // Add progress indicator for password fields
        if (input.type === 'password' && (input.name === 'password' || input.name === 'new_password')) {
            this.addPasswordStrengthIndicator(container, input);
        }
    }
    
    addPasswordStrengthIndicator(container, input) {
        const strengthContainer = document.createElement('div');
        strengthContainer.className = 'password-strength-container mt-2';
        
        const strengthBar = document.createElement('div');
        strengthBar.className = 'password-strength-bar h-2 bg-gray-200 rounded-full overflow-hidden';
        
        const strengthFill = document.createElement('div');
        strengthFill.className = 'password-strength-fill h-full transition-all duration-300 rounded-full';
        
        const strengthText = document.createElement('div');
        strengthText.className = 'password-strength-text text-xs mt-1 text-gray-600';
        
        strengthBar.appendChild(strengthFill);
        strengthContainer.appendChild(strengthBar);
        strengthContainer.appendChild(strengthText);
        container.appendChild(strengthContainer);
        
        input.addEventListener('input', () => {
            this.updatePasswordStrength(input, strengthFill, strengthText);
        });
    }
    
    updatePasswordStrength(input, strengthFill, strengthText) {
        const password = input.value;
        const strength = this.calculatePasswordStrength(password);
        
        const strengthLevels = [
            { width: '0%', color: 'bg-gray-300', text: '' },
            { width: '25%', color: 'bg-red-500', text: 'Weak' },
            { width: '50%', color: 'bg-yellow-500', text: 'Fair' },
            { width: '75%', color: 'bg-blue-500', text: 'Good' },
            { width: '100%', color: 'bg-green-500', text: 'Strong' }
        ];
        
        const level = strengthLevels[strength];
        strengthFill.style.width = level.width;
        strengthFill.className = `password-strength-fill h-full transition-all duration-300 rounded-full ${level.color}`;
        strengthText.textContent = level.text;
    }
    
    calculatePasswordStrength(password) {
        if (!password) return 0;
        
        let score = 0;
        
        // Length check
        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        
        // Character variety
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;
        
        // Common patterns (reduce score)
        if (/(.)\1{2,}/.test(password)) score--; // Repeated characters
        if (/123|abc|qwe/i.test(password)) score--; // Sequential patterns
        
        return Math.max(0, Math.min(4, Math.floor(score / 1.5)));
    }
    
    addInputEnhancements(container, input) {
        // Add input styling
        input.className = `form-input w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 ${input.className}`;
        
        // Add character counter for text inputs with maxlength
        if (input.maxLength && input.maxLength > 0 && (input.type === 'text' || input.tagName === 'TEXTAREA')) {
            this.addCharacterCounter(container, input);
        }
        
        // Add input masks for specific types
        this.addInputMask(input);
    }
    
    addCharacterCounter(container, input) {
        const counter = document.createElement('div');
        counter.className = 'character-counter text-xs text-gray-500 mt-1 text-right';
        
        const updateCounter = () => {
            const current = input.value.length;
            const max = input.maxLength;
            counter.textContent = `${current}/${max}`;
            
            if (current > max * 0.9) {
                counter.className = 'character-counter text-xs text-yellow-600 mt-1 text-right';
            } else if (current === max) {
                counter.className = 'character-counter text-xs text-red-600 mt-1 text-right';
            } else {
                counter.className = 'character-counter text-xs text-gray-500 mt-1 text-right';
            }
        };
        
        input.addEventListener('input', updateCounter);
        updateCounter();
        
        container.appendChild(counter);
    }
    
    addInputMask(input) {
        // Phone number mask
        if (input.type === 'tel' || input.name === 'phone') {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length >= 6) {
                    value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
                } else if (value.length >= 3) {
                    value = value.replace(/(\d{3})(\d{0,3})/, '($1) $2');
                }
                e.target.value = value;
            });
        }
        
        // Credit card mask
        if (input.name === 'card_number' || input.dataset.mask === 'card') {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                value = value.replace(/(\d{4})(?=\d)/g, '$1 ');
                e.target.value = value;
            });
        }
    }
    
    getValidators(input) {
        const validators = [];
        
        // Required validation
        if (input.required) {
            validators.push({
                name: 'required',
                validate: (value) => {
                    // Required field validation
                    return value && value.trim().length > 0;
                },
                message: 'This field is required'
            });
        }
        
        // Email validation
        if (input.type === 'email') {
            validators.push({
                name: 'email',
                validate: (value) => {
                    // Email field validation
                    return !value || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
                },
                message: 'Please enter a valid email address'
            });
        }
        
        // Password validation
        if (input.type === 'password') {
            validators.push({
                name: 'password',
                validate: (value) => !value || value.length >= 8,
                message: 'Password must be at least 8 characters long'
            });
        }
        
        // Confirm password validation
        if (input.name === 'confirm_password' || input.name === 'password_confirmation') {
            validators.push({
                name: 'confirm_password',
                validate: (value) => {
                    const passwordField = this.form.querySelector('input[name="password"], input[name="new_password"]');
                    return !value || !passwordField || value === passwordField.value;
                },
                message: 'Passwords do not match'
            });
        }
        
        // Length validation
        if (input.minLength) {
            validators.push({
                name: 'minLength',
                validate: (value) => !value || value.length >= input.minLength,
                message: `Must be at least ${input.minLength} characters long`
            });
        }
        
        if (input.maxLength) {
            validators.push({
                name: 'maxLength',
                validate: (value) => !value || value.length <= input.maxLength,
                message: `Must be no more than ${input.maxLength} characters long`
            });
        }
        
        // Pattern validation
        if (input.pattern) {
            validators.push({
                name: 'pattern',
                validate: (value) => !value || new RegExp(input.pattern).test(value),
                message: input.title || 'Invalid format'
            });
        }
        
        // Custom validators
        const customValidator = this.options.customValidators[input.name];
        if (customValidator) {
            validators.push(customValidator);
        }
        
        return validators;
    }
    
    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
        
        // Field validation on blur/input
        this.fields.forEach((fieldConfig, fieldName) => {
            const input = fieldConfig.element;
            
            if (this.options.validateOnBlur) {
                input.addEventListener('blur', () => {
                    fieldConfig.isDirty = true;
                    this.validateField(fieldName);
                });
            }
            
            if (this.options.validateOnInput) {
                input.addEventListener('input', () => {
                    if (fieldConfig.isDirty) {
                        this.validateField(fieldName);
                    }
                });
            }
            
            // Real-time validation for password confirmation
            if (input.name === 'confirm_password' || input.name === 'password_confirmation') {
                input.addEventListener('input', () => {
                    this.validateField(fieldName);
                });
                
                const passwordField = this.form.querySelector('input[name="password"], input[name="new_password"]');
                if (passwordField) {
                    passwordField.addEventListener('input', () => {
                        if (fieldConfig.isDirty) {
                            this.validateField(fieldName);
                        }
                    });
                }
            }
        });
    }
    
    validateField(fieldName) {
        const fieldConfig = this.fields.get(fieldName);
        if (!fieldConfig) return false;
        
        const input = fieldConfig.element;
        const value = input.value;
        
        // Reset validation state
        fieldConfig.isValid = true;
        fieldConfig.errorMessage = '';
        
        // Run validators
        for (const validator of fieldConfig.validators) {
            if (!validator.validate(value)) {
                fieldConfig.isValid = false;
                fieldConfig.errorMessage = validator.message;
                break;
            }
        }
        
        // Update UI
        this.updateFieldUI(fieldConfig);
        
        // Update form validity
        this.updateFormValidity();
        
        return fieldConfig.isValid;
    }
    
    updateFieldUI(fieldConfig) {
        const input = fieldConfig.element;
        const container = input.closest('.form-field');
        const messageContainer = container.querySelector('.validation-message');
        const iconContainer = container.querySelector('.validation-icon');
        
        // Remove existing classes
        input.classList.remove('border-red-500', 'border-green-500', 'focus:ring-red-500', 'focus:ring-green-500');
        
        if (fieldConfig.isDirty) {
            if (fieldConfig.isValid) {
                // Success state
                if (this.options.showSuccessStates && input.value.length > 0) {
                    input.classList.add('border-green-500', 'focus:ring-green-500');
                    iconContainer.innerHTML = '<i class="fas fa-check text-green-500"></i>';
                    messageContainer.innerHTML = '';
                } else {
                    iconContainer.innerHTML = '';
                    messageContainer.innerHTML = '';
                }
            } else {
                // Error state
                input.classList.add('border-red-500', 'focus:ring-red-500');
                iconContainer.innerHTML = '<i class="fas fa-exclamation-circle text-red-500"></i>';
                messageContainer.innerHTML = `<span class="text-red-500">${fieldConfig.errorMessage}</span>`;
            }
        }
    }
    
    updateFormValidity() {
        let allValid = true;
        
        this.fields.forEach((fieldConfig) => {
            if (!fieldConfig.isValid) {
                allValid = false;
            }
        });
        
        this.isValid = allValid;
        
        // Update submit button state
        const submitButton = this.form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitButton) {
            submitButton.disabled = !allValid;
            if (allValid) {
                submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
            } else {
                submitButton.classList.add('opacity-50', 'cursor-not-allowed');
            }
        }
    }
    
    validateAll() {
        let allValid = true;
        
        this.fields.forEach((fieldConfig, fieldName) => {
            fieldConfig.isDirty = true;
            if (!this.validateField(fieldName)) {
                allValid = false;
            }
        });
        
        return allValid;
    }
    
    setupMultiStep() {
        const steps = this.form.querySelectorAll('.form-step');
        if (steps.length <= 1) return;
        
        this.totalSteps = steps.length;
        this.currentStep = 0;
        
        // Hide all steps except first
        steps.forEach((step, index) => {
            if (index !== 0) {
                step.classList.add('hidden');
            }
        });
        
        // Add step navigation
        this.createStepNavigation();
        this.createStepIndicator();
    }
    
    createStepNavigation() {
        const navigationContainer = document.createElement('div');
        navigationContainer.className = 'step-navigation flex justify-between mt-6';
        
        const prevButton = document.createElement('button');
        prevButton.type = 'button';
        prevButton.className = 'btn-secondary px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed';
        prevButton.innerHTML = '<i class="fas fa-arrow-left mr-2"></i>Previous';
        prevButton.disabled = true;
        prevButton.addEventListener('click', () => this.previousStep());
        
        const nextButton = document.createElement('button');
        nextButton.type = 'button';
        nextButton.className = 'btn-primary px-6 py-2 rounded-lg';
        nextButton.innerHTML = 'Next<i class="fas fa-arrow-right ml-2"></i>';
        nextButton.addEventListener('click', () => this.nextStep());
        
        navigationContainer.appendChild(prevButton);
        navigationContainer.appendChild(nextButton);
        
        this.form.appendChild(navigationContainer);
        
        this.prevButton = prevButton;
        this.nextButton = nextButton;
    }
    
    createStepIndicator() {
        const indicatorContainer = document.createElement('div');
        indicatorContainer.className = 'step-indicator flex justify-center mb-8';
        
        for (let i = 0; i < this.totalSteps; i++) {
            const indicator = document.createElement('div');
            indicator.className = `step-indicator-item w-8 h-8 rounded-full flex items-center justify-center mx-2 transition-all duration-200 ${
                i === 0 ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
            }`;
            indicator.textContent = i + 1;
            
            if (i < this.totalSteps - 1) {
                const connector = document.createElement('div');
                connector.className = 'step-connector w-12 h-1 bg-gray-300 mx-2 mt-4';
                indicatorContainer.appendChild(indicator);
                indicatorContainer.appendChild(connector);
            } else {
                indicatorContainer.appendChild(indicator);
            }
        }
        
        this.form.insertBefore(indicatorContainer, this.form.firstChild);
        this.stepIndicators = indicatorContainer.querySelectorAll('.step-indicator-item');
        this.stepConnectors = indicatorContainer.querySelectorAll('.step-connector');
    }
    
    nextStep() {
        if (this.currentStep >= this.totalSteps - 1) return;
        
        // Validate current step
        if (!this.validateCurrentStep()) {
            return;
        }
        
        // Hide current step
        const currentStepElement = this.form.querySelectorAll('.form-step')[this.currentStep];
        currentStepElement.classList.add('hidden');
        
        // Show next step
        this.currentStep++;
        const nextStepElement = this.form.querySelectorAll('.form-step')[this.currentStep];
        nextStepElement.classList.remove('hidden');
        
        // Update navigation
        this.updateStepNavigation();
        this.updateStepIndicator();
        
        // Focus first input in new step
        const firstInput = nextStepElement.querySelector('input, textarea, select');
        if (firstInput) {
            firstInput.focus();
        }
    }
    
    previousStep() {
        if (this.currentStep <= 0) return;
        
        // Hide current step
        const currentStepElement = this.form.querySelectorAll('.form-step')[this.currentStep];
        currentStepElement.classList.add('hidden');
        
        // Show previous step
        this.currentStep--;
        const prevStepElement = this.form.querySelectorAll('.form-step')[this.currentStep];
        prevStepElement.classList.remove('hidden');
        
        // Update navigation
        this.updateStepNavigation();
        this.updateStepIndicator();
    }
    
    validateCurrentStep() {
        const currentStepElement = this.form.querySelectorAll('.form-step')[this.currentStep];
        const stepInputs = currentStepElement.querySelectorAll('input, textarea, select');
        
        let stepValid = true;
        
        stepInputs.forEach(input => {
            const fieldName = input.name || input.id;
            const fieldConfig = this.fields.get(fieldName);
            if (fieldConfig) {
                fieldConfig.isDirty = true;
                if (!this.validateField(fieldName)) {
                    stepValid = false;
                }
            }
        });
        
        return stepValid;
    }
    
    updateStepNavigation() {
        this.prevButton.disabled = this.currentStep === 0;
        
        if (this.currentStep === this.totalSteps - 1) {
            this.nextButton.innerHTML = 'Submit<i class="fas fa-check ml-2"></i>';
            this.nextButton.type = 'submit';
        } else {
            this.nextButton.innerHTML = 'Next<i class="fas fa-arrow-right ml-2"></i>';
            this.nextButton.type = 'button';
        }
    }
    
    updateStepIndicator() {
        this.stepIndicators.forEach((indicator, index) => {
            if (index < this.currentStep) {
                // Completed step
                indicator.className = 'step-indicator-item w-8 h-8 rounded-full flex items-center justify-center mx-2 transition-all duration-200 bg-green-500 text-white';
                indicator.innerHTML = '<i class="fas fa-check"></i>';
            } else if (index === this.currentStep) {
                // Current step
                indicator.className = 'step-indicator-item w-8 h-8 rounded-full flex items-center justify-center mx-2 transition-all duration-200 bg-green-500 text-white';
                indicator.textContent = index + 1;
            } else {
                // Future step
                indicator.className = 'step-indicator-item w-8 h-8 rounded-full flex items-center justify-center mx-2 transition-all duration-200 bg-gray-300 text-gray-600';
                indicator.textContent = index + 1;
            }
        });
        
        // Update connectors
        this.stepConnectors.forEach((connector, index) => {
            if (index < this.currentStep) {
                connector.className = 'step-connector w-12 h-1 bg-green-500 mx-2 mt-4 transition-all duration-200';
            } else {
                connector.className = 'step-connector w-12 h-1 bg-gray-300 mx-2 mt-4 transition-all duration-200';
            }
        });
    }
    
    setupSubmissionHandling() {
        // Override form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
    }
    
    async handleSubmit() {
        // Validate all fields
        if (!this.validateAll()) {
            this.showNotification('Please fix the errors before submitting', 'error');
            return;
        }
        
        // Show loading state
        this.setSubmissionState(true);
        
        try {
            // Get form data
            const formData = new FormData(this.form);
            
            // Convert to JSON if needed
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            // Submit form
            const response = await fetch(this.form.action || window.location.href, {
                method: this.form.method || 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showNotification(result.message || 'Form submitted successfully', 'success');
                
                // Handle redirect
                if (result.redirect) {
                    setTimeout(() => {
                        window.location.href = result.redirect;
                    }, 1000);
                } else {
                    // Reset form if no redirect
                    this.resetForm();
                }
            } else {
                // Handle server validation errors
                if (result.errors) {
                    this.handleServerErrors(result.errors);
                } else {
                    this.showNotification(result.message || 'An error occurred', 'error');
                }
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.showNotification('Network error. Please try again.', 'error');
        } finally {
            this.setSubmissionState(false);
        }
    }
    
    handleServerErrors(errors) {
        Object.keys(errors).forEach(fieldName => {
            const fieldConfig = this.fields.get(fieldName);
            if (fieldConfig) {
                fieldConfig.isValid = false;
                fieldConfig.isDirty = true;
                fieldConfig.errorMessage = errors[fieldName];
                this.updateFieldUI(fieldConfig);
            }
        });
        
        this.updateFormValidity();
        this.showNotification('Please fix the errors and try again', 'error');
    }
    
    setSubmissionState(isSubmitting) {
        const submitButton = this.form.querySelector('button[type="submit"], input[type="submit"]');
        
        if (isSubmitting) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Submitting...';
            this.form.classList.add('form-submitting');
        } else {
            submitButton.disabled = false;
            submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
            this.form.classList.remove('form-submitting');
        }
    }
    
    resetForm() {
        this.form.reset();
        
        this.fields.forEach((fieldConfig) => {
            fieldConfig.isValid = false;
            fieldConfig.isDirty = false;
            fieldConfig.errorMessage = '';
            this.updateFieldUI(fieldConfig);
        });
        
        // Reset multi-step if applicable
        if (this.totalSteps > 1) {
            this.currentStep = 0;
            const steps = this.form.querySelectorAll('.form-step');
            steps.forEach((step, index) => {
                if (index === 0) {
                    step.classList.remove('hidden');
                } else {
                    step.classList.add('hidden');
                }
            });
            this.updateStepNavigation();
            this.updateStepIndicator();
        }
        
        this.updateFormValidity();
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-x-full`;
        
        // Set notification style based on type
        const styles = {
            success: 'bg-green-100 border-l-4 border-green-500 text-green-700',
            error: 'bg-red-100 border-l-4 border-red-500 text-red-700',
            warning: 'bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700',
            info: 'bg-blue-100 border-l-4 border-blue-500 text-blue-700'
        };
        
        notification.className += ` ${styles[type] || styles.info}`;
        
        // Set notification content
        notification.innerHTML = `
            <div class="flex items-center">
                <div class="flex-1">
                    <p class="font-medium">${message}</p>
                </div>
                <button class="ml-4 text-current opacity-70 hover:opacity-100" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    }
}

// Form component utilities
class FormComponents {
    static createFormField(config) {
        const {
            type = 'text',
            name,
            label,
            placeholder,
            required = false,
            validators = [],
            className = '',
            ...attributes
        } = config;
        
        const container = document.createElement('div');
        container.className = 'form-field relative mb-4';
        
        const input = document.createElement(type === 'textarea' ? 'textarea' : 'input');
        if (type !== 'textarea') {
            input.type = type;
        }
        
        input.name = name;
        input.id = name;
        input.placeholder = placeholder || label;
        input.required = required;
        input.className = `form-input w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 ${className}`;
        
        // Apply additional attributes
        Object.keys(attributes).forEach(key => {
            input.setAttribute(key, attributes[key]);
        });
        
        container.appendChild(input);
        
        return container;
    }
    
    static createMultiStepForm(steps) {
        const form = document.createElement('form');
        form.className = 'multi-step-form';
        
        steps.forEach((stepConfig, index) => {
            const stepElement = document.createElement('div');
            stepElement.className = `form-step ${index !== 0 ? 'hidden' : ''}`;
            
            if (stepConfig.title) {
                const title = document.createElement('h3');
                title.className = 'text-lg font-semibold mb-4';
                title.textContent = stepConfig.title;
                stepElement.appendChild(title);
            }
            
            if (stepConfig.description) {
                const description = document.createElement('p');
                description.className = 'text-gray-600 mb-6';
                description.textContent = stepConfig.description;
                stepElement.appendChild(description);
            }
            
            stepConfig.fields.forEach(fieldConfig => {
                const field = FormComponents.createFormField(fieldConfig);
                stepElement.appendChild(field);
            });
            
            form.appendChild(stepElement);
        });
        
        return form;
    }
}

// Auto-initialize forms with data-form-validator attribute
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('[data-form-validator]');
    
    forms.forEach(form => {
        const options = {};
        
        // Parse options from data attributes
        if (form.dataset.validateOnBlur !== undefined) {
            options.validateOnBlur = form.dataset.validateOnBlur === 'true';
        }
        
        if (form.dataset.validateOnInput !== undefined) {
            options.validateOnInput = form.dataset.validateOnInput === 'true';
        }
        
        if (form.dataset.showSuccessStates !== undefined) {
            options.showSuccessStates = form.dataset.showSuccessStates === 'true';
        }
        
        new FormValidator(form, options);
    });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FormValidator, FormComponents };
}