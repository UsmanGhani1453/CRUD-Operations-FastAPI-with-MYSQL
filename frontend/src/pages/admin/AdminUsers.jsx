import { useState } from "react";
import { createUser } from "../../api/resources";
import { extractErrorMessage } from "../../api/client";

export default function AdminUsers() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);
    try {
      const user = await createUser({
        email: form.email.trim(),
        password: form.password,
      });
      setSuccess(
        `User ${user.email} created. A verification email has been sent to them.`
      );
      setForm({ email: "", password: "" });
    } catch (err) {
      setError(extractErrorMessage(err, "Couldn't create user."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ maxWidth: 440 }}>
      <p className="field-hint" style={{ marginBottom: 20 }}>
        New accounts are created here by an admin, then verify their own
        email via the link sent to them. To grant admin rights, promote the
        user's <code>role</code> column directly in the database — there's
        no API endpoint for that by design.
      </p>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <form className="panel" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="u-email">Email</label>
          <input
            id="u-email"
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="u-password">Temporary password</label>
          <input
            id="u-password"
            type="password"
            minLength={8}
            required
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          <span className="field-hint">At least 8 characters.</span>
        </div>
        <button className="btn btn-primary btn-block" type="submit" disabled={saving}>
          {saving ? "Creating…" : "Create user"}
        </button>
      </form>
    </div>
  );
}
