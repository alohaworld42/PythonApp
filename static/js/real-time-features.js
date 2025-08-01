/**
 * Real-time Features for BuyRoll
 * WebSocket connections, live updates, and collaborative features
 */

class RealTimeFeatures {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        this.init();
    }

    init() {
        this.setupWebSocket();
        this.setupLiveNotifications();
        this.setupCollaborativeFeatures();
        this.setupRealTimeUpdates();
        this.setupPresenceIndicators();
    }

    // WebSocket Connection
    setupWebSocket() {
        // For demo purposes, we'll simulate WebSocket functionality
        // In production, you'd connect to a real WebSocket server
        this.simulateWebSocket();
    }

    simulateWebSocket() {
        // Simulate connection
        setTimeout(() => {
            this.isConnected = true;
            this.onConnect();
            
            // Simulate periodic messages
            setInterval(() => {
                this.simulateIncomingMessage();
            }, 15000); // Every 15 seconds
        }, 1000);
    }

    onConnect() {
        console.log('🔗 Real-time connection established');
        this.showConnectionStatus('connected');
        
        // Send user presence
        this.sendPresence('online');
        
        // Join user's rooms/channels
        this.joinUserChannels();
    }

    simulateIncomingMessage() {
        const messageTypes = [
            'new_product',
            'price_drop',
            'friend_activity',
            'system_notification',
            'user_mention'
        ];
        
        const randomType = messageTypes[Math.floor(Math.random() * messageTypes.length)];
        this.handleIncomingMessage(randomType);
    }

    handleIncomingMessage(type) {
        switch (type) {
            case 'new_product':
                this.handleNewProduct();
                break;
            case 'price_drop':
                this.handlePriceDrop();
                break;
            case 'friend_activity':
                this.handleFriendActivity();
                break;
            case 'system_notification':
                this.handleSystemNotification();
                break;
            case 'user_mention':
                this.handleUserMention();
                break;
        }
    }

    // Live Notifications
    setupLiveNotifications() {
        this.createNotificationCenter();
        this.setupNotificationPermissions();
    }

    createNotificationCenter() {
        const notificationCenter = document.createElement('div');
        notificationCenter.className = 'notification-center';
        notificationCenter.innerHTML = `
            <div class="notification-center-header">
                <h3>Live Updates</h3>
                <button class="notification-center-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="notification-center-body">
                <div class="notification-list" id="liveNotificationList">
                    <div class="notification-item system">
                        <div class="notification-icon">
                            <i class="fas fa-info-circle"></i>
                        </div>
                        <div class="notification-content">
                            <p>Real-time updates are now active</p>
                            <span class="notification-time">Just now</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(notificationCenter);
        this.setupNotificationCenterEvents(notificationCenter);
    }

    setupNotificationCenterEvents(center) {
        const closeBtn = center.querySelector('.notification-center-close');
        closeBtn.addEventListener('click', () => {
            center.classList.remove('active');
        });

        // Add notification bell to navigation
        const navActions = document.querySelector('.nav .flex.items-center.space-x-4');
        if (navActions) {
            const bellBtn = navActions.querySelector('button[data-tooltip="Notifications"]');
            if (bellBtn) {
                bellBtn.addEventListener('click', () => {
                    center.classList.toggle('active');
                });
            }
        }
    }

    setupNotificationPermissions() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.showBrowserNotification('BuyRoll', 'Notifications enabled! You\'ll receive live updates.');
                }
            });
        }
    }

    // Collaborative Features
    setupCollaborativeFeatures() {
        this.setupLiveComments();
        this.setupCollaborativeLists();
        this.setupRealTimeChat();
    }

    setupLiveComments() {
        const productCards = document.querySelectorAll('.product-card');
        productCards.forEach(card => {
            this.addLiveCommentFeature(card);
        });
    }

    addLiveCommentFeature(card) {
        const commentBtn = document.createElement('button');
        commentBtn.className = 'btn btn-ghost btn-sm live-comment-btn';
        commentBtn.innerHTML = '<i class="fas fa-comment mr-1"></i><span class="comment-count">0</span>';
        
        const actions = card.querySelector('.product-actions');
        if (actions) {
            actions.appendChild(commentBtn);
            
            commentBtn.addEventListener('click', () => {
                this.openLiveComments(card);
            });
        }
    }

    openLiveComments(card) {
        const modal = this.createLiveCommentsModal(card);
        document.body.appendChild(modal);
        modal.classList.add('active');
        
        // Simulate live comments
        this.simulateLiveComments(modal);
    }

    createLiveCommentsModal(card) {
        const modal = document.createElement('div');
        modal.className = 'live-comments-modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Live Comments</h3>
                    <button class="modal-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="comments-list" id="liveCommentsList">
                        <!-- Comments will be populated here -->
                    </div>
                    <div class="comment-input-container">
                        <input type="text" class="comment-input" placeholder="Add a comment...">
                        <button class="btn btn-primary btn-sm send-comment">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Setup modal events
        const closeBtn = modal.querySelector('.modal-close');
        const backdrop = modal.querySelector('.modal-backdrop');
        [closeBtn, backdrop].forEach(el => {
            el.addEventListener('click', () => {
                modal.remove();
            });
        });
        
        return modal;
    }

    // Real-time Updates
    setupRealTimeUpdates() {
        this.setupPriceUpdates();
        this.setupStockUpdates();
        this.setupActivityFeed();
    }

    setupPriceUpdates() {
        const priceElements = document.querySelectorAll('.current-price');
        priceElements.forEach(element => {
            this.watchPriceChanges(element);
        });
    }

    watchPriceChanges(element) {
        // Simulate price changes
        setInterval(() => {
            if (Math.random() > 0.95) { // 5% chance
                this.updatePrice(element);
            }
        }, 10000);
    }

    updatePrice(element) {
        const currentPrice = parseFloat(element.textContent.replace('$', ''));
        const change = (Math.random() - 0.5) * 10; // Random change up to $5
        const newPrice = Math.max(0.99, currentPrice + change);
        
        element.textContent = `$${newPrice.toFixed(2)}`;
        element.classList.add('price-updated');
        
        setTimeout(() => {
            element.classList.remove('price-updated');
        }, 2000);
        
        // Show notification
        this.addLiveNotification('price_update', `Price updated: ${element.textContent}`);
    }

    // Presence Indicators
    setupPresenceIndicators() {
        this.createPresenceIndicators();
        this.updateUserPresence();
    }

    createPresenceIndicators() {
        const userLinks = document.querySelectorAll('.user-link');
        userLinks.forEach(link => {
            const indicator = document.createElement('span');
            indicator.className = 'presence-indicator online';
            link.appendChild(indicator);
        });
    }

    updateUserPresence() {
        setInterval(() => {
            const indicators = document.querySelectorAll('.presence-indicator');
            indicators.forEach(indicator => {
                // Randomly update presence
                if (Math.random() > 0.9) {
                    const states = ['online', 'away', 'offline'];
                    const newState = states[Math.floor(Math.random() * states.length)];
                    indicator.className = `presence-indicator ${newState}`;
                }
            });
        }, 30000);
    }

    // Event Handlers
    handleNewProduct() {
        this.addLiveNotification('new_product', 'New product added by @techguru');
        this.updateProductCount();
    }

    handlePriceDrop() {
        this.addLiveNotification('price_drop', 'Price drop alert: Wireless Headphones now $179.99');
        this.showBrowserNotification('Price Drop!', 'Wireless Headphones price dropped to $179.99');
    }

    handleFriendActivity() {
        this.addLiveNotification('friend_activity', '@sarah_m liked your product');
        this.updateActivityFeed();
    }

    handleSystemNotification() {
        this.addLiveNotification('system', 'System maintenance scheduled for tonight');
    }

    handleUserMention() {
        this.addLiveNotification('mention', '@john_doe mentioned you in a comment');
        this.showBrowserNotification('You were mentioned!', '@john_doe mentioned you in a comment');
    }

    // Utility Methods
    addLiveNotification(type, message) {
        const list = document.getElementById('liveNotificationList');
        if (!list) return;

        const notification = document.createElement('div');
        notification.className = `notification-item ${type}`;
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            </div>
            <div class="notification-content">
                <p>${message}</p>
                <span class="notification-time">Just now</span>
            </div>
        `;

        list.insertBefore(notification, list.firstChild);

        // Remove old notifications (keep only 10)
        const notifications = list.querySelectorAll('.notification-item');
        if (notifications.length > 10) {
            notifications[notifications.length - 1].remove();
        }

        // Update notification badge
        this.updateNotificationBadge();
    }

    getNotificationIcon(type) {
        const icons = {
            new_product: 'plus',
            price_drop: 'tag',
            friend_activity: 'heart',
            system: 'info-circle',
            mention: 'at',
            price_update: 'dollar-sign'
        };
        return icons[type] || 'bell';
    }

    updateNotificationBadge() {
        const badge = document.querySelector('.nav button[data-tooltip="Notifications"] .absolute');
        if (badge) {
            const currentCount = parseInt(badge.textContent) || 0;
            badge.textContent = currentCount + 1;
        }
    }

    showBrowserNotification(title, body) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: body,
                icon: '/static/favicon.ico',
                badge: '/static/favicon.ico'
            });
        }
    }

    showConnectionStatus(status) {
        const statusIndicator = document.createElement('div');
        statusIndicator.className = `connection-status ${status}`;
        statusIndicator.innerHTML = `
            <i class="fas fa-${status === 'connected' ? 'wifi' : 'exclamation-triangle'}"></i>
            <span>${status === 'connected' ? 'Connected' : 'Disconnected'}</span>
        `;
        
        document.body.appendChild(statusIndicator);
        
        setTimeout(() => {
            statusIndicator.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            statusIndicator.remove();
        }, 3000);
    }

    sendPresence(status) {
        console.log(`📡 Sending presence: ${status}`);
        // In production, send to WebSocket server
    }

    joinUserChannels() {
        console.log('🏠 Joining user channels');
        // In production, join relevant channels/rooms
    }

    updateProductCount() {
        // Update product counters in dashboard
        const counters = document.querySelectorAll('[data-count]');
        counters.forEach(counter => {
            if (counter.textContent.includes('Products')) {
                const current = parseInt(counter.textContent) || 0;
                counter.textContent = current + 1;
            }
        });
    }

    updateActivityFeed() {
        // Update activity feed in dashboard
        const activityList = document.querySelector('.activity-list');
        if (activityList) {
            const newActivity = document.createElement('div');
            newActivity.className = 'activity-item';
            newActivity.innerHTML = `
                <div class="activity-icon">
                    <i class="fas fa-heart text-red-500"></i>
                </div>
                <div class="activity-content">
                    <p class="activity-text">@sarah_m liked your product</p>
                    <span class="activity-time">Just now</span>
                </div>
            `;
            
            activityList.insertBefore(newActivity, activityList.firstChild);
        }
    }

    simulateLiveComments(modal) {
        const commentsList = modal.querySelector('#liveCommentsList');
        const sampleComments = [
            { user: '@techguru', text: 'Great product! I have one and love it.', time: '2 min ago' },
            { user: '@shopaholic', text: 'Is this still available?', time: '5 min ago' },
            { user: '@reviewer', text: 'The quality is amazing for the price.', time: '10 min ago' }
        ];
        
        sampleComments.forEach((comment, index) => {
            setTimeout(() => {
                const commentElement = document.createElement('div');
                commentElement.className = 'comment-item';
                commentElement.innerHTML = `
                    <div class="comment-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="comment-content">
                        <div class="comment-header">
                            <span class="comment-user">${comment.user}</span>
                            <span class="comment-time">${comment.time}</span>
                        </div>
                        <p class="comment-text">${comment.text}</p>
                    </div>
                `;
                
                commentsList.appendChild(commentElement);
            }, index * 1000);
        });
    }
}

// Initialize real-time features
document.addEventListener('DOMContentLoaded', () => {
    window.realTimeFeatures = new RealTimeFeatures();
});

// Export for use in other modules
window.RealTimeFeatures = RealTimeFeatures;