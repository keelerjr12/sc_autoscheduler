from typing import List
from pydantic import BaseModel, validator
import models

class Organization(BaseModel):
    name: str = None 
    
    class Config:
        orm_mode = True

class Qualification(BaseModel):
    name: str = None 
    
    class Config:
        orm_mode = True

class PersonLine(BaseModel):
    id: int

    first_name: str
    middle_name: str
    last_name: str
    
    ausm_tier: int

    assigned_org: str | None
    quals: List[str]

    class Config:
        orm_mode = True

    @validator('assigned_org', pre=True)
    def parse_org(cls, org):
        if hasattr(org, 'name'):
            return org.name

        return org

    @validator('quals', pre=True)
    def parse_quals(cls, quals):
        return [qual.name if hasattr(qual, 'name') else qual for qual in quals]