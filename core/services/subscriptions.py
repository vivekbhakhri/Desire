"""Seller subscription lifecycle: validity windows, entry quotas, expiry."""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone


def has_active_subscription(user: User) -> bool:
    from core.models import Profile

    profile = Profile.objects.filter(user=user).first()
    return bool(profile and profile.subcription)


def has_remaining_entries(user: User) -> bool:
    from core.models import Profile

    profile = Profile.objects.filter(user=user).first()
    return bool(profile and (profile.entries_remaining or 0) > 0)


def remaining_subscription_days(user: User) -> int:
    """
    Returns days left in the seller's plan; 0 once expired (and clears
    plan refs on the profile so future calls short-circuit).
    """
    from core.models import Profile

    profile = Profile.objects.filter(user=user).first()
    if profile is None:
        return 0
    if not has_active_subscription(user):
        return 0

    now = timezone.now()
    if profile.booster:
        delta = (now - profile.subs_date).days + (now - profile.booster_date).days
    elif profile.subcription:
        delta = (now - profile.subs_date).days
    else:
        delta = 0

    days = max((profile.days_valid or 0) - delta, 0)
    if days == 0:
        profile.subcription = None
        profile.booster = None
        profile.entries_remaining = 0
        profile.save()
    return days


def booster_days(profile) -> int:
    """Validity contributed by an active booster pack (0 if none)."""
    return profile.booster.validity if profile.booster else 0


def order_within_subscription(order, user: User) -> bool:
    """True if the order was placed inside the seller's billable window."""
    from core.models import OrderItem, Profile

    profile = Profile.objects.filter(user=user).first()
    fresh_order = OrderItem.objects.filter(id=order.id).first()
    if not (profile and fresh_order and profile.subs_date):
        return False
    cutoff = profile.subs_date + timedelta(days=profile.days_valid or 0)
    return fresh_order.ordered_date < cutoff
