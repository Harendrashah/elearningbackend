# e_learning_platform/views.py

from django.http import JsonResponse
from django.urls import reverse
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_root(request, format=None):
    """
    A simple API Root view to provide navigation links.
    """
    return JsonResponse({
        'message': 'Welcome to the E-Learning Platform API!',
        'endpoints': {
            'auth': {
                'register': request.build_absolute_uri(reverse('register')),
                'login': request.build_absolute_uri(reverse('login')),
                'profile': request.build_absolute_uri(reverse('user-profile')),
            },
            # We will add more endpoints here as we build them
            # 'courses': request.build_absolute_uri('/api/courses/'),
        }
    })