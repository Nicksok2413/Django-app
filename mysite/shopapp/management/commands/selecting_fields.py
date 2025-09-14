from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Order, Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Start demo select fields")

        #1 - Instance.objects.values()
        products_values = Product.objects.values("pk", "name")
        # SELECT "shopapp_product"."id" AS "pk", "shopapp_product"."name" AS "name" FROM "shopapp_product" ORDER BY 2 ASC, "shopapp_product"."price" ASC;

        for p_values in products_values:
            print(p_values)

        # Получим dict(str, Any)
        # {'pk': 7, 'name': 'Desktop'}
        # {'pk': 6, 'name': 'Laptop'}
        # {'pk': 3, 'name': 'Smartphone'}


        #2 - Instance.objects.values_list()
        users_info = User.objects.values_list("pk", "username")
        #  SELECT "auth_user"."id" AS "pk", "auth_user"."username" AS "username" FROM "auth_user";

        for user_info in users_info:
            print(user_info)

        # Получим tuple(int, str)
        # (1, 'Nick')
        # (5, 'Sam')
        # (8, 'Tom')

        users_names = User.objects.values_list("username")
        #  SELECT "auth_user"."username" AS "username" FROM "auth_user";

        for user_name in users_names:
            print(user_name)

        # Получим tuple(str, )
        # ('Nick',)
        # ('Sam',)
        # ('Tom',)

        self.stdout.write("done")

        # Чтобы вывести данные одним 'плоским' списком (а не кортежами)
        users_names = User.objects.values_list("username", flat=True)
        # SELECT "auth_user"."username" AS "username" FROM "auth_user" LIMIT 21;

        print(users_names)

        # Получим
        # <QuerySet ['Alex', 'Bob', 'Manager', 'Nick', 'Sam', 'Tom']>

        print(list(users_names))

        # Получим
        # ['Alex', 'Bob', 'Manager', 'Nick', 'Sam', 'Tom']