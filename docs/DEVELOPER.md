# BuyRoll Developer Documentation

## Overview

This documentation is for developers who want to contribute to BuyRoll, extend its functionality, or integrate with its APIs. BuyRoll is built with Flask, SQLAlchemy, and modern web technologies.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Environment](#development-environment)
3. [Code Structure](#code-structure)
4. [Database Design](#database-design)
5. [API Development](#api-development)
6. [Frontend Development](#frontend-development)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Contributing](#contributing)

## Architecture Overview

### Technology Stack

**Backend:**
- **Framework**: Flask 2.3+
- **Database**: SQLAlchemy with SQLite (dev) / PostgreSQL (prod)
- **Authentication**: Flask-Login with session management
- **Password Hashing**: Flask-Bcrypt
- **Email**: Flask-Mail
- **Migrations**: Flask-Migrate
- **CORS**: Flask-CORS
- **Scheduling**: APScheduler (for background tasks)

**Frontend:**
- **Templates**: Jinja2
- **CSS Framework**: Tailwind CSS
- **JavaScript**: Vanilla JS with Alpine.js for reactivity
- **Charts**: Chart.js for analytics visualizations
- **Icons**: Heroicons

**Infrastructure:**
- **Web Server**: Nginx (production)
- **Process Manager**: systemd
- **Cache**: Redis (optional)
- **Monitoring**: Custom health checks and metrics

### Application Structure

```
buyroll/
├── app/                    # Main application package
│   ├── models/            # Database models
│   ├── routes/            # Route handlers (blueprints)
│   ├── services/          # Business logic services
│   ├── utils/             # Utility functions
│   ├── templates/         # Jinja2 templates
│   ├── static/            # Static assets (CSS, JS, images)
│   └── __init__.py        # App factory
├── migrations/            # Database migration scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
├── config.py              # Configuration classes
├── app.py                 # Application entry point
└── requirements.txt       # Python dependencies
```

## Development Environment

### Prerequisites

- Python 3.9+
- Node.js 16+ (for frontend tooling)
- Git
- Code editor (VS Code recommended)

### Setup

1. **Clone and Setup**:
```bash
git clone https://github.com/yourusername/buyroll.git
cd buyroll
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Database Setup**:
```bash
python migrations/migrate.py migrate
python migrations/migrate.py seed  # Optional test data
```

4. **Run Development Server**:
```bash
python app.py
# Or use Flask CLI
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### Development Tools

#### Code Quality
```bash
# Install development dependencies
pip install black flake8 isort pytest pytest-cov

# Format code
black app/ tests/

# Check code style
flake8 app/ tests/

# Sort imports
isort app/ tests/
```

#### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Code Structure

### Application Factory Pattern

The app uses the factory pattern for better testability and configuration management:

```python
# app/__init__.py
def create_app(config_class=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        app.config.from_object('config.DevelopmentConfig')
    else:
        app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    # ... other extensions
    
    # Register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    
    return app
```

### Blueprint Structure

Routes are organized into blueprints by functionality:

```python
# app/routes/user.py
from flask import Blueprint

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')
```

### Service Layer

Business logic is separated into service classes:

```python
# app/services/purchase_service.py
class PurchaseService:
    @staticmethod
    def share_purchase(purchase_id, user_id, comment=None):
        purchase = Purchase.query.get_or_404(purchase_id)
        
        # Validate ownership
        if purchase.user_id != user_id:
            raise PermissionError("Cannot share another user's purchase")
        
        # Update sharing status
        purchase.is_shared = True
        purchase.share_comment = comment
        db.session.commit()
        
        return purchase
```

### Model Design

Models use SQLAlchemy with proper relationships:

```python
# app/models/user.py
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Relationships
    purchases = db.relationship('Purchase', backref='user', lazy=True)
    sent_connections = db.relationship('Connection', 
                                     foreign_keys='Connection.user_id',
                                     backref='sender', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
```

## Database Design

### Core Models

#### User Model
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))
    profile_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
```

#### Purchase Model
```python
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False)
    store_name = db.Column(db.String(100))
    order_id = db.Column(db.String(100))
    is_shared = db.Column(db.Boolean, default=False)
    share_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Migrations

Use Flask-Migrate for database schema changes:

```bash
# Create migration
flask db migrate -m "Add user profile image"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### Database Utilities

Custom migration utilities in `migrations/migrate.py`:

```python
# Create backup before migration
python migrations/migrate.py backup

# Run health check
python migrations/migrate.py health

# Seed test data
python migrations/migrate.py seed
```

## API Development

### API Structure

APIs are organized by functionality with consistent response formats:

```python
# app/routes/api_user.py
@api_user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    try:
        user_data = {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'profile_image': current_user.profile_image
        }
        
        return jsonify({
            'success': True,
            'data': {'user': user_data}
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
```

### Error Handling

Consistent error handling across all APIs:

```python
# app/utils/api_helpers.py
def api_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': e.messages
            }), 422
        except PermissionError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 403
        except Exception as e:
            current_app.logger.error(f"API error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    return wrapper
```

### Authentication

API endpoints use session-based authentication:

```python
from flask_login import login_required, current_user

@api_bp.route('/protected-endpoint')
@login_required
def protected_endpoint():
    # current_user is available here
    pass
```

### Pagination

Consistent pagination for list endpoints:

```python
def paginate_query(query, page=1, per_page=20):
    """Paginate a SQLAlchemy query"""
    paginated = query.paginate(
        page=page,
        per_page=min(per_page, 100),  # Max 100 items per page
        error_out=False
    )
    
    return {
        'items': [item.to_dict() for item in paginated.items],
        'pagination': {
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
    }
```

## Frontend Development

### Template Structure

Templates use Jinja2 with a base layout:

```html
<!-- app/templates/layout.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}BuyRoll{% endblock %}</title>
    <link href="{{ url_for('static', filename='css/main.css') }}" rel="stylesheet">
</head>
<body>
    <nav>
        <!-- Navigation -->
    </nav>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

### CSS Architecture

Using Tailwind CSS with custom components:

```css
/* app/static/css/main.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom components */
.btn-primary {
    @apply bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors;
}

.card {
    @apply bg-white rounded-lg shadow-md p-6;
}
```

### JavaScript Architecture

Modular JavaScript with Alpine.js for reactivity:

```javascript
// app/static/js/main.js
document.addEventListener('alpine:init', () => {
    Alpine.data('purchaseCard', () => ({
        isShared: false,
        isLoading: false,
        
        async toggleShare() {
            this.isLoading = true;
            
            try {
                const response = await fetch(`/api/purchases/${this.purchaseId}/share`, {
                    method: this.isShared ? 'DELETE' : 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (response.ok) {
                    this.isShared = !this.isShared;
                }
            } catch (error) {
                console.error('Error toggling share:', error);
            } finally {
                this.isLoading = false;
            }
        }
    }));
});
```

### Component Development

Reusable template components:

```html
<!-- app/templates/components/purchase_card.html -->
<div class="card" x-data="purchaseCard" x-init="purchaseId = {{ purchase.id }}; isShared = {{ purchase.is_shared|tojson }}">
    <div class="flex justify-between items-start">
        <div class="flex-1">
            <h3 class="text-lg font-semibold">{{ purchase.product.title }}</h3>
            <p class="text-gray-600">${{ purchase.product.price }}</p>
        </div>
        
        <button @click="toggleShare()" 
                :disabled="isLoading"
                class="btn-primary">
            <span x-show="!isLoading">
                <span x-show="isShared">Unshare</span>
                <span x-show="!isShared">Share</span>
            </span>
            <span x-show="isLoading">Loading...</span>
        </button>
    </div>
</div>
```

## Testing

### Test Structure

Tests are organized by functionality:

```
tests/
├── conftest.py           # Test configuration and fixtures
├── test_models.py        # Model tests
├── test_auth.py          # Authentication tests
├── test_api_endpoints.py # API endpoint tests
├── test_integration.py   # Integration tests
└── test_utilities.py     # Utility function tests
```

### Test Configuration

```python
# tests/conftest.py
import pytest
from app import create_app, db
from app.models import User, Product, Purchase

@pytest.fixture
def app():
    app = create_app('config.TestingConfig')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_user(app):
    user = User(name='Test User', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user
```

### Unit Tests

```python
# tests/test_models.py
def test_user_password_hashing():
    user = User(name='Test', email='test@example.com')
    user.set_password('password123')
    
    assert user.password_hash is not None
    assert user.check_password('password123') is True
    assert user.check_password('wrongpassword') is False

def test_purchase_sharing():
    user = User(name='Test', email='test@example.com')
    product = Product(title='Test Product', price=99.99)
    purchase = Purchase(user=user, product=product)
    
    assert purchase.is_shared is False
    
    purchase.is_shared = True
    assert purchase.is_shared is True
```

### API Tests

```python
# tests/test_api_endpoints.py
def test_get_profile_authenticated(client, auth_user):
    # Login
    client.post('/auth/login', data={
        'email': auth_user.email,
        'password': 'password123'
    })
    
    # Test API endpoint
    response = client.get('/api/user/profile')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['user']['email'] == auth_user.email

def test_get_profile_unauthenticated(client):
    response = client.get('/api/user/profile')
    assert response.status_code == 401
```

### Integration Tests

```python
# tests/test_integration.py
def test_purchase_sharing_flow(client, auth_user):
    # Login
    client.post('/auth/login', data={
        'email': auth_user.email,
        'password': 'password123'
    })
    
    # Create purchase
    product = Product(title='Test Product', price=99.99)
    purchase = Purchase(user=auth_user, product=product)
    db.session.add_all([product, purchase])
    db.session.commit()
    
    # Share purchase
    response = client.post(f'/api/purchases/{purchase.id}/share')
    assert response.status_code == 200
    
    # Verify sharing
    updated_purchase = Purchase.query.get(purchase.id)
    assert updated_purchase.is_shared is True
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_user"
```

## Deployment

### Environment Configuration

Different configurations for different environments:

```python
# config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # ... common settings

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    # Production-specific settings
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Deployment Script

Use the provided deployment script:

```bash
# Deploy to production
./deploy.sh deploy

# Rollback if needed
./deploy.sh rollback

# Check health
./deploy.sh health
```

### Monitoring

Health checks and metrics are available:

```python
# app/utils/monitoring.py
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': check_database_health(),
        'timestamp': datetime.utcnow().isoformat()
    })
```

## Contributing

### Development Workflow

1. **Fork and Clone**:
```bash
git clone https://github.com/yourusername/buyroll.git
cd buyroll
git remote add upstream https://github.com/original/buyroll.git
```

2. **Create Feature Branch**:
```bash
git checkout -b feature/your-feature-name
```

3. **Make Changes**:
- Write code following the style guide
- Add tests for new functionality
- Update documentation if needed

4. **Test Changes**:
```bash
pytest
black app/ tests/
flake8 app/ tests/
```

5. **Commit and Push**:
```bash
git add .
git commit -m "Add feature: your feature description"
git push origin feature/your-feature-name
```

6. **Create Pull Request**:
- Open PR against main branch
- Describe changes and testing done
- Wait for review and approval

### Code Style

#### Python Style
- Follow PEP 8
- Use Black for formatting
- Use type hints where appropriate
- Write docstrings for functions and classes

```python
def calculate_spending_by_category(user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, float]:
    """
    Calculate user spending by category for a date range.
    
    Args:
        user_id: The user's ID
        start_date: Start of date range
        end_date: End of date range
    
    Returns:
        Dictionary mapping category names to spending amounts
    """
    # Implementation here
    pass
```

#### JavaScript Style
- Use modern ES6+ features
- Follow consistent naming conventions
- Add comments for complex logic
- Use Alpine.js for reactivity

#### HTML/CSS Style
- Use semantic HTML
- Follow Tailwind CSS conventions
- Ensure accessibility compliance
- Test responsive design

### Pull Request Guidelines

#### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

#### Review Process
1. Automated checks must pass
2. At least one code review required
3. All conversations must be resolved
4. Tests must pass
5. Documentation must be updated

### Issue Reporting

#### Bug Reports
Include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots if applicable
- Error messages/logs

#### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Additional context

### Development Best Practices

#### Security
- Never commit secrets or credentials
- Validate all user input
- Use parameterized queries
- Implement proper authentication/authorization
- Follow OWASP guidelines

#### Performance
- Optimize database queries
- Use pagination for large datasets
- Implement caching where appropriate
- Monitor application performance
- Profile slow operations

#### Maintainability
- Write clear, self-documenting code
- Add comprehensive tests
- Keep functions small and focused
- Use consistent naming conventions
- Document complex business logic

## Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Alpine.js Documentation](https://alpinejs.dev/)

### Tools
- [VS Code](https://code.visualstudio.com/) - Recommended editor
- [Postman](https://www.postman.com/) - API testing
- [DB Browser for SQLite](https://sqlitebrowser.org/) - Database inspection
- [Git](https://git-scm.com/) - Version control

### Community
- [GitHub Issues](https://github.com/yourusername/buyroll/issues)
- [Discussions](https://github.com/yourusername/buyroll/discussions)
- [Discord Server](https://discord.gg/buyroll) (if available)

---

For questions or support, contact the development team at dev@buyroll.com