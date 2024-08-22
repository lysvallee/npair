from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime


class Image(SQLModel, table=True):
    image_id: int = Field(primary_key=True)
    image_name: str
    image_category: str


class Movie(SQLModel, table=True):
    movie_id: int = Field(primary_key=True)
    movie_title: str = Field(index=True)
    movie_palette: Optional[str]


class Show(SQLModel, table=True):
    show_id: int = Field(primary_key=True)
    show_title: str = Field(index=True)
    show_palette: Optional[str]


class Tmdb(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(index=True)
    first_air_date: Optional[int]
    popularity: Optional[float]
    networks: Optional[str]
    poster_path: Optional[str]
    overview: Optional[str]


class Brand(SQLModel, table=True):
    brand_id: int = Field(primary_key=True)
    brand_name: str = Field(index=True)
    brand_palette: Optional[str]


class Material(SQLModel, table=True):
    material_id: int = Field(primary_key=True)
    material_name: str
    material_roughness: float
    material_metalness: float


class Usage(SQLModel, table=True):
    usage_id: int = Field(primary_key=True)
    selection_time: datetime
    selected_category: str
    selected_image_path: Optional[str] = None
    selected_movie: Optional[int] = Field(default=None, foreign_key="movie.movie_id")
    selected_show: Optional[int] = Field(default=None, foreign_key="show.show_id")
    selected_brand: Optional[int] = Field(default=None, foreign_key="brand.brand_id")
    selected_material: Optional[int] = Field(
        default=None, foreign_key="material.material_id"
    )
    object_3d: Optional[str] = None
    object_2d: Optional[str] = None
    movie: Optional["Movie"] = Relationship()
    show: Optional["Show"] = Relationship()
    brand: Optional["Brand"] = Relationship()
    material: Optional["Material"] = Relationship()


class ServiceMetrics(SQLModel, table=True):
    id: int = Field(primary_key=True)
    service_name: str
    endpoint: str
    response_time_ms: float
    status_code: int
    timestamp: datetime
