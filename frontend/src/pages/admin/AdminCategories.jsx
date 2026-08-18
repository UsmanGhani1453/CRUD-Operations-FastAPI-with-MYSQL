import { useEffect, useState } from "react";
import {
  fetchCategories,
  createCategory,
  updateCategory,
  deleteCategory,
} from "../../api/resources";
import { extractErrorMessage } from "../../api/client";
import { PageSpinner } from "../../components/RouteGuards";
import Modal from "../../components/Modal";

const EMPTY_FORM = { name: "", description: "" };

export default function AdminCategories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  function load() {
    setLoading(true);
    fetchCategories({ limit: 200 })
      .then(setCategories)
      .catch((err) => setError(extractErrorMessage(err, "Couldn't load categories.")))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  function openCreate() {
    setForm(EMPTY_FORM);
    setFormError("");
    setEditing({});
  }

  function openEdit(category) {
    setForm({ name: category.name, description: category.description || "" });
    setFormError("");
    setEditing(category);
  }

  async function handleSave(e) {
    e.preventDefault();
    setFormError("");
    setSaving(true);
    const payload = {
      name: form.name.trim(),
      description: form.description.trim() || null,
      extra_data: null,
    };
    try {
      if (editing?.id) {
        await updateCategory(editing.id, payload);
      } else {
        await createCategory(payload);
      }
      setEditing(null);
      load();
    } catch (err) {
      setFormError(extractErrorMessage(err, "Couldn't save category."));
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(category) {
    if (!window.confirm(`Delete "${category.name}"? Employees in this category will be affected.`)) return;
    try {
      await deleteCategory(category.id);
      load();
    } catch (err) {
      alert(extractErrorMessage(err, "Couldn't delete category."));
    }
  }

  return (
    <div>
      <div className="admin-toolbar">
        <p className="field-hint" style={{ margin: 0 }}>
          {categories.length} categor{categories.length === 1 ? "y" : "ies"}
        </p>
        <button className="btn btn-primary btn-sm" onClick={openCreate}>
          + New category
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
                <th>Description</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {categories.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.description || <span style={{ color: "var(--ivory-faint)" }}>—</span>}</td>
                  <td>
                    <div className="row-actions">
                      <button className="btn btn-outline btn-sm" onClick={() => openEdit(c)}>
                        Edit
                      </button>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(c)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {categories.length === 0 && (
                <tr>
                  <td colSpan={3} style={{ textAlign: "center", color: "var(--ivory-faint)" }}>
                    No categories yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {editing !== null && (
        <Modal title={editing.id ? "Edit category" : "New category"} onClose={() => setEditing(null)}>
          {formError && <div className="alert alert-error">{formError}</div>}
          <form onSubmit={handleSave}>
            <div className="field">
              <label htmlFor="c-name">Name</label>
              <input
                id="c-name"
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>
            <div className="field">
              <label htmlFor="c-desc">Description</label>
              <textarea
                id="c-desc"
                rows={3}
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <button className="btn btn-primary btn-block" type="submit" disabled={saving}>
              {saving ? "Saving…" : "Save category"}
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}
