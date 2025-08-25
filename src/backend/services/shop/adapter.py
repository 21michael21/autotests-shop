from typing import Dict, Optional
import requests
from src.backend.clients.http_client.client import HTTPClient

class ShopAdapter:
    def __init__(self, client: HTTPClient) -> None:
        self.client = client


    def register_user(self, username: str, password: str) -> requests.Response:
        return self.client.post("/auth/register", json={"username": username, "password": password})

    def login_user(self, username: str, password: str) -> requests.Response:
        return self.client.post("/auth/login", json={"username": username, "password": password})


    def get_cart(self, token: str) -> requests.Response:
        return self.client.get("/cart/", headers={"Authorization": f"Bearer {token}"})

    def add_item_to_cart(self, token: str, item_id: int, quantity: int) -> requests.Response:
        return self.client.post("/cart/add", headers={"Authorization": f"Bearer {token}"}, json={"item_id": item_id, "quantity": quantity})

    def remove_item_from_cart(self, token: str, item_id: int) -> requests.Response:
        return self.client.post("/cart/remove", headers={"Authorization": f"Bearer {token}"}, json={"item_id": item_id})


    def get_catalog(self, token: Optional[str] = None, min_price: Optional[int] = None, max_price: Optional[int] = None, sort_by: Optional[str] = None, sort_order: Optional[str] = None, brand: Optional[str] = None) -> requests.Response:
            params: Dict[str, str] = {}
            if min_price is not None:
                params["min_price"] = str(min_price)
            if max_price is not None:
                params["max_price"] = str(max_price)
            if brand is not None:
                params["brand"] = brand
            if sort_by is not None:
                if sort_by == "price":
                    params["sort"] = "price_asc" if sort_order == "asc" else "price_desc"
                elif sort_by == "name":
                    params["sort"] = "name_asc" if sort_order == "asc" else "name_desc"
            headers = {"Authorization": f"Bearer {token}"} if token else None
            return self.client.get("/catalog/", headers=headers, params=params or None)


    def create_order(self, token: str) -> requests.Response:
        return self.client.post("/orders/", headers={"Authorization": f"Bearer {token}"})

    def get_order_details(self, token: str, order_id: int) -> requests.Response:
        return self.client.get(f"/orders/{order_id}", headers={"Authorization": f"Bearer {token}"})
