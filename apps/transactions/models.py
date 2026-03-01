"""
Transaction models for the Library Management System.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class Transaction(models.Model):
    """
    Transaction model for tracking book checkouts and returns.

    Transaction Types:
        CHECKOUT: Book borrowed by user
        RETURN: Book returned by user

    Status:
        ACTIVE: Book is currently checked out
        RETURNED: Book has been returned
        OVERDUE: Book is overdue (past due_date)
    """
    TRANSACTION_TYPE_CHOICES = [
        ('CHECKOUT', 'Checkout'),
        ('RETURN', 'Return'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    checkout_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-checkout_date']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['book', 'status']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.transaction_type})"

    @property
    def is_overdue(self):
        """Check if the transaction is overdue."""
        if self.status == 'RETURNED':
            return False
        return timezone.now().date() > self.due_date

    def calculate_penalty(self, penalty_per_day=None):
        """
        Calculate penalty for overdue books.
        Default: Uses PENALTY_PER_DAY from settings or $1.00 per day overdue.
        """
        if not self.is_overdue:
            return Decimal('0.00')

        if penalty_per_day is None:
            penalty_per_day = Decimal(str(getattr(settings, 'PENALTY_PER_DAY', 1.00)))

        days_overdue = (timezone.now().date() - self.due_date).days
        return penalty_per_day * days_overdue

    def save(self, *args, **kwargs):
        """Update status to OVERDUE if past due date."""
        if self.status == 'ACTIVE' and self.is_overdue:
            self.status = 'OVERDUE'
        super().save(*args, **kwargs)


class Penalty(models.Model):
    """
    Penalty model for tracking fines.

    Links to a transaction and tracks payment status.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('WAIVED', 'Waived'),
    ]

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='penalty'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    paid_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Penalty'
        verbose_name_plural = 'Penalties'
        ordering = ['-created_at']

    def __str__(self):
        return f"Penalty: ${self.amount} - {self.status} ({self.transaction.user.username})"

    def mark_as_paid(self):
        """Mark the penalty as paid."""
        self.status = 'PAID'
        self.paid_date = timezone.now()
        self.save()

    def waive(self):
        """Waive the penalty."""
        self.status = 'WAIVED'
        self.save()
