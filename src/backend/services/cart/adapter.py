from typing import Dict
import requests
from src.backend.clients.http_client import HTTPClient


class CartAdapter:
    def __init__(self, client: HTTPClient) -> None:
        self.client = client

    def get_cart(self, token: str) -> requests.Response:
        return self.client.get('/cart/', headers={'Authorization': token})

    def add_to_cart(self, token: str, data: Dict) -> requests.Response:
        return self.client.post('/cart/add', headers={'Authorization': token}, json=data)

    def remove_from_cart(self, token: str, data: Dict) -> requests.Response:
        return self.client.post('/cart/remove', headers={'Authorization': token}, json=data)

    # Methods expected by tests
    def add_item(self, token: str, item_id: int, quantity: int) -> requests.Response:
        return self.add_to_cart(token, {"item_id": item_id, "quantity": quantity})

    def remove_item(self, token: str, item_id: int) -> requests.Response:
        return self.remove_from_cart(token, {"item_id": item_id})
