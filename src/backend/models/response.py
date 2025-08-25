# Модели ответов для shop API
from pydantic import BaseModel
from typing import List, Optional

class RegistrationResponse(BaseModel):
    message: str

class LoginResponse(BaseModel):
    token: str

class CartItem(BaseModel):
    item_id: int
    name: str
    price: int
    quantity: int
    image_url: Optional[str]

class CartResponse(BaseModel):
    items: List[CartItem]

class CatalogItem(BaseModel):
    id: int
    name: str
    brand: str
    price: int
    image_url: Optional[str]

class CatalogResponse(BaseModel):
    __root__: List[CatalogItem]

class OrderResponse(BaseModel):
    message: str
    order_id: int

class OrderDetailsResponse(BaseModel):
    order_id: int
    total_price: int
    created_at: str
    items: List[CartItem]

