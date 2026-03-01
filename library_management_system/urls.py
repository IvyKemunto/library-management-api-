"""
URL configuration for library_management_system project.

API Structure:
    /api/v1/books/          - Books management
    /api/v1/users/          - Users management
    /api/v1/transactions/   - Transactions (checkout/return)
    /api/token/             - JWT authentication
    /api-auth/              - Session authentication (browsable API)
    /admin/                 - Django admin
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


def api_root(request):
    """API root endpoint with available endpoints."""
    return JsonResponse({
        'message': 'Welcome to the Library Management System API',
        'version': 'v1',
        'endpoints': {
            'books': '/api/v1/books/',
            'authors': '/api/v1/books/authors/',
            'users': '/api/v1/users/',
            'transactions': '/api/v1/transactions/',
            'authentication': {
                'obtain_token': '/api/token/',
                'refresh_token': '/api/token/refresh/',
                'verify_token': '/api/token/verify/',
            }
        },
        'documentation': {
            'register': 'POST /api/v1/users/register/',
            'login': 'POST /api/token/',
            'profile': 'GET /api/v1/users/profile/',
            'checkout_book': 'POST /api/v1/transactions/checkout/',
            'return_book': 'POST /api/v1/transactions/return/{transaction_id}/',
            'my_transactions': 'GET /api/v1/transactions/my-transactions/',
        }
    })


urlpatterns = [
    # API Root
    path('', api_root, name='api-root'),

    # Admin
    path('admin/', admin.site.urls),

    # API v1 endpoints
    path('api/v1/', include([
        # Books endpoints
        path('books/', include('apps.books.urls')),

        # Users endpoints
        path('users/', include('apps.users.urls')),

        # Transactions endpoints
        path('transactions/', include('apps.transactions.urls')),
    ])),

    # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Session Authentication (DRF browsable API)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
