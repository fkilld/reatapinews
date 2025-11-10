from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *


urlpatterns = [
    # User Registration Endpoint
    # Example: POST /api/auth/register/
    # Purpose: Create new user accounts with email verification
    # Request: {"email": "user@example.com", "username": "johndoe", "password": "pass123", ...}
    # Response: {"id": 1, "email": "user@example.com", "username": "johndoe", ...}
    path('register/',UserRegistrationView.as_view(),name='user-register'),
    path('login/',UserLoginView.as_view(),name='user-login'),
    path('logout/',UserLogoutView.as_view(),name='user-logout'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token-refresh'),
    path('profile/',UserProfileView.as_view(),name='user-profile'),
    path('change-password/',ChangePasswordView.as_view(),name='change-password'),
    path('verify-email/',EmailVerificationView.as_view(),name='email-verify'),
    path('resend-verification/',ResendVerificationEmailView.as_view(),name='resend-verification'),
]
