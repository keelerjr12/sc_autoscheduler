from datetime import date, timedelta
from database import Session, get_db 
from sqlalchemy.orm import joinedload
from fastapi import Depends
import models

class PersonnelRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def get_all_personnel(self):
        personnel = self.db.query(models.PersonLine).all()
        return personnel

    async def update_person(self, *, id: int, first_name: str, middle_name: str, last_name:str, ausm_tier: int, assigned_org: str, quals: list[str]):
        person_in_db = self.db.query(models.PersonLine).filter_by(id = id).first()

        person_in_db.assigned_org = self.db.query(models.Organization).filter_by(name = assigned_org).first()
        person_in_db.quals = self.db.query(models.Qualification).filter(models.Qualification.name.in_(quals)).all()
        
        self.db.commit()

class ScheduleRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def get_schedules(self):
        return self.db.query(models.Schedule).all()

class ScheduleShellRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def get_flying_shell(self, date: date):
        return self.db.query(models.ShellLine).options(joinedload(models.ShellLine.org)).filter(models.ShellLine.start_date_time.between(date, date + timedelta(days = 1))).all()

    async def get_duty_shell(self, date: date):
        return self.db.query(models.ShellDuty).options(joinedload(models.ShellDuty.duty)).filter(models.ShellDuty.start_date_time.between(date, date + timedelta(days = 1))).all()