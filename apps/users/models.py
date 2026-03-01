"""
User models for the Library Management System.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    """Custom user manager for LibraryUser model."""

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class LibraryUser(AbstractUser):
    """
    Custom User model extending AbstractUser.

    Fields:
        username: Inherited from AbstractUser (unique)
        email: Required email field (unique)
        date_of_membership: Auto-set on user creation
        is_active: Active status (inherited, repurposed for library membership)
        role: User role (Admin or Member)
        phone_number: Optional phone number
        address: Optional address
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
    ]

    email = models.EmailField(unique=True)
    date_of_membership = models.DateField(auto_now_add=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='MEMBER'
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    objects = CustomUserManager()

    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'Library User'
        verbose_name_plural = 'Library Users'

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'ADMIN'

    @property
    def is_member(self):
        """Check if user is a member."""
        return self.role == 'MEMBER'
