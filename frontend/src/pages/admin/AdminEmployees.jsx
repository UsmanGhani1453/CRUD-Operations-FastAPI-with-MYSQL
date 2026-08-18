import { useEffect, useState } from "react";
import { api } from "../../api/client";
import {
  fetchCategories,
  createEmployee,
  updateEmployee,
  deleteEmployee,
} from "../../api/resources";
import { extractErrorMessage } from "../../api/client";
import { PageSpinner } from "../../components/RouteGuards";
import Modal from "../../components/Modal";

const EMPTY_FORM = { name: "", email: "", category_id: "" };

export default function AdminEmployees() {
  const [employees, setEmployees] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  function load() {
    setLoading(true);
    setError("");
    Promise.all([
      api.get("/employees/", { params: { limit: 200 } }).then((r) => r.data),
      fetchCategories({ limit: 200 }),
    ])
      .then(([emps, cats]) => {
        setEmployees(emps);
        setCategories(cats);
      })
      .catch((err) => setError(extractErrorMessage(err, "Couldn't load employees.")))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  function categoryName(id) {
    return categories.find((c) => c.id === id)?.name || `#${id}`;
  }

  function openCreate() {
    setForm({ ...EMPTY_FORM, category_id: categories[0]?.id ?? "" });
    setFormError("");
    setEditing({});
  }

  function openEdit(employee) {
    setForm({
      name: employee.name,
      email: employee.email,
      category_id: employee.category_id,
    });
    setFormError("");
    setEditing(employee);
  }

  async function handleSave(e) {
    e.preventDefault();
    setFormError("");
    setSaving(true);
    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
      category_id: Number(form.category_id),
      extra_data: null,
    };
    try {
      if (editing?.id) {
        await updateEmployee(editing.id, payload);
      } else {
        await createEmployee(payload);
      }
      setEditing(null);
      load();
    } catch (err) {
      setFormError(extractErrorMessage(err, "Couldn't save employee."));
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(employee) {
    if (!window.confirm(`Remove ${employee.name}?`)) return;
    try {
      await deleteEmployee(employee.id);
      load();
    } catch (err) {
      alert(extractErrorMessage(err, "Couldn't delete employee."));
    }
  }

  const noCategoriesYet = !loading && categories.length === 0;

  return (
    <div>
      <div className="admin-toolbar">
        <p className="field-hint" style={{ margin: 0 }}>
          {employees.length} employee{employees.length === 1 ? "" : "s"}
        </p>
        <button
          className="btn btn-primary btn-sm"
          onClick={openCreate}
          disabled={noCategoriesYet}
          title={noCategoriesYet ? "Create a category first" : undefined}
        >
          + New employee
        </button>
      </div>

      {noCategoriesYet && (
        <div className="alert alert-error">
          You need at least one category before adding employees.
        </div>
      )}
      {error && <div className="alert alert-error">{error}</div>}
      {loading && <PageSpinner />}

      {!loading && !error && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Category</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {employees.map((e) => (
                <tr key={e.id}>
                  <td>{e.name}</td>
                  <td>{e.email}</td>
                  <td>{categoryName(e.category_id)}</td>
                  <td>
                    <div className="row-actions">
                      <button className="btn btn-outline btn-sm" onClick={() => openEdit(e)}>
                        Edit
                      </button>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(e)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {employees.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ textAlign: "center", color: "var(--ivory-faint)" }}>
                    No employees yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {editing !== null && (
        <Modal title={editing.id ? "Edit employee" : "New employee"} onClose={() => setEditing(null)}>
          {formError && <div className="alert alert-error">{formError}</div>}
          <form onSubmit={handleSave}>
            <div className="field">
              <label htmlFor="e-name">Name</label>
              <input
                id="e-name"
                required
                value={form.name}
                onChange={(f) => setForm({ ...form, name: f.target.value })}
              />
            </div>
            <div className="field">
              <label htmlFor="e-email">Email</label>
              <input
                id="e-email"
                type="email"
                required
                value={form.email}
                onChange={(f) => setForm({ ...form, email: f.target.value })}
              />
            </div>
            <div className="field">
              <label htmlFor="e-cat">Category</label>
              <select
                id="e-cat"
                required
                value={form.category_id}
                onChange={(f) => setForm({ ...form, category_id: f.target.value })}
              >
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <button className="btn btn-primary btn-block" type="submit" disabled={saving}>
              {saving ? "Saving…" : "Save employee"}
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}
