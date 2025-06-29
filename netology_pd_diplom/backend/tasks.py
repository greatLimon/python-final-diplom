from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from backend.models import Shop
import requests
from yaml import load as load_yaml, Loader

@shared_task
def send_email(subject, message, to_email):
    """Асинхронная отправка email"""
    msg = EmailMultiAlternatives(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [to_email]
    )
    msg.send()

@shared_task
def do_import(shop_id, url):
    """Асинхронный импорт товаров"""
    shop = Shop.objects.get(id=shop_id)
    stream = requests.get(url).content
    data = load_yaml(stream, Loader=Loader)
    
    # Ваш код импорта из PartnerUpdate
    for category in data['categories']:
        category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        category_object.shops.add(shop.id)
    
    ProductInfo.objects.filter(shop_id=shop.id).delete()
    
    for item in data['goods']:
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
        product_info = ProductInfo.objects.create(
            product_id=product.id,
            external_id=item['id'],
            model=item['model'],
            price=item['price'],
            price_rrc=item['price_rrc'],
            quantity=item['quantity'],
            shop_id=shop.id
        )
        for name, value in item['parameters'].items():
            parameter_object, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(
                product_info_id=product_info.id,
                parameter_id=parameter_object.id,
                value=value
            )
    
    return f"Импорт для {shop.name} завершен"