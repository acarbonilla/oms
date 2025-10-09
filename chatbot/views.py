import json
import uuid
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import ChatSession, ChatMessage, ChatbotConfiguration
from .ai_service import ai_service


@login_required
def chat_widget(request):
    """Render the chat widget page"""
    # Get or create chatbot configuration
    config, created = ChatbotConfiguration.objects.get_or_create(
        id=1,
        defaults={
            'name': 'OMS Assistant',
            'welcome_message': "Hi there! 👋 I'm your OMS Assistant. Click 'Quick Questions' below for common tasks, or ask me anything about facilities, activities, and reports!",
            'model_name': 'llama-3.3-70b-versatile',
            'is_active': True
        }
    )
    
    context = {
        'chatbot_config': config,
        'user': request.user
    }
    return render(request, 'chatbot/chat_widget.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def send_message(request):
    """Handle sending messages to the chatbot"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create chat session
        if session_id:
            chat_session = get_object_or_404(ChatSession, session_id=session_id, user=request.user)
        else:
            session_id = str(uuid.uuid4())
            chat_session = ChatSession.objects.create(
                user=request.user,
                session_id=session_id
            )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='user',
            content=message
        )
        
        # Get conversation history for context
        recent_messages = ChatMessage.objects.filter(
            session=chat_session
        ).order_by('-timestamp')[:10]
        
        conversation_history = [
            {
                'message_type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in recent_messages
        ]
        
        # Prepare user context
        user_groups = [group.name for group in request.user.groups.all()]
        
        # Determine user's region based on groups
        region = None
        if any('_D' in group for group in user_groups):
            region = 'Danao'
        elif any('_M' in group for group in user_groups):
            region = 'Mindanao'
        else:
            region = 'C2'
        
        user_context = {
            'user_groups': user_groups,
            'region': region,
            'user_id': request.user.id,
            'username': request.user.username
        }
        
        # Generate AI response with user context
        try:
            ai_response = ai_service.generate_response(message, conversation_history, user_context)
        except Exception as ai_error:
            print(f"AI service error: {str(ai_error)}")
            # Fallback response
            ai_response = f"I understand you're asking about: '{message}'. Let me help you with that. Could you please rephrase your question or try asking about facilities, activities, or reports?"
        
        # Ensure we have a response
        if not ai_response or len(ai_response.strip()) < 10:
            ai_response = "I'm here to help with your OMS operations. You can ask me about facilities, technical activities, quality assessments, or reports. How can I assist you?"
        
        # Save bot response
        bot_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='bot',
            content=ai_response
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'bot_response': ai_response,
            'user_message': message,
            'timestamp': bot_message.timestamp.isoformat()
        })
        
    except Exception as e:
        print(f"Chatbot view error: {str(e)}")
        # Return a helpful error message instead of 500
        return JsonResponse({
            'success': False,
            'bot_response': "I'm experiencing some technical difficulties right now. Please try asking your question again, or contact support if the issue persists.",
            'error': 'Temporary service issue'
        }, status=200)


@login_required
@require_http_methods(["GET"])
def get_chat_history(request, session_id):
    """Get chat history for a specific session"""
    try:
        chat_session = get_object_or_404(ChatSession, session_id=session_id, user=request.user)
        
        messages = ChatMessage.objects.filter(
            session=chat_session
        ).order_by('timestamp')
        
        message_list = [
            {
                'id': msg.id,
                'message_type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'is_read': msg.is_read
            }
            for msg in messages
        ]
        
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'messages': message_list
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error retrieving chat history: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_user_sessions(request):
    """Get all chat sessions for the current user"""
    try:
        sessions = ChatSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-updated_at')[:10]  # Last 10 sessions
        
        session_list = [
            {
                'session_id': session.session_id,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'message_count': session.messages.count()
            }
            for session in sessions
        ]
        
        return JsonResponse({
            'success': True,
            'sessions': session_list
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error retrieving sessions: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def start_new_session(request):
    """Start a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        chat_session = ChatSession.objects.create(
            user=request.user,
            session_id=session_id
        )
        
        # Get chatbot configuration
        config = ChatbotConfiguration.objects.first()
        welcome_message = config.welcome_message if config else "Hello! How can I help you today?"
        
        # Create welcome message
        welcome_msg = ChatMessage.objects.create(
            session=chat_session,
            message_type='bot',
            content=welcome_message
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'welcome_message': welcome_message,
            'timestamp': welcome_msg.timestamp.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error creating new session: {str(e)}'
        }, status=500)