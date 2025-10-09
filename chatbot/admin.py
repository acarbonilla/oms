from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from .models import ChatSession, ChatMessage, ChatbotConfiguration
from .training_service import training_service


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp', 'quality_score']
    list_filter = ['message_type', 'is_read', 'timestamp']
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def quality_score(self, obj):
        if obj.message_type == 'bot':
            # Calculate quality score for bot messages
            # Get the previous user message
            prev_message = obj.session.messages.filter(
                message_type='user',
                timestamp__lt=obj.timestamp
            ).order_by('-timestamp').first()
            
            if prev_message:
                score = training_service._calculate_response_quality(prev_message.content, obj.content)
                color = 'green' if score >= 0.7 else 'orange' if score >= 0.5 else 'red'
                return format_html('<span style="color: {};">{:.2f}</span>', color, score)
        return '-'
    quality_score.short_description = 'Quality'


@admin.register(ChatbotConfiguration)
class ChatbotConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_name', 'is_active', 'created_at', 'training_actions']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def training_actions(self, obj):
        """Add training action buttons"""
        train_url = reverse('admin:chatbot_train_ai')
        stats_url = reverse('admin:chatbot_training_stats')
        return format_html(
            '<a class="button" href="{}">Train AI</a> '
            '<a class="button" href="{}">Stats</a>',
            train_url, stats_url
        )
    training_actions.short_description = 'Training Actions'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('train-ai/', self.train_ai_view, name='chatbot_train_ai'),
            path('training-stats/', self.training_stats_view, name='chatbot_training_stats'),
        ]
        return custom_urls + urls
    
    def train_ai_view(self, request):
        """Admin view for training AI"""
        if request.method == 'POST':
            try:
                # Collect training data
                conversation_data = training_service.collect_conversation_data(days=30)
                
                if not conversation_data:
                    messages.error(request, "No conversation data found. Start using the chatbot first!")
                    return redirect('..')
                
                # Create dataset and train
                dataset = training_service.create_training_dataset(conversation_data)
                model_path = training_service.fine_tune_model(dataset)
                
                # Evaluate model
                evaluation_results = training_service.evaluate_model_performance(model_path)
                avg_score = evaluation_results['average_quality_score']
                
                messages.success(
                    request, 
                    f"AI training completed! Model saved to: {model_path}. Average quality score: {avg_score:.3f}"
                )
                
            except Exception as e:
                messages.error(request, f"Training failed: {str(e)}")
            
            return redirect('..')
        
        # Show training form
        stats = training_service.get_training_statistics()
        context = {
            'title': 'Train AI Chatbot',
            'stats': stats,
        }
        
        from django.shortcuts import render
        return render(request, 'admin/chatbot/train_ai.html', context)
    
    def training_stats_view(self, request):
        """Admin view for training statistics"""
        stats = training_service.get_training_statistics()
        context = {
            'title': 'AI Training Statistics',
            'stats': stats,
        }
        
        from django.shortcuts import render
        return render(request, 'admin/chatbot/training_stats.html', context)