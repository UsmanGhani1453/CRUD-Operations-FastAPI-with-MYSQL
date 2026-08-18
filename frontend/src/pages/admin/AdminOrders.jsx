import { useEffect, useState } from "react";
import { fetchAllOrders, updateOrderStatus } from "../../api/resources";
import { extractErrorMessage } from "../../api/client";
import { formatMoney } from "../../utils/money";
import { PageSpinner } from "../../components/RouteGuards";
import StatusBadge from "../../components/StatusBadge";

const STATUSES = ["PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"];

export default function AdminOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingId, setUpdatingId] = useState(null);

  function load() {
    setLoading(true);
    fetchAllOrders({ limit: 200 })
      .then(setOrders)
      .catch((err) => setError(extractErrorMessage(err, "Couldn't load orders.")))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleStatusChange(order, status) {
    setUpdatingId(order.id);
    try {
      const updated = await updateOrderStatus(order.id, status);
      setOrders((prev) => prev.map((o) => (o.id === updated.id ? updated : o)));
    } catch (err) {
      alert(extractErrorMessage(err, "Couldn't update order status."));
    } finally {
      setUpdatingId(null);
    }
  }

  return (
    <div>
      <p className="field-hint" style={{ marginBottom: 16 }}>
        {orders.length} order{orders.length === 1 ? "" : "s"}
      </p>

      {error && <div className="alert alert-error">{error}</div>}
      {loading && <PageSpinner />}

      {!loading && !error && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Items</th>
                <th>Total</th>
                <th>Placed</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {orders
                .slice()
                .sort((a, b) => b.id - a.id)
                .map((order) => (
                  <tr key={order.id}>
                    <td>#{order.id}</td>
                    <td>User #{order.user_id}</td>
                    <td>
                      {order.items.reduce((sum, i) => sum + i.quantity, 0)} item
                      {order.items.length === 1 ? "" : "s"}
                    </td>
                    <td>{formatMoney(order.total_price)}</td>
                    <td>{new Date(order.created_at).toLocaleDateString()}</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <StatusBadge status={order.status} />
                        <select
                          value={order.status}
                          disabled={updatingId === order.id}
                          onChange={(e) => handleStatusChange(order, e.target.value)}
                          style={{
                            background: "var(--ink-900)",
                            border: "1px solid var(--ink-600)",
                            color: "var(--ivory)",
                            borderRadius: 3,
                            padding: "5px 8px",
                            fontSize: 12.5,
                          }}
                        >
                          {STATUSES.map((s) => (
                            <option key={s} value={s}>
                              {s}
                            </option>
                          ))}
                        </select>
                      </div>
                    </td>
                  </tr>
                ))}
              {orders.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", color: "var(--ivory-faint)" }}>
                    No orders yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
