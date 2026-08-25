"""Tests for `core.services.subscriptions` — plan validity, quota, expiry."""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from shop.models import Profile, Subcription
from shop.services.subscriptions import (
    booster_days,
    has_active_subscription,
    has_remaining_entries,
    remaining_subscription_days,
)


def _make_plan(*, validity=30, entries=10, is_booster=False, name="Plan"):
    return Subcription.objects.create(
        name=name, price=999, validity=validity, entries=entries, is_booster=is_booster
    )


class HasActiveSubscriptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", password="pw")

    def test_no_profile_returns_false(self):
        self.assertFalse(has_active_subscription(self.user))

    def test_profile_without_plan_returns_false(self):
        Profile.objects.create(user=self.user, contact_number="60000001")
        self.assertFalse(has_active_subscription(self.user))

    def test_profile_with_plan_returns_true(self):
        plan = _make_plan()
        Profile.objects.create(
            user=self.user, contact_number="60000001", subcription=plan
        )
        self.assertTrue(has_active_subscription(self.user))


class HasRemainingEntriesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", password="pw")

    def test_zero_entries_returns_false(self):
        Profile.objects.create(
            user=self.user, contact_number="60000001", entries_remaining=0
        )
        self.assertFalse(has_remaining_entries(self.user))

    def test_positive_entries_returns_true(self):
        Profile.objects.create(
            user=self.user, contact_number="60000001", entries_remaining=3
        )
        self.assertTrue(has_remaining_entries(self.user))


class RemainingSubscriptionDaysTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", password="pw")

    def test_no_subscription_is_zero(self):
        Profile.objects.create(user=self.user, contact_number="60000001")
        self.assertEqual(remaining_subscription_days(self.user), 0)

    def test_active_plan_returns_remaining_days(self):
        plan = _make_plan(validity=30)
        Profile.objects.create(
            user=self.user,
            contact_number="60000001",
            subcription=plan,
            days_valid=30,
            subs_date=timezone.now() - timedelta(days=10),
        )
        # 30 days valid, 10 elapsed → ~20 remaining.
        self.assertEqual(remaining_subscription_days(self.user), 20)

    def test_expired_plan_clears_profile_and_returns_zero(self):
        plan = _make_plan(validity=5)
        Profile.objects.create(
            user=self.user,
            contact_number="60000001",
            subcription=plan,
            days_valid=5,
            entries_remaining=4,
            subs_date=timezone.now() - timedelta(days=20),
        )

        self.assertEqual(remaining_subscription_days(self.user), 0)

        profile = Profile.objects.get(user=self.user)
        # Expiry side-effect: plan refs nulled, entries reset to 0.
        self.assertIsNone(profile.subcription)
        self.assertIsNone(profile.booster)
        self.assertEqual(profile.entries_remaining, 0)


class BoosterDaysTests(TestCase):
    def test_no_booster_is_zero(self):
        profile = Profile(booster=None)
        self.assertEqual(booster_days(profile), 0)

    def test_booster_returns_validity(self):
        booster = _make_plan(validity=7, is_booster=True, name="Booster")
        profile = Profile(booster=booster)
        self.assertEqual(booster_days(profile), 7)
