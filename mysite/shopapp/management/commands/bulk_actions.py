from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Start demo bulk actions")

        new_products_info = [
            ('Smartphone 1', 199),
            ('Smartphone 2', 299),
            ('Smartphone 3', 399),
        ]

        new_products = [
            Product(name=name, price=price, created_by=User.objects.get(pk=1))
            for name, price in new_products_info
        ]

        # Создаём сразу несколько объектов Product в БД
        result = Product.objects.bulk_create(new_products)

        for obj in result:
            print(obj)

        # Обновляем сразу несколько записей в одном запросе
        result = Product.objects.filter(name__contains="Smartphone").update(discount=10)
        #  UPDATE "shopapp_product" SET "discount" = 10 WHERE "shopapp_product"."name" LIKE '%Smartphone%' ESCAPE '\';

        print(result)

        self.stdout.write("done")