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
        self.stdout.write("Greate order with products")
        user = User.objects.get(username="Nick")

        # .defer(<fields>) исключает поля <fields> из SQL-запроса
        # Это нужно для того, чтобы исключить загрузку ненужных полей при запросе
        # products: QuerySet[Product] = Product.objects.defer("description", "price", "created_at")

        # .only(<fields>) включает в SQL-запрос ТОЛЬКО поля <fields>
        # Это нужно для того, чтобы не перечислять ненужные поля, а передать в запрос только необходимые поля
        products: QuerySet[Product] = Product.objects.only("pk")

        order, created = Order.objects.get_or_create(
            delivery_address="123 Test st",
            promocode="SALE",
            user=user,
        )

        for product in products:
            order.products.add(product)

        order.save()
        self.stdout.write(f"Created order: {order}")