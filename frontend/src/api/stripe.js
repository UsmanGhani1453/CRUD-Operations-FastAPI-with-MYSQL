import { loadStripe } from "@stripe/stripe-js";

// loadStripe() is memoized internally by Stripe.js itself, but keeping our
// own singleton promise avoids re-triggering the dynamic script load on
// every re-render of whatever component calls this.
let stripePromise;

export function getStripe() {
  const key = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
  if (!stripePromise) {
    if (!key || key.startsWith("pk_test_...")) {
      // Don't call loadStripe with a placeholder - it'll throw a confusing
      // error deep in Stripe.js. Surface a clear one instead.
      return Promise.reject(
        new Error(
          "VITE_STRIPE_PUBLISHABLE_KEY is not set. Add it to frontend/.env.local."
        )
      );
    }
    stripePromise = loadStripe(key);
  }
  return stripePromise;
}
