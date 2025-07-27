// BuyRoll Features Section JavaScript

class FeaturesSection {
  constructor() {
    this.activeTab = 0;
    this.activeDemo = 0;
    this.init();
  }

  init() {
    this.setupFeatureCards();
    this.setupTabs();
    this.setupScrollAnimations();
    this.setupFeatureDemo();
    this.setupComparisonTable();
    this.setupStatCounters();
  }

  // Interactive Feature Cards
  setupFeatureCards() {
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach((card, index) => {
      // Add click interaction
      card.addEventListener('click', () => {
        this.activateFeatureCard(card, index);
      });

      // Add keyboard support
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.activateFeatureCard(card, index);
        }
      });

      // Add hover effects
      card.addEventListener('mouseenter', () => {
        this.previewFeature(card, index);
      });

      card.addEventListener('mouseleave', () => {
        this.resetFeaturePreview(card, index);
      });
    });
  }

  activateFeatureCard(card, index) {
    // Remove active class from all cards
    document.querySelectorAll('.feature-card').forEach(c => {
      c.classList.remove('active');
    });

    // Add active class to clicked card
    card.classList.add('active');

    // Show feature details or demo
    this.showFeatureDetails(index);

    // Announce to screen readers
    this.announceFeatureChange(card.querySelector('.feature-title').textContent);
  }

  previewFeature(card, index) {
    if (!card.classList.contains('active')) {
      card.style.transform = 'translateY(-12px) scale(1.02)';
    }
  }

  resetFeaturePreview(card, index) {
    if (!card.classList.contains('active')) {
      card.style.transform = '';
    }
  }

  showFeatureDetails(index) {
    const features = [
      {
        title: 'Unified Shopping Dashboard',
        demo: 'dashboard-demo',
        description: 'See all your orders, addresses, and shopping activity in one place.'
      },
      {
        title: 'Social Shopping Network',
        demo: 'social-demo',
        description: 'Connect with friends and share your favorite products.'
      },
      {
        title: 'Smart Price Tracking',
        demo: 'tracking-demo',
        description: 'Get notified when prices drop on items you want.'
      }
    ];

    const feature = features[index];
    if (feature) {
      this.updateFeatureDemo(feature);
    }
  }

  // Tab System
  setupTabs() {
    const tabs = document.querySelectorAll('.features-tab');
    const tabContents = document.querySelectorAll('.features-tab-content');

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => {
        this.switchTab(index, tabs, tabContents);
      });

      tab.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.switchTab(index, tabs, tabContents);
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
          e.preventDefault();
          const direction = e.key === 'ArrowLeft' ? -1 : 1;
          const newIndex = (index + direction + tabs.length) % tabs.length;
          tabs[newIndex].focus();
          this.switchTab(newIndex, tabs, tabContents);
        }
      });
    });
  }

  switchTab(index, tabs, tabContents) {
    // Remove active class from all tabs and contents
    tabs.forEach(tab => tab.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));

    // Add active class to selected tab and content
    tabs[index].classList.add('active');
    if (tabContents[index]) {
      tabContents[index].classList.add('active');
    }

    this.activeTab = index;

    // Animate tab content
    this.animateTabContent(tabContents[index]);
  }

  animateTabContent(content) {
    if (!content) return;

    content.style.opacity = '0';
    content.style.transform = 'translateY(20px)';

    setTimeout(() => {
      content.style.transition = 'all 0.3s ease-out';
      content.style.opacity = '1';
      content.style.transform = 'translateY(0)';
    }, 50);
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

    // Observe feature cards
    document.querySelectorAll('.feature-card').forEach((card, index) => {
      card.classList.add('animate-feature-card');
      card.style.animationDelay = `${index * 0.1}s`;
      observer.observe(card);
    });

    // Observe feature showcases
    document.querySelectorAll('.feature-showcase').forEach((showcase, index) => {
      showcase.classList.add('animate-feature-showcase');
      showcase.style.animationDelay = `${index * 0.2}s`;
      observer.observe(showcase);
    });

    // Observe other elements
    document.querySelectorAll('.features-header, .feature-comparison, .feature-stats').forEach(el => {
      observer.observe(el);
    });
  }

  animateElement(element) {
    if (element.classList.contains('animate-feature-card') || 
        element.classList.contains('animate-feature-showcase')) {
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

  // Feature Demo
  setupFeatureDemo() {
    const demoButtons = document.querySelectorAll('.demo-button');
    const demoContent = document.querySelector('.demo-content');

    demoButtons.forEach((button, index) => {
      button.addEventListener('click', () => {
        this.switchDemo(index, demoButtons, demoContent);
      });
    });

    // Initialize first demo
    if (demoButtons.length > 0) {
      this.switchDemo(0, demoButtons, document.querySelector('.demo-content'));
    }
  }

  switchDemo(index, buttons, content) {
    // Remove active class from all buttons
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Add active class to selected button
    buttons[index].classList.add('active');

    this.activeDemo = index;

    // Update demo content
    this.updateDemoContent(index, content);
  }

  updateDemoContent(index, content) {
    const demos = [
      {
        title: 'Dashboard Overview',
        html: `
          <div class="demo-dashboard">
            <div class="demo-card">
              <h4>Recent Orders</h4>
              <div class="demo-order">📦 Nike Shoes - Delivered</div>
              <div class="demo-order">🎧 AirPods - In Transit</div>
            </div>
            <div class="demo-card">
              <h4>Price Alerts</h4>
              <div class="demo-alert">💰 iPhone 15 - Price Drop!</div>
            </div>
          </div>
        `
      },
      {
        title: 'Social Features',
        html: `
          <div class="demo-social">
            <div class="demo-friend">
              <div class="demo-avatar">👤</div>
              <div>Sarah shared a product</div>
            </div>
            <div class="demo-friend">
              <div class="demo-avatar">👤</div>
              <div>Mike liked your review</div>
            </div>
          </div>
        `
      },
      {
        title: 'Price Tracking',
        html: `
          <div class="demo-tracking">
            <div class="demo-chart">📈 Price History</div>
            <div class="demo-notification">🔔 Price dropped by 20%!</div>
          </div>
        `
      }
    ];

    const demo = demos[index] || demos[0];
    
    // Fade out
    content.style.opacity = '0';
    
    setTimeout(() => {
      content.innerHTML = demo.html;
      content.style.opacity = '1';
      this.styleDemoContent();
    }, 200);
  }

  styleDemoContent() {
    const style = document.createElement('style');
    style.textContent = `
      .demo-dashboard, .demo-social, .demo-tracking {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        width: 100%;
        max-width: 400px;
      }
      
      .demo-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }
      
      .demo-card h4 {
        margin: 0 0 0.5rem 0;
        color: var(--color-primary-900);
      }
      
      .demo-order, .demo-alert, .demo-friend {
        padding: 0.5rem;
        background: var(--color-primary-300);
        background-opacity: 0.1;
        border-radius: 0.25rem;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }
      
      .demo-avatar {
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        background: var(--color-primary-800);
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .demo-chart, .demo-notification {
        padding: 1rem;
        text-align: center;
        background: var(--color-primary-300);
        background-opacity: 0.1;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
      }
    `;
    
    if (!document.querySelector('#demo-styles')) {
      style.id = 'demo-styles';
      document.head.appendChild(style);
    }
  }

  updateFeatureDemo(feature) {
    const demoContent = document.querySelector('.demo-content');
    if (demoContent) {
      demoContent.innerHTML = `
        <div class="feature-demo-content">
          <h3>${feature.title}</h3>
          <p>${feature.description}</p>
          <div class="demo-placeholder">Interactive demo coming soon...</div>
        </div>
      `;
    }
  }

  // Comparison Table
  setupComparisonTable() {
    const table = document.querySelector('.comparison-table');
    if (!table) return;

    // Add hover effects to rows
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
      row.addEventListener('mouseenter', () => {
        row.style.backgroundColor = 'rgba(106, 190, 17, 0.05)';
      });

      row.addEventListener('mouseleave', () => {
        row.style.backgroundColor = '';
      });
    });

    // Make table responsive
    this.makeTableResponsive(table);
  }

  makeTableResponsive(table) {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-responsive';
    wrapper.style.cssText = `
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      border-radius: var(--radius-lg);
    `;

    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);

    // Add scroll indicators
    const scrollIndicator = document.createElement('div');
    scrollIndicator.className = 'scroll-indicator';
    scrollIndicator.textContent = '← Scroll to see more →';
    scrollIndicator.style.cssText = `
      text-align: center;
      padding: 0.5rem;
      background: var(--color-primary-300);
      background-opacity: 0.1;
      font-size: var(--font-size-sm);
      color: var(--color-primary-900);
      display: none;
    `;

    wrapper.appendChild(scrollIndicator);

    // Show/hide scroll indicator
    wrapper.addEventListener('scroll', () => {
      const isScrollable = wrapper.scrollWidth > wrapper.clientWidth;
      const isAtEnd = wrapper.scrollLeft >= wrapper.scrollWidth - wrapper.clientWidth - 10;
      
      scrollIndicator.style.display = isScrollable && !isAtEnd ? 'block' : 'none';
    });

    // Initial check
    setTimeout(() => {
      const isScrollable = wrapper.scrollWidth > wrapper.clientWidth;
      scrollIndicator.style.display = isScrollable ? 'block' : 'none';
    }, 100);
  }

  // Statistics Counter
  setupStatCounters() {
    const statNumbers = document.querySelectorAll('.feature-stat-number[data-count]');
    
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

  // Utility Methods
  announceFeatureChange(featureName) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = `Selected feature: ${featureName}`;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }

  // Public API
  activateTab(index) {
    const tabs = document.querySelectorAll('.features-tab');
    const tabContents = document.querySelectorAll('.features-tab-content');
    
    if (tabs[index]) {
      this.switchTab(index, tabs, tabContents);
    }
  }

  activateFeature(index) {
    const cards = document.querySelectorAll('.feature-card');
    
    if (cards[index]) {
      this.activateFeatureCard(cards[index], index);
    }
  }

  getCurrentTab() {
    return this.activeTab;
  }

  getCurrentDemo() {
    return this.activeDemo;
  }
}

// Initialize Features Section
document.addEventListener('DOMContentLoaded', () => {
  window.featuresSection = new FeaturesSection();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FeaturesSection;
}