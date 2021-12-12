from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from accounts.models import Customer


def customer_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='Customer')

        instance.groups.add(group)
        Customer.objects.create(
            user=instance,
            name=instance.username
        )
        print("Profile Created via Signals")


post_save.connect(customer_profile, sender=User)


