from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Places 
class PlaceCreate(BaseModel):
    external_id: str
    notes: Optional[str] = None


class PlaceUpdate(BaseModel):
    notes: Optional[str]
    visited: Optional[bool]


class PlaceOut(BaseModel):
    id: int
    external_id: str
    title: str
    notes: Optional[str]
    visited: bool

    class Config:
        orm_mode = True


# Projects 
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str]
    start_date: Optional[date]
    places: Optional[List[PlaceCreate]] = []


class ProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    start_date: Optional[date]


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    completed: bool
    places: List[PlaceOut] = []

    class Config:
        orm_mode = True
