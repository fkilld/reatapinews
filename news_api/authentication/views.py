"""
Django REST Framework Views for Authentication App

This module contains all API view classes that handle user authentication,
profile management, password changes, and email verification functionality.
Each view class corresponds to a specific API endpoint and handles the
business logic for user operations.

Key Features:
- User registration with email verification
- JWT-based authentication and authorization
- Profile management and password changes
- Email verification token handling
- Comprehensive error handling and responses

API Endpoints Handled:
- POST /api/auth/register/ - User registration
- POST /api/auth/login/ - User authentication
- POST /api/auth/logout/ - User logout
- GET/PUT /api/auth/profile/ - Profile management
- POST /api/auth/change-password/ - Password change
- POST /api/auth/verify-email/ - Email verification
- POST /api/auth/resend-verification/ - Resend verification email

Authentication Flow:
1. User registers → Account created + verification email sent
2. User logs in → JWT tokens generated
3. User verifies email → Account activated
4. User accesses protected endpoints → JWT token required
5. User logs out → JWT token invalidated
"""

from django.shortcuts import render

# Create your views here.
from rest_framework import status, generics,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.contrib.auth import login
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import * 

from .serializers import *




class UserRegistrationView(generics.CreateAPIView):
    """
    API View for user registration endpoint.
    
    This view handles new user account creation with comprehensive validation,
    automatic email verification setup, and immediate JWT token generation.
    
    Features:
    - User account creation with password validation
    - Automatic email verification token generation
    - Immediate JWT token generation for seamless login
    - Email verification status tracking
    - Comprehensive error handling
    
    Endpoint: POST /api/auth/register/
    Permission: AllowAny (no authentication required)
    
    Example Request:
    {
        "email": "user@example.com",
        "username": "johndoe",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe"
    }
    
    Example Response (Success):
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
        "tokens": {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        },
        "message": "User registered successfully. Verification email sent.",
        "verification_email_sent": true
    }
    """
       

    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email_sent = send_verification_email(user)
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh' : str(refresh),
            'access' : str(refresh.access_token),
        } 
        response_data = {
            'user':UserSerializer(user).data,
            'token':tokens,
            'message': 'user registered successfully'
        }  
        
        if email_sent:
            response_data['verification_email_send'] = True
            response_data['message'] += '. verification email sent'
        else:
            response_data['verification_email_send'] = False
            response_data['message'] += '. Failed to send verification email '
        return Response(response_data,status=status.HTTP_201_CREATED)
            
class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request,user)
        ##############
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh' : str(refresh),
            'access' : str(refresh.access_token),
        } 
        return Response({
            'user':UserSerializer(user).data,
            'token':tokens,
            'message': 'user logged in successfully'
        },status=status.HTTP_200_OK)  
        
class UserLogoutView(APIView):
    permission_classes =[permissions.IsAuthenticated]
    def post(self,request):
        try:
            refresh_token = request.data['refresh']
            token= RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'message':'logout successful'
            },status=status.HTTP_200_OK)
        except:
            return Response({
                'message':'invalid token',
            },status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes =[permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user
    
class ChangePasswordView(APIView):
    permission_classes =[permissions.IsAuthenticated]
    def post(self,request):
        serializer = ChangePasswordSerializer(data= request.data,context={'request':request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message':'password change successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_200_OK)
    
class EmailVerificationView(APIView):
    permission_classes =[permissions.AllowAny]
    def post(self,request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            token_value = serializer.validated_data['token']
            verification_token = EmailVerificationToken.objects.get(token=token_value,is_used=False)
            user = verification_token.user
            user.is_email_verified =True
            user.save()
            verification_token.is_used =True
            verification_token.save()
            return Response({'message':'email verified successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.AllowAny] # for endpoint access without authentication
    def post(self,request): # for endpoint method post
        serializers = ResendVerificationSerializer(data=request.data)
        if serializers.is_valid():
            email = serializers.validated_data['email']
            user = CustomUser.objects.get(email=email)
            # print(user,'azad')
            email_sent = send_verification_email(user)
            print(email_sent)
            if email_sent:
                return Response({'message':'verification email resent successfully'},status=status.HTTP_200_OK)
            else:
                return Response({'message':'failed to send verification email'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def send_verification_email(user):
    # uuid token = '<uuid>'
    verification_token = EmailVerificationToken.objects.create(user=user)
    verification_url = f"{settings.API_BASE_URL}/api/auth/verify-email/"
    subject = 'Verify your email azad'
    html_message = render_to_string(f'email_verification.html', {
        'subject': subject,
        'user': user,
        
        'verification_url': verification_url,
        'token': verification_token.token,
    })
    
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


    
    
    

    








































