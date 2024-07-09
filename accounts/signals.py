from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from .models import Profile, User

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    reset_password_url = "{}?token={}".format(
        instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
        reset_password_token.key)

    email_plaintext_message = f"Hi {reset_password_token.user.username},\n\n" \
                              f"You requested a password reset. Click the link below to reset your password:\n" \
                              f"{reset_password_url}\n\n" \
                              f"If you did not request a password reset, please ignore this email."

    send_mail(
        "Password Reset for DreamBoard",
        email_plaintext_message,
        "noreply@dreamboard.onrender.com",
        [reset_password_token.user.email],
        fail_silently=False,
    )
