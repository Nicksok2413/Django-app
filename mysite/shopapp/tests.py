import json

from random import choices
from string import ascii_letters

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": "Tablet 3",
                "price": "123.45",
                "description": "A pretty good tablet",
                "discount": "10",
            },
        )
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())
        self.assertRedirects(response, reverse("shopapp:products_list"))


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name="Best product")

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    # def setUp(self) -> None:
    #     self.product = Product.objects.create(name="Best product")
    #
    # def tearDown(self) -> None:
    #     self.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse(
                "shopapp:product_details",
                kwargs={"pk": self.product.pk}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse(
                "shopapp:product_details",
                kwargs={"pk": self.product.pk}
            )
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]

    def test_get_products_list(self):
        response = self.client.get(reverse("shopapp:products_list"))
        # 1
        for product in Product.objects.filter(archived=False).all():
            self.assertContains(response, product.name)

        # 2
        products = Product.objects.filter(archived=False).all()
        products_ = response.context["products"]

        for p, p_ in zip(products, products_):
            self.assertEqual(p.pk, p_.pk)

        # 3
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(product.pk for product in response.context["products"]),
            transform=lambda p: p.pk,
        )

        # 4
        self.assertTemplateUsed(response, 'shopapp/products_list.html')


# class OrdersListViewTestCase(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.credentials = dict(name="nick_test", password="Qwerty123!")
#         cls.user = User.objects.create_user(**cls.credentials)
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.user.delete()
#
#     def setUp(self):
#         self.client.login(**self.credentials)
#
#     def test_get_orders_list(self):
#         response = self.client.get(reverse("shopapp:orders_list"))
#         self.assertContains(response, "Orders")


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(name="nick_test", password="Qwerty123!")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_orders_list(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_get_orders_list_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        # self.assertRedirects(response, str(settings.LOGIN_URL))
        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]

    def test_get_products_view(self):
        response = self.client.get("shopapp:products_export")
        self.assertEqual(response.status_code, 200)

        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "descriptions": product.description,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(products_data["products"], expected_data)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="nick_test", password="Qwerty123!")
        cls.user.user_permissions.add(
            Permission.objects.get(
            codename="view_order",
            )
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address="123 Test st",
            promocode="SALE",
            user=self.user,
        )

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(
            reverse(
                "shopapp:order_details",
                kwargs={"pk": self.order.pk}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shopapp/order_detail.html")
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context["order"].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
        "users-fixture.json",
        "products-fixture.json",
        "orders-fixture.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(pk=1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_order_data_export_view(self):
        response = self.client.get(reverse("shopapp:orders_export"))
        self.assertEqual(response.status_code, 200)

        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.pk,
                "products": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]
        orders_data = response.json()

        print('\n*** Expected data ***')
        print(json.dumps(expected_data, indent=4, default=str))
        print('\n*** Orders data ***')
        print(json.dumps(orders_data["orders"], indent=4, default=str))

        self.assertEqual(orders_data["orders"], expected_data)