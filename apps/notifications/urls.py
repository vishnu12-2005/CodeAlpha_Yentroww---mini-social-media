from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_view, name='notifications_view'),
    path('read/<int:id>/', views.read_notification, name='read_notification'),
    path('read-all/', views.read_all_notifications, name='read_all_notifications'),
    path('poll/', views.poll_notifications, name='poll_notifications'),
]
