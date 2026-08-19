import { useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Elements, PaymentElement, useElements, useStripe } from "@stripe/react-stripe-js";
import { getStripe } from "../api/stripe";
import { formatMoney } from "../utils/money";

export default function Payment() {
  const { orderId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  // The order + client_secret are handed off from Checkout via router
  // state (set right after order creation, when they're fresh). If
  // someone lands here directly - refreshed the page, followed a stale
  // link - we don't have a valid client_secret to resume with, so send
  // them to their order history instead of showing a broken form.
  const order = location.state?.order;
  const clientSecret = location.state?.clientSecret;

  if (!order || !clientSecret) {
    return (
      <div className="container">
        <div className="state-block">
          <h3>Nothing to pay right now</h3>
          <p>
            This page only works right after placing an order. Check your
            order history to see its current status.
          </p>
          <button className="btn btn-primary" onClick={() => navigate("/orders")}>
            Go to my orders
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ maxWidth: 520, padding: "56px 24px" }}>
      <span className="eyebrow">Order #{orderId}</span>
      <h1 style={{ fontSize: 28 }}>Payment</h1>
      <p className="field-hint" style={{ marginBottom: 24 }}>
        Total due: <strong style={{ color: "var(--ivory)" }}>{formatMoney(order.total_price)}</strong>
      </p>

      <div className="panel">
        <Elements
          stripe={getStripe()}
          options={{
            clientSecret,
            appearance: {
              theme: "night",
              variables: {
                colorPrimary: "#c19a4e",
                colorBackground: "#17140f",
                colorText: "#ece5d6",
                colorDanger: "#a6493b",
                fontFamily: "Inter, sans-serif",
                borderRadius: "3px",
              },
            },
          }}
        >
          <PaymentForm orderId={orderId} />
        </Elements>
      </div>
    </div>
  );
}

function PaymentForm({ orderId }) {
  const stripe = useStripe();
  const elements = useElements();
  const navigate = useNavigate();

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!stripe || !elements) return; // Stripe.js hasn't finished loading yet

    setSubmitting(true);
    setError("");

    // redirect: "if_required" keeps the customer on this page for card
    // payments (the common case) and only navigates away if the chosen
    // payment method truly requires a redirect (e.g. certain bank
    // methods). Either way, the actual "did this succeed" source of
    // truth is the backend's Stripe webhook, not this client-side result -
    // this just tells us whether to show a success or error state here.
    const { error: confirmError, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/orders`,
      },
      redirect: "if_required",
    });

    if (confirmError) {
      setError(confirmError.message || "Payment failed. Please try again.");
      setSubmitting(false);
      return;
    }

    if (paymentIntent && paymentIntent.status === "succeeded") {
      navigate("/orders", { state: { justPlacedId: orderId, paymentConfirmed: true } });
      return;
    }

    // Some methods land in "processing" - the webhook will settle it
    // shortly. Send the customer to their orders page either way; the
    // payment_status badge there reflects the real, webhook-confirmed state.
    navigate("/orders", { state: { justPlacedId: orderId, paymentConfirmed: false } });
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="alert alert-error">{error}</div>}
      <PaymentElement />
      <button
        className="btn btn-primary btn-block"
        type="submit"
        disabled={!stripe || submitting}
        style={{ marginTop: 20 }}
      >
        {submitting ? "Processing…" : "Pay now"}
      </button>
    </form>
  );
}
