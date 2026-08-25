"""Public view surface.

Re-exports every view function under its legacy name so `core/urls.py` (and
any older imports) keep working unchanged after the package split.
"""

from .analytics import payment_graph_view, subscription_graph_view
from .auth import (
    customer_login_page,
    customerregistrtion_page,
    registration_page,
    registration_sp_page,
    service_login_page,
    user_logout_page,
)
from .seller import (
    accept_order,
    addbankdetails,
    addMsg,
    addproduct_page,
    buySubcription,
    decline_order,
    deleteAttachment,
    deleteItem,
    delivered_order,
    ordersreceived_page,
    profile_page,
    serviceproduct_page,
    servicesingleproduct_page,
    subcription_payment_status,
    subscription_page,
    tempView,
    updateproduct_page,
)
from .storefront import (
    addcomment,
    addItemToCart,
    cart_page,
    changepassword_page,
    checkout_page,
    confirpasswordmessage_page,
    forgotpassword_page,
    forgotpasswordmessage_page,
    myorders_page,
    payment_status,
    product_page,
    product_page_json,
    productpage_page,
    removeFromCart,
    removeSingleItem,
    testimonials_page,
    welcome_page,
)
