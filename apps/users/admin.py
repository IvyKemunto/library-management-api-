from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import LibraryUser


@admin.register(LibraryUser)
class LibraryUserAdmin(UserAdmin):
    """Admin configuration for LibraryUser model."""

    list_display = ('username', 'email', 'role', 'is_active', 'date_of_membership', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Library Information', {
            'fields': ('role', 'phone_number', 'address', 'date_of_membership'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Library Information', {
            'fields': ('email', 'role', 'phone_number', 'address'),
        }),
    )

    readonly_fields = ('date_of_membership',)
