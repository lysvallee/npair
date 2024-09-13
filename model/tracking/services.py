import os
from sqlmodel import Session, create_engine, SQLModel
from models import (
    Image,
    Movie,
    Show,
    Brand,
    Material,
    Usage,
    ServiceMetrics,
    ModelMetrics,
)

# Database URL
NPAIR_DB_URL = os.environ.get("NPAIR_DB_URL")

# Create engines for both databases
engine = create_engine(NPAIR_DB_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session
