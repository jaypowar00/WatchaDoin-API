import os
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from dotenv import load_dotenv
load_dotenv()


def send_verification_email(username: str, email: str, token):
    uidb64 = urlsafe_base64_encode(force_bytes(username))
    domain = os.getenv('EMAIL_VERIFICATION_DOMAIN')
    verification_url = f"{domain}/user/auth/verify-email?uid={uidb64}&token={token}"
    subject = f'Verify your Account ({uidb64})'
    message = f'''Dear {username},

Thank you for signing up for Watcha Doin.

An account has been created using this email address.
To complete your registration and confirm ownership of this email, please verify your account by clicking the link below:

{verification_url}

(The link will expire after 1 hour)

If you did not initiate this registration, you can safely ignore this message.
For any queries or concerns, feel free to reach us at watcha.doin.api@gmail.com.

Best Regards,  
Watcha Doin
'''
    html_body = f'''<p>Dear {username},</p>

<p>Thank you for signing up for <strong>Watcha Doin</strong>.</p>

<p>An account has been created using this email address.<br>
To complete your registration and confirm ownership of this email, please verify your account by clicking the button below:</p>

<p><a href="{verification_url}" style="display:inline-block;padding:8px 12px;background-color:#2c7d2f;color:white;text-decoration:none;border-radius:5px;">Verify Account</a></p>

<p>(This link will expire after 1 hour)</p>

<p>If you did not initiate this registration, you can safely ignore this message.<br>
For any queries or concerns, feel free to reach us at <a href="mailto:watcha.doin.api@gmail.com">watcha.doin.api@gmail.com</a>.</p>

<p>Best Regards,<br>
Watcha Doin</p>
'''

    send_mail(
        subject,
        message,
        None,
        [email],
        fail_silently=False,
        html_message=html_body,
    )


def send_congratulations_email(user):
    subject = '🎉 Congratulations! Your Account is Verified'
    message = (
        f'Dear {user.username},\n\n'
        f'Congratulations!\n\nYour account on "Watcha Doin" has been successfully verified.\n'
        f'You can now log in and enjoy the full features of the platform.\n\n'
        f'If you didn’t request this verification, please contact us immediately at watcha.doin.api@gmail.com.\n\n'
        f'Thanks for joining us!🚀\n\n'
        f'Best Regards\nWatcha Doin'
    )
    send_mail(
        subject,
        message,
        None,
        [user.email],
        fail_silently=False,
    )
