import datetime
from pyexpat import model
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Union
from functools import wraps
import requests


app = FastAPI()
employee_api_endpoint = "http://127.0.0.1:8080/employees/"

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def check_employee(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        employee_id = kwargs['employee_id']
        r = requests.get(employee_api_endpoint + str(employee_id), timeout=5)
        if r.status_code == 404:
            raise HTTPException(
            status_code=404,
            detail=f"Employee ID {employee_id} : Does not exist"
        )
        return await func(*args, **kwargs)
    return wrapper


class TimeSheet(BaseModel):
    employe_id: int = Field()
    date: Union[datetime.date] = Field()
    hours_worked: int = Field()


@app.get("/timesheet/{employee_id}")
@check_employee
async def list_timesheet_records(employee_id: int, db: Session = Depends(get_db)):
    return db.query(models.TimeSheet).filter(models.TimeSheet.employee_id == employee_id).values(models.TimeSheet.employee_id, models.TimeSheet.date, models.TimeSheet.hours_worked)


@app.post("/timesheet")
def create_timesheet(timesheet: TimeSheet, db: Session = Depends(get_db)):

    tm_model = models.TimeSheet()
    tm_model.employee_id = timesheet.employe_id
    tm_model.date = timesheet.date
    tm_model.hours_worked = timesheet.hours_worked

    db.add(tm_model)
    db.commit()

    return timesheet


@app.get("/timesheet/{employee_id}/{date}")
@check_employee
async def get_timesheet_record(employee_id: int, date: datetime.date, db: Session = Depends(get_db)):
    print(date)
    return db.query(models.TimeSheet).filter(
        models.TimeSheet.employee_id == employee_id,
        models.TimeSheet.date == date).values(models.TimeSheet.employee_id, models.TimeSheet.date, models.TimeSheet.hours_worked)
