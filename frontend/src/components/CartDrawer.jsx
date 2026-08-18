import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { formatMoney } from "../utils/money";

export default function CartDrawer() {
  const { isOpen, closeCart, lineItems, total, setQuantity, removeItem } = useCart();
  const navigate = useNavigate();

  if (!isOpen) return null;

  function goToCheckout() {
    closeCart();
    navigate("/checkout");
  }

  return (
    <>
      <div className="cart-backdrop" onClick={closeCart} />
      <aside className="cart-drawer">
        <div className="cart-head">
          <h3 style={{ margin: 0 }}>Your bag</h3>
          <button className="modal-close" onClick={closeCart} aria-label="Close cart">
            &times;
          </button>
        </div>

        <div className="cart-items">
          {lineItems.length === 0 && (
            <div className="state-block">
              <p>Your bag is empty.</p>
            </div>
          )}
          {lineItems.map(({ product, quantity }) => (
            <div className="cart-line" key={product.id}>
              <div>
                <div className="name">{product.name}</div>
                <div className="unit">
                  {formatMoney(product.price)} &middot; {product.stock} in stock
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div className="qty-stepper">
                  <button onClick={() => setQuantity(product.id, quantity - 1)}>-</button>
                  <span>{quantity}</span>
                  <button
                    onClick={() => setQuantity(product.id, quantity + 1)}
                    disabled={quantity >= product.stock}
                  >
                    +
                  </button>
                </div>
                <button
                  className="btn-ghost"
                  style={{ padding: 4 }}
                  onClick={() => removeItem(product.id)}
                  aria-label={`Remove ${product.name}`}
                >
                  &times;
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="cart-foot">
          <div className="cart-total-row">
            <span>Subtotal</span>
            <span>{formatMoney(total)}</span>
          </div>
          <button
            className="btn btn-primary btn-block"
            disabled={lineItems.length === 0}
            onClick={goToCheckout}
          >
            Checkout
          </button>
        </div>
      </aside>
    </>
  );
}
