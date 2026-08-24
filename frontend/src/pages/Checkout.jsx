import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import {
  createOrder,
  fetchSafepayConfig,
  confirmSafepayPayment,
} from "../api/resources";
import { extractErrorMessage } from "../api/client";
import { formatMoney } from "../utils/money";
import SafepayButton from "../components/SafepayButton";

export default function Checkout() {
  const { lineItems, total, clear } = useCart();
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  // Once the order is placed, we hold onto it here and show the Safepay
  // button for that specific order (Safepay's checkout is a button you
  // render on the page, not a URL you redirect to).
  const [placedOrder, setPlacedOrder] = useState(null);
  const [safepayConfig, setSafepayConfig] = useState(null);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    fetchSafepayConfig()
      .then(setSafepayConfig)
      .catch(() => {
        // Non-fatal: the "pay later" button still works without Safepay
        // configured; we just won't render the Safepay button.
      });
  }, []);

  async function placeOrder() {
    setError("");
    setSubmitting(true);
    try {
      const items = lineItems.map((li) => ({
        product_id: li.product.id,
        quantity: li.quantity,
      }));
      const order = await createOrder(items);
      clear();
      setPlacedOrder(order);
    } catch (err) {
      // Most likely cause: stock changed between browsing and checkout
      // (the backend re-validates and locks stock at order time).
      setError(extractErrorMessage(err, "Couldn't place your order."));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSafepayPayment(data) {
    // The Safepay button's onPayment callback fired - the customer
    // approved payment in the Safepay overlay. Confirm it server-side
    // before trusting it (never mark paid off the client callback alone).
    const trackerToken = data?.tracker || data?.token || data?.payment?.tracker;
    if (!trackerToken) {
      setError("Safepay didn't return a payment reference. Please contact support.");
      return;
    }

    setConfirming(true);
    setError("");
    try {
      await confirmSafepayPayment(placedOrder.id, trackerToken);
      navigate("/orders", { state: { justPlacedId: placedOrder.id } });
    } catch (err) {
      setError(extractErrorMessage(err, "We couldn't confirm your payment. Please contact support."));
    } finally {
      setConfirming(false);
    }
  }

  if (lineItems.length === 0 && !placedOrder) {
    return (
      <div className="container">
        <div className="state-block">
          <h3>Your bag is empty</h3>
          <p>Add something from the shop before checking out.</p>
          <button className="btn btn-primary" onClick={() => navigate("/")}>
            Back to shop
          </button>
        </div>
      </div>
    );
  }

  // Step 2: order placed, waiting on payment.
  if (placedOrder) {
    return (
      <div className="container" style={{ maxWidth: 640, padding: "56px 24px" }}>
        <span className="eyebrow">Order #{placedOrder.id}</span>
        <h1 style={{ fontSize: 30 }}>Complete your payment</h1>

        {error && <div className="alert alert-error">{error}</div>}
        {confirming && <div className="alert alert-success">Confirming your payment…</div>}

        <div className="panel" style={{ padding: "18px 22px", marginBottom: 20 }}>
          <div className="cart-total-row" style={{ margin: 0 }}>
            <span>Total</span>
            <span>{formatMoney(placedOrder.total_price)}</span>
          </div>
        </div>

        {safepayConfig ? (
          <SafepayButton
            config={safepayConfig}
            orderId={placedOrder.id}
            amount={placedOrder.total_price}
            onPayment={handleSafepayPayment}
            onCancel={() => setError("Payment cancelled.")}
          />
        ) : (
          <p className="field-hint">
            Safepay isn't configured yet - set SAFEPAY_API_KEY in the backend .env.
          </p>
        )}

        <button
          className="btn btn-secondary btn-block"
          style={{ marginTop: 16 }}
          onClick={() => navigate("/orders", { state: { justPlacedId: placedOrder.id } })}
        >
          Pay later instead (order stays unpaid)
        </button>
      </div>
    );
  }

  // Step 1: review cart, place the order.
  return (
    <div className="container" style={{ maxWidth: 640, padding: "56px 24px" }}>
      <span className="eyebrow">Review &amp; confirm</span>
      <h1 style={{ fontSize: 30 }}>Your order</h1>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="panel" style={{ padding: 0, overflow: "hidden" }}>
        {lineItems.map(({ product, quantity }) => (
          <div
            key={product.id}
            className="cart-line"
            style={{ padding: "16px 22px", borderColor: "var(--ink-700)" }}
          >
            <div>
              <div className="name">{product.name}</div>
              <div className="unit">
                {quantity} &times; {formatMoney(product.price)}
              </div>
            </div>
            <span className="price-tag">{formatMoney(quantity * product.price)}</span>
          </div>
        ))}
        <div
          className="cart-total-row"
          style={{ padding: "18px 22px", background: "var(--ink-800)", margin: 0 }}
        >
          <span>Total</span>
          <span>{formatMoney(total)}</span>
        </div>
      </div>

      <button
        className="btn btn-primary btn-block"
        style={{ marginTop: 24 }}
        onClick={placeOrder}
        disabled={submitting}
      >
        {submitting ? "Placing order…" : "Place order"}
      </button>
    </div>
  );
}
