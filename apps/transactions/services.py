"""
Email notification services for the Library Management System.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


def send_checkout_confirmation(transaction):
    """Send email confirmation when a book is checked out."""
    subject = f'Library: Book Checkout Confirmation - {transaction.book.title}'
    message = f"""
Dear {transaction.user.first_name or transaction.user.username},

You have successfully checked out:

Book: {transaction.book.title}
Author: {transaction.book.author.name}
Checkout Date: {transaction.checkout_date.strftime('%Y-%m-%d %H:%M')}
Due Date: {transaction.due_date}

Please return the book by the due date to avoid penalties.

Thank you for using our library services!

Best regards,
Library Management System
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[transaction.user.email],
        fail_silently=True,
    )


def send_return_confirmation(transaction):
    """Send email confirmation when a book is returned."""
    subject = f'Library: Book Return Confirmation - {transaction.book.title}'

    # Check if there was a penalty
    penalty_info = ""
    if hasattr(transaction, 'penalty'):
        penalty_info = f"""
Penalty Information:
Amount: ${transaction.penalty.amount}
Status: {transaction.penalty.status}
"""

    message = f"""
Dear {transaction.user.first_name or transaction.user.username},

You have successfully returned:

Book: {transaction.book.title}
Return Date: {transaction.return_date.strftime('%Y-%m-%d %H:%M')}
{penalty_info}
Thank you for using our library services!

Best regards,
Library Management System
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[transaction.user.email],
        fail_silently=True,
    )


def send_overdue_notification(transaction):
    """Send notification for overdue books."""
    days_overdue = (timezone.now().date() - transaction.due_date).days
    penalty = transaction.calculate_penalty()

    subject = f'Library: Overdue Book Notice - {transaction.book.title}'
    message = f"""
Dear {transaction.user.first_name or transaction.user.username},

This is a reminder that the following book is overdue:

Book: {transaction.book.title}
Author: {transaction.book.author.name}
Due Date: {transaction.due_date}
Days Overdue: {days_overdue}
Current Penalty: ${penalty}

Please return the book as soon as possible to avoid additional penalties.

Penalty Rate: ${settings.PENALTY_PER_DAY} per day

Best regards,
Library Management System
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[transaction.user.email],
        fail_silently=True,
    )


def send_book_available_notification(user, book):
    """Notify user when a previously unavailable book becomes available."""
    subject = f'Library: Book Now Available - {book.title}'
    message = f"""
Dear {user.first_name or user.username},

Good news! The book you were interested in is now available:

Book: {book.title}
Author: {book.author.name}
Available Copies: {book.copies_available}

Visit the library or use our API to check it out before it's gone!

Best regards,
Library Management System
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def send_due_date_reminder(transaction, days_until_due=3):
    """Send reminder when book is due soon."""
    subject = f'Library: Book Due Soon - {transaction.book.title}'
    message = f"""
Dear {transaction.user.first_name or transaction.user.username},

This is a friendly reminder that the following book is due soon:

Book: {transaction.book.title}
Author: {transaction.book.author.name}
Due Date: {transaction.due_date}
Days Until Due: {days_until_due}

Please return the book by the due date to avoid penalties.

Best regards,
Library Management System
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[transaction.user.email],
        fail_silently=True,
    )
