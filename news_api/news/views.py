"""
Django REST Framework Views for News App

This module contains all API view classes that handle news content management,
user interactions, content discovery, and personal content management.
Each view class corresponds to specific API endpoints and handles the
business logic for news operations.

Key Features:
- News article CRUD operations with rich content management
- User interaction tracking (likes, comments, bookmarks)
- Content discovery through search, filtering, and recommendations
- Personal content management (user's articles, interactions)
- Category and tag-based content organization
- Reading history tracking for personalized recommendations
- Comprehensive permission handling and data validation

API Endpoints Handled:
- GET /api/news/ - List published articles
- GET /api/news/{slug}/ - Get article details
- POST /api/news/create/ - Create new article
- PUT /api/news/{slug}/update/ - Update article
- DELETE /api/news/{slug}/delete/ - Delete article
- POST /api/news/{slug}/publish/ - Publish article
- GET /api/news/search/ - Search articles
- GET /api/news/my/* - Personal content management
- POST /api/news/{id}/like/ - Like/unlike article
- POST /api/news/{id}/comment/ - Add comment
- POST /api/news/{id}/bookmark/ - Bookmark/unbookmark
- GET /api/news/recommendations/ - Get recommendations
"""



from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *



class NewsCreateView(generics.CreateAPIView):
    """
    API View for creating new news articles.
    
    This view handles the creation of new news articles with
    comprehensive content management and validation.
    
    Features:
    - Article creation with rich content support
    - Tag assignment and category classification
    - Featured image upload support
    - Publication status management
    - Automatic author assignment
    - Authentication required
    
    Endpoint: POST /api/news/create/
    Permission: IsAuthenticated (JWT access token required)
    
    Example Request:
    {
        "title": "Latest Technology News",
        "content": "Article content here...",
        "category": 1,
        "tags": [1, 2, 3],
        "featured_image": <file>,
        "status": "draft"
    }
    
    Example Response:
    {
        "id": 1,
        "title": "Latest Technology News",
        "slug": "latest-technology-news",
        "content": "Article content here...",
        "author": 1,
        "category": 1,
        "tags": [...],
        "status": "draft",
        "created_at": "2024-01-15T10:30:00Z"
    }
    """
   
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NewsCreateUpdateSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        

class NewsListView(generics.ListAPIView):
    """
    API View for listing published news articles with advanced filtering.
    
    This view provides a comprehensive listing of published news articles
    with advanced filtering, searching, and ordering capabilities.
    
    Features:
    - Advanced filtering by category, author, and status
    - Full-text search across title, content, author, and category
    - Multiple ordering options (date, views, likes)
    - Optimized queries with select_related and prefetch_related
    - Pagination support for large datasets
    
    Endpoint: GET /api/news/
    Permission: AllowAny (no authentication required)
    
    Query Parameters:
    - ?category=1 - Filter by category ID
    - ?author=2 - Filter by author ID
    - ?search=technology - Search in title, content, author, category
    - ?ordering=-published_date - Order by published date (newest first)
    - ?page=1 - Pagination
    
    Example Response:
    {
        "results": [
            {
                "id": 1,
                "title": "Latest AI Breakthrough",
                "slug": "latest-ai-breakthrough",
                "content": "Article content...",
                "author": 1,
                "author_name": "john_doe",
                "category": 1,
                "category_name": "Technology",
                "tags": [...],
                "view_count": 150,
                "like_count": 25,
                "is_liked": false,
                "is_bookmarked": true,
                "comment_count": 8,
                "published_date": "2024-01-15T14:30:00Z"
            }
        ],
        "count": 100,
        "next": "http://api/news/?page=2",
        "previous": null
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NewsListSerializer
    
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields  = ['category','author','status']
    search_fields = ['title','content','author__username']
    ordering_fields =  ['-published', 'view_count','like_count','create_at']
    def get_queryset(self):
        return News.objects.filter(status='published').select_related('author','category').prefetch_related('tags')
    
    
from rest_framework import viewsets
 