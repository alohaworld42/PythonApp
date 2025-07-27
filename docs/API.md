# BuyRoll API Documentation

## Overview

The BuyRoll API provides endpoints for managing users, purchases, social connections, and analytics in the social e-commerce platform. All API endpoints return JSON responses and use standard HTTP status codes.

## Base URL

```
Development: http://localhost:5000/api
Production: https://your-domain.com/api
```

## Authentication

Most API endpoints require authentication. The API uses session-based authentication with cookies.

### Login Required

Endpoints marked with 🔒 require user authentication. If not authenticated, you'll receive a 401 Unauthorized response.

## Rate Limiting

- API endpoints: 100 requests per hour per IP
- Login endpoints: 5 requests per minute per IP

## Response Format

All responses follow this format:

```json
{
  "success": true,
  "data": {...},
  "message": "Optional message",
  "errors": []
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "errors": ["Detailed error messages"]
}
```

## Authentication Endpoints

### POST /api/auth/register

Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "created_at": "2024-01-01T00:00:00Z"
    }
  },
  "message": "Registration successful"
}
```

### POST /api/auth/login

Authenticate user and create session.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123",
  "remember": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    }
  },
  "message": "Login successful"
}
```

### POST /api/auth/logout 🔒

End user session.

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

### POST /api/auth/reset-password

Request password reset email.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

## User Management Endpoints

### GET /api/user/profile 🔒

Get current user profile.

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "profile_image": "/static/uploads/profile_1.jpg",
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-02T10:30:00Z"
    }
  }
}
```

### PUT /api/user/profile 🔒

Update user profile.

**Request Body:**
```json
{
  "name": "John Smith",
  "profile_image": "base64_encoded_image_data"
}
```

## Friends Management Endpoints

### GET /api/user/friends 🔒

Get user's friends list.

**Query Parameters:**
- `status` (optional): Filter by connection status (`accepted`, `pending`, `sent`)

**Response:**
```json
{
  "success": true,
  "data": {
    "friends": [
      {
        "id": 2,
        "name": "Jane Doe",
        "email": "jane@example.com",
        "profile_image": "/static/uploads/profile_2.jpg",
        "connection_status": "accepted",
        "connected_at": "2024-01-01T12:00:00Z"
      }
    ],
    "total": 1
  }
}
```

### POST /api/user/friends/request 🔒

Send friend request.

**Request Body:**
```json
{
  "email": "friend@example.com"
}
```

### PUT /api/user/friends/{friend_id}/accept 🔒

Accept friend request.

**Response:**
```json
{
  "success": true,
  "message": "Friend request accepted"
}
```

### PUT /api/user/friends/{friend_id}/reject 🔒

Reject friend request.

### DELETE /api/user/friends/{friend_id} 🔒

Remove friend connection.

### GET /api/user/friends/suggestions 🔒

Get friend suggestions based on email contacts or mutual friends.

## Purchase Management Endpoints

### GET /api/purchases 🔒

Get user's purchase history.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)
- `store` (optional): Filter by store name
- `category` (optional): Filter by product category
- `shared` (optional): Filter by sharing status (`true`, `false`)
- `sort` (optional): Sort by (`date`, `price`, `store`) (default: `date`)
- `order` (optional): Sort order (`asc`, `desc`) (default: `desc`)

**Response:**
```json
{
  "success": true,
  "data": {
    "purchases": [
      {
        "id": 1,
        "product": {
          "id": 1,
          "title": "Wireless Headphones",
          "description": "High-quality wireless headphones",
          "image_url": "https://example.com/image.jpg",
          "price": 99.99,
          "currency": "USD",
          "category": "Electronics"
        },
        "purchase_date": "2024-01-01T10:00:00Z",
        "store_name": "TechStore",
        "is_shared": true,
        "share_comment": "Great sound quality!",
        "interactions": {
          "likes": 5,
          "comments": 2,
          "saves": 1
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 50,
      "pages": 3
    }
  }
}
```

### GET /api/purchases/{purchase_id} 🔒

Get specific purchase details.

### PUT /api/purchases/{purchase_id}/share 🔒

Share a purchase with friends.

**Request Body:**
```json
{
  "comment": "Optional comment about the purchase"
}
```

### PUT /api/purchases/{purchase_id}/unshare 🔒

Unshare a purchase.

## Social Feed Endpoints

### GET /api/feed 🔒

Get social feed of friends' shared purchases.

**Query Parameters:**
- `page` (optional): Page number
- `per_page` (optional): Items per page
- `friend_id` (optional): Filter by specific friend

**Response:**
```json
{
  "success": true,
  "data": {
    "feed_items": [
      {
        "id": 1,
        "user": {
          "id": 2,
          "name": "Jane Doe",
          "profile_image": "/static/uploads/profile_2.jpg"
        },
        "purchase": {
          "id": 5,
          "product": {
            "title": "Running Shoes",
            "image_url": "https://example.com/shoes.jpg",
            "price": 129.99,
            "currency": "USD"
          },
          "store_name": "SportShop",
          "purchase_date": "2024-01-02T14:30:00Z"
        },
        "share_comment": "Perfect for my morning runs!",
        "shared_at": "2024-01-02T15:00:00Z",
        "interactions": {
          "likes": 3,
          "comments": 1,
          "saves": 0,
          "user_liked": false,
          "user_saved": false
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 25,
      "pages": 2
    }
  }
}
```

### POST /api/feed/item/{purchase_id}/like 🔒

Like a shared purchase.

### DELETE /api/feed/item/{purchase_id}/like 🔒

Unlike a shared purchase.

### POST /api/feed/item/{purchase_id}/comment 🔒

Comment on a shared purchase.

**Request Body:**
```json
{
  "content": "Great choice! I have the same one."
}
```

### POST /api/feed/item/{purchase_id}/save 🔒

Save a purchase to user's saved items.

### DELETE /api/feed/item/{purchase_id}/save 🔒

Remove purchase from saved items.

## Analytics Endpoints

### GET /api/analytics/spending 🔒

Get spending analytics.

**Query Parameters:**
- `period` (optional): Time period (`month`, `quarter`, `year`) (default: `month`)
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_spending": 1250.99,
    "currency": "USD",
    "period": "month",
    "spending_by_category": [
      {
        "category": "Electronics",
        "amount": 599.99,
        "percentage": 48.0,
        "count": 3
      },
      {
        "category": "Clothing",
        "amount": 350.00,
        "percentage": 28.0,
        "count": 5
      }
    ],
    "spending_by_store": [
      {
        "store": "TechStore",
        "amount": 299.99,
        "percentage": 24.0,
        "count": 2
      }
    ],
    "daily_spending": [
      {
        "date": "2024-01-01",
        "amount": 99.99
      }
    ]
  }
}
```

### GET /api/analytics/trends 🔒

Get spending trends over time.

### GET /api/analytics/categories 🔒

Get category-based analytics.

### GET /api/analytics/stores 🔒

Get store-based analytics.

## E-commerce Integration Endpoints

### GET /api/integrations 🔒

Get user's connected e-commerce integrations.

### POST /api/integrations/connect 🔒

Connect a new e-commerce store.

**Request Body:**
```json
{
  "platform": "shopify",
  "store_url": "mystore.myshopify.com",
  "access_token": "encrypted_access_token"
}
```

### DELETE /api/integrations/{integration_id} 🔒

Disconnect an e-commerce integration.

### POST /api/integrations/{integration_id}/sync 🔒

Manually trigger synchronization for an integration.

## Health and Monitoring Endpoints

### GET /health

Check application health status.

**Response:**
```json
{
  "overall_status": "healthy",
  "database": {
    "status": "healthy",
    "user_count": 150,
    "response_time": "fast"
  },
  "disk_space": {
    "status": "healthy",
    "free_space_percent": 75.5,
    "free_space_gb": 45.2
  },
  "memory": {
    "status": "healthy",
    "used_percent": 65.3,
    "available_gb": 2.8
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### GET /metrics

Get application metrics (requires admin access).

### GET /status

Simple status check.

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Common Error Responses

### Validation Error (422)
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    "Email is required",
    "Password must be at least 8 characters"
  ]
}
```

### Rate Limit Exceeded (429)
```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "retry_after": 3600
}
```

### Authentication Required (401)
```json
{
  "success": false,
  "message": "Authentication required"
}
```

## SDK and Examples

### JavaScript/Node.js Example

```javascript
// Login
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();
if (data.success) {
  console.log('Logged in:', data.data.user);
}

// Get purchases
const purchases = await fetch('/api/purchases?page=1&per_page=10');
const purchaseData = await purchases.json();
```

### Python Example

```python
import requests

# Login
login_response = requests.post('http://localhost:5000/api/auth/login', json={
    'email': 'user@example.com',
    'password': 'password123'
})

if login_response.json()['success']:
    # Get purchases (session cookie automatically included)
    purchases_response = requests.get('http://localhost:5000/api/purchases')
    purchases = purchases_response.json()['data']['purchases']
```

## Webhooks

BuyRoll supports webhooks for real-time notifications of events.

### Webhook Events

- `purchase.shared` - When a user shares a purchase
- `friend.request` - When a friend request is sent
- `friend.accepted` - When a friend request is accepted
- `interaction.created` - When someone likes or comments

### Webhook Payload

```json
{
  "event": "purchase.shared",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "user_id": 1,
    "purchase_id": 5,
    "share_comment": "Love this product!"
  }
}
```