from django.urls import path
from . import views

# Temporary simple URLs - will be replaced with DRF URLs
urlpatterns = [
    path('', views.placeholder_view, name='results_api'),
]
