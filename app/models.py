from sqlalchemy import (
    Integer,
    Column,
    String,
    Date,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)

    places = relationship(
        "Place", back_populates="project", cascade="all, delete-orphan"
    )


class Place(Base):
    __tablename__ = "places"
    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="_project_place_uc"),
        {"extend_existing": True},
    )
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    is_visited = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="places")
