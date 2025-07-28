// BuyRoll Enhanced Form Components JavaScript

class FormComponents {
  constructor() {
    this.wizards = new Map();
    this.fileUploads = new Map();
    this.customSelects = new Map();
    this.init();
  }

  init() {
    this.setupFloatingLabels();
    this.setupFormWizards();
    this.setupFileUploads();
    this.setupCustomSelects();
    this.setupTooltips();
    this.setupFormValidation();
  }

  // Floating Labels
  setupFloatingLabels() {
    const floatingInputs = document.querySelectorAll('.floating-input-field');
    
    floatingInputs.forEach(input => {
      // Set placeholder to ensure floating label works
      if (!input.placeholder) {
        input.placeholder = ' ';
      }

      // Handle autofill
      this.handleAutofill(input);
    });
  }

  handleAutofill(input) {
    // Check for autofill on load
    setTimeout(() => {
      if (input.value) {
        input.classList.add('has-value');
      }
    }, 100);

    // Monitor for autofill changes
    input.addEventListener('animationstart', (e) => {
      if (e.animationName === 'onAutoFillStart') {
        input.classList.add('has-value');
      }
    });

    input.addEventListener('input', () => {
      if (input.value) {
        input.classList.add('has-value');
      } else {
        input.classList.remove('has-value');
      }
    });
  }

  // Form Wizards
  setupFormWizards() {
    const wizards = document.querySelectorAll('.form-wizard');
    