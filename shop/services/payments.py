"""Payment gateway clients.

Razorpay is the primary gateway. InstaMojo is loaded best-effort because the
upstream wrapper is unmaintained and lacks Python 3.10+ wheels.
"""
from __future__ import annotations

import logging

import razorpay
from django.conf import settings

logger = logging.getLogger(__name__)

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

instamojo_client = None
try:  # pragma: no cover - depends on optional, unmaintained SDK
    from instamojo_wrapper import Instamojo

    instamojo_client = Instamojo(
        api_key=settings.INSTAMOJO_API_KEY,
        auth_token=settings.INSTAMOJO_AUTH_TOKEN,
        endpoint=settings.INSTAMOJO_ENDPOINT,
    )
except Exception:
    logger.info(
        "instamojo_wrapper is unavailable; InstaMojo flows will be disabled."
    )
