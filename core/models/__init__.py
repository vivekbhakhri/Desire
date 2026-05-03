"""Re-export every model so migrations and the rest of the codebase can keep
using `from core.models import X` regardless of which sub-module owns it.

ModelForms (`CommentForm`, `ContactForm`) live in `core.forms` — import them
from there, not from `core.models`.
"""

from .accounts import Profile, Subcription, SubscriptionPayment
from .catalog import Attachment, Category, HomeImage, Item, Slide, Tax
from .content import Comment, Contact, Seo, Testimonial
from .orders import BillingAddress, Coupon, OrderItem, Payment

__all__ = [
    "Attachment",
    "BillingAddress",
    "Category",
    "Comment",
    "Contact",
    "Coupon",
    "HomeImage",
    "Item",
    "OrderItem",
    "Payment",
    "Profile",
    "Seo",
    "Slide",
    "Subcription",
    "SubscriptionPayment",
    "Tax",
    "Testimonial",
]
