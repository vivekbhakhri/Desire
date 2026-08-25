"""Pricing helpers: cart totals, ref code generation."""
from __future__ import annotations

import random
import string
from typing import Iterable


def create_ref_code(length: int = 20) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def cart_totals(items: Iterable) -> dict[str, float]:
    """Aggregate sub-total, grand-total, tax for the items in a cart."""
    sub_total = grand_total = tax_amount = 0.0
    for item in items:
        sub_total += item.price or 0
        grand_total += item.totalPrice or 0
        tax_amount += item.tax or 0
    return {
        "sub_total": sub_total,
        "grand_total": grand_total,
        "tax_amount": tax_amount,
    }


def effective_price(item) -> float:
    return item.discount_price if item.discount_price else item.price
