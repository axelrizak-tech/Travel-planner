from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectPlaceBase(BaseModel):
    external_id: int = Field(..., gt=0)
    notes: Optional[str] = None


class ProjectPlaceCreate(ProjectPlaceBase):
    pass


class ProjectPlaceUpdate(BaseModel):
    notes: Optional[str] = None
    visited: Optional[bool] = None


class ProjectPlaceOut(ProjectPlaceBase):
    id: int
    visited: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    places: Optional[List[ProjectPlaceCreate]] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectOut(ProjectBase):
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    places: List[ProjectPlaceOut] = []

    class Config:
        from_attributes = True
