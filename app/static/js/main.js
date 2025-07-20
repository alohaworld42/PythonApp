// BuyRoll main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
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
    
    // Like functionality with AJAX
    const likeButtons = document.querySelectorAll('.like-button');
    likeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const purchaseId = this.dataset.purchaseId;
            const likeCountElement = document.querySelector(`.like-count[data-purchase-id="${purchaseId}"]`);
            
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
                        this.innerHTML = '<i class="fas fa-heart mr-1"></i> Unlike';
                        this.classList.add('text-green-800');
                        this.classList.remove('text-gray-500');
                        
                        // Increment like count
                        if (likeCountElement) {
                            const currentCount = parseInt(likeCountElement.textContent);
                            likeCountElement.textContent = currentCount + 1;
                        }
                    } else {
                        this.innerHTML = '<i class="far fa-heart mr-1"></i> Like';
                        this.classList.remove('text-green-800');
                        this.classList.add('text-gray-500');
                        
                        // Decrement like count
                        if (likeCountElement) {
                            const currentCount = parseInt(likeCountElement.textContent);
                            likeCountElement.textContent = currentCount - 1;
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
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