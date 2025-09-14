from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LatestProductsFeed,
    OrderCreateView,
    OrdersDataExportView,
    OrderDeleteView,
    OrderDetailView,
    OrdersListView,
    OrderUpdateView,
    OrderViewSet,
    ProductArchiveView,
    ProductCreateView,
    ProductsDataExportView,
    ProductDetailsView,
    ProductListView,
    ProductUpdateView,
    ProductViewSet,
    ShopIndexView,
    UserOrdersListView,
    UserOrdersDataExportView,
)

app_name = "shopapp"

router = DefaultRouter()
router.register("orders", OrderViewSet)
router.register("products", ProductViewSet)

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("api/", include(router.urls)),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/export/", OrdersDataExportView.as_view(), name="orders_export"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/confirm-delete/", OrderDeleteView.as_view(), name="order_delete"),
    path("products/", ProductListView.as_view(), name="products_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/export/", ProductsDataExportView.as_view(), name="products_export"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/confirm-archive/", ProductArchiveView.as_view(), name="product_archive"),
    path("products/latest/feed/", LatestProductsFeed(), name="products_feed"),
    path("users/<int:pk>/orders/", UserOrdersListView.as_view(), name="user_orders"),
    path("users/<int:pk>/orders/export", UserOrdersDataExportView.as_view(), name="user_orders_export"),
]
