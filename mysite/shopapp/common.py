from csv import DictReader
from io import TextIOWrapper

from django.contrib.auth.models import User
from django.db import transaction

from .models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )

    reader = DictReader(csv_file)
    products = []

    for row in reader:
        user_id = row.pop("created_by")
        user = User.objects.get(pk=user_id)
        product = Product(**row, created_by=user)
        products.append(product)

    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )

    reader = DictReader(csv_file)
    orders = []

    with transaction.atomic():
        for i, row in enumerate(reader):
            delivery_address = row.get("delivery_address", "")
            promocode = row.get("promocode", "")

            user_id = row.get("user")
            user = User.objects.get(pk=user_id)

            order = Order.objects.create(
                user=user,
                delivery_address=delivery_address,
                promocode=promocode,
            )

            product_ids_str = row.get("product", "")

            if product_ids_str:
                product_ids = [int(p_id.strip()) for p_id in product_ids_str.split(',')]
                products = Product.objects.filter(pk__in=product_ids)
                order.products.set(products)

    return orders
