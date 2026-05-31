from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_story, name='create_story'),
    path('<int:id>/view/', views.view_story, name='view_story'),
    path('<int:id>/report/', views.report_story, name='report_story'),
    path('<int:id>/reply/', views.reply_story, name='reply_story'),
    path('user/<int:user_id>/', views.stories_for_user, name='stories_for_user'),
]
