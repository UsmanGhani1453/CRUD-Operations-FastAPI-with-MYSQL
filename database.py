from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Format: mysql+pymysql://user:password@host:port/db_name
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/my_database"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to inject DB sessions into routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        