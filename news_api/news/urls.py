from django.urls import path

from .views import *


urlpatterns = [
    path('',NewsListView.as_view(), name='news-list'),
    path('create/', NewsCreateView.as_view(), name='news-create'),


]
