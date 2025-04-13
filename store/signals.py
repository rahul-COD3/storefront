from django.db.models.signals import post_save
from django.dispatch import receiver

from storefront import settings
from .models import Customer

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender, **kwargs):
    """
    Signal to create a Customer instance when a new User is created.
    """
    if kwargs['created']:
        user = kwargs['instance']
        Customer.objects.create(user=user)