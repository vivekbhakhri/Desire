"""Tests for `core.services.permissions` — role and profile-completion checks."""
from __future__ import annotations

from django.contrib.auth.models import AnonymousUser, Group, User
from django.test import TestCase

from shop.constants import GROUP_CUSTOMERS, GROUP_SERVICE_PROVIDERS
from shop.models import Profile
from shop.services.permissions import (
    has_completed_profile,
    is_customer,
    is_service_provider,
)


class RoleCheckTests(TestCase):
    def setUp(self):
        self.customers = Group.objects.create(name=GROUP_CUSTOMERS)
        self.sellers = Group.objects.create(name=GROUP_SERVICE_PROVIDERS)
        self.user = User.objects.create_user(username="alice", password="pw")

    def test_anonymous_user_is_neither(self):
        self.assertFalse(is_customer(AnonymousUser()))
        self.assertFalse(is_service_provider(AnonymousUser()))

    def test_user_with_no_groups_is_neither(self):
        self.assertFalse(is_customer(self.user))
        self.assertFalse(is_service_provider(self.user))

    def test_customer_membership_only_satisfies_customer_check(self):
        self.user.groups.add(self.customers)
        self.assertTrue(is_customer(self.user))
        self.assertFalse(is_service_provider(self.user))

    def test_seller_membership_only_satisfies_seller_check(self):
        self.user.groups.add(self.sellers)
        self.assertFalse(is_customer(self.user))
        self.assertTrue(is_service_provider(self.user))


class HasCompletedProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", password="pw")

    def test_no_profile_returns_false(self):
        self.assertFalse(has_completed_profile(self.user))

    def test_profile_without_both_flags_returns_false(self):
        Profile.objects.create(
            user=self.user,
            contact_number="60000001",
            saved=True,
            bank_details_saved=False,
        )
        self.assertFalse(has_completed_profile(self.user))

    def test_profile_with_both_flags_returns_true(self):
        Profile.objects.create(
            user=self.user,
            contact_number="60000001",
            saved=True,
            bank_details_saved=True,
        )
        self.assertTrue(has_completed_profile(self.user))
