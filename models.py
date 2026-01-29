from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class TravelProject(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(Date)
    completed = Column(Boolean, default=False)

    places = relationship("Place", cascade="all, delete", back_populates="project")


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    external_id = Column(String, nullable=False)
    title = Column(String)
    notes = Column(String)
    visited = Column(Boolean, default=False)

    project = relationship("TravelProject", back_populates="places")

    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="unique_place_per_project"),
    )
