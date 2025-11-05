

# Create your views here.
"""
Django REST Framework Serializers for News App

This module contains all serializers used for news content management,
categorization, and user interaction handling. Serializers handle data
validation, serialization, and deserialization for API endpoints.

Key Features:
- News article serialization with rich metadata
- Category and tag management
- User interaction tracking (likes, comments, bookmarks)
- Dynamic field calculation based on user context
- Comprehensive data validation and error handling
- Optimized queries for performance

Example API Usage:
    GET /api/news/ - List news articles
    GET /api/news/{id}/ - Get news article details
    POST /api/news/ - Create news article
    PUT /api/news/{id}/ - Update news article
    POST /api/news/{id}/like/ - Like/unlike article
    POST /api/news/{id}/comment/ - Add comment
    POST /api/news/{id}/bookmark/ - Bookmark/unbookmark article
"""
from rest_framework import serializers
from django.utils import timezone
from .models import *



class CategorySerializer(serializers.Serializer):
    news_count = serializers.SerializerMethodField()
    
    