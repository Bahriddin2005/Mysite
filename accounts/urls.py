from django.urls import path
from . import views

urlpatterns = [
    # User registration and authentication
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # API placeholder
    path('api/', views.placeholder_view, name='accounts_api'),
]
