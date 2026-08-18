import { createContext, useContext, useMemo, useState } from "react";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  // items: { [productId]: { product, quantity } }
  const [items, setItems] = useState({});
  const [isOpen, setIsOpen] = useState(false);

  function addItem(product, quantity = 1) {
    setItems((prev) => {
      const existing = prev[product.id];
      const nextQty = Math.min(
        (existing?.quantity || 0) + quantity,
        product.stock
      );
      return { ...prev, [product.id]: { product, quantity: nextQty } };
    });
    setIsOpen(true);
  }

  function setQuantity(productId, quantity) {
    setItems((prev) => {
      if (quantity <= 0) {
        const { [productId]: _drop, ...rest } = prev;
        return rest;
      }
      const existing = prev[productId];
      if (!existing) return prev;
      const clamped = Math.min(quantity, existing.product.stock);
      return { ...prev, [productId]: { ...existing, quantity: clamped } };
    });
  }

  function removeItem(productId) {
    setItems((prev) => {
      const { [productId]: _drop, ...rest } = prev;
      return rest;
    });
  }

  function clear() {
    setItems({});
  }

  const lineItems = useMemo(() => Object.values(items), [items]);
  const count = useMemo(
    () => lineItems.reduce((sum, i) => sum + i.quantity, 0),
    [lineItems]
  );
  const total = useMemo(
    () => lineItems.reduce((sum, i) => sum + i.quantity * i.product.price, 0),
    [lineItems]
  );

  const value = {
    lineItems,
    count,
    total,
    addItem,
    setQuantity,
    removeItem,
    clear,
    isOpen,
    openCart: () => setIsOpen(true),
    closeCart: () => setIsOpen(false),
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within a CartProvider");
  return ctx;
}
