import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Project, Place
from app.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    PlaceCreate,
    PlaceUpdate,
    PlaceRead,
)
from app.services import check_artic_existence

router = APIRouter()


@router.post("/projects", response_model=ProjectRead, status_code=201)
async def create_project(
    project_data: ProjectCreate, db: AsyncSession = Depends(get_db)
):
    tasks = [check_artic_existence(p.external_id) for p in project_data.places]
    await asyncio.gather(*tasks)

    unique_ids = {p.external_id for p in project_data.places}
    if len(unique_ids) != len(project_data.places):
        raise HTTPException(status_code=400, detail="Duplicate places in request")

    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        start_date=project_data.start_date,
    )
    db.add(new_project)
    await db.flush()

    for p in project_data.places:
        db.add(Place(**p.model_dump(), project_id=new_project.id))

    await db.commit()
    stmt = (
        select(Project)
        .where(Project.id == new_project.id)
        .options(selectinload(Project.places))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.get("/projects", response_model=List[ProjectRead])
async def get_projects(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    query = (
        select(Project).options(selectinload(Project.places)).offset(skip).limit(limit)
    )
    result = await db.execute(query)
    projects = result.scalars().all()
    return projects


@router.get("/projects/{project_id}", response_model=ProjectRead)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.patch("/projects/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int, project_data: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project)

    return project


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )

    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if any(place.is_visited for place in project.places):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete travel project: some places are already marked as visited",
        )

    await db.delete(project)
    await db.commit()

    return None


# -- Places --


@router.post("/projects/{project_id}/places", response_model=PlaceRead)
async def add_place(
    project_id: int, place_data: PlaceCreate, db: AsyncSession = Depends(get_db)
):
    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if len(project.places) >= 10:
        raise HTTPException(
            status_code=400, detail="Maximum limit of 10 places per project reached"
        )

    if any(p.external_id == place_data.external_id for p in project.places):
        raise HTTPException(
            status_code=400, detail="This place is already added to the project"
        )

    await check_artic_existence(place_data.external_id)

    new_place = Place(**place_data.model_dump(), project_id=project_id)
    db.add(new_place)

    project.is_completed = False

    await db.commit()
    await db.refresh(new_place)

    return new_place


@router.get("/projects/{project_id}/places", response_model=List[PlaceRead])
async def get_places(project_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project.places


@router.get("/projects/{project_id}/places/{place_id}")
async def get_place(project_id: int, place_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Place).where(Place.id == place_id, Place.project_id == project_id)
    result = await db.execute(query)
    place = result.scalar_one_or_none()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found in this project")
    return place


@router.patch("/projects/{project_id}/places/{place_id}", response_model=PlaceRead)
async def update_place(
    project_id: int,
    place_id: int,
    place_data: PlaceUpdate,
    db: AsyncSession = Depends(get_db),
):
    query = select(Place).where(Place.id == place_id, Place.project_id == project_id)
    result = await db.execute(query)
    place = result.scalar_one_or_none()
    if not place:

        raise HTTPException(status_code=404, detail="Place not found in this project")

    update_dict = place_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(place, key, value)

    await db.flush()

    proj_query = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )
    proj_result = await db.execute(proj_query)
    project = proj_result.scalar_one_or_none()

    if all(p.is_visited for p in project.places):
        project.is_completed = True
    else:
        project.is_completed = False

    await db.commit()
    await db.refresh(place)
    return place


@router.delete("/projects/{project_id}/places/{place_id}", status_code=204)
async def delete_place(
    project_id: int, place_id: int, db: AsyncSession = Depends(get_db)
):
    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    place_to_delete = next((p for p in project.places if p.id == place_id), None)

    if not place_to_delete:
        raise HTTPException(status_code=404, detail="Place not found")

    await db.delete(place_to_delete)
    await db.flush()

    if project.places and all(p.is_visited for p in project.places):
        project.is_completed = True
    else:
        project.is_completed = False if not project.places else project.is_completed

    await db.commit()
    return None
