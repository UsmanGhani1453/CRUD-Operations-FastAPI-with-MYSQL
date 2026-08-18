import { useEffect, useState } from "react";
import {
  fetchProducts,
  createProduct,
  updateProduct,
  deleteProduct,
} from "../../api/resources";
import { extractErrorMessage } from "../../api/client";
import { formatMoney } from "../../utils/money";
import { PageSpinner } from "../../components/RouteGuards";
import Modal from "../../components/Modal";

const EMPTY_FORM = { name: "", price: "", stock: "" };

export default function AdminProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null); // product being edited, or {} for new
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  function load() {
    setLoading(true);
    fetchProducts({ limit: 200 })
      .then(setProducts)
      .catch((err) => setError(extractErrorMessage(err, "Couldn't load products.")))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  function openCreate() {
    setForm(EMPTY_FORM);
    setFormError("");
    setEditing({});
  }

  function openEdit(product) {
    setForm({
      name: product.name,
      price: String(product.price),
      stock: String(product.stock),
    });
    setFormError("");
    setEditing(product);
  }

  async function handleSave(e) {
    e.preventDefault();
    setFormError("");
    setSaving(true);
    const payload = {
      name: form.name.trim(),
      price: Number(form.price),
      stock: Number(form.stock),
      extra_data: null,
    };
    try {
      if (editing?.id) {
        await updateProduct(editing.id, payload);
      } else {
        await createProduct(payload);
      }
      setEditing(null);
      load();
    } catch (err) {
      setFormError(extractErrorMessage(err, "Couldn't save product."));
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(product) {
    if (!window.confirm(`Delete "${product.name}"? This cannot be undone.`)) return;
    try {
      await deleteProduct(product.id);
      load();
    } catch (err) {
      alert(extractErrorMessage(err, "Couldn't delete product."));
    }
  }

  return (
    <div>
      <div className="admin-toolbar">
        <p className="field-hint" style={{ margin: 0 }}>
          {products.length} product{products.length === 1 ? "" : "s"}
        </p>
        <button className="btn btn-primary btn-sm" onClick={openCreate}>
          + New product
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {loading && <PageSpinner />}

      {!loading && !error && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Price</th>
                <th>Stock</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id}>
                  <td>{p.name}</td>
                  <td>{formatMoney(p.price)}</td>
                  <td>{p.stock}</td>
                  <td>
                    <div className="row-actions">
                      <button className="btn btn-outline btn-sm" onClick={() => openEdit(p)}>
                        Edit
                      </button>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(p)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {products.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ textAlign: "center", color: "var(--ivory-faint)" }}>
                    No products yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {editing !== null && (
        <Modal title={editing.id ? "Edit product" : "New product"} onClose={() => setEditing(null)}>
          {formError && <div className="alert alert-error">{formError}</div>}
          <form onSubmit={handleSave}>
            <div className="field">
              <label htmlFor="p-name">Name</label>
              <input
                id="p-name"
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>
            <div className="field-row">
              <div className="field">
                <label htmlFor="p-price">Price</label>
                <input
                  id="p-price"
                  type="number"
                  min="1"
                  required
                  value={form.price}
                  onChange={(e) => setForm({ ...form, price: e.target.value })}
                />
              </div>
              <div className="field">
                <label htmlFor="p-stock">Stock</label>
                <input
                  id="p-stock"
                  type="number"
                  min="0"
                  required
                  value={form.stock}
                  onChange={(e) => setForm({ ...form, stock: e.target.value })}
                />
              </div>
            </div>
            <button className="btn btn-primary btn-block" type="submit" disabled={saving}>
              {saving ? "Saving…" : "Save product"}
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}
