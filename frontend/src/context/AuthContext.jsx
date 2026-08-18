import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getToken, setToken as persistToken } from "../api/client";
import { fetchMe, login as loginRequest } from "../api/resources";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    if (!getToken()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await fetchMe();
      setUser(me);
    } catch {
      persistToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
    // The API client dispatches this when any request comes back 401,
    // so an expired/invalid token clears the session everywhere at once.
    const onExpire = () => setUser(null);
    window.addEventListener("auth-expired", onExpire);
    return () => window.removeEventListener("auth-expired", onExpire);
  }, [loadUser]);

  async function login(email, password) {
    const { access_token } = await loginRequest(email, password);
    persistToken(access_token);
    const me = await fetchMe();
    setUser(me);
    return me;
  }

  function logout() {
    persistToken(null);
    setUser(null);
  }

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.role === "admin",
    login,
    logout,
    refresh: loadUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
