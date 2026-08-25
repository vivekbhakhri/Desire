"""Choice tuples and shared enum-like constants used across the app."""

LABEL_CHOICES = (
    ("New", "New"),
    ("Sale", "Sale"),
    ("Promotion", "Promotion"),
)

TAX_VALUE_TYPES = (
    ("In Rupees", "Rs"),
    ("In Percentage", "Percent"),
)

ADDRESS_CHOICES = (
    ("B", "Billing"),
)

ROLES = (
    ("Customer", "Customer"),
    ("Seller", "Seller"),
)

COMMENT_STATUS = (
    ("New", "New"),
    ("True", "True"),
    ("False", "False"),
)

PAYMENT_CHOICES = (
    ("InstaMojo", "Online(Debit/Credit Cards"),
    ("COD", "Cash On Delivery"),
)

# Auth groups (set up via Django admin / fixtures).
GROUP_CUSTOMERS = "Customers"
GROUP_SERVICE_PROVIDERS = "Service Providers"

# Razorpay/InstaMojo redirect base used by checkout & subscription flows.
PAYMENT_REDIRECT_HOST = "http://localhost:8000"
