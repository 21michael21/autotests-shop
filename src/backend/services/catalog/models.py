from typing import List
from pydantic import BaseModel, Field


class CatalogItem(BaseModel):
    id: int
    name: str
    brand: str
    price: int
    image_url: str


class CatalogResponse(BaseModel):
    items: List[CatalogItem] = Field(default_factory=list)
