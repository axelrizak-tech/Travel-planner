from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import TravelProject, Place
from schemas import *
from art_api import validate_place

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# PROJECTS 
@router.post("/projects", response_model=ProjectOut)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    if len(project.places) > 10:
        raise HTTPException(400, "Max 10 places per project")

    db_project = TravelProject(
        name=project.name,
        description=project.description,
        start_date=project.start_date
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    for place in project.places:
        art = validate_place(place.external_id)
        if not art:
            raise HTTPException(400, f"Place {place.external_id} not found")

        db_place = Place(
            project_id=db_project.id,
            external_id=art["external_id"],
            title=art["title"],
            notes=place.notes
        )
        db.add(db_place)

    db.commit()
    return db_project


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(TravelProject).all()


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TravelProject, project_id)
    if not project:
        raise HTTPException(404)
    return project


@router.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(TravelProject, project_id)
    if not project:
        raise HTTPException(404)

    for field, value in data.dict(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    return project


@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TravelProject, project_id)
    if not project:
        raise HTTPException(404)

    if any(p.visited for p in project.places):
        raise HTTPException(400, "Cannot delete project with visited places")

    db.delete(project)
    db.commit()
    return {"status": "deleted"}


# PLACES
@router.post("/projects/{project_id}/places", response_model=PlaceOut)
def add_place(project_id: int, place: PlaceCreate, db: Session = Depends(get_db)):
    project = db.get(TravelProject, project_id)
    if not project:
        raise HTTPException(404)

    if len(project.places) >= 10:
        raise HTTPException(400, "Max 10 places reached")

    if any(p.external_id == place.external_id for p in project.places):
        raise HTTPException(400, "Place already exists")

    art = validate_place(place.external_id)
    if not art:
        raise HTTPException(400, "Place not found")

    db_place = Place(
        project_id=project.id,
        external_id=art["external_id"],
        title=art["title"],
        notes=place.notes
    )
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place


@router.get("/projects/{project_id}/places", response_model=list[PlaceOut])
def list_places(project_id: int, db: Session = Depends(get_db)):
    return db.query(Place).filter_by(project_id=project_id).all()


@router.put("/projects/{project_id}/places/{place_id}", response_model=PlaceOut)
def update_place(project_id: int, place_id: int, data: PlaceUpdate, db: Session = Depends(get_db)):
    place = db.get(Place, place_id)
    if not place or place.project_id != project_id:
        raise HTTPException(404)

    for field, value in data.dict(exclude_unset=True).items():
        setattr(place, field, value)

    db.commit()

    project = db.get(TravelProject, project_id)
    project.completed = all(p.visited for p in project.places)
    db.commit()

    return place
