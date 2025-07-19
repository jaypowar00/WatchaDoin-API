import os
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from dotenv import load_dotenv
load_dotenv()


def send_verification_email(user, token):
    uidb64 = urlsafe_base64_encode(force_bytes(user.uid))
    domain = os.getenv('EMAIL_VERIFICATION_DOMAIN')
    verification_url = f"{domain}/user/auth/verify-email?uid={uidb64}&token={token}"
    subject = f'Verify your email: {uidb64}'
    body = f'''Dear {user.username},

Thank you for signing up for Watcha Doin.

An account has been created using this email address.
To complete your registration and confirm ownership of this email, please verify your account by clicking the link below:

{verification_url}
(The link will expire after 24 hours)

If you did not initiate this registration, you can safely ignore this message.
For any queries or concerns, feel free to reach us at watcha.doin.api@gmail.com.

Best Regards,  
Watcha Doin
'''

    send_mail(
        subject,
        body,
        None,
        [user.email],
        fail_silently=False
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
