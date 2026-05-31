from django.urls import path
from users.views import (
    settings_view, request_verification, toggle_account_type,
    mute_user, unmute_user, unmute_story, unblock_user, search_users
)

urlpatterns = [
    path('', settings_view, name='settings'),
    path('verify/', request_verification, name='request_verification'),
    path('toggle-account-type/', toggle_account_type, name='toggle_account_type'),
    path('mute/<str:username>/', mute_user, name='mute_user'),
    path('unmute/<str:username>/', unmute_user, name='unmute_user'),
    path('unmute-story/<str:username>/', unmute_story, name='unmute_story'),
    path('unblock/<str:username>/', unblock_user, name='unblock_user'),
    path('search-users/', search_users, name='search_users'),
]
