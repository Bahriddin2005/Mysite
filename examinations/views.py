from django.shortcuts import render
from django.http import JsonResponse

def placeholder_view(request):
    """Placeholder view for development"""
    return JsonResponse({'message': 'Examinations API placeholder'})

# Create your views here.
