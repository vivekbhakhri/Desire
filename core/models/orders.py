"""Cart, billing, payments, coupons."""
from django.conf import settings
from django.db import models

from core.constants import ADDRESS_CHOICES

from .catalog import Item


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fname = models.CharField(max_length=100, null=True, blank=True, verbose_name="First Name")
    lname = models.CharField(max_length=100, null=True, blank=True, verbose_name="Last Name")
    email = models.CharField(max_length=50, null=True, blank=True, verbose_name="Email Id")
    number = models.CharField(max_length=20, null=True, blank=True, verbose_name="Phone Number")
    street_address = models.CharField(max_length=100, blank=True)
    apartment_address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip = models.CharField(max_length=100, blank=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES, blank=True)
    default = models.BooleanField(default=False)
    country = models.CharField(max_length=1, null=True, blank=True)
    specialInstructions = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name_plural = "BillingAddresses"

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Payments"

    def __str__(self):
        return self.user.username


class OrderItem(models.Model):
    """One row per item in a cart/order. `ordered=False` rows are the live cart."""

    unique_id = models.CharField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(null=True, blank=True)
    tax = models.FloatField(
        null=True, blank=True, default=0, verbose_name="Service Charges"
    )
    totalPrice = models.FloatField(null=True, blank=True, default=0)
    ref_code = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Reference ID"
    )
    start_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ordered_date = models.DateTimeField(null=True, blank=True)
    billing_address = models.ForeignKey(
        BillingAddress,
        related_name="billing_address",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Delivery Address",
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    being_delivered = models.BooleanField(default=False, verbose_name="Order Delivered")
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    order_rejected = models.BooleanField(default=False, verbose_name="Order Cancelled")
    order_placed = models.BooleanField(default=False, verbose_name="Order Accepted")
    seller_msg = models.CharField(
        max_length=1000, null=True, blank=True, verbose_name="Reason"
    )

    class Meta:
        verbose_name_plural = "Orders Details"

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        unit = self.price if self.price else self.item.price
        return self.quantity * unit

    def get_total_discount_item_price(self):
        unit = self.price if self.price else self.item.discount_price
        return self.quantity * unit

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        return self.price

    def getTaxAmount(self):
        from .catalog import Tax

        total = 0.0
        for tax in Tax.objects.filter(categoryId=self.item.category):
            if tax.ValueType == "In Rupees":
                total += tax.TaxValue
            elif tax.ValueType == "In Percentage":
                total += float((self.price * tax.TaxValue) / 100.0)
        return total


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code
