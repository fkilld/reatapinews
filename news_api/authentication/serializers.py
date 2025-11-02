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
    