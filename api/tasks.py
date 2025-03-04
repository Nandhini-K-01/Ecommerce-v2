from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.db.models import Q # to combine multiple conditions in single query
from django.template.loader import render_to_string # render html with dynamic data
import io
from xhtml2pdf import pisa


@shared_task(bind=True)
def update_subscription_status(self):
    today = now().date()
    get_user_model().objects.filter(subscription_end_date__lte=today).update(is_subscription_active=False)
    return "success"


def generate_invoice_pdf(user):
    # Render HTML with user data
    html_content = render_to_string("invoice_template.html", {
        "invoice_number": f'INV-{str(user.uuid)[:8]}-{user.subscription_end_date.strftime("%Y%m%d")}',
        "user_name": user.name,
        "user_email": user.email,
        "subscription_plan": user.subscription_type.name,
        "amount": user.subscription_type.price,
        "invoice_date": user.subscription_end_date.strftime("%Y-%m-%d")
    })

    # Generate PDF from HTML
    pdf_buffer = io.BytesIO() # creates empty file like in main memory
    pisa_status = pisa.CreatePDF(io.StringIO(html_content), dest=pdf_buffer)

    if pisa_status.err:
        return None
    return pdf_buffer.getvalue()


@shared_task(bind=True)
def send_mail_func(self):
    today = now().date()
    users = get_user_model().objects.filter(
        Q(subscription_end_date = today + timedelta(days=4)) |
        Q(subscription_end_date = today + timedelta(days=1)) |
        Q(subscription_end_date = today) |
        Q(subscription_end_date = today - timedelta(days=3)) |
        Q(subscription_end_date = today - timedelta(weeks=2))
    )
    
    if not users.exists():
        return "No users to notify"

    for user in users:
        if user.subscription_end_date >= today:
            pdf_data = generate_invoice_pdf(user)
            if not pdf_data:
                print("PDF generation failed")
        mail_subject = "Renew you subscription for ShopHereZone"
        message = f"Dear {user.name}, It's a remainder message for ur ShopHereZone subscription"
        to_email = user.email
        email = EmailMessage(
            subject=mail_subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email]
        )
        email.attach('invoice.pdf', pdf_data, 'application/pdf')
        email.send()
    return "Done"