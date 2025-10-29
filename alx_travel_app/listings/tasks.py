# listings/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Payment
from django.utils.html import strip_tags
from .models import Booking
import uuid

@shared_task
def send_payment_confirmation_email(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return {"status": "error", "detail": "payment not found"}

    # Compose email
    subject = f"Payment Confirmation — {payment.booking_reference}"
    to_email = payment.user.email if payment.user else None
    if not to_email:
        # no user email; skip
        return {"status": "skipped", "detail": "no user email available"}
    context = {
        "payment": payment
    }
    # Render plain or HTML templates (create templates/payment_confirmation.html if you want)
    message = render_to_string("emails/payment_confirmation.txt", context)
    # send_mail returns number of emails sent
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
    return {"status": "sent", "to": to_email}



@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_id):
    """
    Send a booking confirmation email asynchronously.
    
    Args:
        booking_id: The UUID of the booking to confirm
    
    Retries up to 3 times if the task fails.
    """
    try:
        # Convert to UUID if it's a string
        if isinstance(booking_id, str):
            booking_id = uuid.UUID(booking_id)
        
        booking = Booking.objects.get(booking_id=booking_id)
        
        # Calculate number of nights
        number_of_nights = (booking.end_date - booking.start_date).days
        
        # Prepare email context
        context = {
            'guest_name': booking.user_id.first_name or booking.user_id.username,
            'listing_title': booking.listing_id.title,
            'start_date': booking.start_date,
            'end_date': booking.end_date,
            'number_of_nights': number_of_nights,
            'booking_id': booking.booking_id,
            'status': booking.get_status_display(),
        }
        
        # Render HTML email template
        html_message = render_to_string('listings/booking_confirmation_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=f'Booking Confirmation - {booking.listing_id.title}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user_id.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f'Email sent successfully for booking {booking_id}'
        
    except Booking.DoesNotExist:
        return f'Booking {booking_id} not found'
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_booking_status_update_email(self, booking_id, new_status):
    """
    Send a booking status update email.
    
    Args:
        booking_id: The UUID of the booking
        new_status: The new status of the booking
    """
    try:
        if isinstance(booking_id, str):
            booking_id = uuid.UUID(booking_id)
        
        booking = Booking.objects.get(booking_id=booking_id)
        
        # Determine email subject and message based on status
        if new_status == 'confirmed':
            subject = f'Booking Confirmed - {booking.listing_id.title}'
            template = 'listings/booking_confirmed_email.html'
        elif new_status == 'canceled':
            subject = f'Booking Cancelled - {booking.listing_id.title}'
            template = 'listings/booking_cancelled_email.html'
        else:
            subject = f'Booking Status Updated - {booking.listing_id.title}'
            template = 'listings/booking_status_email.html'
        
        context = {
            'guest_name': booking.user_id.first_name or booking.user_id.username,
            'listing_title': booking.listing_id.title,
            'booking_id': booking.booking_id,
            'status': new_status.capitalize(),
        }
        
        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user_id.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f'Status update email sent for booking {booking_id}'
        
    except Booking.DoesNotExist:
        return f'Booking {booking_id} not found'
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def send_bulk_emails(user_emails, subject, message):
    """
    Send bulk emails to multiple users.
    
    Args:
        user_emails: List of email addresses
        subject: Email subject
        message: Email message body
    """
    failed_emails = []
    
    for email in user_emails:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            failed_emails.append({'email': email, 'error': str(e)})
    
    if failed_emails:
        return f'Sent bulk emails to {len(user_emails) - len(failed_emails)} users. Failed: {failed_emails}'
    
    return f'Successfully sent bulk emails to {len(user_emails)} users'


@shared_task
def debug_task():
    """Debug task for testing Celery setup."""
    print('Debug task executed!')
    return 'Debug task completed'