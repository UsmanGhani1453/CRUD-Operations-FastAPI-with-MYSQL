import os
import secrets

import config  # noqa: F401  (loads .env / validates config on import)
from database import SessionLocal, engine, Base
from models import User, Category, Product
from security import get_password_hash


def seed_database():
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    try:
        admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@haak.com")
        admin_password = os.getenv("SEED_ADMIN_PASSWORD")

        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            if not admin_password:
                # Never fall back to a fixed, guessable password like the
                # old "admin123" - generate a strong one-time password and
                # print it once so it can be copied and changed after login.
                admin_password = secrets.token_urlsafe(12)
                print(
                    "⚠️  SEED_ADMIN_PASSWORD not set - generated a random "
                    f"one-time admin password: {admin_password}\n"
                    "   Log in and change it immediately."
                )

            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                is_verified=True,
                role="admin",
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Admin user created ({admin_email}).")
        else:
            print("ℹ️ Admin user already exists.")

        categories = ["Wallets", "Watches", "Clutch Bags"]
        for cat_name in categories:
            category = db.query(Category).filter(Category.name == cat_name).first()
            if not category:
                category = Category(name=cat_name, owner_id=admin_user.id)
                db.add(category)
                db.commit()
        print("✅ Categories seeded.")

        products = [
            {"name": "HAAK Premium Leather Wallet", "price": 2500, "stock": 50},
            {"name": "HAAK Minimalist Watch", "price": 4500, "stock": 30},
            {"name": "HAAK Evening Clutch", "price": 3000, "stock": 20},
        ]
        for prod in products:
            product = db.query(Product).filter(Product.name == prod["name"]).first()
            if not product:
                new_product = Product(
                    name=prod["name"],
                    price=prod["price"],
                    stock=prod["stock"],
                    owner_id=admin_user.id,
                )
                db.add(new_product)
                db.commit()
        print("✅ HAAK Products seeded successfully! Ready for presentation.")

    finally:
        db.close()


if __name__ == "__main__":
    print("Starting database seed...")
    seed_database()
