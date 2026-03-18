from datetime import date
from typing import Optional, List

from pydantic import BaseModel, Field


class PlaceCreate(BaseModel):
    external_id: int
    notes: Optional[str] = None


class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None


class PlaceRead(BaseModel):
    id: int
    external_id: int
    notes: Optional[str]
    is_visited: bool
    project_id: int

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    places: List[PlaceCreate] = Field(min_length=1, max_items=10)


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    is_completed: bool
    places: List[PlaceRead] = []

    class Config:
        from_attributes = True
