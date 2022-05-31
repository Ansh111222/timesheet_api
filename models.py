from sqlalchemy import Column, Integer, String, Date
from database import Base


class TimeSheet(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    date = Column(Date)
    hours_worked = Column(Integer)