// Product prices are stored as plain integers in the backend (whole
// currency units - see models.Product.price / schemas.ProductBase.price).
// This formats them for display; swap the locale/currency to match your
// deployment.
// frontend/src/utils/money.js

export function formatMoney(amount) {
  return new Intl.NumberFormat("en-PK", {
    style: "currency",
    currency: "PKR",
    maximumFractionDigits: 0,
  }).format(amount);
}