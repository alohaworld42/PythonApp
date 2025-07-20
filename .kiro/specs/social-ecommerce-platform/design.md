# Social E-commerce Platform Design Document

## Overview

BuyRoll is a social e-commerce platform that connects users' shopping experiences across different online stores and allows them to share selected purchases with friends. The platform integrates with e-commerce systems like Shopify and WooCommerce to automatically import purchase history based on email matching. Users can view their complete purchase history in a unified dashboard, choose which items to share socially, connect with friends, view friends' shared purchases, and analyze their own shopping patterns through intuitive visualizations.

This design document outlines the architecture, components, data models, and user interfaces required to implement the BuyRoll platform according to the requirements.

## Architecture

### System Architecture

The BuyRoll platform will follow a modern web application architecture with these key components:

1. **Frontend Layer**
   - Responsive web interface built with HTML5, CSS3 (Tailwind), JavaScript
   - Alpine.js for reactive UI components
   - Chart.js for analytics visualizations

2. **Backend Layer**
   - Flask web framework for server-side logic
   - RESTful API endpoints for frontend communication
   - Authentication and session management
   - Background tasks for e-commerce synchronization

3. **Data Layer**
   - SQLite database for development (can be migrated to PostgreSQL for production)
   - Efficient data models for users, products, purchases, and social connections
   - Caching layer for performance optimization

4. **Integration Layer**
   - Shopify API integration
   - WooCommerce API integration
   - OAuth for social login providers

### High-Level Architecture Diagram

```mermaid
graph TD
    A[User Browser] -->|HTTP/HTTPS| B[Flask Web Server]
    B -->|Query/Update| C[Database]
    B -->|API Calls| D[Shopify API]
    B -->|API Calls| E[WooCommerce API]
    B -->|OAuth| F[Social Login Providers]
    G[Background Jobs] -->|Sync Data| C
    G -->|API Calls| D
    G -->|API Calls| E
```

## Components and Interfaces

### Core Components

1. **Authentication System**
   - Registration and login forms
   - Social login integration (Google, Facebook, Amazon)
   - Session management
   - Password reset functionality

2. **E-commerce Integration Service**
   - API clients for Shopify and WooCommerce
   - Purchase data synchronization
   - Product metadata extraction
   - Error handling and retry logic

3. **Social Graph Manager**
   - Friend request handling
   - Connection management
   - Privacy controls
   - Friend search functionality

4. **Purchase Sharing System**
   - Sharing toggle controls
   - Privacy management
   - Activity feed generation
   - Notification system

5. **Analytics Engine**
   - Purchase data aggregation
   - Category classification
   - Time-series analysis
   - Visualization generation

6. **User Interface Components**
   - Responsive navigation system
   - Product card components
   - Social feed renderer
   - Dashboard layout manager
   - Chart and graph components

### Component Interactions

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant AuthService
    participant EcommerceService
    participant SocialService
    participant Database
    
    User->>UI: Register/Login
    UI->>AuthService: Authenticate
    AuthService->>Database: Store/Verify Credentials
    AuthService-->>UI: Auth Token
    
    UI->>EcommerceService: Request Purchase History
    EcommerceService->>Database: Check Last Sync
    EcommerceService->>Shopify/WooCommerce: API Request
    Shopify/WooCommerce-->>EcommerceService: Purchase Data
    EcommerceService->>Database: Store Purchases
    EcommerceService-->>UI: Updated Purchase List
    
    User->>UI: Toggle Share Item
    UI->>SocialService: Update Sharing Status
    SocialService->>Database: Update Item Privacy
    SocialService-->>UI: Confirmation
    
    User->>UI: View Friend Feed
    UI->>SocialService: Request Friend Activities
    SocialService->>Database: Query Shared Items
    SocialService-->>UI: Friend Activity Feed
```

## Data Models

### Core Data Models

1. **User Model**
```python
class User:
    id: Integer (Primary Key)
    email: String (Unique)
    password_hash: String
    name: String
    profile_image: String
    created_at: DateTime
    last_login: DateTime
    settings: JSON
```

2. **Connection Model**
```python
class Connection:
    id: Integer (Primary Key)
    user_id: Integer (Foreign Key -> User.id)
    friend_id: Integer (Foreign Key -> User.id)
    status: Enum ('pending', 'accepted', 'rejected', 'blocked')
    created_at: DateTime
    updated_at: DateTime
```

3. **Product Model**
```python
class Product:
    id: Integer (Primary Key)
    external_id: String
    source: String (e.g., 'shopify', 'woocommerce')
    title: String
    description: Text
    image_url: String
    price: Decimal
    currency: String
    category: String
    metadata: JSON
```

4. **Purchase Model**
```python
class Purchase:
    id: Integer (Primary Key)
    user_id: Integer (Foreign Key -> User.id)
    product_id: Integer (Foreign Key -> Product.id)
    purchase_date: DateTime
    store_name: String
    order_id: String
    is_shared: Boolean (default: False)
    share_comment: Text
    created_at: DateTime
    updated_at: DateTime
```

5. **Interaction Model**
```python
class Interaction:
    id: Integer (Primary Key)
    user_id: Integer (Foreign Key -> User.id)
    purchase_id: Integer (Foreign Key -> Purchase.id)
    type: Enum ('like', 'comment', 'save')
    content: Text
    created_at: DateTime
```

6. **Store Integration Model**
```python
class StoreIntegration:
    id: Integer (Primary Key)
    user_id: Integer (Foreign Key -> User.id)
    platform: String (e.g., 'shopify', 'woocommerce')
    store_url: String
    access_token: String (encrypted)
    metadata: JSON
    last_sync: DateTime
    created_at: DateTime
    updated_at: DateTime
```

### Database Schema Diagram

```mermaid
erDiagram
    USER {
        int id PK
        string email
        string password_hash
        string name
        string profile_image
        datetime created_at
        datetime last_login
        json settings
    }
    
    CONNECTION {
        int id PK
        int user_id FK
        int friend_id FK
        enum status
        datetime created_at
        datetime updated_at
    }
    
    PRODUCT {
        int id PK
        string external_id
        string source
        string title
        text description
        string image_url
        decimal price
        string currency
        string category
        json metadata
    }
    
    PURCHASE {
        int id PK
        int user_id FK
        int product_id FK
        datetime purchase_date
        string store_name
        string order_id
        boolean is_shared
        text share_comment
        datetime created_at
        datetime updated_at
    }
    
    INTERACTION {
        int id PK
        int user_id FK
        int purchase_id FK
        enum type
        text content
        datetime created_at
    }
    
    STORE_INTEGRATION {
        int id PK
        int user_id FK
        string platform
        string store_url
        string access_token
        json metadata
        datetime last_sync
        datetime created_at
        datetime updated_at
    }
    
    USER ||--o{ CONNECTION : has
    USER ||--o{ PURCHASE : makes
    USER ||--o{ INTERACTION : performs
    USER ||--o{ STORE_INTEGRATION : connects
    PRODUCT ||--o{ PURCHASE : included_in
    PURCHASE ||--o{ INTERACTION : receives
```

## User Interface Design

### Key Screens and Flows

1. **Authentication Flow**
   - Landing page with value proposition
   - Registration form
   - Login form
   - Social login options
   - Password reset flow

2. **Dashboard**
   - Header with navigation and user menu
   - Purchase history grid/list with sharing toggles
   - Filtering and sorting controls
   - Quick stats summary
   - Recent friend activity preview

3. **Friends Feed**
   - Chronological feed of friends' shared purchases
   - Interaction controls (like, comment, save)
   - Infinite scroll pagination
   - Filter by friend or category

4. **Friends Management**
   - Friend search
   - Friend requests (sent/received)
   - Current friends list
   - Friend removal option

5. **Analytics Dashboard**
   - Spending by category chart
   - Monthly spending trend
   - Top stores visualization
   - Time period selector
   - Detailed breakdown tables

6. **Settings**
   - Profile information management
   - Password change
   - Privacy settings
   - E-commerce account connections
   - Notification preferences

### UI Mockups

#### Navigation Structure

```mermaid
graph TD
    A[Landing Page] --> B[Login]
    A --> C[Register]
    B --> D[Dashboard]
    C --> D
    D --> E[Friends Feed]
    D --> F[Friends Management]
    D --> G[Analytics]
    D --> H[Settings]
    E --> I[Product Detail]
    F --> J[Friend Profile]
```

#### Dashboard Layout

```mermaid
graph TD
    A[Dashboard] --> B[Header Navigation]
    A --> C[Quick Stats Panel]
    A --> D[Filter Controls]
    A --> E[Purchase Grid]
    E --> F[Product Card]
    F --> G[Sharing Toggle]
    F --> H[Product Details]
    A --> I[Recent Friend Activity]
```

#### Mobile Navigation Flow

```mermaid
graph TD
    A[Bottom Nav Bar] --> B[Home/Dashboard]
    A --> C[Friends Feed]
    A --> D[Add/Search]
    A --> E[Analytics]
    A --> F[Profile/Settings]
```

## Design System

### Color Palette

- **Primary Colors**
  - Green-900: #55970f (Dark green for primary actions)
  - Green-800: #6abe11 (Light green for gradients and accents)
  - White: #FFFFFF (Background and text on dark surfaces)
  - Black: #000000 (Text and dark surfaces)

- **Secondary Colors**
  - Green-300: #A3E635 (Light green for backgrounds and accents)
  - Green-750: #8DC63F (Medium green for borders and secondary elements)
  - Yellow-500: #EAB308 (For ratings and highlights)
  - Gray-400: #9CA3AF (For secondary text and disabled states)
  - Gray-500: #6B7280 (For tertiary text and subtle elements)

- **Functional Colors**
  - Success: #10B981 (Green for success states)
  - Error: #EF4444 (Red for error states)
  - Warning: #F59E0B (Amber for warning states)
  - Info: #3B82F6 (Blue for information states)

### Typography

- **Font Families**
  - Primary: System font stack for optimal performance
  - Headings: Same as primary for consistency

- **Font Sizes**
  - Base: 16px (1rem)
  - Scale: 1.25 ratio for a harmonious type scale
  - Responsive adjustments at breakpoints

- **Font Weights**
  - Regular: 400
  - Medium: 500
  - Semibold: 600
  - Bold: 700
  - Black: 900 (for specific emphasis)

### Component Design

1. **Product Card**
   - Consistent sizing and padding
   - Product image with aspect ratio constraint
   - Clear typography hierarchy
   - Price and store prominently displayed
   - Sharing toggle with clear states
   - Hover and focus states

2. **Navigation**
   - Desktop: Horizontal navigation with dropdowns
   - Mobile: Bottom navigation bar with icons and labels
   - Active state indicators
   - Consistent spacing and alignment

3. **Buttons**
   - Primary: Green gradient with white text
   - Secondary: White with green border
   - Tertiary: Text-only with hover state
   - Icon buttons with tooltips
   - Consistent padding and border radius

4. **Forms**
   - Floating labels for better UX
   - Clear validation states
   - Consistent input styling
   - Helpful error messages
   - Logical tab order

5. **Charts and Visualizations**
   - Consistent color coding
   - Clear legends and labels
   - Interactive tooltips
   - Responsive sizing
   - Accessible alternatives for screen readers

## API Design

### Authentication Endpoints

```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/social-login
POST /api/auth/logout
POST /api/auth/reset-password
```

### User and Friends Endpoints

```
GET /api/user/profile
PUT /api/user/profile
GET /api/user/friends
POST /api/user/friends/request
PUT /api/user/friends/{id}/accept
PUT /api/user/friends/{id}/reject
DELETE /api/user/friends/{id}
GET /api/user/friends/suggestions
```

### Purchase and Sharing Endpoints

```
GET /api/purchases
GET /api/purchases/{id}
PUT /api/purchases/{id}/share
PUT /api/purchases/{id}/unshare
POST /api/purchases/{id}/comment
GET /api/feed
POST /api/feed/item/{id}/like
POST /api/feed/item/{id}/comment
POST /api/feed/item/{id}/save
```

### E-commerce Integration Endpoints

```
GET /api/integrations
POST /api/integrations/connect
DELETE /api/integrations/{id}
POST /api/integrations/{id}/sync
GET /api/integrations/{id}/status
```

### Analytics Endpoints

```
GET /api/analytics/spending
GET /api/analytics/categories
GET /api/analytics/stores
GET /api/analytics/trends
```

## Integration Strategy

### Shopify Integration

1. **Authentication**
   - OAuth flow for store connection
   - API key and secret storage
   - Token refresh mechanism

2. **Data Synchronization**
   - Orders API for purchase history
   - Products API for product details
   - Customers API for email matching
   - Webhooks for real-time updates

3. **Error Handling**
   - Rate limit management
   - Retry mechanism for failed requests
   - Fallback to scheduled polling

### WooCommerce Integration

1. **Authentication**
   - REST API keys
   - Secure storage of credentials

2. **Data Synchronization**
   - Orders endpoint for purchase history
   - Products endpoint for product details
   - Customers endpoint for email matching
   - Scheduled polling for updates

3. **Error Handling**
   - Connection timeout handling
   - Partial data processing
   - Sync status tracking

## Security Considerations

1. **Authentication Security**
   - Password hashing with bcrypt
   - CSRF protection
   - Rate limiting for login attempts
   - Secure session management

2. **Data Protection**
   - Encryption for sensitive data
   - API key rotation
   - HTTPS for all communications
   - Input validation and sanitization

3. **Privacy Controls**
   - Granular sharing permissions
   - Clear privacy indicators
   - Data retention policies
   - User data export and deletion options

## Performance Optimization

1. **Frontend Performance**
   - Lazy loading of images and components
   - Code splitting for JavaScript
   - Critical CSS inlining
   - Asset minification and compression

2. **Backend Performance**
   - Database query optimization
   - Caching of frequent queries
   - Background processing for heavy tasks
   - Connection pooling

3. **API Performance**
   - Response pagination
   - Partial resource updates
   - Efficient data serialization
   - Rate limiting for API consumers

## Testing Strategy

1. **Unit Testing**
   - Test individual components and functions
   - Mock external dependencies
   - Cover edge cases and error conditions

2. **Integration Testing**
   - Test component interactions
   - Verify database operations
   - Test API endpoints

3. **UI Testing**
   - Test user flows
   - Verify responsive behavior
   - Accessibility testing

4. **Performance Testing**
   - Load testing for concurrent users
   - Response time benchmarking
   - Memory usage monitoring

## Deployment Considerations

1. **Environment Setup**
   - Development, staging, and production environments
   - Configuration management
   - Environment-specific settings

2. **Database Migration**
   - Schema version control
   - Data migration scripts
   - Rollback procedures

3. **Monitoring and Logging**
   - Application performance monitoring
   - Error tracking and alerting
   - User activity logging
   - Security event monitoring

## Future Considerations

1. **Feature Expansion**
   - Additional e-commerce platform integrations
   - Mobile app development
   - Advanced recommendation engine
   - Influencer features

2. **Technical Improvements**
   - Migration to PostgreSQL for scalability
   - Microservices architecture for specific components
   - Real-time notifications with WebSockets
   - Content delivery network integration

3. **Business Development**
   - Affiliate marketing integration
   - Premium features for subscription model
   - Business analytics for brands
   - Social commerce direct purchasing