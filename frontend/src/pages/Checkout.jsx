import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { createOrder } from "../api/resources";
import { extractErrorMessage } from "../api/client";
import { formatMoney } from "../utils/money";

export default function Checkout() {
  const { lineItems, total, clear } = useCart();
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

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
      navigate("/orders", { state: { justPlacedId: order.id } });
    } catch (err) {
      // Most likely cause: stock changed between browsing and checkout
      // (the backend re-validates and locks stock at order time).
      setError(extractErrorMessage(err, "Couldn't place your order."));
    } finally {
      setSubmitting(false);
    }
  }

  if (lineItems.length === 0) {
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
