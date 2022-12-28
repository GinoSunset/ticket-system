from django.dispatch import receiver
from django.db.models.signals import post_save
from users.models import Customer, User, CustomerProfile


@receiver(post_save, sender=Customer)
def create_customer_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.CUSTOMER:
        CustomerProfile.objects.create(user=instance)
