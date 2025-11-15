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
from .models import News, Category, Tag, Like, Comment, Bookmark
from users.models import ReadingHistory
from .serializers import (
    NewsListSerializer,
    NewsDetailSerializer,
    NewsCreateUpdateSerializer,
    CategorySerializer,
    TagSerializer,
    CommentSerializer,
    LikeSerializer,
    BookmarkSerializer,
)


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
    
    # Serializer for article data formatting
    # Example: Handles user context and engagement metrics
    serializer_class = NewsListSerializer
    
    # No authentication required for public article listing
    # Example: Anyone can view published articles
    permission_classes = [permissions.AllowAny]
    
    # Advanced filtering and search backends
    # Example: Enables filtering, searching, and ordering capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Fields that can be filtered
    # Example: Filter by category=1, author=2, status=published
    filterset_fields = ['category', 'author', 'status']
    
    # Fields that can be searched
    # Example: Search in title, content, author username, category name
    search_fields = ['title', 'content', 'author__username', 'category__name']
    
    # Fields that can be used for ordering
    # Example: Order by published_date, view_count, like_count, created_at
    ordering_fields = ['published_date', 'view_count', 'like_count', 'created_at']
    
    # Default ordering (newest published articles first)
    # Example: Most recently published articles appear first
    ordering = ['-published_date']

    def get_queryset(self):
        """
        Get optimized queryset for published news articles.
        
        This method returns only published articles with optimized
        database queries to prevent N+1 problems.
        
        Returns:
            QuerySet: Published news articles with related data
            
        Example:
            Returns articles with author, category, and tags data
            loaded efficiently in minimal database queries
        """
        # Filter only published articles with optimized queries
        # Example: Loads author and category data in single query, tags in separate query
        return News.objects.filter(status='published').select_related(
            'author', 'category'
        ).prefetch_related('tags')


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
    
    # Serializer for detailed article data with comments
    # Example: Includes article details plus recent comments
    serializer_class = NewsDetailSerializer
    
    # No authentication required for article viewing
    # Example: Anyone can view published articles
    permission_classes = [permissions.AllowAny]
    
    # Use slug field for URL lookup instead of ID
    # Example: /api/news/latest-ai-breakthrough/ instead of /api/news/1/
    lookup_field = 'slug'

    def get_queryset(self):
        """
        Get optimized queryset for news articles with related data.
        
        This method returns articles with all related data loaded
        efficiently to prevent N+1 queries.
        
        Returns:
            QuerySet: News articles with author, category, tags, and comments
            
        Example:
            Loads article with author, category, tags, and comments with users
            in optimized database queries
        """
        # Load article with all related data in optimized queries
        # Example: Single query for author/category, separate query for tags/comments
        return News.objects.select_related('author', 'category').prefetch_related('tags', 'comments__user')

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve article details with view tracking and reading history.
        
        This method handles the article retrieval process:
        1. Gets the article instance
        2. Increments view count
        3. Adds to reading history if user is authenticated
        4. Returns serialized article data
        
        Args:
            request: HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            Response: JSON response with article details
            
        Example Flow:
            Input: GET /api/news/latest-ai-breakthrough/
            Process: Get Article → Increment Views → Track History → Serialize
            Output: {"id": 1, "title": "...", "view_count": 151, ...}
        """
        # Get the article instance
        # Example: Retrieves article by slug from URL
        instance = self.get_object()

        # Increment view count for analytics
        # Example: Tracks how many times article has been viewed
        instance.view_count += 1
        instance.save(update_fields=['view_count'])

        # Add to reading history if user is authenticated
        # Example: Tracks user's reading history for recommendations
        if request.user.is_authenticated:
            ReadingHistory.objects.get_or_create(user=request.user, news=instance)

        # Serialize and return article data
        # Example: Returns complete article information with comments
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
    
    # Serializer for article data formatting
    # Example: Same as public listing but for user's articles
    serializer_class = NewsListSerializer
    
    # Authentication required for personal content
    # Example: User must be logged in to view their articles
    permission_classes = [permissions.IsAuthenticated]
    
    # Search and ordering backends
    # Example: Enables searching and ordering capabilities
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    
    # Fields that can be searched
    # Example: Search in article title and content
    search_fields = ['title', 'content']
    
    # Fields that can be used for ordering
    # Example: Order by creation date, update date, published date
    ordering_fields = ['created_at', 'updated_at', 'published_date']
    
    # Default ordering (newest created articles first)
    # Example: Most recently created articles appear first
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Get user's articles with optimized queries.
        
        This method returns only articles created by the current user
        with optimized database queries.
        
        Returns:
            QuerySet: User's articles with related data
            
        Example:
            Returns articles authored by current user with category and tags
            loaded efficiently
        """
        # Filter articles by current user with optimized queries
        # Example: Loads category data in single query, tags in separate query
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
    
    # Serializer for article data formatting
    # Example: Same as other article listings
    serializer_class = NewsListSerializer
    
    # Authentication required for personal content
    # Example: User must be logged in to view their drafts
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get user's draft articles with optimized queries.
        
        This method returns only draft articles created by the current user
        with optimized database queries.
        
        Returns:
            QuerySet: User's draft articles with related data
            
        Example:
            Returns only unpublished articles authored by current user
        """
        # Filter draft articles by current user with optimized queries
        # Example: Only unpublished articles with category and tags loaded
        return News.objects.filter(author=self.request.user, status='draft').select_related('category').prefetch_related('tags')


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
    
    # Serializer for article creation and updates
    # Example: Handles content validation and tag management
    serializer_class = NewsCreateUpdateSerializer
    
    # Authentication required for article creation
    # Example: User must be logged in to create articles
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Create article with automatic author assignment.
        
        This method automatically assigns the current user as the
        author of the new article.
        
        Args:
            serializer: Validated article data
            
        Example:
            User creates article → Automatically sets author to current user
        """
        # Automatically assign current user as author
        # Example: Sets article author to the logged-in user
        serializer.save(author=self.request.user)


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
    
    # Serializer for article creation and updates
    # Example: Same as creation but for updates
    serializer_class = NewsCreateUpdateSerializer
    
    # Authentication required for article updates
    # Example: User must be logged in to update articles
    permission_classes = [permissions.IsAuthenticated]
    
    # Use slug field for URL lookup
    # Example: /api/news/my-article/update/ instead of /api/news/1/update/
    lookup_field = 'slug'

    def get_queryset(self):
        """
        Get user's articles for updating.
        
        This method returns only articles created by the current user,
        ensuring users can only update their own articles.
        
        Returns:
            QuerySet: User's articles only
            
        Example:
            Returns only articles authored by current user for editing
        """
        # Filter articles by current user (author-only editing)
        # Example: Only articles created by the logged-in user
        return News.objects.filter(author=self.request.user)


class NewsDeleteView(generics.DestroyAPIView):
    """
    API View for deleting news articles.
    
    This view handles the deletion of news articles created by the
    authenticated user with proper authorization checks.
    
    Features:
    - Article deletion with confirmation
    - Author-only deletion restriction
    - Permanent removal from database
    - Authentication required
    
    Endpoint: DELETE /api/news/{slug}/delete/
    Permission: IsAuthenticated (JWT access token required)
    
    Example Response:
    {
        "message": "Article deleted successfully"
    }
    """
    
    # Authentication required for article deletion
    # Example: User must be logged in to delete articles
    permission_classes = [permissions.IsAuthenticated]
    
    # Use slug field for URL lookup
    # Example: /api/news/my-article/delete/ instead of /api/news/1/delete/
    lookup_field = 'slug'

    def get_queryset(self):
        """
        Get user's articles for deletion.
        
        This method returns only articles created by the current user,
        ensuring users can only delete their own articles.
        
        Returns:
            QuerySet: User's articles only
            
        Example:
            Returns only articles authored by current user for deletion
        """
        # Filter articles by current user (author-only deletion)
        # Example: Only articles created by the logged-in user
        return News.objects.filter(author=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def publish_news(request, slug):
    """
    Function-based view for publishing news articles.
    
    This view changes an article's status from draft to published
    and sets the published date if not already set.
    
    Features:
    - Status change from draft to published
    - Automatic published date setting
    - Author-only publishing restriction
    - Authentication required
    
    Endpoint: POST /api/news/{slug}/publish/
    Permission: IsAuthenticated (JWT access token required)
    
    Example Response:
    {
        "message": "News published successfully"
    }
    """
    # Get article by slug, ensuring user is the author
    # Example: Only allows author to publish their own articles
    news = get_object_or_404(News, slug=slug, author=request.user)
    
    # Change status to published
    # Example: Makes article visible to public
    news.status = 'published'
    
    # Set published date if not already set
    # Example: Records when article was first published
    if not news.published_date:
        from django.utils import timezone
        news.published_date = timezone.now()
    
    # Save changes to database
    # Example: Persists status and date changes
    news.save()
    
    # Return success response
    # Example: Confirms article was published successfully
    return Response({'message': 'News published successfully'}, status=status.HTTP_200_OK)


class CategoryListView(generics.ListAPIView):
    """
    API View for listing active news categories.
    
    Endpoint: GET /api/news/categories/
    Purpose: Display all active categories with article counts
    Permission: AllowAny
    """
    # Only show active categories
    # Example: Filters out inactive/hidden categories
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryCreateView(generics.CreateAPIView):
    """
    API View for creating new categories (admin only).
    
    Endpoint: POST /api/news/categories/create/
    Purpose: Create new news categories for content organization
    Permission: IsAdminUser
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # Only admin users can create categories
    # Example: Prevents regular users from creating categories
    permission_classes = [permissions.IsAdminUser]


class CategoryNewsView(generics.ListAPIView):
    """
    API View for listing articles in a specific category.
    
    Endpoint: GET /api/news/categories/{id}/news/
    Purpose: Display all published articles in a category
    Permission: AllowAny
    """
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Get category ID from URL
        # Example: /api/news/categories/1/news/ → category_id = 1
        category_id = self.kwargs['category_id']
        
        # Filter published articles in this category with optimized queries
        # Example: Loads author/category in single query, tags in separate query
        return News.objects.filter(
            category_id=category_id, status='published'
        ).select_related('author', 'category').prefetch_related('tags')


class TagListView(generics.ListAPIView):
    """
    API View for listing all content tags.
    
    Endpoint: GET /api/news/tags/
    Purpose: Display all available tags with usage statistics
    Permission: AllowAny
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class PopularTagsView(generics.ListAPIView):
    """
    API View for listing most popular tags.
    
    Endpoint: GET /api/news/tags/popular/
    Purpose: Display most frequently used tags for content discovery
    Permission: AllowAny
    """
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Get tags with usage count > 0, ordered by popularity, limited to 20
        # Example: Shows most popular tags for content discovery
        return Tag.objects.filter(usage_count__gt=0).order_by('-usage_count')[:20]


class TagNewsView(generics.ListAPIView):
    """
    API View for listing articles with a specific tag.
    
    Endpoint: GET /api/news/tags/{id}/news/
    Purpose: Display all published articles tagged with specific tag
    Permission: AllowAny
    """
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Get tag ID from URL
        # Example: /api/news/tags/1/news/ → tag_id = 1
        tag_id = self.kwargs['tag_id']
        
        # Filter published articles with this tag with optimized queries
        # Example: Loads author/category in single query, tags in separate query
        return News.objects.filter(
            tags__id=tag_id, status='published'
        ).select_related('author', 'category').prefetch_related('tags')


class NewsSearchView(APIView):
    """
    API View for advanced news article search.
    
    This view provides comprehensive search functionality across
    multiple fields with filtering and pagination support.
    
    Features:
    - Full-text search across title, content, author, category, tags
    - Category filtering by slug
    - Author filtering by username
    - Date range filtering
    - Pagination support
    - Optimized queries for performance
    
    Endpoint: GET /api/news/search/
    Permission: AllowAny (no authentication required)
    
    Query Parameters:
    - ?q=search_term - Search in title, content, author, category, tags
    - ?category=technology - Filter by category slug
    - ?author=john_doe - Filter by author username
    - ?date_from=2024-01-01 - Filter articles from date
    - ?date_to=2024-12-31 - Filter articles to date
    - ?page=1 - Pagination
    
    Example Response:
    {
        "results": [...],
        "count": 25,
        "next": "http://api/news/search/?q=technology&page=2",
        "previous": null
    }
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Perform advanced search with multiple filters.
        
        This method handles comprehensive search across multiple fields
        with various filtering options and pagination.
        
        Args:
            request: HTTP request object with query parameters
            
        Returns:
            Response: Paginated search results
        """
        # Extract search parameters from request
        # Example: ?q=technology&category=sports&author=john
        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        author = request.GET.get('author', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')

        # Start with published articles only
        # Example: Only search in published content
        news_qs = News.objects.filter(status='published')

        # Apply full-text search if query provided
        # Example: Search across title, content, author, category, and tags
        if query:
            news_qs = news_qs.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(author__username__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()

        # Apply category filter if provided
        # Example: Filter by category slug
        if category:
            news_qs = news_qs.filter(category__slug=category)

        # Apply author filter if provided
        # Example: Filter by author username
        if author:
            news_qs = news_qs.filter(author__username__icontains=author)

        # Apply date range filters if provided
        # Example: Filter articles published between dates
        if date_from:
            news_qs = news_qs.filter(published_date__gte=date_from)

        if date_to:
            news_qs = news_qs.filter(published_date__lte=date_to)

        # Optimize queries to prevent N+1 problems
        # Example: Loads author/category in single query, tags in separate query
        news_qs = news_qs.select_related('author', 'category').prefetch_related('tags')

        # Paginate results for performance
        # Example: Limits results to 20 per page
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(news_qs, request)

        # Serialize results with request context
        # Example: Includes user-specific data like is_liked, is_bookmarked
        serializer = NewsListSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


# Like, Comment, Bookmark Views
class LikeToggleView(APIView):
    """
    API View for toggling like status on news articles.
    
    This view handles like/unlike functionality with automatic
    like count updates and duplicate prevention.
    
    Features:
    - Toggle like/unlike status
    - Automatic like count updates
    - Duplicate prevention with get_or_create
    - Authentication required
    
    Endpoint: POST /api/news/{id}/like/
    Permission: IsAuthenticated (JWT access token required)
    
    Example Response (Like Added):
    {
        "message": "Like added",
        "liked": true
    }
    
    Example Response (Like Removed):
    {
        "message": "Like removed", 
        "liked": false
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, news_id):
        """
        Toggle like status for a news article.
        
        This method creates a like if it doesn't exist, or removes it if it does,
        while updating the article's like count accordingly.
        
        Args:
            request: HTTP request object
            news_id: ID of the news article to like/unlike
            
        Returns:
            Response: JSON response with like status and message
        """
        # Get the news article
        # Example: Retrieves article by ID from URL
        news = get_object_or_404(News, id=news_id)
        
        # Create like if it doesn't exist, get existing if it does
        # Example: Prevents duplicate likes from same user
        like, created = Like.objects.get_or_create(user=request.user, news=news)

        if not created:
            # Like already existed, so remove it
            # Example: User unlikes an article they previously liked
            like.delete()
            news.like_count = max(0, news.like_count - 1)
            news.save(update_fields=['like_count'])
            return Response({'message': 'Like removed', 'liked': False}, status=status.HTTP_200_OK)
        else:
            # Like was created, so add it
            # Example: User likes an article for the first time
            news.like_count += 1
            news.save(update_fields=['like_count'])
            return Response({'message': 'Like added', 'liked': True}, status=status.HTTP_201_CREATED)


class NewsLikesView(generics.ListAPIView):
    """
    API View for listing users who liked a specific article.
    
    Endpoint: GET /api/news/{id}/likes/
    Purpose: Display users who liked a specific article
    Permission: AllowAny
    """
    serializer_class = LikeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Get article ID from URL and filter likes
        # Example: /api/news/1/likes/ → news_id = 1
        news_id = self.kwargs['news_id']
        return Like.objects.filter(news_id=news_id).select_related('user')


class MyLikesView(generics.ListAPIView):
    """
    API View for listing current user's liked articles.
    
    Endpoint: GET /api/news/my/likes/
    Purpose: Display articles that current user has liked
    Permission: IsAuthenticated
    """
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter likes by current user with optimized query
        # Example: Returns articles user has liked
        return Like.objects.filter(user=self.request.user).select_related('news')


class CommentCreateView(generics.CreateAPIView):
    """
    API View for creating comments on news articles.
    
    Endpoint: POST /api/news/{id}/comments/create/
    Purpose: Add new comment to a specific article
    Permission: IsAuthenticated
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Get article ID from URL and assign to comment
        # Example: Links comment to specific article
        news_id = self.kwargs['news_id']
        news = get_object_or_404(News, id=news_id)
        serializer.save(user=self.request.user, news=news)


class CommentListView(generics.ListAPIView):
    """
    API View for listing comments on a specific article.
    
    Endpoint: GET /api/news/{id}/comments/
    Purpose: Display all comments on a specific article
    Permission: AllowAny
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Get article ID from URL and filter comments
        # Example: /api/news/1/comments/ → news_id = 1
        news_id = self.kwargs['news_id']
        return Comment.objects.filter(news_id=news_id).select_related('user')


class CommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API View for updating/deleting comments (author only).
    
    Endpoint: PUT/DELETE /api/news/comments/{id}/
    Purpose: Update or delete specific comment
    Permission: IsAuthenticated (author only)
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow users to edit their own comments
        # Example: Prevents users from editing others' comments
        return Comment.objects.filter(user=self.request.user)


class BookmarkToggleView(APIView):
    """
    API View for toggling bookmark status on news articles.
    
    Endpoint: POST /api/news/{id}/bookmark/
    Purpose: Bookmark or unbookmark a specific article
    Permission: IsAuthenticated
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, news_id):
        """
        Toggle bookmark status for a news article.
        
        Creates bookmark if it doesn't exist, removes it if it does.
        """
        # Get the news article
        news = get_object_or_404(News, id=news_id)
        
        # Create bookmark if it doesn't exist, get existing if it does
        # Example: Prevents duplicate bookmarks from same user
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, news=news)

        if not created:
            # Bookmark already existed, so remove it
            bookmark.delete()
            return Response({'message': 'Bookmark removed', 'bookmarked': False}, status=status.HTTP_200_OK)
        else:
            # Bookmark was created, so add it
            return Response({'message': 'Bookmark added', 'bookmarked': True}, status=status.HTTP_201_CREATED)


class MyBookmarksView(generics.ListAPIView):
    """
    API View for listing current user's bookmarked articles.
    
    Endpoint: GET /api/news/my/bookmarks/
    Purpose: Display articles that current user has bookmarked
    Permission: IsAuthenticated
    """
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter bookmarks by current user with optimized query
        # Example: Returns articles user has bookmarked
        return Bookmark.objects.filter(user=self.request.user).select_related('news')


class RemoveBookmarkView(generics.DestroyAPIView):
    """
    API View for removing specific bookmarks.
    
    Endpoint: DELETE /api/news/bookmarks/{id}/remove/
    Purpose: Remove specific bookmark by ID
    Permission: IsAuthenticated (owner only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow users to remove their own bookmarks
        # Example: Prevents users from removing others' bookmarks
        return Bookmark.objects.filter(user=self.request.user)


# Recommendations View
class RecommendationsView(APIView):
    """
    API View for personalized article recommendations.
    
    This view provides personalized article recommendations based on
    the user's reading history and preferences using collaborative filtering.
    
    Features:
    - Personalized recommendations based on reading history
    - Category and tag-based filtering
    - Fallback to popular articles if no recommendations
    - Excludes already read articles
    - Authentication required
    
    Endpoint: GET /api/news/recommendations/
    Permission: IsAuthenticated (JWT access token required)
    
    Example Response:
    {
        "results": [
            {
                "id": 5,
                "title": "Recommended Article",
                "category_name": "Technology",
                "tags": [...],
                "view_count": 100,
                "like_count": 15
            }
        ],
        "count": 10
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get personalized article recommendations for the current user.
        
        This method analyzes the user's reading history to recommend
        similar articles based on categories and tags, with a fallback
        to popular articles if no personalized recommendations exist.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: JSON response with recommended articles
        """
        user = request.user

        # Get user's reading history
        # Example: Articles the user has previously read
        read_news_ids = ReadingHistory.objects.filter(user=user).values_list('news_id', flat=True)

        # Get categories from read news
        # Example: Categories of articles user has read
        read_categories = News.objects.filter(id__in=read_news_ids).values_list('category_id', flat=True).distinct()

        # Get tags from read news
        # Example: Tags of articles user has read
        read_tags = News.objects.filter(id__in=read_news_ids).values_list('tags__id', flat=True).distinct()

        # Recommend news from same categories and tags, excluding already read
        # Example: Find articles in similar categories/tags that user hasn't read
        recommended_news = News.objects.filter(
            status='published'
        ).filter(
            Q(category_id__in=read_categories) | Q(tags__id__in=read_tags)
        ).exclude(
            id__in=read_news_ids
        ).distinct().select_related(
            'author', 'category'
        ).prefetch_related('tags')[:10]

        # If no recommendations, get popular news
        # Example: Fallback to most viewed/liked articles if no personalized recommendations
        if not recommended_news.exists():
            recommended_news = News.objects.filter(
                status='published'
            ).exclude(
                id__in=read_news_ids
            ).order_by('-view_count', '-like_count')[:10]

        # Serialize recommendations with user context
        # Example: Includes user-specific data like is_liked, is_bookmarked
        serializer = NewsListSerializer(recommended_news, many=True, context={'request': request})
        return Response(serializer.data)
