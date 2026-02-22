import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ChatSession, ChatMessage
from .services import get_ai_response


@login_required
def chat_home(request):
    sessions = ChatSession.objects.filter(user=request.user)
    if request.method == 'POST':
        session = ChatSession.objects.create(user=request.user)
        return redirect('chat_session', session_id=session.pk)
    return render(request, 'ai_advisor/chat_home.html', {'sessions': sessions})


@login_required
def chat_session_view(request, session_id):
    session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
    chat_messages = session.messages.order_by('created_at')
    all_sessions = ChatSession.objects.filter(user=request.user)

    profile = None
    try:
        profile = request.user.userprofile
    except Exception:
        pass

    return render(request, 'ai_advisor/chat_session.html', {
        'session': session,
        'chat_messages': chat_messages,
        'all_sessions': all_sessions,
        'profile': profile,
    })


@login_required
@require_POST
def send_message(request, session_id):
    session = get_object_or_404(ChatSession, pk=session_id, user=request.user)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except Exception:
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Message is empty.'}, status=400)

    if len(user_message) > 2000:
        return JsonResponse({'error': 'Message too long (max 2000 chars).'}, status=400)

    # Save user message
    ChatMessage.objects.create(session=session, role='user', content=user_message)

    # Auto-title session on first message
    if session.messages.count() == 1:
        session.title = user_message[:60] + ('…' if len(user_message) > 60 else '')
        session.save()

    # Get profile for personalised context
    profile = None
    try:
        profile = request.user.userprofile
    except Exception:
        pass

    ai_text = get_ai_response(session, user_message, profile)
    ChatMessage.objects.create(session=session, role='assistant', content=ai_text)
    session.save()  # bump updated_at

    return JsonResponse({
        'response': ai_text,
        'session_title': session.title,
    })


@login_required
@require_POST
def delete_session(request, session_id):
    session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
    session.delete()
    return redirect('chat_home')


@login_required
@require_POST
def clear_session(request, session_id):
    session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
    session.messages.all().delete()
    session.title = 'New Chat'
    session.save()
    return redirect('chat_session', session_id=session.pk)
