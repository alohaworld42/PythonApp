# BuyRoll Installation Guide

## Overview

This guide will help you set up the BuyRoll social e-commerce platform on your local development environment or production server.

## System Requirements

### Minimum Requirements

- **Python**: 3.9 or higher
- **Database**: SQLite (development) or PostgreSQL (production)
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 10GB free space minimum
- **Operating System**: Linux, macOS, or Windows

### Recommended Production Requirements

- **Python**: 3.9+
- **Database**: PostgreSQL 12+
- **Memory**: 8GB RAM
- **Storage**: 50GB SSD
- **Web Server**: Nginx
- **Process Manager**: systemd or supervisor
- **Cache**: Redis (optional but recommended)

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/buyroll.git
cd buyroll
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit the .env file with your configuration
nano .env
```

**Required Environment Variables:**

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_APP=app.py

# Database
DATABASE_URL=sqlite:///buyroll.db

# Mail Configuration (for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@buyroll.com

# Social Login (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret

# E-commerce Integration (optional)
SHOPIFY_API_KEY=your-shopify-api-key
SHOPIFY_API_SECRET=your-shopify-api-secret
```

### 5. Initialize Database

```bash
# Run database migrations
python migrations/migrate.py migrate

# Optional: Seed with sample data
python migrations/migrate.py seed
```

### 6. Run the Application

```bash
# Start development server
python app.py

# Or use Flask's built-in server
flask run
```

The application will be available at `http://localhost:5000`

### 7. Verify Installation

1. Open your browser and navigate to `http://localhost:5000`
2. Register a new account
3. Check that the health endpoint works: `http://localhost:5000/health`

## Production Deployment

### Option 1: Traditional Server Deployment

#### 1. Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Create application user
sudo useradd -m -s /bin/bash buyroll
sudo usermod -aG sudo buyroll
```

#### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE buyroll;
CREATE USER buyroll WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE buyroll TO buyroll;
\q
```

#### 3. Application Deployment

```bash
# Switch to application user
sudo su - buyroll

# Clone repository
git clone https://github.com/yourusername/buyroll.git
cd buyroll

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.production .env
nano .env  # Edit with your production settings

# Run migrations
python migrations/migrate.py migrate
```

#### 4. Configure Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/buyroll.service
```

Add the following content:

```ini
[Unit]
Description=BuyRoll Social E-commerce Platform
After=network.target

[Service]
Type=simple
User=buyroll
WorkingDirectory=/home/buyroll/buyroll
Environment=PATH=/home/buyroll/buyroll/venv/bin
ExecStart=/home/buyroll/buyroll/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable buyroll
sudo systemctl start buyroll
sudo systemctl status buyroll
```

#### 5. Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/buyroll
```

Add the configuration from `nginx.conf` file, then:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/buyroll /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. SSL Certificate (Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Option 2: Docker Deployment

#### 1. Install Docker and Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Configure Environment

```bash
# Copy production environment
cp .env.production .env

# Edit environment variables for Docker
nano .env
```

Update database URL for Docker:
```bash
DATABASE_URL=postgresql://buyroll:password@db:5432/buyroll
```

#### 3. Deploy with Docker Compose

```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f web
```

#### 4. Initialize Database

```bash
# Run migrations
docker-compose exec web python migrations/migrate.py migrate

# Optional: Seed data
docker-compose exec web python migrations/migrate.py seed
```

### Option 3: Automated Deployment Script

Use the provided deployment script:

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh deploy
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key | - | Yes |
| `FLASK_ENV` | Environment mode | development | No |
| `DATABASE_URL` | Database connection string | sqlite:///buyroll.db | No |
| `MAIL_SERVER` | SMTP server | smtp.gmail.com | No |
| `MAIL_USERNAME` | SMTP username | - | No |
| `MAIL_PASSWORD` | SMTP password | - | No |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | - | No |
| `SHOPIFY_API_KEY` | Shopify API key | - | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `CACHE_TYPE` | Cache backend type | simple | No |

### Database Configuration

#### SQLite (Development)
```bash
DATABASE_URL=sqlite:///buyroll.db
```

#### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql://username:password@localhost/buyroll
```

### Mail Configuration

#### Gmail
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

#### SendGrid
```bash
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error:** `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file`

**Solution:**
```bash
# Check file permissions
ls -la buyroll.db

# Fix permissions
chmod 664 buyroll.db
chown buyroll:buyroll buyroll.db
```

#### 2. Import Error

**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Ensure you're in the correct directory
pwd  # Should show /path/to/buyroll

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. Port Already in Use

**Error:** `OSError: [Errno 98] Address already in use`

**Solution:**
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>

# Or use a different port
export FLASK_RUN_PORT=5001
flask run
```

#### 4. Permission Denied

**Error:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# Fix directory permissions
sudo chown -R buyroll:buyroll /path/to/buyroll
chmod -R 755 /path/to/buyroll

# Fix log directory permissions
sudo mkdir -p /var/log/buyroll
sudo chown buyroll:buyroll /var/log/buyroll
```

### Health Checks

#### Application Health
```bash
curl http://localhost:5000/health
```

#### Database Health
```bash
python migrations/migrate.py health
```

#### Service Status
```bash
sudo systemctl status buyroll
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Log Files

#### Application Logs
```bash
# Development
tail -f logs/app.log

# Production
tail -f /var/log/buyroll/app.log
```

#### System Logs
```bash
# Application service
sudo journalctl -u buyroll -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Maintenance

### Backup

#### Database Backup
```bash
# Create backup
python migrations/migrate.py backup

# Restore from backup
python migrations/migrate.py restore /path/to/backup.db
```

#### Full Application Backup
```bash
# Using deployment script
./deploy.sh backup

# Manual backup
tar -czf buyroll-backup-$(date +%Y%m%d).tar.gz \
  /home/buyroll/buyroll \
  /var/log/buyroll \
  /etc/nginx/sites-available/buyroll
```

### Updates

#### Application Updates
```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run migrations
python migrations/migrate.py migrate

# Restart service
sudo systemctl restart buyroll
```

#### System Updates
```bash
# Update packages
sudo apt update && sudo apt upgrade

# Restart services if needed
sudo systemctl restart nginx
sudo systemctl restart postgresql
```

### Monitoring

#### Performance Monitoring
```bash
# Check system resources
htop

# Check disk usage
df -h

# Check memory usage
free -h

# Check application metrics
curl http://localhost:5000/metrics
```

#### Log Monitoring
```bash
# Monitor application logs
tail -f /var/log/buyroll/app.log | grep ERROR

# Monitor access logs
tail -f /var/log/nginx/access.log
```

## Security Considerations

### SSL/TLS
- Always use HTTPS in production
- Use strong SSL certificates
- Configure proper SSL settings in Nginx

### Database Security
- Use strong database passwords
- Restrict database access to application server only
- Regular security updates

### Application Security
- Keep dependencies updated
- Use strong secret keys
- Implement proper input validation
- Regular security audits

### Server Security
- Keep system updated
- Use firewall (ufw/iptables)
- Disable unnecessary services
- Regular security monitoring

## Support

For additional help:

1. Check the [API Documentation](API.md)
2. Review the [User Guide](USER_GUIDE.md)
3. Check [GitHub Issues](https://github.com/yourusername/buyroll/issues)
4. Contact support: support@buyroll.com