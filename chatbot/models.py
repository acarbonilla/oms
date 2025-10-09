from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatSession(models.Model):
    """Model to track chat sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chat Session {self.session_id} - {self.user.username}"


class ChatMessage(models.Model):
    """Model to store chat messages"""
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."


class ChatbotConfiguration(models.Model):
    """Model to store chatbot configuration"""
    name = models.CharField(max_length=100, default='OMS Assistant')
    welcome_message = models.TextField(
        default="Hi there! 👋 I'm your OMS Assistant. Click 'Quick Questions' below for common tasks, or ask me anything about facilities, activities, and reports!"
    )
    model_name = models.CharField(
        max_length=100, 
        default='llama-3.3-70b-versatile',
        help_text='Groq model name (e.g., llama-3.3-70b-versatile, mixtral-8x7b-32768)'
    )
    max_response_length = models.IntegerField(default=500)
    temperature = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.model_name}"