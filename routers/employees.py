from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from dependencies import get_current_user
import models, schemas, database
from dependencies import get_current_admin

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.post("/", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db),admin_user: models.User = Depends(get_current_admin)):
    existing = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email registered")
    
    db_employee = models.Employee(**employee.model_dump(), owner_id=admin_user.id)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.get("/{employee_id}", response_model=schemas.Employee, tags=["Employees"])
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

@router.get("/search",response_model=list[schemas.Employee])
def search_employee_extra_data(key:str,value:str,db: Session = Depends(database.get_db)):
    results = db.query(models.Employee).filter(func.json_unquote(models.Employee.extra_data[key])==value).all()
    if not results:
        raise HTTPException(status_code=404,detail=f"No Employee found with {key} = {value}")
    return results

@router.put("/{employee_id}", response_model=schemas.Employee, tags=["Employees"])
def update_employee(
    employee_id: int, 
    employee: schemas.EmployeeCreate, 
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin)# Locked!
):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if bool(db_employee.owner_id != admin_user.id):
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

@router.delete("/{employee_id}", tags=["Employees"])
def delete_employee(
    employee_id: int, 
    db: Session = Depends(get_db),
     admin_user: models.User = Depends(get_current_admin)# Locked!
):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    if bool(db_employee.owner_id != admin_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to modify this employee")
    db.delete(db_employee)
    db.commit()
    return {"message": "Employee deleted successfully"}


