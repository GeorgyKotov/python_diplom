from celery import shared_task
from django.core.mail import send_mail
from easy_thumbnails.files import generate_all_aliases
from django.apps import apps


@shared_task
def send_registration_confirmation_email(email, link):
    """Асинхронная отправка письма с подтверждением регистрации"""
    subject = "Подтверждение регистрации"
    message = f"Для активации аккаунта перейдите по ссылке: {link}"
    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[email],
        fail_silently=True,
    )


@shared_task
def send_order_confirmation_email(order_id, user_email):
    """
    Асинхронная отправка письма с подтверждением заказа
    """
    subject = f"Заказ №{order_id} создан"
    message = f"Ваш заказ {order_id} успешно оформлен."
    send_mail(
        subject=subject,
        message=message,
        from_email=None,  # Можно указать EMAIL_HOST_USER, если настроено
        recipient_list=[user_email],
        fail_silently=True,
    )


@shared_task
def generate_profile_avatar_thumbnails(profile_id):
    Profile = apps.get_model('diplom', 'Profile')
    profile = Profile.objects.get(id=profile_id)

    if not profile.avatar:
        return

    generate_all_aliases(profile.avatar, include_global=True)


@shared_task
def generate_product_image_thumbnails(productinfo_id):
    ProductInfo = apps.get_model('diplom', 'ProductInfo')
    product = ProductInfo.objects.get(id=productinfo_id)

    if not product.image:
        return

    generate_all_aliases(product.image, include_global=True)
