from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('predict/', views.predict_view, name='predict'),  # URL for predict endpoint
]
