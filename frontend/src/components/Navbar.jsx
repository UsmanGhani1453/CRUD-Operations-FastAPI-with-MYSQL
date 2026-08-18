import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function Navbar() {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const { count, openCart } = useCart();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="brand">
          <span className="brand-mark">HAAK</span>
          <span className="brand-sub">Leather &amp; Metal</span>
        </Link>

        <nav className="nav-links">
          <Link to="/">Shop</Link>
          {isAuthenticated && <Link to="/orders">My Orders</Link>}
          {isAdmin && <Link to="/admin">Admin</Link>}
        </nav>

        <div className="nav-actions">
          <button className="cart-btn" onClick={openCart} aria-label="Open cart">
            Cart
            {count > 0 && <span className="cart-count">{count}</span>}
          </button>

          {isAuthenticated ? (
            <div className="nav-user">
              <span className="nav-email">{user?.email}</span>
              <button className="btn btn-ghost btn-sm" onClick={handleLogout}>
                Log out
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn btn-outline btn-sm">
              Log in
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
