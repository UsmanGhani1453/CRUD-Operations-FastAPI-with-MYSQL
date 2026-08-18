import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { fetchMyOrders } from "../api/resources";
import { extractErrorMessage } from "../api/client";
import { formatMoney } from "../utils/money";
import { PageSpinner } from "../components/RouteGuards";
import StatusBadge from "../components/StatusBadge";

export default function MyOrders() {
  const location = useLocation();
  const justPlacedId = location.state?.justPlacedId;
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchMyOrders()
      .then(setOrders)
      .catch((err) => setError(extractErrorMessage(err, "Couldn't load your orders.")))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container" style={{ padding: "56px 24px 80px" }}>
      <span className="eyebrow">Order history</span>
      <h1 style={{ fontSize: 30 }}>My orders</h1>

      {justPlacedId && (
        <div className="alert alert-success">
          Order #{justPlacedId} placed successfully.
        </div>
      )}
      {error && <div className="alert alert-error">{error}</div>}
      {loading && <PageSpinner />}

      {!loading && !error && orders.length === 0 && (
        <div className="state-block">
          <h3>No orders yet</h3>
          <p>Once you place an order it'll show up here.</p>
        </div>
      )}

      {!loading &&
        orders
          .slice()
          .sort((a, b) => b.id - a.id)
          .map((order) => (
            <div key={order.id} className="panel" style={{ marginBottom: 16 }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 14,
                }}
              >
                <div>
                  <strong>Order #{order.id}</strong>
                  <div className="field-hint">
                    {new Date(order.created_at).toLocaleString()}
                  </div>
                </div>
                <StatusBadge status={order.status} />
              </div>

              {order.items.map((item) => (
                <div
                  key={item.id}
                  className="cart-line"
                  style={{ borderColor: "var(--ink-800)" }}
                >
                  <span className="unit">
                    Product #{item.product_id} &middot; {item.quantity} &times;{" "}
                    {formatMoney(item.unit_price)}
                  </span>
                  <span>{formatMoney(item.quantity * item.unit_price)}</span>
                </div>
              ))}

              <div className="cart-total-row" style={{ marginTop: 10, marginBottom: 0 }}>
                <span>Total</span>
                <span>{formatMoney(order.total_price)}</span>
              </div>
            </div>
          ))}
    </div>
  );
}
