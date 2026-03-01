from django.contrib import admin
from .models import Transaction, Penalty


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin configuration for Transaction model."""

    list_display = (
        'id', 'user', 'book', 'transaction_type', 'status',
        'checkout_date', 'due_date', 'return_date', 'is_overdue'
    )
    list_filter = ('transaction_type', 'status', 'checkout_date', 'due_date')
    search_fields = ('user__username', 'book__title', 'book__isbn')
    ordering = ('-checkout_date',)
    readonly_fields = ('checkout_date', 'created_at', 'updated_at')

    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'book', 'transaction_type', 'status')
        }),
        ('Dates', {
            'fields': ('checkout_date', 'due_date', 'return_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    """Admin configuration for Penalty model."""

    list_display = (
        'id', 'transaction', 'amount', 'status', 'paid_date', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'transaction__user__username',
        'transaction__book__title'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Penalty Details', {
            'fields': ('transaction', 'amount', 'status', 'paid_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_paid', 'waive_penalties']

    @admin.action(description='Mark selected penalties as paid')
    def mark_as_paid(self, request, queryset):
        for penalty in queryset:
            penalty.mark_as_paid()
        self.message_user(request, f'{queryset.count()} penalties marked as paid.')

    @admin.action(description='Waive selected penalties')
    def waive_penalties(self, request, queryset):
        for penalty in queryset:
            penalty.waive()
        self.message_user(request, f'{queryset.count()} penalties waived.')
