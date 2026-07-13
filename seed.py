from database import SessionLocal
from models import User,Category,Product
from security import get_password_hash

def seed_database():
    db = SessionLocal()
    try:
        admin_email = "admin@haak.com"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = User(
                email = admin_email,
                hashed_password = get_password_hash("admin123"),
                is_verified = True,
                role = "admin"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("✅ Admin user created (admin@haak.com / admin123).")
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
            {"name": "HAAK Evening Clutch", "price": 3000, "stock": 20}
        ]
        for prod in products:
            product = db.query(Product).filter(Product.name == prod["name"]).first()
            if not product:
                new_product = Product(
                    name=prod["name"],
                    price=prod["price"],
                    stock=prod["stock"],
                    owner_id=admin_user.id
                )
                db.add(new_product)
                db.commit()
        print("✅ HAAK Products seeded successfully! Ready for presentation.")

    finally:
        db.close()
    
if __name__ == "__main__":
    print("Starting database seed...")
    seed_database()