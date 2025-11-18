from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, ProductInfo
from .tasks import (
    generate_profile_avatar_thumbnails,
    generate_product_image_thumbnails
)


@receiver(post_save, sender=Profile)
def process_profile_avatar(sender, instance, created, **kwargs):
    if instance.avatar:
        generate_profile_avatar_thumbnails.delay(instance.id)


@receiver(post_save, sender=ProductInfo)
def process_product_image(sender, instance, created, **kwargs):
    if instance.image:
        generate_product_image_thumbnails.delay(instance.id)
