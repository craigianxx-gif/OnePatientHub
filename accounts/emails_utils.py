from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_account_approval_email(
    user,
    temporary_password,
    account_request
):
    """
    Sends an account approval email to the newly created user.
    """

    subject = "OnePatient Hub - Your Account Has Been Approved"

    context = {
        "user": user,
        "account_request": account_request,
        "temporary_password": temporary_password,
        "login_url": "http://127.0.0.1:8000/accounts/",
    }

    html_content = render_to_string(
        "accounts/emails/account_approved.html",
        context
    )

    text_content = f"""
OnePatient Hub Account Approved

Dear {account_request.full_name},

Your OnePatient Hub account has been approved.

Username: {user.username}
Temporary Password: {temporary_password}

Please log in and change your temporary password immediately.

Login:
http://127.0.0.1:8000/accounts/

Regards,
OnePatient Hub Administration
"""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(
        html_content,
        "text/html"
    )

    return email.send(fail_silently=False)