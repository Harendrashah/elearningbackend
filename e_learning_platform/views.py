# e_learning_platform/views.py

from django.http import JsonResponse
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
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
            'admin': {
                'all_users': request.build_absolute_uri(reverse('admin-user-list')),
                'user_detail_example': request.build_absolute_uri(reverse('admin-user-detail', kwargs={'id': 1})),
            },
            'courses': request.build_absolute_uri('/api/courses/'),
        }
    })
