import axios from "axios";

// Base URL comes from Vite env var so it can differ between local dev
// and a deployed build without touching code. See .env.example.
const baseURL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const api = axios.create({ baseURL });

const TOKEN_KEY = "haak_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

// Attach the bearer token to every outgoing request, if we have one.
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Centralize "session expired" handling: any 401 clears the stored token
// and lets the app redirect to /login on next render (AuthContext watches
// this via the authExpired custom event).
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      setToken(null);
      window.dispatchEvent(new CustomEvent("auth-expired"));
    }
    return Promise.reject(error);
  }
);

// Normalizes FastAPI error payloads (which use { detail: "..." } or
// { detail: [{ msg, loc }, ...] } for validation errors) into one string.
export function extractErrorMessage(error, fallback = "Something went wrong.") {
  const detail = error?.response?.data?.detail;
  if (!detail) return error?.message || fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === "string" ? d : d.msg))
      .filter(Boolean)
      .join(" ");
  }
  return fallback;
}
