// BuyRoll Loading Manager

class LoadingManager {
  constructor() {
    this.loadingStates = new Map();
    this.init();
  }

  init() {
    this.setupPageTransitions();
    this.setupLazyLoading();
    this.setupProgressBars();
    this.setupSkeletonLoading();
  }

  // Page Transitions
  setupPageTransitions() {
    // Handle page navigation transitions
    document.addEventListener('DOMContentLoaded', () => {
      document.body.classList.add('page-loaded');
    });

    // Handle link clicks for smooth transitions
    document.querySelectorAll('a[data-transition]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        this.transitionToPage(link.href, link.dataset.transition);
      });
    });
  }

  transitionToPage(url, transitionType = 'fade') {
    const overlay = this.createTransitionOverlay(transitionType);
    document.body.appendChild(overlay);

    // Animate out
    setTimeout(() => {
      overlay.classList.add('active');
    }, 10);

    // Navigate after animation
    setTimeout(() => {
      window.location.href = url;
    }, 300);
  }

  createTransitionOverlay(type) {
    const overlay = document.createElement('div');
    overlay.className = `page-transition-overlay page-transition-${type}`;
    
    const styles = {
      position: 'fixed',
      top: '0',
      left: '0',
      width: '100%',
      height: '100%',
      zIndex: '9999',
      pointerEvents: 'none'
    };

    Object.assign(overlay.style, styles);

    switch (type) {
      case 'fade':
        overlay.style.background = 'rgba(255, 255, 255, 0)';
        overlay.style.transition = 'background 0.3s ease';
        break;
      case 'slide':
        overlay.style.background = 'var(--color-white)';
        overlay.style.transform = 'translateX(100%)';
        overlay.style.transition = 'transform 0.3s ease';
        break;
      case 'scale':
        overlay.style.background = 'var(--color-white)';
        overlay.style.transform = 'scale(0)';
        overlay.style.borderRadius = '50%';
        overlay.style.transition = 'transform 0.3s ease';
        break;
    }

    // Add active state styles
    overlay.addEventListener('transitionend', () => {
      if (overlay.classList.contains('active')) {
        switch (type) {
          case 'fade':
            overlay.style.background = 'rgba(255, 255, 255, 1)';
            break;
          case 'slide':
            overlay.style.transform = 'translateX(0)';
            break;
          case 'scale':
            overlay.style.transform = 'scale(2)';
            overlay.style.borderRadius = '0';
            break;
        }
      }
    });

    return overlay;
  }

  // Lazy Loading
  setupLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    const lazyElements = document.querySelectorAll('[data-lazy]');

    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.loadImage(entry.target);
            imageObserver.unobserve(entry.target);
          }
        });
      });

      const elementObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.loadElement(entry.target);
            elementObserver.unobserve(entry.target);
          }
        });
      });

      lazyImages.forEach(img => imageObserver.observe(img));
      lazyElements.forEach(el => elementObserver.observe(el));
    } else {
      // Fallback for browsers without IntersectionObserver
      lazyImages.forEach(img => this.loadImage(img));
      lazyElements.forEach(el => this.loadElement(el));
    }
  }

  loadImage(img) {
    img.classList.add('lazy-loading');
    
    const tempImg = new Image();
    tempImg.onload = () => {
      img.src = img.dataset.src;
      img.classList.remove('lazy-loading');
      img.classList.add('lazy-loaded');
      img.removeAttribute('data-src');
    };
    tempImg.onerror = () => {
      img.classList.remove('lazy-loading');
      img.classList.add('lazy-error');
      this.showImageError(img);
    };
    tempImg.src = img.dataset.src;
  }

  loadElement(element) {
    element.classList.add('lazy-loading');
    
    // Simulate loading delay
    setTimeout(() => {
      element.classList.remove('lazy-loading');
      element.classList.add('lazy-loaded');
      element.removeAttribute('data-lazy');
    }, 500);
  }

  showImageError(img) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'image-error';
    errorDiv.innerHTML = `
      <i class="fas fa-image"></i>
      <span>Failed to load image</span>
    `;
    img.parentNode.replaceChild(errorDiv, img);
  }

  // Progress Bars
  setupProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
      const fill = bar.querySelector('.progress-bar-fill');
      const targetValue = parseInt(bar.dataset.value) || 0;
      
      this.animateProgressBar(fill, targetValue);
    });

    // Circular progress bars
    const circularBars = document.querySelectorAll('.progress-circle');
    circularBars.forEach(circle => {
      const fill = circle.querySelector('.progress-circle-fill');
      const text = circle.querySelector('.progress-circle-text');
      const targetValue = parseInt(circle.dataset.value) || 0;
      
      this.animateCircularProgress(fill, text, targetValue);
    });
  }

  animateProgressBar(fill, targetValue, duration = 1000) {
    let currentValue = 0;
    const increment = targetValue / (duration / 16); // 60fps
    
    const animate = () => {
      currentValue += increment;
      if (currentValue >= targetValue) {
        currentValue = targetValue;
      }
      
      fill.style.width = `${currentValue}%`;
      
      if (currentValue < targetValue) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }

  animateCircularProgress(fill, text, targetValue, duration = 1000) {
    const circumference = 251.2; // 2 * π * 40 (radius)
    let currentValue = 0;
    const increment = targetValue / (duration / 16);
    
    const animate = () => {
      currentValue += increment;
      if (currentValue >= targetValue) {
        currentValue = targetValue;
      }
      
      const offset = circumference - (currentValue / 100) * circumference;
      fill.style.strokeDashoffset = offset;
      
      if (text) {
        text.textContent = `${Math.round(currentValue)}%`;
      }
      
      if (currentValue < targetValue) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }

  // Skeleton Loading
  setupSkeletonLoading() {
    const skeletonContainers = document.querySelectorAll('[data-skeleton]');
    
    skeletonContainers.forEach(container => {
      const skeletonType = container.dataset.skeleton;
      const skeletonHTML = this.generateSkeletonHTML(skeletonType);
      
      container.innerHTML = skeletonHTML;
      container.classList.add('skeleton-container');
      
      // Simulate loading completion
      const loadingTime = parseInt(container.dataset.loadingTime) || 2000;
      setTimeout(() => {
        this.hideSkeleton(container);
      }, loadingTime);
    });
  }

  generateSkeletonHTML(type) {
    const skeletons = {
      'product-card': `
        <div class="skeleton-product-card">
          <div class="skeleton skeleton-badge"></div>
          <div class="skeleton skeleton-image"></div>
          <div class="skeleton skeleton-title"></div>
          <div class="skeleton skeleton-price"></div>
          <div class="skeleton skeleton-source"></div>
          <div class="skeleton-rating">
            <div class="skeleton skeleton-stars"></div>
            <div class="skeleton skeleton-share"></div>
          </div>
          <div class="skeleton skeleton-shipping"></div>
          <div class="skeleton skeleton-button"></div>
        </div>
      `,
      'text': `
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text"></div>
      `,
      'profile': `
        <div style="display: flex; align-items: center; gap: 1rem;">
          <div class="skeleton skeleton-avatar"></div>
          <div style="flex: 1;">
            <div class="skeleton skeleton-text-lg" style="width: 60%; margin-bottom: 0.5rem;"></div>
            <div class="skeleton skeleton-text-sm" style="width: 40%;"></div>
          </div>
        </div>
      `,
      'card': `
        <div class="skeleton skeleton-card"></div>
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text"></div>
      `
    };
    
    return skeletons[type] || skeletons.text;
  }

  hideSkeleton(container) {
    container.classList.add('skeleton-fade-out');
    
    setTimeout(() => {
      container.classList.remove('skeleton-container', 'skeleton-fade-out');
      container.innerHTML = container.dataset.content || '<p>Content loaded!</p>';
      container.classList.add('content-loaded');
    }, 300);
  }

  // Loading States Management
  showLoading(element, type = 'spinner') {
    const loadingId = this.generateLoadingId();
    this.loadingStates.set(loadingId, { element, type });
    
    element.classList.add(`${type}-loading`);
    
    if (type === 'overlay') {
      this.showLoadingOverlay(element);
    }
    
    return loadingId;
  }

  hideLoading(loadingId) {
    const loadingState = this.loadingStates.get(loadingId);
    if (!loadingState) return;
    
    const { element, type } = loadingState;
    element.classList.remove(`${type}-loading`);
    
    if (type === 'overlay') {
      this.hideLoadingOverlay();
    }
    
    this.loadingStates.delete(loadingId);
  }

  showLoadingOverlay(content = null) {
    const existing = document.querySelector('.loading-overlay');
    if (existing) return;
    
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    
    const overlayContent = document.createElement('div');
    overlayContent.className = 'loading-overlay-content';
    
    if (content) {
      overlayContent.appendChild(content);
    } else {
      overlayContent.innerHTML = `
        <div class="loading-overlay-spinner">
          <div class="spinner-lg"></div>
        </div>
        <div class="loading-overlay-text">Loading...</div>
      `;
    }
    
    overlay.appendChild(overlayContent);
    document.body.appendChild(overlay);
    
    // Animate in
    setTimeout(() => {
      overlay.style.opacity = '1';
    }, 10);
  }

  hideLoadingOverlay() {
    const overlay = document.querySelector('.loading-overlay');
    if (!overlay) return;
    
    overlay.style.opacity = '0';
    setTimeout(() => {
      if (overlay.parentNode) {
        overlay.parentNode.removeChild(overlay);
      }
    }, 300);
  }

  generateLoadingId() {
    return `loading_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Utility Methods
  showError(element, message = 'An error occurred') {
    element.innerHTML = `
      <div class="error-state">
        <div class="error-state-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="error-state-message">${message}</div>
        <button class="btn btn-outline error-state-action" onclick="location.reload()">
          Try Again
        </button>
      </div>
    `;
  }

  showEmpty(element, title = 'No items found', message = 'There are no items to display at the moment.') {
    element.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">
          <i class="fas fa-inbox"></i>
        </div>
        <div class="empty-state-title">${title}</div>
        <div class="empty-state-message">${message}</div>
      </div>
    `;
  }

  showSuccess(element, message = 'Operation completed successfully!') {
    element.innerHTML = `
      <div class="success-state">
        <div class="success-state-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="success-state-message">${message}</div>
      </div>
    `;
  }
}

// Initialize Loading Manager
document.addEventListener('DOMContentLoaded', () => {
  window.loadingManager = new LoadingManager();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LoadingManager;
}