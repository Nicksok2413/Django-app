from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import QuerySet

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Create order
    """

    @transaction.atomic
    def handle(self, *args, **options):
        # with transaction.atomic():  # <- Контекстный менеджер (аналог декоратора) для вложенных транзакций
        #     ...
        self.stdout.write("Greate order with products")
        user = User.objects.get(username="Nick")
        products: QuerySet[Product] = Product.objects.filter(archived=False)
        order, created = Order.objects.get_or_create(
            delivery_address="123 Main st",
            promocode="BLACKFRIDAY",
            user=user,
        )

        for product in products:
            order.products.add(product)

        order.save()
        self.stdout.write(f"Created order: {order}")