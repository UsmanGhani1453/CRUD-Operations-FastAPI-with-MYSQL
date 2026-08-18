const STYLES = {
  PENDING: "badge-brass",
  PROCESSING: "badge-brass",
  SHIPPED: "badge-moss",
  DELIVERED: "badge-moss",
  CANCELLED: "badge-clay",
};

export default function StatusBadge({ status }) {
  const cls = STYLES[status] || "";
  return <span className={`badge ${cls}`}>{status}</span>;
}
