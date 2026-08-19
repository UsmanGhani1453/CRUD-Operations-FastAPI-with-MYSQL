const STYLES = {
  paid: "badge-moss",
  unpaid: "badge-brass",
  failed: "badge-clay",
};

const LABELS = {
  paid: "Paid",
  unpaid: "Payment pending",
  failed: "Payment failed",
};

export default function PaymentStatusBadge({ status }) {
  const cls = STYLES[status] || "";
  return <span className={`badge ${cls}`}>{LABELS[status] || status}</span>;
}
