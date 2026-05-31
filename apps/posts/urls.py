from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_post, name='create_post'),
    path('<int:id>/', views.post_detail, name='post_detail'),
    path('<int:id>/react/', views.react_post, name='react_post'),
    path('<int:id>/comment/', views.comment_post, name='comment_post'),
    path('<int:id>/share/', views.share_post, name='share_post'),
    path('<int:id>/report/', views.report_post, name='report_post'),
]
