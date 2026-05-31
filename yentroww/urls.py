from django.contrib import admin
from django.urls import path, include
from users.views import landing_page
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='landing'),
    path('auth/', include('users.urls')),
    path('', include('social.urls')),
    path('posts/', include('posts.urls')),
    path('reels/', include('posts.reels_urls')), # Reels are in posts app based on models
    path('stories/', include('posts.stories_urls')), # Stories are in posts app
    path('profile/', include('users.profile_urls')),
    path('settings/', include('users.settings_urls')),
    path('activity/', include('users.activity_urls')),
    path('follow/', include('users.follow_urls')),
    path('messages/', include('messaging.urls')),
    path('notifications/', include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
