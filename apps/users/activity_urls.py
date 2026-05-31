from django.urls import path
from . import views

urlpatterns = [
    path('', views.activity_home, name='activity_home'),
    path('saved/', views.activity_saved, name='activity_saved'),
    path('comments/', views.activity_comments, name='activity_comments'),
    path('dashboard/', views.activity_dashboard, name='activity_dashboard'),
    path('<str:r_type>/', views.activity_reactions, name='activity_reactions'), # yentroww, abboww, sarlee
]
