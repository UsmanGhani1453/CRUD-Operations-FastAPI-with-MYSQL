import { useEffect, useState } from "react";
import {
  fetchProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  uploadProductImage,
} from "../../api/resources";
import { extractErrorMessage } from "../../api/client";
import { formatMoney } from "../../utils/money";
import { PageSpinner } from "../../components/RouteGuards";
import Modal from "../../components/Modal";

const EMPTY_FORM = { name: "", price: "", stock: "", image_url: "" };

export default function AdminProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null); // product being edited, or {} for new
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

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
      image_url: product.image_url || "",
    });
    setFormError("");
    setEditing(product);
  }

  async function handleImageChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFormError("");
    setUploading(true);
    try {
      const { url } = await uploadProductImage(file);
      setForm((f) => ({ ...f, image_url: url }));
    } catch (err) {
      setFormError(extractErrorMessage(err, "Couldn't upload image."));
    } finally {
      setUploading(false);
      e.target.value = ""; // allow re-selecting the same file later
    }
  }

  async function handleSave(e) {
    e.preventDefault();
    setFormError("");
    setSaving(true);
    const payload = {
      name: form.name.trim(),
      price: Number(form.price),
      stock: Number(form.stock),
      image_url: form.image_url.trim() || null,
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
                <th></th>
                <th>Name</th>
                <th>Price</th>
                <th>Stock</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id}>
                  <td>
                    <div className="admin-thumb">
                      {p.image_url ? (
                        <img src={p.image_url} alt={p.name} />
                      ) : (
                        <span>No image</span>
                      )}
                    </div>
                  </td>
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
                  <td colSpan={5} style={{ textAlign: "center", color: "var(--ivory-faint)" }}>
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
            <div className="field">
              <label htmlFor="p-image">Product picture</label>
              <input
                id="p-image"
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                onChange={handleImageChange}
                disabled={uploading}
              />
              {uploading && <p className="field-hint">Uploading…</p>}
              {form.image_url && !uploading && (
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 10 }}>
                  <div className="admin-thumb admin-thumb-preview">
                    <img src={form.image_url} alt="Preview" />
                  </div>
                  <button
                    type="button"
                    className="btn btn-outline btn-sm"
                    onClick={() => setForm((f) => ({ ...f, image_url: "" }))}
                  >
                    Remove
                  </button>
                </div>
              )}
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
            <button className="btn btn-primary btn-block" type="submit" disabled={saving || uploading}>
              {saving ? "Saving…" : "Save product"}
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}
