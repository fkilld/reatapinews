

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



class CategorySerializer(serializers.ModelSerializer):
    news_count = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields =   ['id', 'name', 'description', 'slug', 'color_code', 'is_active', 'news_count', 'created_at']
        read_only_fields =[ 'id','slug','created_at']
    
    def get_news_count(self,obj):
        return obj.news_articles.filter(status='published').count()

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields =   ['id', 'name', 'slug', 'usage_count', 'created_at']
        read_only_fields = ['id', 'slug', 'usage_count', 'created_at']
    

class NewsListSerializer(serializers.ModelSerializer):
    #     old_password = serializers.CharField(required=True)
    # new_password = serializers.CharField(required=True, validators=[validate_password])
    # new_password_confirm =serializers.CharField(required=True)
    author_name = serializers.CharField(source='author.username',read_only=True)
    category_name = serializers.CharField(source='category.username',read_only=True)
    tags = TagSerializer(many=True,read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    class Meta:
        fields = ['id', 'title', 'slug', 'content', 'author', 'author_name', 'category', 'category_name',
                 'tags', 'featured_image', 'status', 'published_date', 'view_count', 'like_count',
                 'is_liked', 'is_bookmarked', 'comment_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'author', 'view_count', 'like_count', 'created_at', 'updated_at']
    def get_is_liked(self,obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, news=obj).exists()
        return False
    def get_is_bookmarked(self,obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Bookmark.objects.filter(user=request.user, news=obj).exists()
        return False
    def get_comment_count(self,obj):
        return obj.comments.count()
    
    
    
class NewsDetailSerializer(NewsListSerializer):
    """
    Serializer for News model in detail views with comments.
    
    This serializer extends NewsListSerializer to include comments
    for detailed article views, providing a complete article
    experience with user discussions.
    
    Features:
    - All features from NewsListSerializer
    - Recent comments display (limited to 10)
    - Optimized comment queries with user data
    - Nested comment serialization
    
    Example response data:
    {
        "id": 1,
        "title": "Latest AI Breakthrough",
        "content": "Full article content...",
        "author_name": "john_doe",
        "category_name": "Technology",
        "tags": [...],
        "is_liked": true,
        "is_bookmarked": false,
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
        ...
    }
    """
    
    # Dynamic field to include recent comments
    # Example: Shows latest 10 comments for article discussion
    comments = serializers.SerializerMethodField()

    class Meta(NewsListSerializer.Meta):
        # Add comments field to the base fields
        # Example: Includes all list fields plus comments
        fields = NewsListSerializer.Meta.fields + ['comments']

    def get_comments(self, obj):
        """
        Get recent comments for this article with user information.
        
        This method retrieves the most recent comments (limited to 10)
        with optimized queries to include user data and avoid N+1 queries.
        
        Args:
            obj: News instance
            
        Returns:
            list: Serialized comment data with user information
            
        Example:
            Article with 15 comments → Returns 10 most recent comments
            Article with 3 comments → Returns all 3 comments
        """
        # Get recent comments with user data (optimized query)
        # Example: Fetches comments with user info in single query
        comments = obj.comments.select_related('user')[:10]
        
        # Serialize comments with context for proper user data
        # Example: Returns formatted comment data with usernames
        return CommentSerializer(comments, many=True, context=self.context).data


class NewsCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating News articles.
    
    This serializer handles article creation and updates with
    proper tag management and publication date handling.
    
    Features:
    - Article content management
    - Tag assignment and updates
    - Publication workflow handling
    - Automatic published date setting
    - Category and image support
    
    Example request data:
    {
        "title": "Latest Technology News",
        "content": "Article content here...",
        "category": 1,
        "tags": [1, 2, 3],
        "featured_image": <file>,
        "status": "published"
    }
    """
    
    # Tag field for many-to-many relationship
    # Example: Accepts list of tag IDs for article tagging
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)

    class Meta:
        model = News
        # Fields that can be provided during creation/update
        # Example: All editable article fields except system-managed ones
        fields = ['title', 'content', 'category', 'tags', 'featured_image', 'status']

    def create(self, validated_data):
        """
        Create a new news article with tags and publication handling.
        
        This method handles the complete article creation process:
        1. Extracts tag data from validated data
        2. Creates the article instance
        3. Assigns tags to the article
        4. Sets published date if status is 'published'
        
        Args:
            validated_data: Validated article data
            
        Returns:
            News: The created article instance
            
        Example:
            Input: {"title": "AI News", "content": "...", "tags": [1, 2], "status": "published"}
            Process: Create article → Assign tags → Set published date
            Output: News instance with tags and published_date set
        """
        # Extract tags data before creating article
        # Example: Remove tags from validated_data to handle separately
        tags_data = validated_data.pop('tags', [])
        
        # Create the article instance
        # Example: Create News object with validated data
        news = News.objects.create(**validated_data)
        
        # Assign tags to the article
        # Example: Set many-to-many relationship with tags
        news.tags.set(tags_data)

        # Set published date if article is published
        # Example: Automatically set published_date when status changes to 'published'
        if news.status == 'published' and not news.published_date:
            news.published_date = timezone.now()
            news.save()

        return news

    def update(self, instance, validated_data):
        """
        Update an existing news article with tags and publication handling.
        
        This method handles the complete article update process:
        1. Extracts tag data from validated data
        2. Updates article fields
        3. Handles published date if status changes to 'published'
        4. Updates tags if provided
        
        Args:
            instance: Existing News instance
            validated_data: Validated update data
            
        Returns:
            News: The updated article instance
            
        Example:
            Input: {"title": "Updated Title", "tags": [1, 3], "status": "published"}
            Process: Update fields → Set published date → Update tags
            Output: Updated News instance with new data
        """
        # Extract tags data before updating article
        # Example: Remove tags from validated_data to handle separately
        tags_data = validated_data.pop('tags', None)

        # Update instance fields
        # Example: Apply all validated data to the article instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle published_date if status changes to published
        # Example: Set published_date when article becomes published
        if instance.status == 'published' and not instance.published_date:
            instance.published_date = timezone.now()

        # Save the updated instance
        # Example: Persist changes to database
        instance.save()

        # Update tags if provided
        # Example: Update many-to-many relationship with new tags
        if tags_data is not None:
            instance.tags.set(tags_data)

        return instance


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model with user information.
    
    This serializer handles comment data serialization including
    user information for display purposes.
    
    Features:
    - Complete comment information display
    - User name resolution for display
    - Read-only system fields protection
    - Timestamp tracking for creation and updates
    
    Example response data:
    {
        "id": 1,
        "user": 2,
        "user_name": "jane_smith",
        "news": 1,
        "content": "Great article! Very informative.",
        "created_at": "2024-01-15T15:30:00Z",
        "updated_at": "2024-01-15T16:45:00Z"
    }
    """
    
    # User username for display purposes
    # Example: "jane_smith" instead of just user ID
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        # Fields exposed in API responses
        # Example: All comment data including user information
        fields = ['id', 'user', 'user_name', 'news', 'content', 'created_at', 'updated_at']
        
        # Fields that cannot be modified by users
        # Example: System-managed fields that users shouldn't edit directly
        read_only_fields = ['id', 'user', 'news', 'created_at', 'updated_at']


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for Like model with user and article information.
    
    This serializer handles like data serialization for tracking
    user engagement with news articles.
    
    Features:
    - Complete like information display
    - User and article relationship tracking
    - Read-only system fields protection
    - Creation timestamp tracking
    
    Example response data:
    {
        "id": 1,
        "user": 2,
        "news": 1,
        "created_at": "2024-01-15T15:30:00Z"
    }
    """
    
    class Meta:
        model = Like
        # Fields exposed in API responses
        # Example: All like data for tracking user engagement
        fields = ['id', 'user', 'news', 'created_at']
        
        # Fields that cannot be modified by users
        # Example: System-managed fields that users shouldn't edit directly
        read_only_fields = ['id', 'user', 'created_at']



class BookmarkSerializer(serializers.ModelSerializer):
    """
    Serializer for Bookmark model with article information.
    
    This serializer handles bookmark data serialization including
    article information for display purposes.
    
    Features:
    - Complete bookmark information display
    - Article title and slug for easy identification
    - User and article relationship tracking
    - Read-only system fields protection
    - Creation timestamp tracking
    
    Example response data:
    {
        "id": 1,
        "user": 2,
        "news": 1,
        "news_title": "Latest AI Breakthrough",
        "news_slug": "latest-ai-breakthrough",
        "created_at": "2024-01-15T15:30:00Z"
    }
    """
    
    # Article title for display purposes
    # Example: "Latest AI Breakthrough" for easy identification
    news_title = serializers.CharField(source='news.title', read_only=True)
    
    # Article slug for URL generation
    # Example: "latest-ai-breakthrough" for linking to article
    news_slug = serializers.CharField(source='news.slug', read_only=True)

    class Meta:
        model = Bookmark
        # Fields exposed in API responses
        # Example: All bookmark data including article information
        fields = ['id', 'user', 'news', 'news_title', 'news_slug', 'created_at']
        
        # Fields that cannot be modified by users
        # Example: System-managed fields that users shouldn't edit directly
        read_only_fields = ['id', 'user', 'created_at']