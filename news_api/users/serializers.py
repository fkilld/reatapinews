from rest_framework import serializers
from .models import *

class UserProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email',read_only=True)
    username = serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model =  UserProfile
        fields = [
            'id', 'user_email','username','profile_picture','full_name','bio','date_of_birth','phone_number','address','created_at','updated_at'
        ]
        read_only_fields = ['id','created_at','updated_at']
        

class ReadingHistorySerializer(serializers.ModelSerializer):
    news_title = serializers.CharField(source='news.title',read_only=True)
    news_slug = serializers.SlugField(source='news.slug',read_only=True)
    class Meta:
        model = ReadingHistory
        fields = [
            'id','news','news_title','news_slug','viewed_at'
        ]
        read_only_fields = ['id','viewed_at']