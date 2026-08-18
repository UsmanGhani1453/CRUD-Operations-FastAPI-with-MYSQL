import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { extractErrorMessage } from "../api/client";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const user = await login(email, password);
      navigate(user.role === "admin" ? "/admin" : from, { replace: true });
    } catch (err) {
      setError(extractErrorMessage(err, "Incorrect email or password."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="container auth-page">
      <div className="panel auth-panel">
        <span className="eyebrow">Welcome back</span>
        <h1 style={{ fontSize: 30, marginTop: 8 }}>Sign in to HAAK</h1>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button className="btn btn-primary btn-block" type="submit" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="field-hint" style={{ marginTop: 18 }}>
          Accounts are created by an administrator. Contact your admin if you
          don't have credentials yet.
        </p>
      </div>
    </div>
  );
}
