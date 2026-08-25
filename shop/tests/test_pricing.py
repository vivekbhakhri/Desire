"""Unit tests for `core.services.pricing` — pure functions, no DB needed."""
from __future__ import annotations

from types import SimpleNamespace
from unittest import TestCase

from shop.services.pricing import cart_totals, create_ref_code, effective_price


class CreateRefCodeTests(TestCase):
    def test_default_length_is_20(self):
        code = create_ref_code()
        self.assertEqual(len(code), 20)

    def test_custom_length(self):
        self.assertEqual(len(create_ref_code(length=8)), 8)

    def test_uses_lowercase_alphanumeric_alphabet(self):
        code = create_ref_code(length=200)
        self.assertTrue(all(c.isalnum() and not c.isupper() for c in code))


class EffectivePriceTests(TestCase):
    def test_returns_discount_when_present(self):
        item = SimpleNamespace(price=100.0, discount_price=80.0)
        self.assertEqual(effective_price(item), 80.0)

    def test_returns_full_price_when_discount_falsy(self):
        for discount in (None, 0, 0.0, False):
            with self.subTest(discount=discount):
                item = SimpleNamespace(price=100.0, discount_price=discount)
                self.assertEqual(effective_price(item), 100.0)


class CartTotalsTests(TestCase):
    def _line(self, price, total, tax):
        return SimpleNamespace(price=price, totalPrice=total, tax=tax)

    def test_empty_cart_zeros_out(self):
        self.assertEqual(
            cart_totals([]),
            {"sub_total": 0.0, "grand_total": 0.0, "tax_amount": 0.0},
        )

    def test_aggregates_each_field(self):
        result = cart_totals(
            [
                self._line(100, 110, 10),
                self._line(50, 55, 5),
                self._line(200, 220, 20),
            ]
        )
        self.assertEqual(result["sub_total"], 350)
        self.assertEqual(result["grand_total"], 385)
        self.assertEqual(result["tax_amount"], 35)

    def test_handles_none_fields(self):
        # Real OrderItem rows can have null `tax` / `totalPrice` before checkout.
        result = cart_totals(
            [self._line(price=None, total=None, tax=None), self._line(10, 11, 1)]
        )
        self.assertEqual(result["sub_total"], 10)
        self.assertEqual(result["grand_total"], 11)
        self.assertEqual(result["tax_amount"], 1)
