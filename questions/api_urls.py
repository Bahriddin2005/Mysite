from django.urls import path
from . import api_views

urlpatterns = [
    # Question management endpoints
    path('questions/', api_views.QuestionListAPIView.as_view(), name='question_list'),
    path('questions/<int:pk>/', api_views.QuestionDetailAPIView.as_view(), name='question_detail'),
]
