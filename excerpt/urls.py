from django.urls import re_path as url
from . import views
from django.urls import path

urlpatterns = [

    path('', views.chatbot_view, name='chatbot'),
    path('predict/', views.predict_view, name='predict'),
    url(r'transcript', views.TextTranscript.as_view(), name=None),
    url(r'chatdata', views.ChatSystem.as_view(), name=None),
    url(r'bot', views.ChatBot.as_view(), name=None)
]