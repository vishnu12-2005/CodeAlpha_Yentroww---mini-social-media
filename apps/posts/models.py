from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField(blank=True)
    media_file = models.FileField(upload_to='posts/', blank=True, null=True)
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('text', 'Text'),
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='text')
    location = models.CharField(max_length=255, blank=True)
    VISIBILITY = (('public', 'Public'), ('private', 'Private'))
    visibility = models.CharField(max_length=10, choices=VISIBILITY, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PostTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

class PostTaggedUser(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Reel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reels')
    video_file = models.FileField(upload_to='reels/')
    caption = models.TextField(blank=True)
    VISIBILITY = (('public', 'Public'), ('private', 'Private'))
    visibility = models.CharField(max_length=10, choices=VISIBILITY, default='public')
    created_at = models.DateTimeField(auto_now_add=True)

def default_expires_at():
    return timezone.now() + timedelta(days=1)

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    media_file = models.FileField(upload_to='stories/')
    media_type = models.CharField(max_length=10, choices=[('image','Image'), ('video','Video')])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expires_at)

class StoryView(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    REACTION_TYPES = (
        ('yentroww', 'Yentroww'),
        ('abboww', 'Abboww'),
        ('sarlee', 'Sarlee'),
    )
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
