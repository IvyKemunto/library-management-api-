"""
Serializers for the Books app.
"""

from rest_framework import serializers
from .models import Book, Author


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author model."""
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id', 'name', 'biography', 'date_of_birth',
            'books_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'books_count']

    def get_books_count(self, obj):
        return obj.books.count()


class AuthorListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Author list views."""

    class Meta:
        model = Author
        fields = ['id', 'name']


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model."""
    author_name = serializers.CharField(source='author.name', read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'author_name', 'isbn',
            'published_date', 'description', 'copies_available',
            'total_copies', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_available']

    def validate_isbn(self, value):
        """Validate ISBN format (13 digits)."""
        if not value.isdigit() or len(value) != 13:
            raise serializers.ValidationError(
                "ISBN must be exactly 13 digits."
            )
        return value

    def validate(self, data):
        """Validate copies_available does not exceed total_copies."""
        copies_available = data.get('copies_available')
        total_copies = data.get('total_copies')

        # Handle update case where we might not have all fields
        if self.instance:
            copies_available = copies_available if copies_available is not None else self.instance.copies_available
            total_copies = total_copies if total_copies is not None else self.instance.total_copies

        if copies_available is not None and total_copies is not None:
            if copies_available > total_copies:
                raise serializers.ValidationError({
                    'copies_available': 'Cannot exceed total copies.'
                })
        return data


class BookDetailSerializer(BookSerializer):
    """Extended serializer with nested author details."""
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        source='author',
        write_only=True
    )

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ['author_id']


class BookListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Book list views."""
    author_name = serializers.CharField(source='author.name', read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author_name', 'isbn',
            'published_date', 'copies_available', 'is_available'
        ]
