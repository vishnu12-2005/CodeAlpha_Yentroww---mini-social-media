from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Conversation, Message
from django.contrib.auth.models import User
import json

@login_required
def dm_list(request):
    conversations = request.user.conversations.all().order_by('-created_at')
    return render(request, 'messaging/dm_list.html', {'conversations': conversations})

@login_required
def chat_view(request, conv_id):
    conversation = get_object_or_404(Conversation, id=conv_id, participants=request.user)
    other_user = conversation.participants.exclude(id=request.user.id).first()
    messages = conversation.messages.all().order_by('created_at')
    return render(request, 'messaging/chat.html', {'conversation': conversation, 'other_user': other_user, 'messages': messages})

@login_required
def send_message(request, conv_id):
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conv_id, participants=request.user)
        data = json.loads(request.body)
        text = data.get('text', '')
        if text:
            msg = Message.objects.create(conversation=conversation, sender=request.user, text=text)
            return JsonResponse({
                'status': 'success',
                'id': msg.id,
                'text': msg.text,
                'sender_id': msg.sender.id,
                'timestamp': msg.created_at.strftime('%I:%M %p')
            })
    return JsonResponse({'status': 'error'})

@login_required
def mark_seen(request, conv_id):
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conv_id, participants=request.user)
        conversation.messages.exclude(sender=request.user).update(is_seen=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def poll_messages(request, conv_id):
    conversation = get_object_or_404(Conversation, id=conv_id, participants=request.user)
    after_id = request.GET.get('after', 0)
    new_msgs = conversation.messages.filter(id__gt=after_id).order_by('created_at')
    
    msgs_data = []
    for msg in new_msgs:
        msgs_data.append({
            'id': msg.id,
            'text': msg.text,
            'sender_id': msg.sender.id,
            'timestamp': msg.created_at.strftime('%I:%M %p')
        })
    return JsonResponse({'status': 'success', 'messages': msgs_data})

@login_required
def start_dm(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return redirect('/messages/')
        
    convs = Conversation.objects.filter(participants=request.user).filter(participants=target_user)
    if convs.exists():
        conv = convs.first()
    else:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, target_user)
    return redirect(f'/messages/{conv.id}/')
