from django.urls import path
from .views import (
    create_sop_order,
    handle_callback,
    initiate_auth,
    authenticated_view,
    line_items,
    sop_order,
    sop_orders,
)


urlpatterns = [
    path("initiate-auth/", initiate_auth, name="initiate_auth"),
    path("callback/", handle_callback, name="callback"),
    path("authenticated/", authenticated_view, name="authenticated_view"),
    path("sop_orders/", sop_orders, name="sop_orders"),
    path("sop_order/<int:order_id>", sop_order, name="sop_order"),
    path("create_sop_order/", create_sop_order, name="create_sop_order"),
    path("test/", line_items, name="payment_method_id"),
]
