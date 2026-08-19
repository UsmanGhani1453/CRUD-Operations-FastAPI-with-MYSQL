import logging

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.session import get_db
from app.models.order import Order
from app.services import payments

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Stripe calls this endpoint directly (not the browser) whenever a
    payment's status changes. This is the source of truth for "did the
    customer actually pay" - never trust the frontend's confirmPayment
    call alone for that, since a closed tab or a client-side bug could
    silently drop it.

    Configure this URL in your Stripe Dashboard (or via `stripe listen
    --forward-to localhost:8000/webhooks/stripe` for local testing) and
    put its signing secret in STRIPE_WEBHOOK_SECRET.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    event = payments.construct_webhook_event(payload, sig_header)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order = (
            db.query(Order)
            .filter(Order.stripe_payment_intent_id == intent["id"])
            .first()
        )
        if order:
            order.payment_status = "paid"  # type: ignore
            db.commit()
        else:
            logger.warning(
                "Received payment_intent.succeeded for unknown intent %s",
                intent["id"],
            )

    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        order = (
            db.query(Order)
            .filter(Order.stripe_payment_intent_id == intent["id"])
            .first()
        )
        if order:
            order.payment_status = "failed"  # type: ignore
            db.commit()

    return {"received": True}
