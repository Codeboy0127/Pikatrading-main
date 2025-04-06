# accounts/signals.py
from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from allauth.socialaccount.models import SocialLogin
from django.contrib.auth.models import User


# This reciever will sovle on if the existing email has already registered via the form, a user can login with the social account without conflict
@receiver(pre_social_login)
def handle_existing_user_email(sender, request, sociallogin, **kwargs):
    # Get the email associated with the social login
    email = sociallogin.account.extra_data.get('email')

    # Check if the email exists in the database
    try:
        existing_user = User.objects.get(email=email)
    except User.DoesNotExist:
        # No existing user, proceed with regular login
        return

    # If an existing user is found, link the social account to this user
    if not sociallogin.is_existing:
        sociallogin.connect(request, existing_user)
