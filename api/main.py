from typing import List
from database import Session, get_db
import schemas, models

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:4200'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

@app.get("/api/personnel", response_model=List[schemas.PersonLine])
async def get_personnel(db: Session = Depends(get_db)):
    personnel = db.query(models.PersonLine).all()
    return personnel

@app.put("/api/personnel/{id}")
async def update_person(id: int, person: schemas.PersonLine, db: Session = Depends(get_db)):
    #TODO: do actual database update
    personnel = db.query(models.PersonLine).all()
    return personnel