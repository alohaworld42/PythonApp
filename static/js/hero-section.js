// BuyRoll Hero Section JavaScript

class HeroSection {
  constructor() {
    this.init();
  }

  init() {
    this.setupScrollIndicator();
    this.setupVideoButton();
    this.setupParallaxEffect();
    this.setupTypingAnimation();
    this.setupCounterAnimation();
    this.setupFloatingElements();
  }

  // Scroll Indicator
  setupScrollIndicator() {
    const scrollIndicator = document.querySelector('.hero-scroll-indicator');
    if (!scrollIndicator) return;

    scrollIndicator.addEventListener('click', () => {
      const nextSection = document.querySelector('.hero-modern').nextElementSibling;
      if (nextSection) {
        nextSection.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });

    // Hide scroll indicator when user scrolls
    let scrollTimeout;
    window.addEventListener('scroll', () => {
      if (window.scrollY > 100) {
        scrollIndicator.style.opacity = '0';
      } else {
        scrollIndicator.style.opacity = '0.8';
      }

      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        if (window.scrollY <= 100) {
          scrollIndicator.style.opacity = '0.8';
        }
      }, 150);
    });
  }

  // Video Button
  setupVideoButton() {
    const videoButton = document.querySelector('.hero-video-button');
    if (!videoButton) return;

    videoButton.addEventListener('click', () => {
      this.openVideoModal();
    });
  }

  openVideoModal() {
    const modal = document.createElement('div');
    modal.className = 'video-modal';
    modal.innerHTML = `
      <div class="video-modal-backdrop"></div>
      <div class="video-modal-content">
        <button class="video-modal-close">&times;</button>
        <div class="video-container">
          <iframe 
            src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1" 
            frameborder="0" 
            allowfullscreen
            allow="autoplay; encrypted-media">
          </iframe>
        </div>
      </div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      .video-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .video-modal-backdrop {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        cursor: pointer;
      }
      
      .video-modal-content {
        position: relative;
        width: 90%;
        max-width: 800px;
        aspect-ratio: 16/9;
        background: #000;
        border-radius: 8px;
        overflow: hidden;
      }
      
      .video-modal-close {
        position: absolute;
        top: -40px;
        right: 0;
        background: none;
        border: none;
        color: white;
        font-size: 2rem;
        cursor: pointer;
        z-index: 1001;
      }
      
      .video-container {
        width: 100%;
        height: 100%;
      }
      
      .video-container iframe {
        width: 100%;
        height: 100%;
      }
    `;

    document.head.appendChild(style);
    document.body.appendChild(modal);

    // Close modal functionality
    const closeModal = () => {
      document.body.removeChild(modal);
      document.head.removeChild(style);
    };

    modal.querySelector('.video-modal-close').addEventListener('click', closeModal);
    modal.querySelector('.video-modal-backdrop').addEventListener('click', closeModal);

    // Close on escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        closeModal();
        document.removeEventListener('keydown', handleEscape);
      }
    };
    document.addEventListener('keydown', handleEscape);
  }

  // Parallax Effect
  setupParallaxEffect() {
    const hero = document.querySelector('.hero-modern');
    const floatingElements = document.querySelectorAll('.floating-shape');
    
    if (!hero || !floatingElements.length) return;

    const handleScroll = () => {
      const scrolled = window.pageYOffset;
      const rate = scrolled * -0.5;

      // Move floating elements
      floatingElements.forEach((element, index) => {
        const speed = 0.2 + (index * 0.1);
        element.style.transform = `translateY(${scrolled * speed}px)`;
      });

      // Parallax background
      const background = hero.querySelector('.hero-background');
      if (background) {
        background.style.transform = `translateY(${rate}px)`;
      }
    };

    window.addEventListener('scroll', this.throttle(handleScroll, 16));
  }

  // Typing Animation
  setupTypingAnimation() {
    const typingElements = document.querySelectorAll('[data-typing]');
    
    typingElements.forEach(element => {
      const text = element.dataset.typing;
      const speed = parseInt(element.dataset.typingSpeed) || 100;
      
      element.textContent = '';
      this.typeText(element, text, speed);
    });
  }

  typeText(element, text, speed) {
    let index = 0;
    
    const type = () => {
      if (index < text.length) {
        element.textContent += text.charAt(index);
        index++;
        setTimeout(type, speed);
      } else {
        // Add blinking cursor
        element.classList.add('typing-complete');
      }
    };
    
    type();
  }

  // Counter Animation
  setupCounterAnimation() {
    const counters = document.querySelectorAll('.hero-stat-number[data-count]');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    });

    counters.forEach(counter => observer.observe(counter));
  }

  animateCounter(element) {
    const target = parseInt(element.dataset.count);
    const duration = parseInt(element.dataset.duration) || 2000;
    const suffix = element.dataset.suffix || '';
    
    let current = 0;
    const increment = target / (duration / 16);
    
    const updateCounter = () => {
      current += increment;
      if (current >= target) {
        current = target;
      }
      
      element.textContent = Math.floor(current).toLocaleString() + suffix;
      
      if (current < target) {
        requestAnimationFrame(updateCounter);
      }
    };
    
    updateCounter();
  }

  // Floating Elements Animation
  setupFloatingElements() {
    const floatingElements = document.querySelectorAll('.floating-shape');
    
    floatingElements.forEach((element, index) => {
      // Random initial position adjustments
      const randomX = (Math.random() - 0.5) * 100;
      const randomY = (Math.random() - 0.5) * 100;
      
      element.style.setProperty('--random-x', `${randomX}px`);
      element.style.setProperty('--random-y', `${randomY}px`);
      
      // Add mouse interaction
      element.addEventListener('mouseenter', () => {
        element.style.transform = `translate(var(--random-x), var(--random-y)) scale(1.2)`;
      });
      
      element.addEventListener('mouseleave', () => {
        element.style.transform = `translate(var(--random-x), var(--random-y)) scale(1)`;
      });
    });
  }

  // CTA Button Enhancements
  setupCTAButtons() {
    const ctaButtons = document.querySelectorAll('.hero-cta-primary');
    
    ctaButtons.forEach(button => {
      // Add ripple effect
      button.addEventListener('click', (e) => {
        this.createRipple(e, button);
      });
      
      // Add loading state for form submissions
      if (button.type === 'submit' || button.dataset.loading) {
        button.addEventListener('click', () => {
          this.showButtonLoading(button);
        });
      }
    });
  }

  createRipple(event, button) {
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s linear;
      pointer-events: none;
    `;
    
    // Add ripple animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes ripple {
        to {
          transform: scale(4);
          opacity: 0;
        }
      }
    `;
    
    if (!document.querySelector('#ripple-styles')) {
      style.id = 'ripple-styles';
      document.head.appendChild(style);
    }
    
    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);
    
    setTimeout(() => {
      ripple.remove();
    }, 600);
  }

  showButtonLoading(button) {
    const originalText = button.textContent;
    button.classList.add('btn-loading');
    button.disabled = true;
    
    // Simulate loading (remove this in production)
    setTimeout(() => {
      button.classList.remove('btn-loading');
      button.disabled = false;
      button.textContent = originalText;
    }, 2000);
  }

  // Utility function
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

  // Intersection Observer for animations
  setupScrollAnimations() {
    const animatedElements = document.querySelectorAll('.hero-badge, .hero-title, .hero-subtitle, .hero-actions, .hero-social-proof, .hero-stats');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    animatedElements.forEach(el => observer.observe(el));
  }
}

// Initialize Hero Section
document.addEventListener('DOMContentLoaded', () => {
  window.heroSection = new HeroSection();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = HeroSection;
}