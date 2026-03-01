"""
Views for the Transactions app.
"""

from rest_framework import viewsets, generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from apps.core.permissions import IsAdminUser
from apps.core.pagination import StandardResultsSetPagination
from .models import Transaction, Penalty
from .serializers import (
    TransactionSerializer,
    CheckoutSerializer,
    ReturnSerializer,
    UserTransactionSerializer,
    PenaltySerializer,
    PenaltyUpdateSerializer,
)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing all transactions (Admin only).

    GET /api/v1/transactions/ - List all transactions
    GET /api/v1/transactions/{id}/ - Get transaction details
    """
    queryset = Transaction.objects.select_related('user', 'book', 'book__author').all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'transaction_type', 'user']
    search_fields = ['user__username', 'book__title', 'book__isbn']
    ordering_fields = ['checkout_date', 'due_date', 'return_date']
    ordering = ['-checkout_date']


class CheckoutView(generics.CreateAPIView):
    """
    Endpoint for checking out a book.
    Authenticated users (Members and Admins) can checkout books.

    POST /api/v1/transactions/checkout/
    Request body:
    {
        "book_id": 1,
        "loan_days": 14  // optional, default 14
    }
    """
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()
        return Response(
            {
                'message': 'Book checked out successfully.',
                'transaction': TransactionSerializer(transaction).data
            },
            status=status.HTTP_201_CREATED
        )


class ReturnView(APIView):
    """
    Endpoint for returning a book.
    Users can return their own books, Admins can return any book.

    POST /api/v1/transactions/return/{transaction_id}/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        serializer = ReturnSerializer(
            data={},
            context={'request': request, 'transaction_id': transaction_id}
        )
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()

        response_data = {
            'message': 'Book returned successfully.',
            'transaction': TransactionSerializer(transaction).data
        }

        # Include penalty info if applicable
        if hasattr(transaction, 'penalty'):
            response_data['penalty'] = {
                'amount': str(transaction.penalty.amount),
                'status': transaction.penalty.status
            }

        return Response(response_data, status=status.HTTP_200_OK)


class UserTransactionsView(generics.ListAPIView):
    """
    Endpoint for users to view their own transactions (borrowing history).

    GET /api/v1/transactions/my-transactions/
    """
    serializer_class = UserTransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'transaction_type']
    ordering_fields = ['checkout_date', 'due_date']
    ordering = ['-checkout_date']

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).select_related('book', 'book__author')


class ActiveLoansView(generics.ListAPIView):
    """
    Endpoint for users to view their active loans.

    GET /api/v1/transactions/active/
    """
    serializer_class = UserTransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user,
            status__in=['ACTIVE', 'OVERDUE']
        ).select_related('book', 'book__author')


class OverdueListView(generics.ListAPIView):
    """
    List all overdue transactions (Admin only).

    GET /api/v1/transactions/overdue/
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Transaction.objects.filter(
            status__in=['ACTIVE', 'OVERDUE'],
            due_date__lt=timezone.now().date()
        ).select_related('user', 'book', 'book__author')


class PenaltyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing penalties (Admin only).

    GET /api/v1/transactions/penalties/ - List all penalties
    GET /api/v1/transactions/penalties/{id}/ - Get penalty details
    PATCH /api/v1/transactions/penalties/{id}/ - Update penalty status
    """
    queryset = Penalty.objects.select_related(
        'transaction__user',
        'transaction__book',
        'transaction__book__author'
    ).all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['amount', 'created_at']
    ordering = ['-created_at']
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_serializer_class(self):
        if self.action in ['partial_update', 'update']:
            return PenaltyUpdateSerializer
        return PenaltySerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'message': f'Penalty status updated to {instance.status}.',
                'penalty': PenaltySerializer(instance).data
            }
        )


class UserPenaltiesView(generics.ListAPIView):
    """
    Endpoint for users to view their own penalties.

    GET /api/v1/transactions/my-penalties/
    """
    serializer_class = PenaltySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Penalty.objects.filter(
            transaction__user=self.request.user
        ).select_related(
            'transaction__book',
            'transaction__book__author'
        )
