from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Project, ProjectPlace
from schemas import (
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    ProjectPlaceCreate,
    ProjectPlaceOut,
    ProjectPlaceUpdate,
)
from art_api import validate_artwork_exists

router = APIRouter()


# Helpers


def recompute_project_completion(db: Session, project: Project) -> None:
    places = project.places
    if places and all(p.visited for p in places):
        project.is_completed = True
    else:
        project.is_completed = False
    db.add(project)


# Project Endpoints


@router.post(
    "/projects",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
    )
    db.add(project)
    db.flush()  # get project.id

    places_payload = payload.places or []
    if len(places_payload) > 10:
        raise HTTPException(
            status_code=400, detail="Maximum 10 places per project is allowed"
        )

    seen_ids = set()
    for p in places_payload:
        if p.external_id in seen_ids:
            raise HTTPException(
                status_code=400, detail="Duplicate external_id in request payload"
            )
        seen_ids.add(p.external_id)

    for p in places_payload:
        exists = await validate_artwork_exists(p.external_id)
        if not exists:
            raise HTTPException(
                status_code=422,
                detail=f"Artwork with id {p.external_id} not found in Art Institute API",
            )
        place = ProjectPlace(
            project_id=project.id,
            external_id=p.external_id,
            notes=p.notes,
        )
        db.add(place)

    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=List[ProjectOut])
def list_projects(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    projects = (
        db.query(Project)
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return projects


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.start_date is not None:
        project.start_date = payload.start_date

    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    any_visited = any(p.visited for p in project.places)
    if any_visited:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete project: at least one place is marked as visited",
        )

    db.delete(project)
    db.commit()
    return


# Project Places Endpoints


@router.post(
    "/projects/{project_id}/places",
    response_model=ProjectPlaceOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_place_to_project(
    project_id: int, payload: ProjectPlaceCreate, db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    count = (
        db.query(ProjectPlace)
        .filter(ProjectPlace.project_id == project_id)
        .count()
    )
    if count >= 10:
        raise HTTPException(
            status_code=400, detail="Maximum 10 places per project is allowed"
        )

    exists = await validate_artwork_exists(payload.external_id)
    if not exists:
        raise HTTPException(
            status_code=422,
            detail=f"Artwork with id {payload.external_id} not found in Art Institute API",
        )

    dup = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.project_id == project_id,
            ProjectPlace.external_id == payload.external_id,
        )
        .first()
    )
    if dup:
        raise HTTPException(
            status_code=400,
            detail="This external place is already added to the project",
        )

    place = ProjectPlace(
        project_id=project_id,
        external_id=payload.external_id,
        notes=payload.notes,
    )
    db.add(place)
    db.commit()
    db.refresh(place)

    recompute_project_completion(db, project)
    db.commit()

    return place


@router.get(
    "/projects/{project_id}/places",
    response_model=List[ProjectPlaceOut],
)
def list_places_for_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    places = (
        db.query(ProjectPlace)
        .filter(ProjectPlace.project_id == project_id)
        .order_by(ProjectPlace.created_at.desc())
        .all()
    )
    return places


@router.get(
    "/projects/{project_id}/places/{place_id}",
    response_model=ProjectPlaceOut,
)
def get_place_in_project(
    project_id: int, place_id: int, db: Session = Depends(get_db)
):
    place = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.id == place_id,
            ProjectPlace.project_id == project_id,
        )
        .first()
    )
    if not place:
        raise HTTPException(status_code=404, detail="Place not found in project")
    return place


@router.patch(
    "/projects/{project_id}/places/{place_id}",
    response_model=ProjectPlaceOut,
)
def update_place_in_project(
    project_id: int,
    place_id: int,
    payload: ProjectPlaceUpdate,
    db: Session = Depends(get_db),
):
    place = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.id == place_id,
            ProjectPlace.project_id == project_id,
        )
        .first()
    )
    if not place:
        raise HTTPException(status_code=404, detail="Place not found in project")

    if payload.notes is not None:
        place.notes = payload.notes
    if payload.visited is not None:
        place.visited = payload.visited

    db.commit()
    db.refresh(place)

    project = place.project
    recompute_project_completion(db, project)
    db.commit()

    return place
