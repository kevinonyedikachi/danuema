# amazon/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from amazon.tests import test_restricted_token, test_retrieve_orders, text_access_token
from .views import (
    AllOrdersView,
    ConfirmShipmentView,
    OrderAdressInfoView,
    OrderBuyerInfoView,
    OrderItems,
    OrdersView,
    SingleOrderView,
    CreateSageOrders,
    sage_amazon_tracking,
)
from django.views.generic.base import RedirectView

# Set the url patterns
urlpatterns = [
    path("text_access_token/", text_access_token, name="text_access_token"),
    path("test_restricted_token/", test_restricted_token, name="test_restricted_token"),
    path("test_retrieve_orders/", test_retrieve_orders, name="test_retrieve_orders"),
    # Get Orders routh
    path("orders/", OrdersView.as_view(), name="getOrders"),  # get_orders
    path("orders/all/", AllOrdersView.as_view(), name="getAllOrders"),
    path("orders/sageOrders/", CreateSageOrders.as_view(), name="postSageOrders"),
    path(
        "orders/sageAmazonTracking/", sage_amazon_tracking, name="sage_amazon_tracking"
    ),
    path("orders/<str:orderId>/", SingleOrderView.as_view(), name="ordersItemsView"),
    path(
        "orders/<str:orderId>/buyerInfo/",
        OrderBuyerInfoView.as_view(),
        name="buyerInfo",
    ),
    path(
        "orders/<str:orderId>/address/",
        OrderAdressInfoView.as_view(),
        name="buyerAddress",
    ),
    path("orders/<str:orderId>/orderItems/", OrderItems.as_view(), name="orderItems"),
    # Post Orders routh
    path(
        "orders/v0/orders/<str:orderId>/shipmentConfirmation/",
        ConfirmShipmentView.as_view(),
        name="confirm_shipment",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
