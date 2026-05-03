"""Subscription plans, payments and seller/customer profile."""
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Subcription(models.Model):
    """Note: legacy spelling kept to preserve existing migrations and DB rows."""

    name = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    validity = models.IntegerField(null=True, blank=True)
    entries = models.IntegerField(null=True, blank=True)
    is_booster = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.name} {self.validity} Days"


class SubscriptionPayment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Subscription Payments"

    def __str__(self):
        return self.user.username


class Profile(models.Model):
    unique_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="User Id"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=255)
    alt_contact_number = models.CharField(max_length=255, null=True, blank=True)
    is_service_provider = models.BooleanField(default=False)

    # Profile completeness flags toggled when the seller saves each section.
    saved = models.BooleanField(default=False)
    bank_details_saved = models.BooleanField(default=False)

    company_name = models.CharField(max_length=255, null=True, blank=True)
    address1 = models.CharField(max_length=255, null=True, blank=True)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=255, null=True, blank=True)

    account_number = models.CharField(max_length=255, null=True, blank=True)
    ifsc_code = models.CharField(max_length=255, null=True, blank=True)
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)

    entries_remaining = models.IntegerField(null=True, blank=True, default=0)
    days_valid = models.IntegerField(null=True, blank=True, default=0)
    subcription = models.ForeignKey(
        Subcription,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        limit_choices_to={"is_booster": False},
    )
    booster = models.ForeignKey(
        Subcription,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
        limit_choices_to={"is_booster": True},
    )
    subs_date = models.DateTimeField(null=True, blank=True)
    booster_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.unique_id)
