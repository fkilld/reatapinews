from django.urls import path

from .views import *


urlpatterns = [
    path('',NewsListView.as_view(), name='news-list'),
    path('create/', NewsCreateView.as_view(), name='news-create'),
    # /api/news/{slug}/
    path('<slug:slug>/', NewsDetailView.as_view(), name='news-detail'),
    path('my/drafts/', MyDraftNewsListView.as_view(), name='my-draft-news-list'),
    path('<slug:slug>/update/', NewsUpdateView.as_view(), name='news-update')


]
