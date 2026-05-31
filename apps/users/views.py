from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileEditForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Follow, MutedAccount, MutedStory, BlockedAccount
from posts.models import Post, Reaction, Reel
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
import json

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('/feed/')
    return render(request, 'landing.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/feed/')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/feed/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/feed/')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/feed/')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def settings_view(request):
    user = request.user
    muted_accounts = MutedAccount.objects.filter(user=user).select_related('muted_user')
    muted_stories = MutedStory.objects.filter(user=user).select_related('muted_user')
    blocked_accounts = BlockedAccount.objects.filter(user=user).select_related('blocked_user')
    return render(request, 'users/settings.html', {
        'user': user,
        'muted_accounts': muted_accounts,
        'muted_stories': muted_stories,
        'blocked_accounts': blocked_accounts,
    })

@login_required
def request_verification(request):
    if request.method == 'POST':
        profile = request.user.profile
        profile.verification_requested = True
        profile.save()
    return redirect('/settings/')

@login_required
def toggle_account_type(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_type = data.get('account_type', 'public')
        if new_type in ['public', 'private']:
            profile = request.user.profile
            profile.account_type = new_type
            profile.save()
            return JsonResponse({'status': 'success', 'account_type': new_type})
    return JsonResponse({'status': 'error'})

@login_required
def mute_user(request, username):
    if request.method == 'POST':
        target = get_object_or_404(User, username=username)
        MutedAccount.objects.get_or_create(user=request.user, muted_user=target)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def unmute_user(request, username):
    if request.method == 'POST':
        target = get_object_or_404(User, username=username)
        MutedAccount.objects.filter(user=request.user, muted_user=target).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def unmute_story(request, username):
    if request.method == 'POST':
        target = get_object_or_404(User, username=username)
        MutedStory.objects.filter(user=request.user, muted_user=target).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def unblock_user(request, username):
    if request.method == 'POST':
        target = get_object_or_404(User, username=username)
        BlockedAccount.objects.filter(user=request.user, blocked_user=target).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def search_users(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'users': []})
    users = User.objects.filter(username__icontains=q).exclude(id=request.user.id)[:15]
    results = []
    for u in users:
        results.append({
            'username': u.username,
            'avatar_url': u.profile.avatar.url if (hasattr(u, 'profile') and u.profile.avatar) else '/static/images/default_avatar.png',
        })
    return JsonResponse({'users': results})

@login_required
def profile_view(request, username):
    target_user = get_object_or_404(User, username=username)
    is_following = Follow.objects.filter(follower=request.user, following=target_user).exists()
    followers_count = Follow.objects.filter(following=target_user).count()
    following_count = Follow.objects.filter(follower=target_user).count()
    
    # Check if we should show posts
    show_posts = True
    if target_user != request.user and target_user.profile.account_type == 'private' and not is_following:
        show_posts = False
        
    posts = target_user.posts.all().order_by('-created_at') if show_posts else []
    reels = target_user.reels.all().order_by('-created_at') if show_posts else []
    
    # Total Yentrowws received
    content_type_post = ContentType.objects.get_for_model(Post)
    post_ids = target_user.posts.values_list('id', flat=True)
    yentrowws_posts = Reaction.objects.filter(content_type=content_type_post, object_id__in=post_ids, reaction_type='yentroww').count()
    
    content_type_reel = ContentType.objects.get_for_model(Reel)
    reel_ids = target_user.reels.values_list('id', flat=True)
    yentrowws_reels = Reaction.objects.filter(content_type=content_type_reel, object_id__in=reel_ids, reaction_type='yentroww').count()
    
    yentrowws_count = yentrowws_posts + yentrowws_reels
    
    return render(request, 'users/profile.html', {
        'target_user': target_user,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'yentrowws_count': yentrowws_count,
        'posts': posts,
        'reels': reels,
        'show_posts': show_posts
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Handle remove avatar
        if request.POST.get('remove_avatar') == '1':
            profile = request.user.profile
            if profile.avatar:
                profile.avatar.delete()
                profile.avatar = None
                profile.save()
            return redirect(f'/profile/{request.user.username}/')
        
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect(f'/profile/{request.user.username}/')
    else:
        form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def followers_list(request, username):
    target_user = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(following=target_user).select_related('follower')
    users = [f.follower for f in follows]
    return render(request, 'users/user_list.html', {'users_list': users, 'title': f"{target_user.username}'s Followers"})

@login_required
def following_list(request, username):
    target_user = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(follower=target_user).select_related('following')
    users = [f.following for f in follows]
    return render(request, 'users/user_list.html', {'users_list': users, 'title': f"{target_user.username} is Following"})

@login_required
def follow_toggle(request, username):
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)
        if target_user == request.user:
            return JsonResponse({'status': 'error'})
            
        follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
        if not created:
            follow.delete()
            action = 'unfollowed'
        else:
            action = 'followed'
            # Create notification logic would go here
            from notifications.models import Notification
            Notification.objects.create(recipient=target_user, sender=request.user, notif_type='follow')
            
        return JsonResponse({'status': 'success', 'action': action})
    return JsonResponse({'status': 'error'})

# --- Activity Views ---
@login_required
def activity_home(request):
    return render(request, 'users/activity.html')

@login_required
def activity_saved(request):
    # Dummy for saved posts since we didn't add Saved model in Step 1, but we can mock it
    return render(request, 'users/activity_sub.html', {'title': 'Saved Posts', 'items': []})

@login_required
def activity_reactions(request, r_type):
    content_type = ContentType.objects.get_for_model(Post)
    reactions = Reaction.objects.filter(user=request.user, content_type=content_type, reaction_type=r_type).order_by('-created_at')
    posts = [r.content_object for r in reactions]
    titles = {'yentroww': 'Yentrowws', 'abboww': 'Abbowws', 'sarlee': 'Sarlees'}
    return render(request, 'users/activity_sub.html', {'title': titles.get(r_type), 'items': posts})

@login_required
def activity_comments(request):
    comments = request.user.comment_set.all().order_by('-created_at')
    posts = list(set([c.post for c in comments if c.post]))
    return render(request, 'users/activity_sub.html', {'title': 'Commented Posts', 'items': posts})

@login_required
def activity_dashboard(request):
    user = request.user
    post_ids = user.posts.values_list('id', flat=True)
    ct = ContentType.objects.get_for_model(Post)
    y_recv = Reaction.objects.filter(content_type=ct, object_id__in=post_ids, reaction_type='yentroww').count()
    a_recv = Reaction.objects.filter(content_type=ct, object_id__in=post_ids, reaction_type='abboww').count()
    s_recv = Reaction.objects.filter(content_type=ct, object_id__in=post_ids, reaction_type='sarlee').count()
    
    # Leaderboard rank
    from social.models import WeeklyLeaderboard
    lb = WeeklyLeaderboard.objects.filter(user=user).first()
    rank = lb.rank if lb else None
    
    stats = {
        'posts': user.posts.count(),
        'reels': user.reels.count(),
        'stories': user.stories.count(),
        'y_recv': y_recv,
        'a_recv': a_recv,
        's_recv': s_recv,
        'rank': rank
    }
    return render(request, 'users/dashboard.html', {'stats': stats})
