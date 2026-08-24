import { useEffect, useRef, useState } from "react";

const SCRIPT_SRC = "https://unpkg.com/@sfpy/checkout-components@0.1.0/dist/sfpy-checkout.js";

let scriptLoadingPromise = null;

function loadSafepayScript() {
  if (window.safepay) return Promise.resolve();
  if (scriptLoadingPromise) return scriptLoadingPromise;

  scriptLoadingPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = SCRIPT_SRC;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Failed to load Safepay checkout script"));
    document.head.appendChild(script);
  });

  return scriptLoadingPromise;
}

/**
 * Renders Safepay's hosted payment button (a Safepay-hosted overlay, not
 * a redirect - see https://github.com/getsafepay/safepay-checkout-components).
 *
 * `config` is the public { api_key, environment, currency } from
 * GET /orders/safepay/config. `onPayment(data)` fires once the customer
 * approves payment in the Safepay overlay - verify it server-side before
 * trusting it (see confirmSafepayPayment in api/resources.js).
 */
export default function SafepayButton({ config, orderId, amount, onPayment, onCancel }) {
  const containerRef = useRef(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    loadSafepayScript()
      .then(() => {
        if (cancelled || !containerRef.current || !window.safepay) return;

        // Clear any previous render (e.g. on re-mount / fast refresh).
        containerRef.current.innerHTML = "";

        window.safepay
          .Button({
            env: config.environment,
            client: { [config.environment]: config.api_key },
            style: { mode: "dark", size: "large", variant: "primary" },
            orderId: String(orderId),
            source: "website",
            payment: { currency: config.currency, amount },
            onPayment: (data) => onPayment(data),
            onCancel: () => onCancel && onCancel(),
          })
          .render(containerRef.current);
      })
      .catch((err) => setError(err.message || "Couldn't load Safepay."));

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderId, amount]);

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return <div ref={containerRef} />;
}
