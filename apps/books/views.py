"""
Views for the Books app.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsAdminOrReadOnly
from apps.core.pagination import StandardResultsSetPagination
from .models import Book, Author
from .serializers import (
    BookSerializer,
    BookDetailSerializer,
    BookListSerializer,
    AuthorSerializer,
    AuthorListSerializer,
)
from .filters import BookFilter


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Book CRUD operations.

    Permissions:
        - List/Retrieve: Any authenticated user
        - Create/Update/Delete: Admin only

    Features:
        - Filtering by title, author, ISBN
        - Search across title, author name
        - Ordering by title, published_date
        - Pagination

    Endpoints:
        GET /api/v1/books/ - List all books
        POST /api/v1/books/ - Create a new book (Admin)
        GET /api/v1/books/{id}/ - Retrieve a book
        PUT /api/v1/books/{id}/ - Update a book (Admin)
        PATCH /api/v1/books/{id}/ - Partial update (Admin)
        DELETE /api/v1/books/{id}/ - Delete a book (Admin)
        GET /api/v1/books/available/ - List available books only
    """
    queryset = Book.objects.select_related('author').all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'author__name', 'isbn']
    ordering_fields = ['title', 'published_date', 'created_at', 'copies_available']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        List only available books (copies_available > 0).

        GET /api/v1/books/available/
        """
        available_books = self.filter_queryset(
            self.queryset.filter(copies_available__gt=0)
        )
        page = self.paginate_queryset(available_books)
        if page is not None:
            serializer = BookListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = BookListSerializer(available_books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unavailable(self, request):
        """
        List only unavailable books (copies_available = 0).

        GET /api/v1/books/unavailable/
        """
        unavailable_books = self.filter_queryset(
            self.queryset.filter(copies_available=0)
        )
        page = self.paginate_queryset(unavailable_books)
        if page is not None:
            serializer = BookListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = BookListSerializer(unavailable_books, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def borrowers(self, request, pk=None):
        """
        List current borrowers of a specific book (Admin only).

        GET /api/v1/books/{id}/borrowers/
        """
        if not request.user.is_admin:
            return Response(
                {'detail': 'Only admins can view borrower information.'},
                status=status.HTTP_403_FORBIDDEN
            )

        book = self.get_object()
        from apps.transactions.models import Transaction
        from apps.transactions.serializers import TransactionSerializer

        active_transactions = Transaction.objects.filter(
            book=book,
            status__in=['ACTIVE', 'OVERDUE']
        ).select_related('user')

        serializer = TransactionSerializer(active_transactions, many=True)
        return Response(serializer.data)


class AuthorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Author CRUD operations.

    Permissions:
        - List/Retrieve: Any authenticated user
        - Create/Update/Delete: Admin only

    Endpoints:
        GET /api/v1/books/authors/ - List all authors
        POST /api/v1/books/authors/ - Create a new author (Admin)
        GET /api/v1/books/authors/{id}/ - Retrieve an author
        PUT /api/v1/books/authors/{id}/ - Update an author (Admin)
        DELETE /api/v1/books/authors/{id}/ - Delete an author (Admin)
    """
    queryset = Author.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return AuthorListSerializer
        return AuthorSerializer

    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """
        List all books by a specific author.

        GET /api/v1/books/authors/{id}/books/
        """
        author = self.get_object()
        books = author.books.all()
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = BookListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)
