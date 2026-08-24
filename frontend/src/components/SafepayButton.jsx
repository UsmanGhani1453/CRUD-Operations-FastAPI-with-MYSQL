import { useState } from "react";
import { api, extractErrorMessage } from "../api/client";

export default function SafepayButton({ orderId, config, onCancel }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCheckout = async () => {
    setLoading(true);
    setError("");

    try {
      // 1. Fetch tracker token from backend session endpoint
      const response = await api.post(`/orders/${orderId}/safepay/session`);
      const trackerToken = response.data.tracker_token;

      if (!trackerToken) {
        throw new Error("Could not retrieve payment tracker from server.");
      }

      // 2. Load Safepay Checkout SDK dynamically if missing
      if (!window.safepay) {
        await new Promise((resolve, reject) => {
          const script = document.createElement("script");
          script.src = "https://unpkg.com/@sfpy/checkout-components@0.1.0/dist/sfpy-checkout.js";
          script.async = true;
          script.onload = resolve;
          script.onerror = () => reject(new Error("Failed to load Safepay payment script."));
          document.head.appendChild(script);
        });
      }

      // 3. Open Safepay's secure credit/debit card popup modal
      const checkout = new window.safepay.Checkout({
        env: config?.environment || "sandbox",
        tracker: trackerToken,
        apiKey: config?.api_key,
        onComplete: (charge) => {
          window.location.href = `/orders?justPlacedId=${orderId}`;
        },
        onCancelled: () => {
          setLoading(false);
        },
      });

      checkout.render();
    } catch (err) {
      setError(extractErrorMessage(err, "Could not open Safepay payment window."));
      setLoading(false);
    }
  };

  return (
    <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: "10px" }}>
      {error && <div className="alert alert-error">{error}</div>}
      <button 
        type="button" 
        className="btn btn-primary btn-block" 
        style={{ padding: "14px", fontSize: "15px", fontWeight: "bold" }}
        onClick={handleCheckout}
        disabled={loading}
      >
        {loading ? "Opening Secure Payment..." : "Pay via Safepay"}
      </button>
      {onCancel && (
        <button 
          type="button" 
          className="btn btn-outline btn-block" 
          onClick={onCancel}
          disabled={loading}
        >
          Cancel Payment
        </button>
      )}
    </div>
  );
}