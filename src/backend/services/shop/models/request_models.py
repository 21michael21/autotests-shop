from pydantic import BaseModel
from typing import Optional


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AddItemToCartRequest(BaseModel):
    item_id: int
    quantity: int


class RemoveItemFromCartRequest(BaseModel):
    item_id: int


class CatalogFilterRequest(BaseModel):
    min_price: Optional[int]
    max_price: Optional[int]
    brand: Optional[str]
    sort: Optional[str]
