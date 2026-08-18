import { useEffect, useState } from "react";
import { fetchProducts } from "../api/resources";
import { extractErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { formatMoney } from "../utils/money";
import { PageSpinner } from "../components/RouteGuards";

export default function Storefront() {
  const { isAuthenticated } = useAuth();
  const { addItem } = useCart();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchProducts({ limit: 100 })
      .then((data) => {
        if (!cancelled) setProducts(data);
      })
      .catch((err) => {
        if (!cancelled) setError(extractErrorMessage(err, "Couldn't load products."));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <>
      <section className="hero">
        <div className="container">
          <span className="eyebrow">Full-grain leather &amp; brass hardware</span>
          <h1>Built for daily carry, made to outlast it.</h1>
          <p>
            Every HAAK piece is cut, stitched, and finished by hand. Browse
            the current collection below.
          </p>
        </div>
      </section>

      <div className="container">
        {!isAuthenticated && (
          <div className="alert alert-error" style={{ marginTop: 32 }}>
            Sign in to view live inventory and place an order.
          </div>
        )}

        {loading && <PageSpinner />}
        {error && <div className="alert alert-error" style={{ marginTop: 32 }}>{error}</div>}

        {!loading && !error && isAuthenticated && (
          <div className="product-grid">
            {products.length === 0 && (
              <div className="state-block">
                <h3>No products yet</h3>
                <p>Check back soon, or ask an admin to add inventory.</p>
              </div>
            )}
            {products.map((product) => (
              <ProductCard key={product.id} product={product} onAdd={addItem} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}

function ProductCard({ product, onAdd }) {
  const outOfStock = product.stock <= 0;
  const lowStock = !outOfStock && product.stock <= 5;

  return (
    <div className="product-card">
      <div className="thumb">HAAK</div>
      <h3>{product.name}</h3>
      <div className={`stock-line ${lowStock ? "low" : ""}`}>
        {outOfStock ? "Out of stock" : lowStock ? `Only ${product.stock} left` : `${product.stock} in stock`}
      </div>
      <div className="card-foot">
        <span className="price-tag">{formatMoney(product.price)}</span>
        <button
          className="btn btn-outline btn-sm"
          disabled={outOfStock}
          onClick={() => onAdd(product, 1)}
        >
          Add
        </button>
      </div>
    </div>
  );
}
