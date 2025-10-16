"""
URL configuration for buxoro_test_system project.
Professional test examination system for Buxoro Bilimdonlar Maktabi
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Main website views
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('tests/', include('examinations.urls')),
    path('questions/', include('questions.urls')),
    path('results/', include('results.urls')),
    
    # Django's built-in authentication views
    path('auth/', include('django.contrib.auth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site configuration
admin.site.site_header = "Buxoro Bilimdonlar Maktabi - Test System"
admin.site.site_title = "Test System Admin"
admin.site.index_title = "Test Management System"
admin.site.index_title = "Test Management Dashboard"
