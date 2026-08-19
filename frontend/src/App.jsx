import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import CartDrawer from "./components/CartDrawer";
import { RequireAuth, RequireAdmin } from "./components/RouteGuards";

import Storefront from "./pages/Storefront";
import Login from "./pages/Login";
import Checkout from "./pages/Checkout";
import MyOrders from "./pages/MyOrders";

import AdminLayout from "./pages/admin/AdminLayout";
import AdminProducts from "./pages/admin/AdminProducts";
import AdminCategories from "./pages/admin/AdminCategories";
import AdminEmployees from "./pages/admin/AdminEmployees";
import AdminOrders from "./pages/admin/AdminOrders";
import AdminUsers from "./pages/admin/AdminUsers";

export default function App() {
  return (
    <>
      <Navbar />
      <CartDrawer />

      <main style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<Storefront />} />
          <Route path="/login" element={<Login />} />

          <Route
            path="/checkout"
            element={
              <RequireAuth>
                <Checkout />
              </RequireAuth>
            }
          />
          <Route
            path="/orders"
            element={
              <RequireAuth>
                <MyOrders />
              </RequireAuth>
            }
          />

          <Route
            path="/admin"
            element={
              <RequireAdmin>
                <AdminLayout />
              </RequireAdmin>
            }
          >
            <Route index element={<AdminProducts />} />
            <Route path="categories" element={<AdminCategories />} />
            <Route path="employees" element={<AdminEmployees />} />
            <Route path="orders" element={<AdminOrders />} />
            <Route path="users" element={<AdminUsers />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>

      <footer className="site-footer">
        <div className="container">
          <span>&copy; {new Date().getFullYear()} HAAK</span>
          <span>Leather &amp; brass, made to order</span>
        </div>
      </footer>
    </>
  );
}

function NotFound() {
  return (
    <div className="container">
      <div className="state-block">
        <h3>Page not found</h3>
      </div>
    </div>
  );
}
