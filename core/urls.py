"""URL configuration for the `core` app.

Grouped by domain for readability. The `app_name` stays as ``"shop"`` because
every reverse lookup in templates and views uses the ``shop:`` prefix.
"""
from django.urls import path

from . import views

app_name = "shop"

# ---------------------------------------------------------------------------
# Storefront (browsing, cart, checkout, comments)
# ---------------------------------------------------------------------------
storefront_patterns = [
    path("", views.welcome_page, name="index"),
    path("cart", views.cart_page, name="cart"),
    path("checkout", views.checkout_page, name="checkout"),
    path("payment_status/", views.payment_status, name="payment_status"),
    path("myorders", views.myorders_page, name="myorders"),
    path("product/<slug>/<id>", views.product_page, name="product"),
    path("productpage/<slug>/<id>", views.productpage_page, name="productpage"),
    path("productsjson/<id>", views.product_page_json, name="get_json"),
    path("add-to-cart/<id>/<qt>/", views.addItemToCart, name="addItemToCart"),
    path("remove-from-cart/<id>/", views.removeFromCart, name="removeFromCart"),
    path("removeSingle/<int:id>", views.removeSingleItem, name="removeSingleItem"),
    path("addcomment/<int:id>/", views.addcomment, name="addcomment"),
    path("testimonials", views.testimonials_page, name="testimonials"),
]

# ---------------------------------------------------------------------------
# Auth + static account pages
# ---------------------------------------------------------------------------
auth_patterns = [
    path("login", views.customer_login_page, name="login"),
    path("service-provider-login", views.service_login_page, name="service_login_page"),
    path("logout", views.user_logout_page, name="logout"),
    path("registration", views.registration_page, name="registration"),
    path("registration_sp", views.registration_sp_page, name="registration_sp"),
    path("changepassword", views.changepassword_page, name="changepassword"),
    path(
        "confirmpasswordmessage",
        views.confirpasswordmessage_page,
        name="confirpasswordmessage",
    ),
    path("forgotpassword", views.forgotpassword_page, name="forgotpassword"),
    path(
        "forgotpasswordmessage",
        views.forgotpasswordmessage_page,
        name="forgotpasswordmessage",
    ),
]

# ---------------------------------------------------------------------------
# Seller dashboard (products, profile, orders received, subscriptions)
# ---------------------------------------------------------------------------
seller_patterns = [
    path("profile", views.profile_page, name="profile"),
    path("addbankdetails", views.addbankdetails, name="addbankdetails"),
    path("addproduct", views.addproduct_page, name="addproduct"),
    path("updateproduct/<slug>/<id>", views.updateproduct_page, name="updateproduct"),
    path("deleteItem/<id>/", views.deleteItem, name="deleteItem"),
    path(
        "deleteAttachment/<id>/<mainid>/",
        views.deleteAttachment,
        name="deleteAttachment",
    ),
    path("serviceproduct", views.serviceproduct_page, name="serviceproduct"),
    path(
        "servicesingleproduct/<slug>/<id>",
        views.servicesingleproduct_page,
        name="servicesingleproduct",
    ),
    path("ordersreceived", views.ordersreceived_page, name="ordersreceived"),
    path("accept-order/<int:id>/", views.accept_order, name="accept_order"),
    path("decline-order/<int:id>/", views.decline_order, name="decline_order"),
    path("delivered-order/<int:id>/", views.delivered_order, name="delivered_order"),
    path("addMsg/<int:id>/", views.addMsg, name="addmsg"),
    path("subscription", views.subscription_page, name="subscription"),
    path("buySubcription/<int:id>/", views.buySubcription, name="buySubcription"),
    path(
        "subcription_payment_status/<int:id>/",
        views.subcription_payment_status,
        name="subcription_payment_status",
    ),
    path("tempView/<int:id>/", views.tempView, name="tempView"),
]

urlpatterns = storefront_patterns + auth_patterns + seller_patterns
