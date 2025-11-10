# News API Documentation

A Django REST Framework API for news management with user authentication, articles, comments, likes, and bookmarks.

## Table of Contents
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [User Authentication Endpoints](#user-authentication-endpoints)
  - [News Endpoints](#news-endpoints-not-implemented-yet)
- [Models Overview](#models-overview)
- [JWT Configuration](#jwt-configuration)

---

## Authentication

This API uses JWT (JSON Web Token) authentication. Most endpoints require authentication.

### Authentication Header Format
```
Authorization: Bearer <access_token>
```

### Token Lifecycle
- **Access Token:** Valid for 60 minutes
- **Refresh Token:** Valid for 7 days
- Token rotation is enabled (new refresh token issued on refresh)
- Old tokens are blacklisted after rotation

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/auth/
```

---

## User Authentication Endpoints

### 1. User Registration

Register a new user account.

**Endpoint:** `POST /api/auth/register/`

**Authentication:** Not required

**Request Body:**
```json
{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Required Fields:**
- `email` (string, unique)
- `username` (string)
- `password` (string, min 8 characters with validation)
- `password_confirm` (string, must match password)

**Optional Fields:**
- `first_name` (string)
- `last_name` (string)

**Success Response (201 Created):**
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "is_email_verified": false,
        "date_joined": "2024-01-15T10:30:00Z"
    },
    "token": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    },
    "message": "user registered successfully. verification email sent",
    "verification_email_send": true
}
```

**Error Response (400 Bad Request):**
```json
{
    "email": ["user with this email already exists."],
    "password": ["This password is too common."]
}
```

**Features:**
- Automatic JWT token generation upon registration
- Password validation using Django's built-in validators
- Email verification token created (24-hour expiry)
- Returns user details and authentication tokens

---

### 2. User Login

Authenticate a user and receive JWT tokens.

**Endpoint:** `POST /api/auth/login/`

**Authentication:** Not required

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

**Required Fields:**
- `email` (string)
- `password` (string)

**Success Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "is_email_verified": true,
        "date_joined": "2024-01-15T10:30:00Z"
    },
    "token": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    },
    "message": "user logged in successfully"
}
```

**Error Response (401 Unauthorized):**
```json
{
    "detail": "invalid credentials"
}
```

**Error Response (403 Forbidden):**
```json
{
    "detail": "please verify your email before logging in"
}
```

**Validation:**
- Email and password must be valid
- User account must be active
- Email must be verified (if enabled)

---

### 3. User Logout

Logout a user by blacklisting their refresh token.

**Endpoint:** `POST /api/auth/logout/`

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Required Fields:**
- `refresh` (string, JWT refresh token)

**Success Response (200 OK):**
```json
{
    "message": "logout successful"
}
```

**Error Response (400 Bad Request):**
```json
{
    "message": "invalid token"
}
```

**Features:**
- Blacklists the refresh token to prevent reuse
- Access token will expire naturally (within 60 minutes)

---

### 4. Token Refresh

Refresh an expired access token using a valid refresh token.

**Endpoint:** `POST /api/auth/token/refresh/`

**Authentication:** Not required

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Required Fields:**
- `refresh` (string, JWT refresh token)

**Success Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Features:**
- Token rotation enabled (returns new refresh token)
- Old refresh token is automatically blacklisted
- Use the new refresh token for subsequent refresh requests

**Error Response (401 Unauthorized):**
```json
{
    "detail": "Token is invalid or expired",
    "code": "token_not_valid"
}
```

---

### 5. Get/Update User Profile

Retrieve or update the authenticated user's profile.

**Endpoint:** `GET /api/auth/profile/` (Retrieve)

**Endpoint:** `PUT /api/auth/profile/` (Full Update)

**Endpoint:** `PATCH /api/auth/profile/` (Partial Update)

**Authentication:** Required (Bearer token)

#### GET Request

**Success Response (200 OK):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "is_email_verified": true,
    "date_joined": "2024-01-15T10:30:00Z"
}
```

#### PUT/PATCH Request

**Request Body:**
```json
{
    "username": "johndoe_updated",
    "first_name": "John",
    "last_name": "Doe Updated"
}
```

**Editable Fields:**
- `username` (string)
- `first_name` (string)
- `last_name` (string)

**Read-Only Fields:**
- `id`
- `email`
- `is_email_verified`
- `date_joined`

**Success Response (200 OK):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe_updated",
    "first_name": "John",
    "last_name": "Doe Updated",
    "is_email_verified": true,
    "date_joined": "2024-01-15T10:30:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
    "username": ["A user with that username already exists."]
}
```

---

### 6. Change Password

Change the authenticated user's password.

**Endpoint:** `POST /api/auth/change-password/`

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
    "old_password": "OldPass123!",
    "new_password": "NewPass123!",
    "new_password_confirm": "NewPass123!"
}
```

**Required Fields:**
- `old_password` (string)
- `new_password` (string, min 8 characters with validation)
- `new_password_confirm` (string, must match new_password)

**Success Response (200 OK):**
```json
{
    "message": "password change successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
    "old_password": ["Wrong password."],
    "new_password": ["This password is too short."],
    "new_password_confirm": ["Passwords do not match."]
}
```

**Validation:**
- Old password must be correct
- New passwords must match
- New password validated with Django's password validators

---

## News Endpoints (Not Implemented Yet)

The following models and serializers exist but views/URLs are not yet implemented:

### Planned Endpoints

#### News Articles
- `GET /api/news/` - List all published news articles
- `POST /api/news/` - Create a new article (authenticated)
- `GET /api/news/{slug}/` - Get article details
- `PUT/PATCH /api/news/{slug}/` - Update article (author only)
- `DELETE /api/news/{slug}/` - Delete article (author only)

#### Categories
- `GET /api/news/categories/` - List all categories
- `POST /api/news/categories/` - Create category (admin only)
- `GET /api/news/categories/{slug}/` - Get category details
- `PUT/PATCH /api/news/categories/{slug}/` - Update category (admin only)

#### Tags
- `GET /api/news/tags/` - List all tags
- `POST /api/news/tags/` - Create tag
- `GET /api/news/tags/{slug}/` - Get tag details

#### Likes
- `POST /api/news/{slug}/like/` - Like/unlike an article
- `GET /api/news/{slug}/likes/` - List users who liked the article

#### Comments
- `GET /api/news/{slug}/comments/` - List article comments
- `POST /api/news/{slug}/comments/` - Add a comment
- `PUT/PATCH /api/news/comments/{id}/` - Update comment (author only)
- `DELETE /api/news/comments/{id}/` - Delete comment (author only)

#### Bookmarks
- `POST /api/news/{slug}/bookmark/` - Bookmark/unbookmark an article
- `GET /api/bookmarks/` - List user's bookmarked articles

---

## Models Overview

### CustomUser Model

**Authentication Model**

Fields:
- `id` - Primary key
- `email` - Unique email (used for login)
- `username` - Username (required)
- `password` - Hashed password
- `first_name` - First name
- `last_name` - Last name
- `is_email_verified` - Email verification status (default: false)
- `is_active` - Account active status
- `is_staff` - Staff status
- `date_joined` - Registration date
- `created_at` - Created timestamp
- `updated_at` - Updated timestamp

**Login Field:** Users login with `email` instead of username

---

### EmailVerificationToken Model

**Email Verification Tracking**

Fields:
- `id` - Primary key
- `user` - ForeignKey to CustomUser
- `token` - Unique UUID token
- `created_at` - Creation timestamp
- `expires_at` - Expiration timestamp (24 hours)
- `is_used` - Whether token has been used

---

### News Model

**Article Management**

Fields:
- `id` - Primary key
- `title` - Article title (max 255 chars)
- `slug` - URL-friendly slug (auto-generated from title)
- `content` - Article content (text)
- `author` - ForeignKey to CustomUser
- `category` - ForeignKey to Category (nullable)
- `tags` - ManyToMany to Tag
- `status` - Status: 'draft', 'published', 'archived' (default: 'draft')
- `published_date` - Publication date (nullable)
- `view_count` - Number of views (default: 0)
- `like_count` - Number of likes (default: 0)
- `created_at` - Creation timestamp
- `updated_at` - Update timestamp

---

### Category Model

**News Categories**

Fields:
- `id` - Primary key
- `name` - Category name (max 100 chars, unique)
- `description` - Category description
- `slug` - URL-friendly slug (auto-generated)
- `color_code` - Hex color code (default: '#000000')
- `is_active` - Active status (default: true)
- `created_at` - Creation timestamp

---

### Tag Model

**Article Tags**

Fields:
- `id` - Primary key
- `name` - Tag name (max 50 chars, unique)
- `slug` - URL-friendly slug (auto-generated)
- `usage_count` - Number of times used (default: 0)
- `created_at` - Creation timestamp

---

### Like Model

**Article Likes**

Fields:
- `id` - Primary key
- `user` - ForeignKey to CustomUser
- `news` - ForeignKey to News
- `created_at` - Creation timestamp

**Constraint:** One like per user per article (unique_together)

---

### Comment Model

**Article Comments**

Fields:
- `id` - Primary key
- `user` - ForeignKey to CustomUser
- `news` - ForeignKey to News
- `content` - Comment text
- `created_at` - Creation timestamp
- `updated_at` - Update timestamp

---

### Bookmark Model

**Saved Articles**

Fields:
- `id` - Primary key
- `user` - ForeignKey to CustomUser
- `news` - ForeignKey to News
- `created_at` - Creation timestamp

**Constraint:** One bookmark per user per article (unique_together)

---

### UserProfile Model

**Extended User Information**

Fields:
- `id` - Primary key
- `user` - OneToOne to CustomUser
- `profile_picture` - Image upload field
- `full_name` - Full name (max 255 chars)
- `bio` - Biography text
- `date_of_birth` - Birth date
- `phone_number` - Phone number (max 20 chars)
- `address` - Address text
- `created_at` - Creation timestamp
- `updated_at` - Update timestamp

---

### ReadingHistory Model

**Article View History**

Fields:
- `id` - Primary key
- `user` - ForeignKey to CustomUser
- `news` - ForeignKey to News
- `viewed_at` - View timestamp

**Constraint:** One record per user per article (unique_together)

---

## JWT Configuration

### Token Settings

```python
ACCESS_TOKEN_LIFETIME = 60 minutes (1 hour)
REFRESH_TOKEN_LIFETIME = 7 days
ROTATE_REFRESH_TOKENS = True
BLACKLIST_AFTER_ROTATION = True
ALGORITHM = HS256
AUTH_HEADER_TYPE = Bearer
```

### Token Usage

1. **Register/Login:** Receive both access and refresh tokens
2. **Authenticated Requests:** Include access token in header:
   ```
   Authorization: Bearer <access_token>
   ```
3. **Token Expired:** Use refresh token to get new access token
4. **Logout:** Blacklist refresh token

---

## Pagination

Default pagination is enabled for list endpoints:
- **Page Size:** 5 items per page
- **Format:** `?page=2`

Example response:
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/news/?page=3",
    "previous": "http://localhost:8000/api/news/?page=1",
    "results": [...]
}
```

---

## Error Response Format

All error responses follow this format:

**400 Bad Request:**
```json
{
    "field_name": ["Error message for this field."],
    "another_field": ["Another error message."]
}
```

**401 Unauthorized:**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
    "detail": "Not found."
}
```

---

## Development Setup

### Prerequisites
- Python 3.8+
- Django 4.x
- Django REST Framework
- djangorestframework-simplejwt

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```
5. Run development server:
   ```bash
   python manage.py runserver
   ```

---

## Current Implementation Status

### Completed (6 endpoints)
- User Registration
- User Login
- User Logout
- Token Refresh
- User Profile (Get/Update)
- Change Password

### Pending Implementation
Models and serializers exist but views/URLs not implemented:
- News article CRUD operations
- Category management
- Tag management
- Like functionality
- Comment system
- Bookmark system
- User profiles (extended)
- Reading history tracking
- Email verification views

---

## Known Issues

1. **Email Verification Logic:** Bug in login validation at `authentication/serializers.py:35` - condition should be `not user.is_email_verified`
2. **Missing Field:** `featured_image` field referenced in News serializers but not in model/migrations
3. **Incomplete Features:** Email verification serializers exist but views are not implemented

---

## License

[Add your license here]

## Contact

[Add your contact information here]
