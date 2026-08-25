import { api } from "./client";

// --- Auth -----------------------------------------------------------
export function login(email, password) {
  // Backend expects OAuth2PasswordRequestForm: form-encoded, "username" field.
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  return api
    .post("/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    })
    .then((res) => res.data);
}

export function fetchMe() {
  return api.get("/users/me").then((res) => res.data);
}

// --- Users (admin) -----------------------------------------------------------
export function createUser(payload) {
  return api.post("/users/", payload).then((res) => res.data);
}

// --- Products -----------------------------------------------------------
export function fetchProducts(params = {}) {
  return api.get("/products/", { params }).then((res) => res.data);
}

export function fetchProduct(id) {
  return api.get(`/products/${id}`).then((res) => res.data);
}

export function createProduct(payload) {
  return api.post("/products/", payload).then((res) => res.data);
}

export function updateProduct(id, payload) {
  return api.put(`/products/${id}`, payload).then((res) => res.data);
}

export function deleteProduct(id) {
  return api.delete(`/products/${id}`).then((res) => res.data);
}

// --- Categories -----------------------------------------------------------
export function fetchCategories(params = {}) {
  return api.get("/categories/", { params }).then((res) => res.data);
}

export function createCategory(payload) {
  return api.post("/categories/", payload).then((res) => res.data);
}

export function updateCategory(id, payload) {
  return api.put(`/categories/${id}`, payload).then((res) => res.data);
}

export function deleteCategory(id) {
  return api.delete(`/categories/${id}`).then((res) => res.data);
}

// --- Employees -----------------------------------------------------------
export function fetchEmployee(id) {
  return api.get(`/employees/${id}`).then((res) => res.data);
}

export function searchEmployees(key, value) {
  return api
    .get("/employees/search", { params: { key, value } })
    .then((res) => res.data);
}

export function createEmployee(payload) {
  return api.post("/employees/", payload).then((res) => res.data);
}

export function updateEmployee(id, payload) {
  return api.put(`/employees/${id}`, payload).then((res) => res.data);
}

export function deleteEmployee(id) {
  return api.delete(`/employees/${id}`).then((res) => res.data);
}

// --- Orders -----------------------------------------------------------
export function createOrder(items) {
  return api.post("/orders/", { items }).then((res) => res.data);
}

export function fetchOrder(id) {
  return api.get(`/orders/${id}`).then((res) => res.data);
}

export function fetchMyOrders() {
  return api.get("/orders/").then((res) => res.data);
}

export function fetchAllOrders(params = {}) {
  return api.get("/orders/all", { params }).then((res) => res.data);
}

export function updateOrderStatus(id, status) {
  return api.put(`/orders/${id}/status`, { status }).then((res) => res.data);
}

export function updatePaymentStatus(id, payment_status) {
  return api.put(`/orders/${id}/payment`, { payment_status }).then((res) => res.data);
}

