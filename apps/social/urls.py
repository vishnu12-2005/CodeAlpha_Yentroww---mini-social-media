from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.feed_view, name='feed'),
    path('explore/', views.explore_view, name='explore'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]
