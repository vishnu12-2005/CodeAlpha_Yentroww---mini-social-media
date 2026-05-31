from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from posts.models import Post, Reel, Story, StoryView, Reaction
from users.models import Follow, MutedAccount, MutedStory
from .models import WeeklyLeaderboard
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
import json

@login_required
def feed_view(request):
    user = request.user
    
    following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
    muted_story_users = MutedStory.objects.filter(user=user).values_list('muted_user', flat=True)
    
    # Build stories list for the stories bar
    my_stories = Story.objects.filter(user=user, expires_at__gt=timezone.now()).order_by('created_at')
    
    other_stories = Story.objects.filter(
        user__in=following_users,
        expires_at__gt=timezone.now()
    ).exclude(user__in=muted_story_users).order_by('user', 'created_at')
    
    stories_by_user = {}
    
    # Always show self in stories bar (for "Add Story" or viewing own stories)
    has_own_stories = my_stories.exists()
    stories_by_user[user.id] = {
        'user': user,
        'stories': list(my_stories),
        'all_seen': True,
        'is_self': True,
        'has_stories': has_own_stories,
    }
        
    for story in other_stories:
        uid = story.user.id
        if uid not in stories_by_user:
            stories_by_user[uid] = {
                'user': story.user,
                'stories': [],
                'all_seen': True,
                'is_self': False,
                'has_stories': True,
            }
        stories_by_user[uid]['stories'].append(story)
        if not StoryView.objects.filter(story=story, viewer=user).exists():
            stories_by_user[uid]['all_seen'] = False
            
    stories_list = list(stories_by_user.values())
    # Self always first, then unseen stories, then seen
    stories_list.sort(key=lambda x: (not x.get('is_self', False), x['all_seen']))
    
    # Build stories_json for JavaScript
    stories_json = []
    for item in stories_list:
        stories_json.append({
            'user_id': item['user'].id,
            'username': item['user'].username,
            'avatar_url': item['user'].profile.avatar.url if (hasattr(item['user'], 'profile') and item['user'].profile.avatar) else '/static/images/default_avatar.png',
            'is_self': item.get('is_self', False),
            'has_stories': item.get('has_stories', False),
            'all_seen': item['all_seen'],
        })
    
    top_scorers = WeeklyLeaderboard.objects.order_by('rank')[:3]
    
    muted_accounts = MutedAccount.objects.filter(user=user).values_list('muted_user', flat=True)
    
    # Include own posts AND followed users' posts
    from django.db.models import Q
    posts = Post.objects.filter(
        Q(user__in=following_users) | Q(user=user)
    ).exclude(user__in=muted_accounts).order_by('-created_at')
    
    # Pre-calculate reactions for posts
    content_type = ContentType.objects.get_for_model(Post)
    for post in posts:
        post.y_count = Reaction.objects.filter(content_type=content_type, object_id=post.id, reaction_type='yentroww').count()
        post.a_count = Reaction.objects.filter(content_type=content_type, object_id=post.id, reaction_type='abboww').count()
        post.s_count = Reaction.objects.filter(content_type=content_type, object_id=post.id, reaction_type='sarlee').count()
        
        user_reaction = Reaction.objects.filter(content_type=content_type, object_id=post.id, user=user).first()
        post.user_reaction_type = user_reaction.reaction_type if user_reaction else None
    
    return render(request, 'posts/feed.html', {
        'stories_list': stories_list,
        'stories_json': json.dumps(stories_json),
        'top_scorers': top_scorers,
        'posts': posts,
    })

@login_required
def explore_view(request):
    q = request.GET.get('q', '').strip()
    tab = request.GET.get('tab', 'all').strip()
    
    posts = Post.objects.filter(visibility='public')
    reels = Reel.objects.filter(visibility='public')
    users = []
    
    if q:
        from django.db.models import Q
        posts = posts.filter(Q(caption__icontains=q) | Q(user__username__icontains=q) | Q(location__icontains=q))
        reels = reels.filter(Q(caption__icontains=q) | Q(user__username__icontains=q))
        
        from django.contrib.auth.models import User
        users = User.objects.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)).exclude(id=request.user.id)[:20]
    else:
        if tab == 'people':
            from django.contrib.auth.models import User
            users = User.objects.exclude(id=request.user.id)[:20]
            
    items = []
    if tab == 'all':
        posts_list = list(posts.order_by('-created_at')[:20])
        reels_list = list(reels.order_by('-created_at')[:20])
        for p in posts_list:
            p.is_post = True
        for r in reels_list:
            r.is_reel = True
        items = posts_list + reels_list
        items.sort(key=lambda x: x.created_at, reverse=True)
        
    elif tab == 'photos':
        posts_list = list(posts.filter(media_type='image').order_by('-created_at')[:30])
        for p in posts_list:
            p.is_post = True
        items = posts_list
        
    elif tab == 'videos':
        posts_list = list(posts.filter(media_type='video').order_by('-created_at')[:20])
        reels_list = list(reels.order_by('-created_at')[:20])
        for p in posts_list:
            p.is_post = True
        for r in reels_list:
            r.is_reel = True
        items = posts_list + reels_list
        items.sort(key=lambda x: x.created_at, reverse=True)
        
    elif tab == 'people':
        pass
        
    elif tab == 'tags':
        from django.db.models import Q
        posts_list = list(posts.filter(Q(caption__icontains=q) | Q(posttag__tag__name__icontains=q)).distinct().order_by('-created_at')[:30])
        for p in posts_list:
            p.is_post = True
        items = posts_list

    return render(request, 'social/explore.html', {
        'items': items,
        'users_list': users,
        'q': q,
        'tab': tab
    })

@login_required
def leaderboard_view(request):
    leaderboard = WeeklyLeaderboard.objects.order_by('rank')
    return render(request, 'social/leaderboard.html', {'leaderboard': leaderboard})
