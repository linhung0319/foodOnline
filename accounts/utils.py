from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings


def detectUser(user):
    if user.role == 1:
        redirectUrl = "accounts:vendorDashboard"
    elif user.role == 2:
        redirectUrl = "accounts:customerDashboard"
    elif user.role == None and user.is_superadmin:
        redirectUrl = "/admin"

    return redirectUrl

def send_verification_email(request, user, mail_subject, mail_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(
        mail_template,
        {"user": user,
         "domain": current_site,
         "uid": urlsafe_base64_encode(force_bytes(user.pk)),
         "token": default_token_generator.make_token(user),
        },
    )
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()
