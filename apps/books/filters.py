"""
Filter classes for the Books app.
"""

import django_filters
from .models import Book


class BookFilter(django_filters.FilterSet):
    """
    FilterSet for Book model.

    Filters:
        - title: Contains search (case-insensitive)
        - author: Filter by author name (contains)
        - isbn: Exact match
        - published_date: Range filtering
        - available: Boolean filter for availability
    """
    title = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(
        field_name='author__name',
        lookup_expr='icontains'
    )
    isbn = django_filters.CharFilter(lookup_expr='exact')
    published_after = django_filters.DateFilter(
        field_name='published_date',
        lookup_expr='gte'
    )
    published_before = django_filters.DateFilter(
        field_name='published_date',
        lookup_expr='lte'
    )
    available = django_filters.BooleanFilter(
        method='filter_available'
    )

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'published_after', 'published_before', 'available']

    def filter_available(self, queryset, name, value):
        """Filter books by availability."""
        if value:
            return queryset.filter(copies_available__gt=0)
        return queryset.filter(copies_available=0)
