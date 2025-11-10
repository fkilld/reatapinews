from django.urls import path

from .views import *


urlpatterns = [
path('profile/',UserProfileDetailView.as_view(),name='user-profile'),
path('profile/<int:id>/',PublicUserProfileView.as_view(),name='user-profile-detail'),
path('profile/picture/',ProfilePictureUploadView.as_view(),name='profile-picture-upload'),

]
