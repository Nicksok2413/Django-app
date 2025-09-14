from email.policy import default

from django.core.management import BaseCommand
from django.db.models import Avg, Count, Max, Min, Sum

from shopapp.models import Product, Order


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Start demo aggregate")

        # .aggregate - агрегирует данные по столбцам/колонкам
        result = Product.objects.aggregate(
            Avg("price"),
            Count("pk"),
            Max("price"),
            Min("price"),
            Sum("price"),
        )

        print(result)
        # {
        #   'price__avg': Decimal('459.243000000000'),
        #   'pk__count': 10,
        #   'price__max': Decimal('1545.45000000000'),
        #   'price__min': Decimal('19.9900000000000'),
        #   'price__sum': Decimal('4592.43000000000')
        # }

        # Агрегирует фильтрованные данные по столбцам/колонкам
        result = Product.objects.filter(name__contains="Smartphone").aggregate(
            Avg("price"),
            count=Count("pk"),
            max_price=Max("price"),  # Переименовываем параметры
            min_price=Min("price"),  # Переименовываем параметры
            summary=Sum("price"),  # Переименовываем параметры
        )
        # {
        #   'count': 7,
        #   'max_price': Decimal('399'),
        #   'min_price': Decimal('199'),
        #   'summary': Decimal('2127'),
        #   'price__avg': Decimal('303.857142857143')
        # }

        print(result)

        # Рассчитываем кол-во товаров в заказе и полную стоимость каждого заказа
        orders = Order.objects.annotate(
            total_price=Sum("products__price", default=0),  # default=0 чтобы не было None если в заказе нет товаров
            products_count=Count("products")
        )

        for order in orders:
            print(
                f"Order #{order.pk}; "
                f"Number of products: {order.products_count}; "
                f"Total worth: ${order.total_price}."
            )
        # Order  # 1; Number of products: 1; Total worth: $19.9900000000000.
        # Order  # 2; Number of products: 2; Total worth: $352.990000000000.
        # Order  # 7; Number of products: 4; Total worth: $2798.43000000000.


        self.stdout.write("done")