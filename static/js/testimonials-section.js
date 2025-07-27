// BuyRoll Testimonials Section JavaScript

class TestimonialsSection {
  constructor() {
    this.currentSlide = 0;
    this.totalSlides = 0;
    this.autoplayInterval = null;
    this.autoplayDelay = 5000;
    this.isPlaying = true;
    this.init();
  }

  init() {
    this.setupCarousel();
    this.setupStatCounters();
    this.setupScrollAnimations();
    this.setupSocialProof();
    this.setupTrustIndicators();
  }

  // Testimonial Carousel
  setupCarousel() {
    const track = document.querySelector('.testimonials-track');
    const slides = document.querySelectorAll('.testimonial-slide');
    const prevButton = document.querySelector('.carousel-prev');
    const nextButton = document.querySelector('.carousel-next');
    const dotsContainer = document.querySelector('.carousel-dots');

    if (!track || !slides.length) return;

    this.totalSlides = slides.length;
    this.track = track;
    this.slides = slides;

    // Create dots
    this.createDots(dotsContainer);

    // Setup event listeners
    if (prevButton) {
      prevButton.addEventListener('click', () => this.prevSlide());
    }

    if (nextButton) {
      nextButton.addEventListener('click', () => this.nextSlide());
    }

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        this.prevSlide();
      } else if (e.key === 'ArrowRight') {
        this.nextSlide();
      }
    });

    // Touch/swipe support
    this.setupTouchEvents();

    // Auto-play
    this.startAutoplay();

    // Pause on hover
    const carousel = document.querySelector('.testimonials-carousel');
    if (carousel) {
      carousel.addEventListener('mouseenter', () => this.pauseAutoplay());
      carousel.addEventListener('mouseleave', () => this.startAutoplay());
    }

    // Initial update
    this.updateCarousel();
  }

  createDots(container) {
    if (!container) return;

    container.innerHTML = '';
    
    for (let i = 0; i < this.totalSlides; i++) {
      const dot = document.createElement('button');
      dot.className = 'carousel-dot';
      dot.setAttribute('aria-label', `Go to testimonial ${i + 1}`);
      
      if (i === 0) {
        dot.classList.add('active');
      }
      
      dot.addEventListener('click', () => this.goToSlide(i));
      container.appendChild(dot);
    }
  }

  setupTouchEvents() {
    let startX = 0;
    let currentX = 0;
    let isDragging = false;

    const carousel = document.querySelector('.testimonials-container');
    if (!carousel) return;

    carousel.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      isDragging = true;
      this.pauseAutoplay();
    });

    carousel.addEventListener('touchmove', (e) => {
      if (!isDragging) return;
      currentX = e.touches[0].clientX;
    });

    carousel.addEventListener('touchend', () => {
      if (!isDragging) return;
      
      const diff = startX - currentX;
      const threshold = 50;

      if (Math.abs(diff) > threshold) {
        if (diff > 0) {
          this.nextSlide();
        } else {
          this.prevSlide();
        }
      }

      isDragging = false;
      this.startAutoplay();
    });

    // Mouse drag support
    let mouseStartX = 0;
    let mouseCurrentX = 0;
    let isMouseDragging = false;

    carousel.addEventListener('mousedown', (e) => {
      mouseStartX = e.clientX;
      isMouseDragging = true;
      carousel.style.cursor = 'grabbing';
      this.pauseAutoplay();
    });

    carousel.addEventListener('mousemove', (e) => {
      if (!isMouseDragging) return;
      mouseCurrentX = e.clientX;
    });

    carousel.addEventListener('mouseup', () => {
      if (!isMouseDragging) return;
      
      const diff = mouseStartX - mouseCurrentX;
      const threshold = 50;

      if (Math.abs(diff) > threshold) {
        if (diff > 0) {
          this.nextSlide();
        } else {
          this.prevSlide();
        }
      }

      isMouseDragging = false;
      carousel.style.cursor = 'grab';
      this.startAutoplay();
    });

    carousel.addEventListener('mouseleave', () => {
      if (isMouseDragging) {
        isMouseDragging = false;
        carousel.style.cursor = 'grab';
        this.startAutoplay();
      }
    });
  }

  nextSlide() {
    this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
    this.updateCarousel();
  }

  prevSlide() {
    this.currentSlide = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
    this.updateCarousel();
  }

  goToSlide(index) {
    this.currentSlide = index;
    this.updateCarousel();
  }

  updateCarousel() {
    if (!this.track) return;

    // Update track position
    const translateX = -this.currentSlide * 100;
    this.track.style.transform = `translateX(${translateX}%)`;

    // Update dots
    const dots = document.querySelectorAll('.carousel-dot');
    dots.forEach((dot, index) => {
      dot.classList.toggle('active', index === this.currentSlide);
    });

    // Update buttons
    const prevButton = document.querySelector('.carousel-prev');
    const nextButton = document.querySelector('.carousel-next');

    if (prevButton) {
      prevButton.disabled = this.currentSlide === 0;
    }

    if (nextButton) {
      nextButton.disabled = this.currentSlide === this.totalSlides - 1;
    }

    // Announce to screen readers
    this.announceSlideChange();
  }

  startAutoplay() {
    if (this.autoplayInterval) {
      clearInterval(this.autoplayInterval);
    }

    this.autoplayInterval = setInterval(() => {
      this.nextSlide();
    }, this.autoplayDelay);

    this.isPlaying = true;
  }

  pauseAutoplay() {
    if (this.autoplayInterval) {
      clearInterval(this.autoplayInterval);
      this.autoplayInterval = null;
    }

    this.isPlaying = false;
  }

  announceSlideChange() {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = `Showing testimonial ${this.currentSlide + 1} of ${this.totalSlides}`;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }

  // Statistics Counter Animation
  setupStatCounters() {
    const statNumbers = document.querySelectorAll('.stat-number[data-count]');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    });

    statNumbers.forEach(stat => observer.observe(stat));
  }

  animateCounter(element) {
    const target = parseInt(element.dataset.count);
    const duration = parseInt(element.dataset.duration) || 2000;
    const suffix = element.dataset.suffix || '';
    const prefix = element.dataset.prefix || '';
    
    let current = 0;
    const increment = target / (duration / 16);
    
    const updateCounter = () => {
      current += increment;
      if (current >= target) {
        current = target;
      }
      
      let displayValue = Math.floor(current);
      
      // Format large numbers
      if (displayValue >= 1000000) {
        displayValue = (displayValue / 1000000).toFixed(1) + 'M';
      } else if (displayValue >= 1000) {
        displayValue = (displayValue / 1000).toFixed(1) + 'K';
      } else {
        displayValue = displayValue.toLocaleString();
      }
      
      element.textContent = prefix + displayValue + suffix;
      
      if (current < target) {
        requestAnimationFrame(updateCounter);
      }
    };
    
    updateCounter();
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
          this.animateElement(entry.target);
        }
      });
    }, observerOptions);

    // Observe testimonial elements
    document.querySelectorAll('.testimonials-header, .testimonial-card, .stat-item, .review-card, .customer-logos, .trust-indicators').forEach((el, index) => {
      el.classList.add('animate-testimonial');
      el.style.animationDelay = `${index * 0.1}s`;
      observer.observe(el);
    });

    // Observe stats with different animation
    document.querySelectorAll('.stat-item').forEach((el, index) => {
      el.classList.add('animate-stat');
      el.style.animationDelay = `${index * 0.2}s`;
      observer.observe(el);
    });
  }

  animateElement(element) {
    if (element.classList.contains('animate-testimonial')) {
      element.classList.add('in-view');
    } else if (element.classList.contains('animate-stat')) {
      element.classList.add('in-view');
    } else {
      element.style.opacity = '0';
      element.style.transform = 'translateY(30px)';
      element.style.transition = 'all 0.6s ease-out';
      
      setTimeout(() => {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
      }, 100);
    }
  }

  // Social Proof Features
  setupSocialProof() {
    // Animate customer logos
    this.animateLogos();
    
    // Setup social media integration
    this.setupSocialLinks();
  }

  animateLogos() {
    const logos = document.querySelectorAll('.customer-logo');
    
    logos.forEach((logo, index) => {
      // Stagger the animation
      setTimeout(() => {
        logo.style.opacity = '0.6';
        logo.style.transform = 'scale(1)';
      }, index * 100);

      // Add hover effect enhancement
      logo.addEventListener('mouseenter', () => {
        logo.style.filter = 'brightness(0) invert(1) drop-shadow(0 0 10px rgba(255,255,255,0.5))';
      });

      logo.addEventListener('mouseleave', () => {
        logo.style.filter = 'brightness(0) invert(1)';
      });
    });
  }

  setupSocialLinks() {
    const socialLinks = document.querySelectorAll('.social-link');
    
    socialLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        // Add click animation
        link.style.transform = 'scale(0.95)';
        setTimeout(() => {
          link.style.transform = '';
        }, 150);

        // Track social media clicks (analytics)
        this.trackSocialClick(link.dataset.platform);
      });
    });
  }

  trackSocialClick(platform) {
    // Analytics tracking for social media clicks
    if (typeof gtag !== 'undefined') {
      gtag('event', 'social_click', {
        'platform': platform,
        'section': 'testimonials'
      });
    }
  }

  // Trust Indicators
  setupTrustIndicators() {
    const trustItems = document.querySelectorAll('.trust-item');
    
    trustItems.forEach((item, index) => {
      // Stagger animation
      item.style.animationDelay = `${index * 0.1}s`;
      
      // Add interactive effects
      item.addEventListener('mouseenter', () => {
        item.style.background = 'rgba(255, 255, 255, 0.2)';
      });

      item.addEventListener('mouseleave', () => {
        item.style.background = 'rgba(255, 255, 255, 0.1)';
      });
    });
  }

  // Review System
  setupReviewSystem() {
    const reviewCards = document.querySelectorAll('.review-card');
    
    reviewCards.forEach(card => {
      // Add click to expand functionality
      card.addEventListener('click', () => {
        this.expandReview(card);
      });

      // Add keyboard support
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.expandReview(card);
        }
      });
    });
  }

  expandReview(card) {
    const content = card.querySelector('.review-content');
    const isExpanded = card.classList.contains('expanded');
    
    if (isExpanded) {
      card.classList.remove('expanded');
      content.style.maxHeight = '3em';
      content.style.overflow = 'hidden';
    } else {
      card.classList.add('expanded');
      content.style.maxHeight = 'none';
      content.style.overflow = 'visible';
    }
  }

  // Public API
  goToTestimonial(index) {
    if (index >= 0 && index < this.totalSlides) {
      this.goToSlide(index);
    }
  }

  playCarousel() {
    this.startAutoplay();
  }

  pauseCarousel() {
    this.pauseAutoplay();
  }

  getCurrentSlide() {
    return this.currentSlide;
  }

  getTotalSlides() {
    return this.totalSlides;
  }

  // Utility Methods
  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
  }

  // Cleanup
  destroy() {
    if (this.autoplayInterval) {
      clearInterval(this.autoplayInterval);
    }
    
    // Remove event listeners
    document.removeEventListener('keydown', this.handleKeydown);
  }
}

// Initialize Testimonials Section
document.addEventListener('DOMContentLoaded', () => {
  window.testimonialsSection = new TestimonialsSection();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TestimonialsSection;
}