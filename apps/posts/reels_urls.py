from django.urls import path
from . import views

urlpatterns = [
    path('', views.reels_feed, name='reels_feed'),
    path('create/', views.create_reel, name='create_reel'),
    path('<int:id>/', views.reel_detail, name='reel_detail'),
    path('<int:id>/react/', views.react_reel, name='react_reel'),
    path('<int:id>/comment/', views.comment_reel, name='comment_reel'),
    path('<int:id>/comments/', views.reel_comments_list, name='reel_comments_list'),
    path('<int:id>/share/', views.share_reel, name='share_reel'),
    path('<int:id>/report/', views.report_reel, name='report_reel'),
]
