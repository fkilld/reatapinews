from rest_framework import serializers
from .models import * 
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,  validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'password_confirm', 'first_name', 'last_name')
    def validate(self, attrs):    
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user

# user login
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email =  attrs.get('email')
        password =  attrs.get('password')
        if email and password:
            user  = authenticate(request=self.context.get('request'),username=email,password=password)
            if not user :
                raise serializers.ValidationError('unable to log in with proviede credentials')
            if not user.is_active :
                raise serializers.ValidationError('user account is disabled')
            if not user.is_email_verified :
                raise serializers.ValidationError('please verify you email')
            
            attrs['user'] = user
            return  attrs
        else:
            raise serializers.ValidationError('must included "email" and "password"')
            
# user serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id','email','username','first_name','last_name','is_email_verified','date_joined')
        
        read_only_fields = ('id','is_email_verified','date_joined')
# changepassword
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm =serializers.CharField(required=True)
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match.")
        return attrs
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value
# email verification
class EmailVerificationSerializer(serializers.Serializer):
    # token must be valid UUID4
    # token must exit in database
    # token must not be already used
    # token must not be expired 
    token = serializers.UUIDField()
    def validate_token(self, value):
        try:
            verification_token = EmailVerificationToken.objects.get(token=value, is_used=False)
            if verification_token.is_expired():
                raise serializers.ValidationError("Token has expired.")
            return value
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid or used token.")
    
# resend verification
class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
            if user.is_email_verified:
                raise serializers.ValidationError("Email is already verified.")
            return value
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
                
        


