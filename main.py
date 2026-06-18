from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Local imports
from database import engine, Base, get_db
import models
import schemas

# Create database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
# ---------------------------CRUD Operations for Product table---------------------------------------------
@app.post("/products/", response_model=schemas.Product,tags=["Products"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # 1. Create the SQLAlchemy model instance
    db_product = models.Product(name=product.name, price=product.price)
    # 2. Add it to the database session
    db.add(db_product)
    # 3. Commit the transaction to save it
    db.commit()
    # 4. Refresh to get the newly generated ID from MySQL
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=list[schemas.Product],tags=["Products"])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=schemas.Product,tags=["Products"])
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=schemas.Product,tags=["Products"])
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update the existing record's attributes
    db_product.name = product.name # type: ignore
    db_product.price = product.price # type: ignore
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Remove the record and commit
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

# ---------------------------CRUD Operations for Categoty table---------------------------------------------
@app.post("/categories/", response_model=schemas.Category,tags=["Categories"])
def create_category(category:schemas.CategoryCreate,db: Session = Depends(get_db)):
    db_category = models.Category(name=category.name,description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=list[schemas.Category],tags=["Categories"])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories

@app.put("/categories/{category_id}", response_model=schemas.Category,tags=["Categories"])
def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update the existing record's attributes (Adding type: ignore just in case Pylance complains again!)
    db_category.name = category.name               # type: ignore
    db_category.description = category.description # type: ignore
    
    db.commit()
    db.refresh(db_category)
    return db_category

@app.delete("/categories/{category_id}", tags=["Categories"])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Remove the record and save the changes
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}
# ---------------------------CRUD Operations for Employee table---------------------------------------------
# ==========================================
# EMPLOYEES
# ==========================================
@app.post("/employees/", response_model=schemas.Employee, tags=["Employees"])
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # 1. NEW: Check if the email is already taken
    existing_employee = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    # 2. Check if the category exists
    category = db.query(models.Category).filter(models.Category.id == employee.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category ID does not exist. Cannot assign employee.")

    # 3. Create the employee
    db_employee = models.Employee(
        name=employee.name, 
        email=employee.email, 
        category_id=employee.category_id
    )
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/{employee_id}", response_model=schemas.Employee, tags=["Employees"])
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.put("/employees/{employee_id}", response_model=schemas.Employee, tags=["Employees"])
def update_employee(employee_id: int, employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if category exists before updating
    category = db.query(models.Category).filter(models.Category.id == employee.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category ID does not exist.")
        
    db_employee.name = employee.name             # type: ignore
    db_employee.email = employee.email           # type: ignore
    db_employee.category_id = employee.category_id # type: ignore
    
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.delete("/employees/{employee_id}", tags=["Employees"])
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db.delete(db_employee)
    db.commit()
    return {"message": "Employee deleted successfully"}