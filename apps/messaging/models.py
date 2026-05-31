from django.db import models
from django.contrib.auth.models import User
from posts.models import Post, Reel

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    media_file = models.FileField(upload_to='messages/', blank=True, null=True)
    shared_post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    shared_reel = models.ForeignKey(Reel, on_delete=models.SET_NULL, null=True, blank=True)
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
