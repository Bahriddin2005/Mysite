from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import TestResultViewSet, CertificateViewSet, UserProgressViewSet

router = DefaultRouter()
router.register(r'results', TestResultViewSet, basename='testresult')
router.register(r'certificates', CertificateViewSet, basename='certificate')
router.register(r'progress', UserProgressViewSet, basename='userprogress')

urlpatterns = [
    path('', include(router.urls)),
]
