# excerpt/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.chatbot_view, name='chatbot_view'),
    path('chatbot/api', views.chatbot_api, name='chatbot_api'),
    path('transcript/', views.TextTranscript.as_view(), name='text_transcript'),
    path('chatdata/', views.ChatSystem.as_view(), name='chat_system'),
    path('bot/', views.ChatBot.as_view(), name='chat_bot'),
]
