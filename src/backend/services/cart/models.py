from typing import List
from pydantic import BaseModel, Field


class CartItem(BaseModel):
    item_id: int
    name: str
    price: int
    quantity: int
    image_url: str


class CartResponse(BaseModel):
    items: List[CartItem] = Field(default_factory=list)


class AddToCartRequest(BaseModel):
    item_id: int
    quantity: int = Field(ge=1)


class RemoveFromCartRequest(BaseModel):
    item_id: int
