"""
Book models for the Library Management System.
"""

from django.db import models
from django.core.validators import MinValueValidator


class Author(models.Model):
    """
    Author model - represents book authors.
    Separate model for normalization and future extensibility.
    """
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Book model with all required fields.

    Fields:
        title: Book title
        author: ForeignKey to Author model
        isbn: Unique 13-character ISBN
        published_date: Date the book was published
        description: Optional book description
        copies_available: Number of copies currently available for checkout
        total_copies: Total copies owned by the library
    """
    title = models.CharField(max_length=300)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books'
    )
    isbn = models.CharField(
        max_length=13,
        unique=True,
        help_text="13-digit ISBN number"
    )
    published_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    copies_available = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)]
    )
    total_copies = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author.name}"

    @property
    def is_available(self):
        """Check if at least one copy is available."""
        return self.copies_available > 0
