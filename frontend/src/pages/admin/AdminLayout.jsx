import { NavLink, Outlet } from "react-router-dom";

const TABS = [
  { to: "/admin", label: "Products", end: true },
  { to: "/admin/categories", label: "Categories" },
  { to: "/admin/employees", label: "Employees" },
  { to: "/admin/orders", label: "Orders" },
  { to: "/admin/users", label: "Users" },
];

export default function AdminLayout() {
  return (
    <div className="container" style={{ padding: "48px 24px 80px" }}>
      <span className="eyebrow">Admin dashboard</span>
      <h1 style={{ fontSize: 30, marginBottom: 28 }}>Manage HAAK</h1>

      <div className="tab-row">
        {TABS.map((tab) => (
          <NavLink
            key={tab.to}
            to={tab.to}
            end={tab.end}
            className={({ isActive }) => (isActive ? "active" : "")}
          >
            {tab.label}
          </NavLink>
        ))}
      </div>

      <Outlet />
    </div>
  );
}
