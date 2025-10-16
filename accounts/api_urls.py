from django.urls import path
from . import api_views

urlpatterns = [
    # Authentication endpoints
    path('login/', api_views.LoginAPIView.as_view(), name='api_login'),
    path('logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),
    path('register/', api_views.RegisterAPIView.as_view(), name='api_register'),
    path('profile/', api_views.ProfileAPIView.as_view(), name='api_profile'),
    path('change-password/', api_views.ChangePasswordAPIView.as_view(), name='api_change_password'),
    
    # User management (admin only)
    path('users/', api_views.UserListAPIView.as_view(), name='api_users'),
    path('students/', api_views.StudentListAPIView.as_view(), name='api_students'),
    path('teachers/', api_views.TeacherListAPIView.as_view(), name='api_teachers'),
    path('users/<int:user_id>/toggle-active/', api_views.ToggleUserActiveAPIView.as_view(), name='api_toggle_user_active'),
]
