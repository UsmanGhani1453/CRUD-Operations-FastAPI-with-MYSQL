"""
Minimal Safepay (https://getsafepay.com) integration for sandbox payment testing.

Safepay's checkout is a client-side JS *button widget* (`@sfpy/checkout-components`),
not a hosted page you redirect to - the widget itself calls Safepay's Order API
when clicked, opens a Safepay overlay for card entry, and fires an `onPayment`
callback in the browser once the customer approves.
See https://github.com/getsafepay/safepay-checkout-components

Because that flow happens client-side, this backend module's job is:
1. Expose the public sandbox config (`SAFEPAY_API_KEY`, environment,
   currency) the frontend needs to render the button - see the
   `GET /orders/safepay/config` route.
2. Once the frontend's `onPayment` callback fires with a tracker token,
   verify that token server-side with Safepay before trusting it and
   marking the order paid (`POST /orders/{id}/safepay/confirm`) - never
   trust the browser-side callback alone, since anyone could call that
   confirm endpoint with a fake token otherwise.

This targets Safepay's SANDBOX environment for testing - no real money moves.
Get sandbox credentials at https://sandbox.api.getsafepay.com.
"""
from __future__ import annotations

import hashlib
import hmac
from typing import Any

import httpx

from app.core.config import (
    SAFEPAY_API_BASE_URL,
    SAFEPAY_API_KEY,
    SAFEPAY_SECRET_KEY,
    SAFEPAY_WEBHOOK_SECRET,
)

class SafepayError(RuntimeError):
    """Raised when Safepay's API returns an error or an unexpected shape."""


def is_configured() -> bool:
    return bool(SAFEPAY_API_KEY)


def verify_payment(tracker_token: str) -> dict[str, Any]:
    """
    Query Safepay for the current state of a tracker, to confirm a
    payment server-side rather than trusting the browser-side
    `onPayment` callback alone.
    """
    if not is_configured():
        raise SafepayError(
            "Safepay is not configured. Set SAFEPAY_API_KEY in your "
            ".env - see .env.example."
        )

    try:
        response = httpx.get(
            f"{SAFEPAY_API_BASE_URL}/order/v1/{tracker_token}",
            headers={
                "Content-Type": "application/json",
                "X-SFPY-MERCHANT-SECRET": SAFEPAY_SECRET_KEY
            },
            timeout=15.0,
        )
    except httpx.HTTPError as exc:
        raise SafepayError(f"Could not reach Safepay: {exc}") from exc

    if response.status_code >= 400:
        raise SafepayError(
            f"Safepay verify failed ({response.status_code}): {response.text}"
        )

    return response.json()


def payment_is_successful(verification_response: dict[str, Any]) -> bool:
    """
    Interpret a verify_payment()/webhook payload as paid or not paid.

    Safepay's docs show `state: "TRACKER_ENDED"` for a completed tracker
    (see https://safepay-docs.netlify.app/concepts/fetch-tracker/) -
    check what your sandbox actually returns and extend this if needed.
    """
    data = verification_response.get("data", verification_response)
    state = str(data.get("state") or data.get("status") or "").upper()
    return state in {"PAID", "COMPLETED", "TRACKER_ENDED", "SUCCESS", "SUCCEEDED"}


def verify_webhook_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """
    Verify a Safepay webhook's HMAC-SHA256 signature against
    SAFEPAY_WEBHOOK_SECRET, so we only trust webhook calls that actually
    came from Safepay.
    """
    if not SAFEPAY_WEBHOOK_SECRET or not signature_header:
        return False

    expected = hmac.new(
        SAFEPAY_WEBHOOK_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)