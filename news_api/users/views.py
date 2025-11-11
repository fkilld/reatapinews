from django.shortcuts import render, get_object_or_404

# Create your views here.
"""
Django REST Framework Views for Users App

This module contains API view classes that handle user profile management,
image uploads, and reading history tracking. Each view class corresponds
to specific API endpoints and handles the business logic for user operations.

Key Features:
- User profile management with automatic profile creation
- Profile picture upload and deletion
- Public profile viewing for other users
- Reading history tracking and management
- Comprehensive error handling and validation
- Authentication and permission management

API Endpoints Handled:
- GET/PUT /api/users/profile/ - User profile management
- GET /api/users/profile/{id}/ - Public profile viewing
- POST/DELETE /api/users/profile/picture/ - Profile picture management
- GET /api/users/reading-history/ - Reading history listing
- DELETE /api/users/reading-history/clear/ - Clear reading history

View Classes:
1. UserProfileDetailView - User's own profile management
2. PublicUserProfileView - Public profile viewing
3. ProfilePictureUploadView - Profile picture upload/delete
4. ReadingHistoryView - Reading history listing
5. ClearReadingHistoryView - Clear all reading history
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    API View for user profile management (retrieve and update).
    
    This view handles the current user's profile information including
    viewing and updating profile data. It automatically creates a profile
    if one doesn't exist for the user.
    
    Features:
    - Automatic profile creation if none exists
    - Profile data retrieval and updates
    - User-specific profile access
    - Authentication required
    - Comprehensive profile validation
    
    Endpoint: GET/PUT /api/users/profile/
    Permission: IsAuthenticated (JWT access token required)
    
    Example GET Response:
    {
        "id": 1,
        "user_email": "john.doe@example.com",
        "username": "johndoe",
        "profile_picture": "/media/profile_pictures/user123.jpg",
        "full_name": "John Doe",
        "bio": "Software developer and tech enthusiast",
        "date_of_birth": "1990-05-15",
        "phone_number": "+1234567890",
        "address": "123 Main St, City, State",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-20T14:45:00Z"
    }
    
    Example PUT Request:
    {
        "full_name": "John Doe",
        "bio": "Updated bio information",
        "phone_number": "+1234567890"
    }
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Get or create user profile for the current user.
        
        This method automatically creates a UserProfile if one doesn't
        exist for the current user, ensuring every user has a profile.
        
        Returns:
            UserProfile: User's profile instance
            
        Example:
            User logs in → Profile automatically created if needed
        """
        profile  , created =  UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class PublicUserProfileView(generics.RetrieveAPIView):
    
    """
    API View for viewing public user profiles.
    
    This view allows viewing other users' public profile information
    by their user ID. It provides read-only access to profile data
    for user discovery and social features.
    
    Features:
    - Public profile viewing by user ID
    - Read-only access to profile data
    - Optimized queries with select_related
    - No authentication required
    - User discovery functionality
    
    Endpoint: GET /api/users/profile/{id}/
    Permission: AllowAny (no authentication required)
    
    Example Response:
    {
        "id": 2,
        "user_email": "jane.smith@example.com",
        "username": "janesmith",
        "profile_picture": "/media/profile_pictures/user456.jpg",
        "full_name": "Jane Smith",
        "bio": "Tech writer and blogger",
        "date_of_birth": "1985-08-20",
        "phone_number": "+0987654321",
        "address": "456 Oak Ave, City, State",
        "created_at": "2024-01-10T09:15:00Z",
        "updated_at": "2024-01-18T16:30:00Z"
    }
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]
    # permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    def get_queryset(self):
        return UserProfile.objects.select_related('user').all()
    
class ProfilePictureUploadView(APIView):
    """
    API View for profile picture upload and deletion.
    
    This view handles profile picture management including
    uploading new images and deleting existing ones. It provides
    comprehensive file handling and validation.
    
    Features:
    - Profile picture upload with file validation
    - Image deletion and cleanup
    - Automatic profile creation if needed
    - File system management
    - Error handling for invalid uploads
    
    Endpoint: POST/DELETE /api/users/profile/picture/
    Permission: IsAuthenticated (JWT access token required)
    
    Example POST Request:
    FormData with 'profile_picture' file field
    
    Example POST Response:
    {
        "id": 1,
        "user_email": "john.doe@example.com",
        "username": "johndoe",
        "profile_picture": "/media/profile_pictures/user123.jpg",
        "full_name": "John Doe",
        ...
    }
    
    Example DELETE Response:
    {
        "message": "Profile picture removed successfully"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if 'profile_picture' not in request.FILES:
            return Response({"error": "No profile picture provided."}, status=status.HTTP_400_BAD_REQUEST)
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def delete(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        profile.profile_picture.delete(save=True)
        return Response({"message": "Profile picture removed successfully"}, status=status.HTTP_200_OK)
    
    
class ReadingHistoryView(generics.ListAPIView):
    """
    API View for listing user's reading history.
    
    This view provides a listing of articles that the current user
    has read, ordered by most recent views first. It enables
    reading history tracking and personalization features.
    
    Features:
    - User-specific reading history filtering
    - Chronological ordering (newest first)
    - Optimized queries with select_related
    - Authentication required
    - Pagination support
    
    Endpoint: GET /api/users/reading-history/
    Permission: IsAuthenticated (JWT access token required)
    
    Example Response:
    {
        "results": [
            {
                "id": 1,
                "news": 5,
                "news_title": "Latest AI Breakthrough",
                "news_slug": "latest-ai-breakthrough",
                "viewed_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "news": 3,
                "news_title": "Technology Trends 2024",
                "news_slug": "technology-trends-2024",
                "viewed_at": "2024-01-14T15:45:00Z"
            }
        ],
        "count": 25,
        "next": "http://api/users/reading-history/?page=2",
        "previous": null
    }
    """
    
    
    serializer_class = ReadingHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ReadingHistory.objects.filter(user=self.request.user).select_related('news')
    
    
class ClearReadingHistoryView(APIView):
    """
    API View for clearing all reading history entries.
    
    This view allows users to clear their entire reading history,
    providing privacy control and data management functionality.
    
    Features:
    - Bulk deletion of all reading history entries
    - User-specific data clearing
    - Privacy control functionality
    - Authentication required
    - Confirmation response
    
    Endpoint: DELETE /api/users/reading-history/clear/
    Permission: IsAuthenticated (JWT access token required)
    
    Example Response:
    {
        "message": "Reading history cleared successfully"
    }
    """
       
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        ReadingHistory.objects.filter(user=self.request.user).delete()
        return Response({"message": "Reading history cleared successfully"}, status=status.HTTP_200_OK)
    