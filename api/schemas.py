from typing import List
from pydantic import BaseModel

class Organization(BaseModel):
    id: int = None
    name: str = None 
    
    class Config:
        orm_mode = True

class Qualification(BaseModel):
    id: int = None
    name: str = None 
    
    class Config:
        orm_mode = True

class PersonLine(BaseModel):
    id: int

    first_name: str
    middle_name: str
    last_name: str
    
    ausm_tier: int

    assigned_org: Organization | None
    quals: List[Qualification]

    class Config:
        orm_mode = True