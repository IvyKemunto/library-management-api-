"""
URL configuration for the Transactions app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransactionViewSet,
    CheckoutView,
    ReturnView,
    UserTransactionsView,
    ActiveLoansView,
    OverdueListView,
    PenaltyViewSet,
    UserPenaltiesView,
)

router = DefaultRouter()
router.register(r'penalties', PenaltyViewSet, basename='penalty')
router.register(r'', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('return/<int:transaction_id>/', ReturnView.as_view(), name='return'),
    path('my-transactions/', UserTransactionsView.as_view(), name='my-transactions'),
    path('active/', ActiveLoansView.as_view(), name='active-loans'),
    path('overdue/', OverdueListView.as_view(), name='overdue-list'),
    path('my-penalties/', UserPenaltiesView.as_view(), name='my-penalties'),
    path('', include(router.urls)),
]
