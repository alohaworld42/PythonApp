#!/bin/bash

# BuyRoll Deployment Script
# This script automates the deployment process for the BuyRoll application

set -e  # Exit on any error

# Configuration
APP_NAME="buyroll"
APP_DIR="/var/www/$APP_NAME"
BACKUP_DIR="/var/backups/$APP_NAME"
LOG_FILE="/var/log/$APP_NAME/deploy.log"
PYTHON_VERSION="3.9"
VENV_NAME="venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 is not installed"
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        error "git is not installed"
    fi
    
    log "✓ System requirements check passed"
}

# Create necessary directories
setup_directories() {
    log "Setting up directories..."
    
    sudo mkdir -p "$APP_DIR"
    sudo mkdir -p "$BACKUP_DIR"
    sudo mkdir -p "/var/log/$APP_NAME"
    sudo mkdir -p "/etc/$APP_NAME"
    
    # Set proper ownership
    sudo chown -R $USER:$USER "$APP_DIR"
    sudo chown -R $USER:$USER "/var/log/$APP_NAME"
    
    log "✓ Directories created"
}

# Backup current deployment
backup_current() {
    if [ -d "$APP_DIR" ] && [ "$(ls -A $APP_DIR)" ]; then
        log "Creating backup of current deployment..."
        
        BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
        sudo cp -r "$APP_DIR" "$BACKUP_DIR/$BACKUP_NAME"
        
        log "✓ Backup created: $BACKUP_DIR/$BACKUP_NAME"
    else
        log "No existing deployment to backup"
    fi
}

# Deploy application
deploy_app() {
    log "Deploying application..."
    
    # Navigate to app directory
    cd "$APP_DIR"
    
    # Pull latest code (assuming git repository)
    if [ -d ".git" ]; then
        log "Updating from git repository..."
        git pull origin main
    else
        log "Initializing git repository..."
        git init
        git remote add origin https://github.com/yourusername/buyroll.git
        git pull origin main
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_NAME" ]; then
        log "Creating virtual environment..."
        python3 -m venv "$VENV_NAME"
    fi
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    log "Installing dependencies..."
    pip install -r requirements.txt
    
    log "✓ Application deployed"
}

# Setup environment configuration
setup_environment() {
    log "Setting up environment configuration..."
    
    # Copy production environment file if it doesn't exist
    if [ ! -f "$APP_DIR/.env" ]; then
        if [ -f "$APP_DIR/.env.production" ]; then
            cp "$APP_DIR/.env.production" "$APP_DIR/.env"
            log "✓ Production environment file copied"
        else
            warning "No .env.production file found. Please create .env manually"
        fi
    else
        log "Environment file already exists"
    fi
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd "$APP_DIR"
    source "$VENV_NAME/bin/activate"
    
    # Backup database before migration
    python migrations/migrate.py backup
    
    # Run migrations
    python migrations/migrate.py migrate
    
    log "✓ Database migrations completed"
}

# Setup systemd service
setup_service() {
    log "Setting up systemd service..."
    
    # Create systemd service file
    sudo tee "/etc/systemd/system/$APP_NAME.service" > /dev/null <<EOF
[Unit]
Description=BuyRoll Social E-commerce Platform
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/$VENV_NAME/bin
ExecStart=$APP_DIR/$VENV_NAME/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable "$APP_NAME"
    
    log "✓ Systemd service configured"
}

# Setup nginx configuration
setup_nginx() {
    log "Setting up nginx configuration..."
    
    # Create nginx configuration
    sudo tee "/etc/nginx/sites-available/$APP_NAME" > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias $APP_DIR/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # Enable site
    sudo ln -sf "/etc/nginx/sites-available/$APP_NAME" "/etc/nginx/sites-enabled/"
    
    # Test nginx configuration
    sudo nginx -t
    
    log "✓ Nginx configuration created"
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start application service
    sudo systemctl start "$APP_NAME"
    sudo systemctl status "$APP_NAME" --no-pager
    
    # Reload nginx
    sudo systemctl reload nginx
    
    log "✓ Services started"
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Wait a moment for services to start
    sleep 5
    
    # Check if application is responding
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        log "✓ Application health check passed"
    else
        warning "Application health check failed"
    fi
    
    # Check database health
    cd "$APP_DIR"
    source "$VENV_NAME/bin/activate"
    python migrations/migrate.py health
}

# Rollback function
rollback() {
    log "Rolling back deployment..."
    
    # Stop services
    sudo systemctl stop "$APP_NAME"
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR" | head -n1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restoring from backup: $LATEST_BACKUP"
        sudo rm -rf "$APP_DIR"
        sudo cp -r "$BACKUP_DIR/$LATEST_BACKUP" "$APP_DIR"
        sudo chown -R $USER:$USER "$APP_DIR"
        
        # Start services
        sudo systemctl start "$APP_NAME"
        
        log "✓ Rollback completed"
    else
        error "No backup found for rollback"
    fi
}

# Main deployment function
deploy() {
    log "Starting deployment of $APP_NAME..."
    
    check_root
    check_requirements
    setup_directories
    backup_current
    deploy_app
    setup_environment
    run_migrations
    setup_service
    setup_nginx
    start_services
    health_check
    
    log "✓ Deployment completed successfully!"
    log "Application is now running at http://your-domain.com"
}

# Script usage
usage() {
    echo "Usage: $0 {deploy|rollback|health|backup}"
    echo "  deploy   - Deploy the application"
    echo "  rollback - Rollback to previous version"
    echo "  health   - Check application health"
    echo "  backup   - Create backup of current deployment"
}

# Main script logic
case "${1:-}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    health)
        health_check
        ;;
    backup)
        backup_current
        ;;
    *)
        usage
        exit 1
        ;;
esac