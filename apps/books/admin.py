from django.contrib import admin
from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin configuration for Author model."""

    list_display = ('name', 'date_of_birth', 'books_count', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

    def books_count(self, obj):
        return obj.books.count()
    books_count.short_description = 'Number of Books'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin configuration for Book model."""

    list_display = (
        'title', 'author', 'isbn', 'published_date',
        'copies_available', 'total_copies', 'is_available'
    )
    list_filter = ('author', 'published_date')
    search_fields = ('title', 'isbn', 'author__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn', 'published_date', 'description')
        }),
        ('Availability', {
            'fields': ('total_copies', 'copies_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_available(self, obj):
        return obj.is_available
    is_available.boolean = True
    is_available.short_description = 'Available'
