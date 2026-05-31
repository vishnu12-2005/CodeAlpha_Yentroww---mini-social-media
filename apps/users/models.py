from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True)
    ACCOUNT_TYPE_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='public')
    is_verified = models.BooleanField(default=False)
    verification_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

class MutedAccount(models.Model):
    user = models.ForeignKey(User, related_name='muted_accounts', on_delete=models.CASCADE)
    muted_user = models.ForeignKey(User, related_name='muted_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class MutedStory(models.Model):
    user = models.ForeignKey(User, related_name='muted_stories', on_delete=models.CASCADE)
    muted_user = models.ForeignKey(User, related_name='story_muted_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class BlockedAccount(models.Model):
    user = models.ForeignKey(User, related_name='blocked_accounts', on_delete=models.CASCADE)
    blocked_user = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
