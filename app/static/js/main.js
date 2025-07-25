// BuyRoll main JavaScript file

// Import form components
if (typeof FormValidator === 'undefined') {
    // Load form components if not already loaded
    const script = document.createElement('script');
    script.src = '/static/js/form-components.js';
    document.head.appendChild(script);
}

document.addEventListener('DOMContentLoaded', function() {
    // Navigation active state management
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('nav-link-active');
        }
    });
    
    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    });
    
    // Password strength meter
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(function(input) {
        if (input.id === 'password' || input.id === 'new_password') {
            // Create password strength indicator
            const strengthIndicator = document.createElement('div');
            strengthIndicator.className = 'password-strength';
            input.parentNode.appendChild(strengthIndicator);
            
            input.addEventListener('input', function() {
                const password = input.value;
                const strength = checkPasswordStrength(password);
                
                // Update strength indicator
                strengthIndicator.className = 'password-strength';
                if (strength === 0) {
                    strengthIndicator.style.width = '0';
                } else if (strength === 1) {
                    strengthIndicator.classList.add('password-strength-weak');
                } else if (strength === 2) {
                    strengthIndicator.classList.add('password-strength-medium');
                } else if (strength === 3) {
                    strengthIndicator.classList.add('password-strength-strong');
                } else {
                    strengthIndicator.classList.add('password-strength-very-strong');
                }
            });
        }
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        const requiredInputs = form.querySelectorAll('[required]');
        
        form.addEventListener('submit', function(event) {
            let isValid = true;
            
            requiredInputs.forEach(function(input) {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('border-red-500');
                    
                    // Add error message if it doesn't exist
                    let errorMessage = input.parentNode.querySelector('.error-message');
                    if (!errorMessage) {
                        errorMessage = document.createElement('div');
                        errorMessage.className = 'text-red-500 text-xs italic mt-1 error-message';
                        errorMessage.textContent = 'This field is required';
                        input.parentNode.appendChild(errorMessage);
                    }
                } else {
                    input.classList.remove('border-red-500');
                    
                    // Remove error message if it exists
                    const errorMessage = input.parentNode.querySelector('.error-message');
                    if (errorMessage) {
                        errorMessage.remove();
                    }
                    
                    // Validate email
                    if (input.type === 'email') {
                        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                        if (!emailRegex.test(input.value)) {
                            isValid = false;
                            input.classList.add('border-red-500');
                            
                            let errorMessage = input.parentNode.querySelector('.error-message');
                            if (!errorMessage) {
                                errorMessage = document.createElement('div');
                                errorMessage.className = 'text-red-500 text-xs italic mt-1 error-message';
                                errorMessage.textContent = 'Please enter a valid email address';
                                input.parentNode.appendChild(errorMessage);
                            }
                        }
                    }
                    
                    // Validate password
                    if (input.type === 'password' && (input.id === 'password' || input.id === 'new_password')) {
                        if (input.value.length < 8) {
                            isValid = false;
                            input.classList.add('border-red-500');
                            
                            let errorMessage = input.parentNode.querySelector('.error-message');
                            if (!errorMessage) {
                                errorMessage = document.createElement('div');
                                errorMessage.className = 'text-red-500 text-xs italic mt-1 error-message';
                                errorMessage.textContent = 'Password must be at least 8 characters long';
                                input.parentNode.appendChild(errorMessage);
                            }
                        }
                    }
                    
                    // Validate password confirmation
                    if (input.id === 'confirm_password') {
                        const passwordInput = form.querySelector('#password') || form.querySelector('#new_password');
                        if (passwordInput && input.value !== passwordInput.value) {
                            isValid = false;
                            input.classList.add('border-red-500');
                            
                            let errorMessage = input.parentNode.querySelector('.error-message');
                            if (!errorMessage) {
                                errorMessage = document.createElement('div');
                                errorMessage.className = 'text-red-500 text-xs italic mt-1 error-message';
                                errorMessage.textContent = 'Passwords do not match';
                                input.parentNode.appendChild(errorMessage);
                            }
                        }
                    }
                }
            });
            
            if (!isValid) {
                event.preventDefault();
            }
        });
        
        // Real-time validation
        requiredInputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                if (!input.value.trim()) {
                    input.classList.add('border-red-500');
                    
                    // Add error message if it doesn't exist
                    let errorMessage = input.parentNode.querySelector('.error-message');
                    if (!errorMessage) {
                        errorMessage = document.createElement('div');
                        errorMessage.className = 'text-red-500 text-xs italic mt-1 error-message';
                        errorMessage.textContent = 'This field is required';
                        input.parentNode.appendChild(errorMessage);
                    }
                } else {
                    input.classList.remove('border-red-500');
                    
                    // Remove error message if it exists
                    const errorMessage = input.parentNode.querySelector('.error-message');
                    if (errorMessage) {
                        errorMessage.remove();
                    }
                }
            });
        });
    });
    
    // Toggle sharing status with AJAX
    const sharingToggles = document.querySelectorAll('.sharing-toggle');
    sharingToggles.forEach(function(toggle) {
        toggle.addEventListener('change', function() {
            const purchaseId = this.dataset.purchaseId;
            const isShared = this.checked;
            
            fetch(`/api/purchases/${purchaseId}/${isShared ? 'share' : 'unshare'}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    comment: ''  // Could be populated from a comment field
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    // Show success message
                    const successMessage = document.createElement('div');
                    successMessage.className = 'fixed bottom-4 right-4 bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded shadow-md fade-in';
                    successMessage.innerHTML = `<p>${data.message}</p>`;
                    document.body.appendChild(successMessage);
                    
                    setTimeout(function() {
                        successMessage.style.opacity = '0';
                        setTimeout(function() {
                            successMessage.remove();
                        }, 300);
                    }, 3000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Revert toggle state on error
                this.checked = !isShared;
                
                // Show error message
                const errorMessage = document.createElement('div');
                errorMessage.className = 'fixed bottom-4 right-4 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-md fade-in';
                errorMessage.innerHTML = `<p>Error updating sharing status</p>`;
                document.body.appendChild(errorMessage);
                
                setTimeout(function() {
                    errorMessage.style.opacity = '0';
                    setTimeout(function() {
                        errorMessage.remove();
                    }, 300);
                }, 3000);
            });
        });
    });
    
    // Product card interaction handlers
    initializeProductCardInteractions();
    
    // Like functionality with AJAX
    const likeButtons = document.querySelectorAll('.like-button');
    likeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const purchaseId = this.dataset.purchaseId;
            const likeCountElement = this.querySelector('.like-count');
            const icon = this.querySelector('i');
            
            // Add loading state
            this.classList.add('loading');
            
            fetch(`/api/feed/item/${purchaseId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Toggle like button appearance
                    if (data.action === 'liked') {
                        icon.className = 'fas fa-heart';
                        this.classList.add('liked');
                        this.classList.add('text-red-500');
                        this.classList.remove('text-gray-500');
                        
                        // Increment like count
                        if (likeCountElement) {
                            const currentCount = parseInt(likeCountElement.textContent) || 0;
                            likeCountElement.textContent = currentCount + 1;
                        }
                    } else {
                        icon.className = 'far fa-heart';
                        this.classList.remove('liked');
                        this.classList.remove('text-red-500');
                        this.classList.add('text-gray-500');
                        
                        // Decrement like count
                        if (likeCountElement) {
                            const currentCount = parseInt(likeCountElement.textContent) || 0;
                            likeCountElement.textContent = Math.max(0, currentCount - 1);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error updating like status', 'error');
            })
            .finally(() => {
                this.classList.remove('loading');
            });
        });
    });
    
    // Initialize any charts if they exist
    if (typeof Chart !== 'undefined') {
        // Spending by category chart
        const categoryChartElement = document.getElementById('categoryChart');
        if (categoryChartElement) {
            const categoryChart = new Chart(categoryChartElement, {
                type: 'doughnut',
                data: {
                    labels: ['Electronics', 'Clothing', 'Home', 'Other'],
                    datasets: [{
                        data: [450, 320, 280, 200],
                        backgroundColor: [
                            '#55970f',
                            '#6abe11',
                            '#8dc63f',
                            '#a3e635'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        // Monthly spending trend chart
        const trendChartElement = document.getElementById('trendChart');
        if (trendChartElement) {
            const trendChart = new Chart(trendChartElement, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Monthly Spending',
                        data: [120, 180, 250, 200, 300, 200],
                        backgroundColor: 'rgba(85, 151, 15, 0.2)',
                        borderColor: '#55970f',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value;
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }
});

// Helper function to check password strength
function checkPasswordStrength(password) {
    // 0 = Empty, 1 = Weak, 2 = Medium, 3 = Strong, 4 = Very Strong
    if (!password) return 0;
    
    let strength = 0;
    
    // Length check
    if (password.length >= 8) strength += 1;
    if (password.length >= 12) strength += 1;
    
    // Complexity checks
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    
    // Cap at 4
    return Math.min(4, Math.floor(strength / 2));
}

// Product card interaction initialization
function initializeProductCardInteractions() {
    // Initialize comment buttons
    const commentButtons = document.querySelectorAll('.comment-button:not([data-initialized])');
    commentButtons.forEach(function(button) {
        button.setAttribute('data-initialized', 'true');
        button.addEventListener('click', function() {
            const purchaseId = this.dataset.purchaseId;
            toggleCommentForm(purchaseId);
        });
    });
    
    // Initialize save buttons
    const saveButtons = document.querySelectorAll('.save-button:not([data-initialized])');
    saveButtons.forEach(function(button) {
        button.setAttribute('data-initialized', 'true');
        button.addEventListener('click', function() {
            const purchaseId = this.dataset.purchaseId;
            toggleSave(purchaseId);
        });
    });
    
    // Initialize like buttons
    const likeButtons = document.querySelectorAll('.like-button:not([data-initialized])');
    likeButtons.forEach(function(button) {
        button.setAttribute('data-initialized', 'true');
        button.addEventListener('click', function() {
            const purchaseId = this.dataset.purchaseId;
            const likeCountElement = this.querySelector('.like-count');
            const icon = this.querySelector('i');
            const isLiked = this.classList.contains('liked');
            
            // Add loading state
            this.classList.add('loading');
            this.disabled = true;
            
            fetch(`/api/feed/item/${purchaseId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Toggle like button appearance
                    if (data.action === 'liked') {
                        icon.className = 'fas fa-heart';
                        this.classList.add('liked');
                        this.classList.add('text-red-500');
                        this.classList.remove('text-gray-500');
                        
                        // Increment like count
                        if (likeCountElement) {
                            const currentCount = parseInt(likeCountElement.textContent) || 0;
                            likeCountElement.textContent = currentCount + 1;
                        }
                    } else {
                        icon.className = 'far fa-heart';
                        this.classList.remove('liked');
                        this.classList.remove('text-red-500');
                        this.classList.add('text-gray-500');
                        
                        // Decrement like count
                        if (likeCountElement) {
                            const currentCount = parseInt(likeCountElement.textContent) || 0;
                            likeCountElement.textContent = Math.max(0, currentCount - 1);
                        }
                    }
                    
                    showNotification(data.message || `Item ${data.action}`, 'success');
                } else {
                    showNotification(data.message || 'Error updating like status', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error updating like status', 'error');
            })
            .finally(() => {
                this.classList.remove('loading');
                this.disabled = false;
            });
        });
    });
    
    // Initialize sharing toggles (if not already initialized)
    const newSharingToggles = document.querySelectorAll('.sharing-toggle:not([data-initialized])');
    newSharingToggles.forEach(function(toggle) {
        toggle.setAttribute('data-initialized', 'true');
        toggle.addEventListener('change', function() {
            const purchaseId = this.dataset.purchaseId;
            const isShared = this.checked;
            const card = this.closest('.product-card');
            
            // Add loading state to card
            card.classList.add('loading');
            this.disabled = true;
            
            // Update sharing status indicator immediately for better UX
            updateSharingStatus(card, isShared);
            
            fetch(`/api/purchases/${purchaseId}/${isShared ? 'share' : 'unshare'}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    comment: ''
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message || 'Sharing status updated', 'success');
                } else {
                    // Revert toggle state on error
                    this.checked = !isShared;
                    updateSharingStatus(card, !isShared);
                    showNotification(data.message || 'Error updating sharing status', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Revert toggle state on error
                this.checked = !isShared;
                updateSharingStatus(card, !isShared);
                showNotification('Error updating sharing status', 'error');
            })
            .finally(() => {
                card.classList.remove('loading');
                this.disabled = false;
            });
        });
    });
    
    // Initialize image loading handlers
    const productImages = document.querySelectorAll('.product-card img:not([data-initialized])');
    productImages.forEach(function(img) {
        img.setAttribute('data-initialized', 'true');
        
        // Handle image load success
        img.addEventListener('load', function() {
            this.style.opacity = '1';
            const placeholder = this.parentNode.querySelector('.loading-placeholder');
            if (placeholder) {
                placeholder.style.display = 'none';
            }
        });
        
        // Handle image load error
        img.addEventListener('error', function() {
            this.src = '/static/images/placeholder-product.svg';
            this.classList.add('opacity-75');
            const placeholder = this.parentNode.querySelector('.loading-placeholder');
            if (placeholder) {
                placeholder.style.display = 'none';
            }
        });
        
        // If image is already loaded (cached), trigger load event
        if (img.complete) {
            img.dispatchEvent(new Event('load'));
        }
    });
}

// Toggle comment form visibility
function toggleCommentForm(purchaseId) {
    const commentForm = document.getElementById(`comment-form-${purchaseId}`);
    if (commentForm) {
        commentForm.classList.toggle('hidden');
        if (!commentForm.classList.contains('hidden')) {
            const input = commentForm.querySelector('input[name="content"]');
            if (input) input.focus();
        }
    }
}

// Submit comment
function submitComment(event, purchaseId) {
    event.preventDefault();
    const form = event.target;
    const content = form.content.value.trim();
    
    if (!content) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Posting...';
    submitButton.disabled = true;
    
    fetch(`/api/feed/item/${purchaseId}/comment`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Clear form
            form.content.value = '';
            
            // Update comment count
            const commentButton = document.querySelector(`.comment-button[data-purchase-id="${purchaseId}"]`);
            if (commentButton) {
                const countElement = commentButton.querySelector('.comment-count');
                if (countElement) {
                    const currentCount = parseInt(countElement.textContent) || 0;
                    countElement.textContent = currentCount + 1;
                }
            }
            
            // Add comment to comments section if it exists
            const commentsSection = document.getElementById(`comments-${purchaseId}`);
            if (commentsSection && data.comment) {
                addCommentToSection(commentsSection, data.comment);
            }
            
            // Hide comment form
            toggleCommentForm(purchaseId);
            
            showNotification('Comment posted successfully', 'success');
        } else {
            showNotification(data.message || 'Error posting comment', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error posting comment', 'error');
    })
    .finally(() => {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    });
}

// Toggle save status
function toggleSave(purchaseId) {
    const saveButton = document.querySelector(`.save-button[data-purchase-id="${purchaseId}"]`);
    if (!saveButton) return;
    
    const icon = saveButton.querySelector('i');
    const isSaved = saveButton.classList.contains('saved');
    
    // Add loading state
    saveButton.classList.add('loading');
    
    fetch(`/api/feed/item/${purchaseId}/save`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.action === 'saved') {
                icon.className = 'fas fa-bookmark';
                saveButton.classList.add('saved');
                saveButton.classList.add('text-yellow-500');
                saveButton.classList.remove('text-gray-500');
            } else {
                icon.className = 'far fa-bookmark';
                saveButton.classList.remove('saved');
                saveButton.classList.remove('text-yellow-500');
                saveButton.classList.add('text-gray-500');
            }
            
            showNotification(data.message || `Item ${data.action}`, 'success');
        } else {
            showNotification(data.message || 'Error updating save status', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating save status', 'error');
    })
    .finally(() => {
        saveButton.classList.remove('loading');
    });
}

// Enhanced image loading handlers with responsive support
function handleImageLoad(img) {
    img.style.opacity = '1';
    img.classList.add('loaded');
    const placeholder = img.parentNode.querySelector('.loading-placeholder');
    if (placeholder) {
        placeholder.style.opacity = '0';
        setTimeout(() => {
            placeholder.style.display = 'none';
        }, 300);
    }
    
    // Add fade-in animation
    img.style.animation = 'fadeIn 0.3s ease-in-out';
}

function handleImageError(img) {
    img.onerror = null; // Prevent infinite loop
    
    // Try different fallback images based on context
    const fallbackImages = [
        '/static/images/placeholder-product.svg',
        '/static/images/placeholder.png',
        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik04MCA4MEgxMjBWMTIwSDgwVjgwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K'
    ];
    
    const currentSrc = img.src;
    const nextFallback = fallbackImages.find(src => src !== currentSrc);
    
    if (nextFallback) {
        img.src = nextFallback;
    }
    
    img.classList.add('opacity-75', 'loaded');
    img.style.opacity = '1';
    img.alt = 'Product image unavailable';
    
    const placeholder = img.parentNode.querySelector('.loading-placeholder');
    if (placeholder) {
        placeholder.style.opacity = '0';
        setTimeout(() => {
            placeholder.style.display = 'none';
        }, 300);
    }
}

// Update sharing status indicators in the card
function updateSharingStatus(card, isShared) {
    const statusIndicators = card.querySelectorAll('[data-sharing]');
    statusIndicators.forEach(indicator => {
        indicator.setAttribute('data-sharing', isShared ? 'shared' : 'private');
    });
    
    // Update sharing status badges
    const statusBadges = card.querySelectorAll('.bg-green-100, .bg-gray-100');
    statusBadges.forEach(badge => {
        if (isShared) {
            badge.className = badge.className.replace('bg-gray-100 text-gray-800', 'bg-green-100 text-green-800');
            const icon = badge.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-share-alt mr-1';
            }
            const text = badge.querySelector('span') || badge;
            if (text.textContent.includes('Private')) {
                text.textContent = text.textContent.replace('Private', 'Shared');
            }
        } else {
            badge.className = badge.className.replace('bg-green-100 text-green-800', 'bg-gray-100 text-gray-800');
            const icon = badge.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-lock mr-1';
            }
            const text = badge.querySelector('span') || badge;
            if (text.textContent.includes('Shared')) {
                text.textContent = text.textContent.replace('Shared', 'Private');
            }
        }
    });
}

// Show notification helper
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const typeClasses = {
        success: 'bg-green-100 border-green-500 text-green-700',
        error: 'bg-red-100 border-red-500 text-red-700',
        warning: 'bg-yellow-100 border-yellow-500 text-yellow-700',
        info: 'bg-blue-100 border-blue-500 text-blue-700'
    };
    
    notification.className = `fixed bottom-4 right-4 ${typeClasses[type]} border-l-4 p-4 rounded shadow-md fade-in z-50 max-w-sm`;
    notification.innerHTML = `
        <div class="flex items-center">
            <p class="text-sm font-medium">${message}</p>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-current hover:opacity-75">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

// Add comment to comments section
function addCommentToSection(commentsSection, comment) {
    const commentElement = document.createElement('div');
    commentElement.className = 'bg-gray-50 rounded-lg p-3 fade-in';
    commentElement.innerHTML = `
        <div class="flex items-center mb-1">
            <img src="/static/images/profile/${comment.user.profile_image || 'default.jpg'}" 
                 alt="${comment.user.name}" 
                 class="w-6 h-6 rounded-full mr-2 object-cover">
            <span class="font-semibold text-sm text-gray-800">${comment.user.name}</span>
            <span class="text-xs text-gray-500 ml-2">just now</span>
        </div>
        <p class="text-gray-700 text-sm">${comment.content}</p>
    `;
    
    // Insert at the beginning of comments
    const commentsContainer = commentsSection.querySelector('.space-y-2');
    if (commentsContainer) {
        commentsContainer.insertBefore(commentElement, commentsContainer.firstChild);
    } else {
        commentsSection.appendChild(commentElement);
    }
}

// View product details
function viewProductDetails(purchaseId) {
    // This could open a modal or navigate to a detail page
    // For now, we'll just log it
    console.log('View product details for purchase:', purchaseId);
    
    // You could implement a modal here or redirect to a details page
    // window.location.href = `/purchases/${purchaseId}`;ails page
    // window.location.href = `/purchases/${purchaseId}`;
}

// Load more comments for a purchase
function loadMoreComments(purchaseId) {
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;
    
    fetch(`/api/purchases/${purchaseId}/comments`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.comments) {
            const commentsSection = document.getElementById(`comments-${purchaseId}`);
            if (commentsSection) {
                // Clear existing comments
                const commentsContainer = commentsSection.querySelector('.space-y-2');
                if (commentsContainer) {
                    commentsContainer.innerHTML = '';
                    
                    // Add all comments
                    data.comments.forEach(comment => {
                        addCommentToSection(commentsSection, comment);
                    });
                }
                
                // Hide the load more button
                button.style.display = 'none';
            }
        } else {
            showNotification('Error loading comments', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error loading comments', 'error');
    })
    .finally(() => {
        button.textContent = originalText;
        button.disabled = false;
    });
}

// Update sharing status indicator
function updateSharingStatus(card, isShared) {
    const statusBadges = card.querySelectorAll('.bg-green-100, .bg-gray-100');
    statusBadges.forEach(badge => {
        if (isShared) {
            badge.className = 'bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full';
            badge.innerHTML = '<i class="fas fa-share-alt mr-1"></i>Shared';
        } else {
            badge.className = 'bg-gray-100 text-gray-800 text-xs font-medium px-2 py-1 rounded-full';
            badge.innerHTML = '<i class="fas fa-lock mr-1"></i>Private';
        }
    });
    
    // Update sharing toggle label
    const toggleLabel = card.querySelector('.toggle-switch + span');
    if (toggleLabel) {
        toggleLabel.textContent = isShared ? 'Shared' : 'Share';
    }
    
    // Update data attribute
    card.setAttribute('data-sharing', isShared ? 'shared' : 'private');
}

// Add comment to comments section
function addCommentToSection(commentsSection, comment) {
    const commentElement = document.createElement('div');
    commentElement.className = 'bg-gray-50 rounded-lg p-3';
    commentElement.innerHTML = `
        <div class="flex items-center mb-1">
            <img src="/static/images/profile/${comment.user.profile_image || 'default.jpg'}" 
                 alt="${comment.user.name}" 
                 class="w-6 h-6 rounded-full mr-2">
            <span class="font-semibold text-sm text-gray-800">${comment.user.name}</span>
            <span class="text-xs text-gray-500 ml-2">${formatDate(comment.created_at)}</span>
        </div>
        <p class="text-gray-700 text-sm">${comment.content}</p>
    `;
    
    const commentsContainer = commentsSection.querySelector('.space-y-2');
    if (commentsContainer) {
        commentsContainer.appendChild(commentElement);
    } else {
        // Create comments container if it doesn't exist
        const newContainer = document.createElement('div');
        newContainer.className = 'space-y-2';
        newContainer.appendChild(commentElement);
        commentsSection.appendChild(newContainer);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-green-100 border-green-500 text-green-700' :
                   type === 'error' ? 'bg-red-100 border-red-500 text-red-700' :
                   'bg-blue-100 border-blue-500 text-blue-700';
    
    notification.className = `fixed bottom-4 right-4 ${bgColor} border-l-4 p-4 rounded shadow-md fade-in z-50`;
    notification.innerHTML = `<p>${message}</p>`;
    
    document.body.appendChild(notification);
    
    setTimeout(function() {
        notification.style.opacity = '0';
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 3000);
}

// Format date helper
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
}