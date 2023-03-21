from datetime import date
from repository import PersonnelRepository, ScheduleRepository, ScheduleShellRepository
import schemas

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

@app.get("/api/personnel", response_model=list[schemas.PersonLine])
async def get_personnel(person_repo: PersonnelRepository = Depends(PersonnelRepository)):
    return await person_repo.get_all_personnel()

@app.put("/api/personnel/{id}")
async def update_person(id: int, person: schemas.PersonLine, person_repo: PersonnelRepository = Depends(PersonnelRepository)):
    await person_repo.update_person(**person.dict())
    return {} #TODO: this needs to return something with the correct status codeA

@app.get("/api/schedules", response_model=list[schemas.Schedule])
async def get_schedules(schedule_repo = Depends(ScheduleRepository)):
    return await schedule_repo.get_schedules()

@app.get("/api/flying_shell")
async def get_flying_shell(date: date, shell_repo = Depends(ScheduleShellRepository)):
    shell = await shell_repo.get_flying_shell(date)
    return shell

@app.get("/api/duty_shell")
async def get_duty_shell(date: date, shell_repo = Depends(ScheduleShellRepository)):
    shell = await shell_repo.get_duty_shell(date)
    return shell