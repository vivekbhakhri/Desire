"""Role / capability checks for `auth.User`."""
from __future__ import annotations

from django.contrib.auth.models import User

from shop.constants import GROUP_CUSTOMERS, GROUP_SERVICE_PROVIDERS


def is_customer(user: User) -> bool:
    return user.is_authenticated and user.groups.filter(name=GROUP_CUSTOMERS).exists()


def is_service_provider(user: User) -> bool:
    return (
        user.is_authenticated
        and user.groups.filter(name=GROUP_SERVICE_PROVIDERS).exists()
    )


def has_completed_profile(user: User) -> bool:
    """A seller can list products only after completing their profile + bank details."""
    from shop.models import Profile

    profile = Profile.objects.filter(user=user).first()
    return bool(profile and profile.saved and profile.bank_details_saved)
