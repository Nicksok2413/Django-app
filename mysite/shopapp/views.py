"""
В этом модуле лежат различные наборы представлений.

Разные View интернет-магазина: по товарам, заказам и т.д.
"""

import logging
from csv import DictWriter

# Django
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

# DRF
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# filters & ordering
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

# app
from .common import save_csv_products
from .forms import OrderForm, ProductForm
from .models import Order, Product, ProductImage
from .serializers import OrderSerializer, ProductSerializer

log = logging.getLogger(__name__)


# *** ShopIndex ***

class ShopIndexView(View):
    # @method_decorator(cache_page(60 * 2))  # Кеширование на 2 минуты
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "products": products,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        print("shop index context:", context)
        return render(request, 'shopapp/shop-index.html', context=context)


# *** DRF ModelViewSet ***
@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.
    Полный CRUD для сущностей товара.
    """

    queryset = (
        Product.objects
        .select_related("created_by")
        .all()
    )
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "discount"]

    @method_decorator(cache_page(60 * 2))  # Кеширование на 2 минуты
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by ID not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f'attachment; filename={filename}'

        queryset = self.filter_queryset(self.get_queryset())
        fields = ["name", "description", "price", "discount", "created_by"]
        queryset = queryset.only(*fields)

        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow(
                {field: getattr(product, field) for field in fields}
            )

        return response

    @action(methods=["post"], detail=False, parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            file=request.FILES["file"].file,
            encoding=request.encoding
        )

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
        .all()
    )
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    ordering_fields = ["delivery_address", "promocode", "created_at", "user"]
    filterset_fields = ["delivery_address", "promocode", "user"]


# *** Products ***

class ProductArchiveView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")
    template_name_suffix = "_confirm_archive"

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        return response


class ProductDetailsView(DetailView):
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductListView(ListView):
    template_name = "shopapp/products_list.html"
    queryset = Product.objects.filter(archived=False)
    context_object_name = "products"


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )

        return response

    def test_func(self):
        user = self.request.user

        if user.is_superuser:
            return True

        return user.has_perm("shopapp.change_product") and self.get_object().created_by == user


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)

        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "descriptions": product.description,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)

        return JsonResponse({"products": products_data})


# *** RSS ***
class LatestProductsFeed(Feed):
    title = "Последние товары в магазине"
    description = "Обновления по последним добавленным товарам в нашем магазине."
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        # Последние 5 неархивированных товаров
        return Product.objects.filter(archived=False).order_by("-created_at")[:5]

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]


# *** Orders ***

class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("shopapp:orders_list")


class OrdersDataExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.pk,
                "products": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = ["shopapp.view_order"]
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/orders_list.html"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderUpdateView(UpdateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


# *** UserOrders ***

class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = 'shopapp/user_orders.html'
    context_object_name = 'orders'
    owner = None

    def get_queryset(self):
        user_pk = self.kwargs['pk']
        self.owner = get_object_or_404(User.objects.select_related('profile'), pk=user_pk)
        return Order.objects.filter(user=self.owner).select_related('user').prefetch_related('products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


class UserOrdersDataExportView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk=int) -> JsonResponse:
        cache_key = f"user_#{pk}_orders_data_export"
        user_orders_data = cache.get(cache_key)

        if user_orders_data is None:
            user = get_object_or_404(User, pk=pk)
            user_orders = (
                Order.objects
                .filter(user=user)
                .order_by("pk")
                .select_related('user')
                .prefetch_related('products')
            )
            serializer = OrderSerializer(user_orders, many=True)
            user_orders_data = {
                "user_id": user.pk,
                "username": user.username,
                "orders": serializer.data,
            }
            cache.set(cache_key, user_orders_data, 300)

        return JsonResponse(user_orders_data)