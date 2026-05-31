import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from .models import Post, Reel, Story, Reaction, Comment, StoryView, Tag, PostTag
from .forms import PostForm, ReelForm, StoryForm
from messaging.models import Conversation, Message
from django.contrib.auth.models import User
from django.utils import timezone

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            if post.media_file:
                ext = post.media_file.name.split('.')[-1].lower()
                if ext in ['mp4', 'mov', 'webm']:
                    post.media_type = 'video'
                else:
                    post.media_type = 'image'
            else:
                post.media_type = 'text'
            post.save()
            return redirect('/feed/')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})

@login_required
def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    if post.visibility == 'private' and post.user != request.user and not post.user.followers.filter(follower=request.user).exists():
        return render(request, 'posts/post_detail.html', {'error': 'This post is private 🔒'})
    return render(request, 'posts/post_detail.html', {'post': post})

@login_required
def react_post(request, id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=id)
        data = json.loads(request.body)
        reaction_type = data.get('reaction_type')
        content_type = ContentType.objects.get_for_model(Post)
        
        reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=post.id,
            defaults={'reaction_type': reaction_type}
        )
        
        if not created:
            if reaction.reaction_type == reaction_type:
                reaction.delete()
                action = 'removed'
            else:
                reaction.reaction_type = reaction_type
                reaction.save()
                action = 'updated'
        else:
            action = 'created'
            
        y_count = Reaction.objects.filter(content_type=content_type, object_id=post.id, reaction_type='yentroww').count()
        a_count = Reaction.objects.filter(content_type=content_type, object_id=post.id, reaction_type='abboww').count()
        s_count = Reaction.objects.filter(content_type=content_type, object_id=post.id, reaction_type='sarlee').count()
        
        return JsonResponse({'status': 'success', 'action': action, 'counts': {'yentroww': y_count, 'abboww': a_count, 'sarlee': s_count}})
    return JsonResponse({'status': 'error'})

@login_required
def comment_post(request, id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=id)
        data = json.loads(request.body)
        text = data.get('text')
        if text:
            comment = Comment.objects.create(user=request.user, post=post, text=text)
            return JsonResponse({
                'status': 'success',
                'comment': {
                    'username': comment.user.username,
                    'avatar_url': comment.user.profile.avatar.url if (hasattr(comment.user, 'profile') and comment.user.profile.avatar) else '',
                    'text': comment.text
                }
            })
    return JsonResponse({'status': 'error'})

@login_required
def share_post(request, id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=id)
        data = json.loads(request.body)
        recipient_username = data.get('username')
        recipient = get_object_or_404(User, username=recipient_username)
        
        convs = Conversation.objects.filter(participants=request.user).filter(participants=recipient)
        if convs.exists():
            conv = convs.first()
        else:
            conv = Conversation.objects.create()
            conv.participants.add(request.user, recipient)
            
        Message.objects.create(conversation=conv, sender=request.user, shared_post=post)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def report_post(request, id):
    if request.method == 'POST':
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def create_reel(request):
    if request.method == 'POST':
        form = ReelForm(request.POST, request.FILES)
        if form.is_valid():
            reel = form.save(commit=False)
            reel.user = request.user
            reel.save()
            return redirect('/reels/')
    else:
        form = ReelForm()
    return render(request, 'posts/create_reel.html', {'form': form})

@login_required
def reels_feed(request):
    reels = Reel.objects.all().order_by('-created_at')
    content_type = ContentType.objects.get_for_model(Reel)
    for reel in reels:
        reel.y_count = Reaction.objects.filter(content_type=content_type, object_id=reel.id, reaction_type='yentroww').count()
        reel.a_count = Reaction.objects.filter(content_type=content_type, object_id=reel.id, reaction_type='abboww').count()
        reel.s_count = Reaction.objects.filter(content_type=content_type, object_id=reel.id, reaction_type='sarlee').count()
        
        user_reaction = Reaction.objects.filter(content_type=content_type, object_id=reel.id, user=request.user).first()
        reel.user_reaction_type = user_reaction.reaction_type if user_reaction else None
    return render(request, 'social/reels.html', {'reels': reels})

@login_required
def reel_detail(request, id):
    reel = get_object_or_404(Reel, id=id)
    content_type = ContentType.objects.get_for_model(Reel)
    reel.y_count = Reaction.objects.filter(content_type=content_type, object_id=reel.id, reaction_type='yentroww').count()
    reel.a_count = Reaction.objects.filter(content_type=content_type, object_id=reel.id, reaction_type='abboww').count()
    reel.s_count = Reaction.objects.filter(content_type=content_type, object_id=reel.id, reaction_type='sarlee').count()
    
    user_reaction = Reaction.objects.filter(content_type=content_type, object_id=reel.id, user=request.user).first()
    reel.user_reaction_type = user_reaction.reaction_type if user_reaction else None
    
    return render(request, 'posts/reel_detail.html', {'reel': reel})

@login_required
def react_reel(request, id):
    if request.method == 'POST':
        reel = get_object_or_404(Reel, id=id)
        data = json.loads(request.body)
        reaction_type = data.get('reaction_type')
        content_type = ContentType.objects.get_for_model(Reel)
        
        reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=reel.id,
            defaults={'reaction_type': reaction_type}
        )
        
        if not created:
            if reaction.reaction_type == reaction_type:
                reaction.delete()
                action = 'removed'
            else:
                reaction.reaction_type = reaction_type
                reaction.save()
                action = 'updated'
        else:
            action = 'created'
            
        y_count = Reaction.objects.filter(content_type=content_type, object_id=reel.id, reaction_type='yentroww').count()
        a_count = Reaction.objects.filter(content_type=content_type, object_id=reel.id, reaction_type='abboww').count()
        s_count = Reaction.objects.filter(content_type=content_type, object_id=reel.id, reaction_type='sarlee').count()
        
        return JsonResponse({'status': 'success', 'action': action, 'counts': {'yentroww': y_count, 'abboww': a_count, 'sarlee': s_count}})
    return JsonResponse({'status': 'error'})

@login_required
def comment_reel(request, id):
    if request.method == 'POST':
        reel = get_object_or_404(Reel, id=id)
        data = json.loads(request.body)
        text = data.get('text')
        if text:
            comment = Comment.objects.create(user=request.user, reel=reel, text=text)
            return JsonResponse({
                'status': 'success',
                'comment': {
                    'username': comment.user.username,
                    'avatar_url': comment.user.profile.avatar.url if (hasattr(comment.user, 'profile') and comment.user.profile.avatar) else '',
                    'text': comment.text
                }
            })
    return JsonResponse({'status': 'error'})

@login_required
def reel_comments_list(request, id):
    reel = get_object_or_404(Reel, id=id)
    comments = reel.comments.all().order_by('created_at')
    comments_data = []
    for c in comments:
        comments_data.append({
            'username': c.user.username,
            'avatar_url': c.user.profile.avatar.url if (hasattr(c.user, 'profile') and c.user.profile.avatar) else '/static/images/default_avatar.png',
            'text': c.text,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'status': 'success', 'comments': comments_data})

@login_required
def share_reel(request, id):
    if request.method == 'POST':
        reel = get_object_or_404(Reel, id=id)
        data = json.loads(request.body)
        recipient_username = data.get('username')
        recipient = get_object_or_404(User, username=recipient_username)
        
        convs = Conversation.objects.filter(participants=request.user).filter(participants=recipient)
        if convs.exists():
            conv = convs.first()
        else:
            conv = Conversation.objects.create()
            conv.participants.add(request.user, recipient)
            
        Message.objects.create(conversation=conv, sender=request.user, shared_reel=reel)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def report_reel(request, id):
    if request.method == 'POST':
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def create_story(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = request.user
            if story.media_file:
                ext = story.media_file.name.split('.')[-1].lower()
                story.media_type = 'video' if ext in ['mp4', 'mov', 'webm'] else 'image'
            story.save()
            return redirect('/feed/')
    else:
        form = StoryForm()
    return render(request, 'posts/create_story.html', {'form': form})

@login_required
def view_story(request, id):
    if request.method == 'POST':
        story = get_object_or_404(Story, id=id)
        StoryView.objects.get_or_create(story=story, viewer=request.user)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def report_story(request, id):
    if request.method == 'POST':
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def stories_for_user(request, user_id):
    """API endpoint: returns JSON list of active stories for a given user."""
    target_user = get_object_or_404(User, id=user_id)
    stories = Story.objects.filter(
        user=target_user,
        expires_at__gt=timezone.now()
    ).order_by('created_at')
    
    stories_data = []
    for s in stories:
        viewed = StoryView.objects.filter(story=s, viewer=request.user).exists()
        stories_data.append({
            'id': s.id,
            'media_url': s.media_file.url if s.media_file else '',
            'media_type': s.media_type,
            'created_at': s.created_at.strftime('%I:%M %p'),
            'viewed': viewed,
        })
    
    return JsonResponse({
        'status': 'success',
        'user_id': target_user.id,
        'username': target_user.username,
        'avatar_url': target_user.profile.avatar.url if (hasattr(target_user, 'profile') and target_user.profile.avatar) else '/static/images/default_avatar.png',
        'is_self': target_user == request.user,
        'stories': stories_data,
    })

@login_required
def reply_story(request, id):
    """Send a DM reply to a story."""
    if request.method == 'POST':
        story = get_object_or_404(Story, id=id)
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        
        if not text:
            return JsonResponse({'status': 'error', 'message': 'Empty reply'})
        
        if story.user == request.user:
            return JsonResponse({'status': 'error', 'message': 'Cannot reply to own story'})
        
        # Find or create conversation
        convs = Conversation.objects.filter(participants=request.user).filter(participants=story.user)
        if convs.exists():
            conv = convs.first()
        else:
            conv = Conversation.objects.create()
            conv.participants.add(request.user, story.user)
        
        # Create message with story reply text
        reply_text = f"📸 Replied to your story: {text}"
        Message.objects.create(conversation=conv, sender=request.user, text=reply_text)
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})
