from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid 
from django.utils import timezone
from datetime import timedelta

# Create your models here.


class CustomUser(AbstractUser):
    """
    Custom User Model extending Django's AbstractUser

    Flow:
    1. User registration creates CustomUser instance with email as username
    2. is_email_verified starts as False
    3. After email verification, is_email_verified becomes True
    4. Email field is unique and used for authentication instead of username

    Features:
    - Email-based authentication instead of username
    - Email verification tracking with is_email_verified field
    - Timestamp tracking for user creation and updates
    """
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
class EmailVerificationToken(models.Model):
    """
    Email Verification Token Model for secure email verification

    Flow:
    1. Token created when user registers or requests resend
    2. Token sent to user's email with verification instructions
    3. User submits token via API to verify email
    4. Token marked as used and user's is_email_verified set to True
    5. Expired or used tokens are rejected

    Security Features:
    - UUID4 tokens (cryptographically secure, unpredictable)
    - 24-hour expiration for security
    - One-time use (marked as used after verification)
    - Automatic cleanup of old tokens possible
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='email_verification_tokens')
    
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_verification_tokens'
        ordering = ['-created_at']
    def save(self, *args, **kwargs):
        """
        Override save method to automatically set expiration time

        Flow:
        1. Check if expires_at is not already set
        2. Set expires_at to 24 hours from current time
        3. Call parent save method to persist to database

        This ensures every token has a 24-hour expiration automatically
        """
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
        
        
    def is_expired(self):
        """
        Check if the token has expired

        Flow:
        1. Compare current time with expires_at
        2. Return True if current time is past expires_at, else False
        """
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Token for {self.user.email} - Used: {self.is_used}"