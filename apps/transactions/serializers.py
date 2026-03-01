"""
Serializers for the Transactions app.
"""

from rest_framework import serializers
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Transaction, Penalty
from apps.books.models import Book


class TransactionSerializer(serializers.ModelSerializer):
    """Full transaction serializer."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    penalty_amount = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_username', 'user_email',
            'book', 'book_title', 'book_isbn',
            'transaction_type', 'status', 'checkout_date', 'due_date',
            'return_date', 'is_overdue', 'penalty_amount', 'days_until_due',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'checkout_date', 'return_date', 'created_at',
            'updated_at', 'is_overdue', 'penalty_amount', 'days_until_due'
        ]

    def get_penalty_amount(self, obj):
        """Get current or calculated penalty amount."""
        if hasattr(obj, 'penalty'):
            return str(obj.penalty.amount)
        return str(obj.calculate_penalty())

    def get_days_until_due(self, obj):
        """Get days until due date (negative if overdue)."""
        if obj.status == 'RETURNED':
            return None
        days = (obj.due_date - timezone.now().date()).days
        return days


class CheckoutSerializer(serializers.Serializer):
    """Serializer for checkout action."""
    book_id = serializers.IntegerField()
    loan_days = serializers.IntegerField(
        default=14,
        min_value=1,
        max_value=30,
        help_text="Number of days for the loan (1-30)"
    )

    def validate_book_id(self, value):
        """Validate that the book exists and is available."""
        try:
            book = Book.objects.get(id=value)
            if not book.is_available:
                raise serializers.ValidationError(
                    "This book is not available. All copies are currently checked out."
                )
            return value
        except Book.DoesNotExist:
            raise serializers.ValidationError("Book not found.")

    def validate(self, attrs):
        """Check if user already has this book checked out."""
        user = self.context['request'].user
        book_id = attrs.get('book_id')

        existing = Transaction.objects.filter(
            user=user,
            book_id=book_id,
            status__in=['ACTIVE', 'OVERDUE']
        ).exists()

        if existing:
            raise serializers.ValidationError({
                'book_id': "You already have this book checked out."
            })

        return attrs

    def create(self, validated_data):
        """Create a checkout transaction."""
        from .services import send_checkout_confirmation

        user = self.context['request'].user
        book = Book.objects.get(id=validated_data['book_id'])
        loan_days = validated_data.get('loan_days', getattr(settings, 'LOAN_PERIOD_DAYS', 14))

        # Create transaction
        transaction = Transaction.objects.create(
            user=user,
            book=book,
            transaction_type='CHECKOUT',
            status='ACTIVE',
            due_date=timezone.now().date() + timedelta(days=loan_days)
        )

        # Decrease available copies
        book.copies_available -= 1
        book.save()

        # Send confirmation email
        send_checkout_confirmation(transaction)

        return transaction


class ReturnSerializer(serializers.Serializer):
    """Serializer for return action."""

    def validate(self, attrs):
        """Validate the transaction can be returned."""
        transaction_id = self.context.get('transaction_id')
        user = self.context['request'].user

        try:
            transaction = Transaction.objects.select_related('book', 'user').get(id=transaction_id)
        except Transaction.DoesNotExist:
            raise serializers.ValidationError("Transaction not found.")

        # Only owner or admin can return
        if not user.is_admin and transaction.user != user:
            raise serializers.ValidationError(
                "You can only return your own books."
            )

        if transaction.status == 'RETURNED':
            raise serializers.ValidationError(
                "This book has already been returned."
            )

        self.transaction = transaction
        return attrs

    def save(self):
        """Process the book return."""
        from .services import send_return_confirmation

        transaction = self.transaction

        # Update transaction
        transaction.status = 'RETURNED'
        transaction.return_date = timezone.now()
        transaction.save()

        # Increase available copies
        transaction.book.copies_available += 1
        transaction.book.save()

        # Create penalty if overdue
        if transaction.is_overdue:
            Penalty.objects.create(
                transaction=transaction,
                amount=transaction.calculate_penalty()
            )

        # Send confirmation email
        send_return_confirmation(transaction)

        return transaction


class UserTransactionSerializer(serializers.ModelSerializer):
    """Simplified transaction serializer for user's own transactions."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author.name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    penalty_amount = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'book_title', 'book_author', 'transaction_type',
            'status', 'checkout_date', 'due_date', 'return_date',
            'is_overdue', 'penalty_amount'
        ]

    def get_penalty_amount(self, obj):
        if hasattr(obj, 'penalty'):
            return str(obj.penalty.amount)
        if obj.is_overdue:
            return str(obj.calculate_penalty())
        return "0.00"


class PenaltySerializer(serializers.ModelSerializer):
    """Serializer for penalties."""
    transaction_id = serializers.IntegerField(source='transaction.id', read_only=True)
    book_title = serializers.CharField(source='transaction.book.title', read_only=True)
    book_isbn = serializers.CharField(source='transaction.book.isbn', read_only=True)
    user_username = serializers.CharField(source='transaction.user.username', read_only=True)
    user_email = serializers.CharField(source='transaction.user.email', read_only=True)
    checkout_date = serializers.DateTimeField(source='transaction.checkout_date', read_only=True)
    due_date = serializers.DateField(source='transaction.due_date', read_only=True)
    return_date = serializers.DateTimeField(source='transaction.return_date', read_only=True)

    class Meta:
        model = Penalty
        fields = [
            'id', 'transaction_id', 'book_title', 'book_isbn',
            'user_username', 'user_email', 'checkout_date', 'due_date',
            'return_date', 'amount', 'status', 'paid_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'amount', 'created_at', 'updated_at'
        ]


class PenaltyUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating penalty status."""

    class Meta:
        model = Penalty
        fields = ['status']

    def update(self, instance, validated_data):
        new_status = validated_data.get('status', instance.status)

        if new_status == 'PAID' and instance.status != 'PAID':
            instance.mark_as_paid()
        elif new_status == 'WAIVED' and instance.status != 'WAIVED':
            instance.waive()
        else:
            instance.status = new_status
            instance.save()

        return instance
