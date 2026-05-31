from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification
from django.utils import timezone
from datetime import timedelta

@login_required
def notifications_view(request):
    notifs = request.user.notifications.all().order_by('-created_at')
    
    today = timezone.now().date()
    
    today_notifs = []
    week_notifs = []
    earlier_notifs = []
    
    for n in notifs:
        ndate = n.created_at.date()
        if ndate == today:
            today_notifs.append(n)
        elif ndate > today - timedelta(days=7):
            week_notifs.append(n)
        else:
            earlier_notifs.append(n)
            
    return render(request, 'notifications/notifications.html', {
        'today_notifs': today_notifs,
        'week_notifs': week_notifs,
        'earlier_notifs': earlier_notifs
    })

@login_required
def read_notification(request, id):
    if request.method == 'POST':
        notif = get_object_or_404(Notification, id=id, recipient=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def read_all_notifications(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def poll_notifications(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'status': 'success', 'unread_count': count})
