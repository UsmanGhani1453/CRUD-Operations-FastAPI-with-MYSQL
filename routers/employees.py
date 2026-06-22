from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
import models, schemas

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.post("/", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    existing = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email registered")
    
    db_employee = models.Employee(**employee.dict(), owner_id=current_user.id)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.get("/employees/{employee_id}", response_model=schemas.Employee, tags=["Employees"])
def read_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    if bool(employee.owner_id != current_user.id):
        raise HTTPException(status_code=401, detail="Not authorized to access this employee")
        
    return employee

@router.put("/employees/{employee_id}", response_model=schemas.Employee, tags=["Employees"])
def update_employee(
    employee_id: int, 
    employee: schemas.EmployeeCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Locked!
):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if bool(db_employee.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to modify this employee")
    category = db.query(models.Category).filter(models.Category.id == employee.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category ID does not exist.")
        
    db_employee.name = employee.name             # type: ignore
    db_employee.email = employee.email           # type: ignore
    db_employee.category_id = employee.category_id # type: ignore
    
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.delete("/employees/{employee_id}", tags=["Employees"])
def delete_employee(
    employee_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Locked!
):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    if bool(db_employee.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to modify this employee")
    db.delete(db_employee)
    db.commit()
    return {"message": "Employee deleted successfully"}


