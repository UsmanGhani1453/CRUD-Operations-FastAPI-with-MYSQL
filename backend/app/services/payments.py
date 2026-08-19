"""
Thin wrapper around the Stripe SDK. Keeping Stripe calls in one place means
the routes stay readable, and if you ever swap providers only this file
(and the webhook route) needs to change.
"""
import logging

import stripe
from fastapi import HTTPException

from app.core import config

logger = logging.getLogger(__name__)

stripe.api_key = config.STRIPE_SECRET_KEY


def _require_stripe_configured():
    if not config.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=503,
            detail=(
                "Payments are not configured on this server. "
                "Set STRIPE_SECRET_KEY in the backend .env."
            ),
        )


def create_payment_intent(amount_major_units: float, order_id: int) -> "stripe.PaymentIntent":
    """
    Create a Stripe PaymentIntent for an order.

    amount_major_units: the order total in whole currency units (e.g. 75.00
    for $75.00), matching how `Order.total_price` is stored. Stripe wants
    the amount in the currency's smallest unit (cents for USD), so we
    convert here rather than asking every caller to remember to do it.
    """
    _require_stripe_configured()
    amount_smallest_unit = round(amount_major_units * 100)

    try:
        return stripe.PaymentIntent.create(
            amount=amount_smallest_unit,
            currency=config.CURRENCY,
            metadata={"order_id": str(order_id)},
            automatic_payment_methods={"enabled": True},
        )
    except stripe.StripeError as exc:
        # Covers auth errors (bad key), connection errors (network/DNS),
        # rate limits, and invalid-request errors alike. Never leak the
        # raw exception (may include request internals) to the client -
        # log it server-side and return a clean, generic message instead.
        logger.error("Stripe PaymentIntent creation failed for order %s: %s", order_id, exc)
        raise HTTPException(
            status_code=502,
            detail="Could not reach the payment provider. Please try again shortly.",
        )


def construct_webhook_event(payload: bytes, sig_header: str) -> "stripe.Event":
    """
    Verify a webhook payload actually came from Stripe (not spoofed) using
    the signing secret from the Stripe Dashboard, then return the parsed
    event. Raises HTTPException on any verification failure.
    """
    _require_stripe_configured()
    if not config.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=503,
            detail="STRIPE_WEBHOOK_SECRET is not configured on this server.",
        )
    try:
        return stripe.Webhook.construct_event(
            payload, sig_header, config.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature")
