from django.urls import path
from .views import welcome_page,addproduct_page,cart_page,changepassword_page,confirpasswordmessage_page,checkout_page,customerregistrtion_page,forgotpassword_page,forgotpasswordmessage_page,customer_login_page,myorders_page,ordersreceived_page,product_page,productpage_page,profile_page,registration_page,serviceproduct_page,servicesingleproduct_page,subscription_page,testimonials_page,updateproduct_page,registration_sp_page, user_logout_page, service_login_page, product_page_json, addItemToCart, removeFromCart, addbankdetails, deleteItem, deleteAttachment, payment_status, addcomment, accept_order, decline_order, delivered_order, buySubcription, subcription_payment_status, tempView, removeSingleItem, addMsg



urlpatterns = [
    path("", welcome_page, name="index"),
    path("addproduct", addproduct_page, name="addproduct"),
    path("cart", cart_page, name="cart"),
    path("changepassword", changepassword_page , name="changepassword"),
    path("confirmpasswordmessage", confirpasswordmessage_page , name="confirpasswordmessage"),
    path("checkout", checkout_page, name="checkout"),
    # path("customerregistration", customerregistrtion_page , name="customerregistration"),
    path("forgotpassword", forgotpassword_page , name="forgotpassword"),
    path("forgotpasswordmessage", forgotpasswordmessage_page , name="forgotpasswordmessage"),
    path("login", customer_login_page , name="login"),
    path("service-provider-login", service_login_page , name="service_login_page"),
    path("logout", user_logout_page , name="logout"),
    path("myorders", myorders_page , name="myorders"),
    path("ordersreceived", ordersreceived_page , name="ordersreceived"),
    path("product/<slug>/<id>", product_page , name="product"),
    path("productpage/<slug>/<id>", productpage_page , name="productpage"),
    path("profile", profile_page , name="profile"),
    path("registration", registration_page, name="registration"),
    path("registration_sp", registration_sp_page, name="registration_sp"),
    path("serviceproduct", serviceproduct_page, name="serviceproduct"),
    path("servicesingleproduct/<slug>/<id>", servicesingleproduct_page, name="servicesingleproduct"),
    path("subscription", subscription_page, name="subscription"),
    path("testimonials", testimonials_page, name="testimonials"),
    path("updateproduct/<slug>/<id>", updateproduct_page, name="updateproduct"),
    path("productsjson/<id>", product_page_json, name="get_json"),
    path("add-to-cart/<id>/<qt>/", addItemToCart, name="addItemToCart"),
    path("remove-from-cart/<id>/", removeFromCart, name="removeFromCart"),
    path("addbankdetails", addbankdetails, name="addbankdetails"),
    path("deleteItem/<id>/",deleteItem, name="deleteItem" ),
    path("deleteAttachment/<id>/<mainid>/", deleteAttachment, name="deleteAttachment"),
    path('payment_status/', payment_status, name = 'payment_status'),
    path('addcomment/<int:id>/', addcomment, name='addcomment'),
    path('accept-order/<int:id>/', accept_order, name='accept_order'),
    path('decline-order/<int:id>/', decline_order, name='decline_order'),
    path('delivered-order/<int:id>/', delivered_order, name='delivered_order'),
    path('buySubcription/<int:id>/', buySubcription, name="buySubcription"),
    path('subcription_payment_status/<int:id>/', subcription_payment_status, name="subcription_payment_status"),
    path("tempView/<int:id>/", tempView, name="tempView"),
    path('removeSingle/<int:id>', removeSingleItem, name="removeSingleItem"),
    path("addMsg/<int:id>/", addMsg, name="addmsg")
]
app_name = 'shop'
