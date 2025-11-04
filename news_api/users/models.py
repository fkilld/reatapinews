from django.db import models
from django.conf import settings
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.email

class ReadingHistory(models.Model):
    # link to the user who viewed the news item
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reading_history')
    # link to the news item that was viewed (string app.model to avoid import cycle)
    news = models.ForeignKey('news.News', on_delete=models.CASCADE)
    # timestamp when this record was first created (when the view was recorded)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ensure one record per (user, news) pair (prevents duplicate rows)
        unique_together = ('user', 'news')
        # default ordering when querying: newest views first
        ordering = ['-viewed_at']

    def __str__(self):
        # human-readable representation: "<email> viewed <title> at <timestamp>"
        return f"{self.user.email} viewed {self.news.title} at {self.viewed_at}"