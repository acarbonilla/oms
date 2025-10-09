from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_widget, name='chat_widget'),
    path('send-message/', views.send_message, name='send_message'),
    path('chat-history/<str:session_id>/', views.get_chat_history, name='get_chat_history'),
    path('sessions/', views.get_user_sessions, name='get_user_sessions'),
    path('new-session/', views.start_new_session, name='start_new_session'),
]
