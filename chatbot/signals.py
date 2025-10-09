from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ChatbotConfiguration


@receiver(post_save, sender=User)
def create_default_chatbot_config(sender, instance, created, **kwargs):
    """Create default chatbot configuration when first user is created"""
    if created and not ChatbotConfiguration.objects.exists():
        ChatbotConfiguration.objects.create(
            name='OMS Assistant',
            welcome_message="Hello! I'm your OMS Assistant. How can I help you with operations management today?",
            model_name='microsoft/DialoGPT-medium',
            is_active=True
        )
