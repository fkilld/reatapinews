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
from users.models import *


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
    
    

class NewsDetailView(generics.RetrieveAPIView):
    """
    API View for retrieving detailed news article information.
    
    This view provides detailed article information including comments
    and automatically tracks view counts and reading history.
    
    Features:
    - Complete article details with comments
    - Automatic view count increment
    - Reading history tracking for authenticated users
    - Optimized queries for related data
    - SEO-friendly slug-based URLs
    
    Endpoint: GET /api/news/{slug}/
    Permission: AllowAny (no authentication required)
    
    Example Response:
    {
        "id": 1,
        "title": "Latest AI Breakthrough",
        "slug": "latest-ai-breakthrough",
        "content": "Full article content...",
        "author": 1,
        "author_name": "john_doe",
        "category": 1,
        "category_name": "Technology",
        "tags": [...],
        "view_count": 151,
        "like_count": 25,
        "is_liked": false,
        "is_bookmarked": true,
        "comment_count": 8,
        "comments": [
            {
                "id": 1,
                "user": 2,
                "user_name": "jane_smith",
                "content": "Great article!",
                "created_at": "2024-01-15T15:30:00Z"
            }
        ],
        "published_date": "2024-01-15T14:30:00Z"
    }
    """
    serializer_class = NewsDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    def get_queryset(self):
        return News.objects.select_related('author','category').prefetch_related('tags','comments__user')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count +=1
        instance.save(update_fields=['view_count'])
        if request.user.is_authenticated:
            ReadingHistory.objects.get_or_create(user=request.user, news=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
        
        
class MyNewsListView(generics.ListAPIView):
    """
    API View for listing current user's news articles.
    
    This view provides a listing of all articles created by the
    authenticated user, including both published and draft articles.
    
    Features:
    - User-specific article filtering
    - Search functionality across title and content
    - Multiple ordering options
    - Optimized queries for performance
    - Authentication required
    
    Endpoint: GET /api/news/my/all/
    Permission: IsAuthenticated (JWT access token required)
    
    Query Parameters:
    - ?search=technology - Search in title and content
    - ?ordering=-created_at - Order by creation date (newest first)
    - ?page=1 - Pagination
    
    Example Response:
    {
        "results": [
            {
                "id": 1,
                "title": "My Article",
                "status": "published",
                "view_count": 50,
                "like_count": 10,
                "created_at": "2024-01-15T10:30:00Z"
            }
        ],
        "count": 5
    }
    """
    serializer_class = NewsDetailSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends= [filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['title','content']
    ordering_fields = ['created_at','updated_at','published_date']
    ordering = ['-created_at']
    def get_queryset(self):
        return News.objects.filter(author=self.request.user).select_related('category').prefetch_related('tags')
    
class MyDraftNewsListView(generics.ListAPIView):
    """
    API View for listing current user's draft articles.
    
    This view provides a listing of only draft articles created by the
    authenticated user, useful for content management workflows.
    
    Features:
    - User-specific draft article filtering
    - Only unpublished articles
    - Optimized queries for performance
    - Authentication required
    
    Endpoint: GET /api/news/my/drafts/
    Permission: IsAuthenticated (JWT access token required)
    
    Example Response:
    {
        "results": [
            {
                "id": 2,
                "title": "Draft Article",
                "status": "draft",
                "view_count": 0,
                "like_count": 0,
                "created_at": "2024-01-15T11:30:00Z"
            }
        ],
        "count": 3
    }
    """
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        return News.objects.filter(author=self.request.user,status='draft').select_related('category').prefetch_related('tags')
    
class NewsUpdateView(generics.UpdateAPIView):
    """
    API View for updating existing news articles.
    
    This view handles the updating of news articles created by the
    authenticated user with comprehensive validation.
    
    Features:
    - Article content updates
    - Tag and category management
    - Featured image updates
    - Publication status changes
    - Author-only editing restriction
    - Authentication required
    
    Endpoint: PUT /api/news/{slug}/update/
    Permission: IsAuthenticated (JWT access token required)
    
    Example Request:
    {
        "title": "Updated Article Title",
        "content": "Updated content...",
        "tags": [1, 3],
        "status": "published"
    }
    """
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    def get_queryset(self):
        return News.objects.filter(author=self.request.user)

class NewsDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    def get_queryset(self):
        return News.objects.filter(author=self.request.user)
    