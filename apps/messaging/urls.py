from django.urls import path
from . import views

urlpatterns = [
    path('', views.dm_list, name='dm_list'),
    path('new/<str:username>/', views.start_dm, name='start_dm'),
    path('<int:conv_id>/', views.chat_view, name='chat_view'),
    path('<int:conv_id>/send/', views.send_message, name='send_message'),
    path('<int:conv_id>/seen/', views.mark_seen, name='mark_seen'),
    path('<int:conv_id>/poll/', views.poll_messages, name='poll_messages'),
]
