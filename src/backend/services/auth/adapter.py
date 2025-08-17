from typing import Dict
import requests
from src.backend.clients.http_client import HTTPClient


class AuthAdapter:
    def __init__(self, client: HTTPClient) -> None:
        self.client = client

    def register(self, data: Dict) -> requests.Response:
        return self.client.post("/auth/register", json=data)

    def login(self, data: Dict) -> requests.Response:
        return self.client.post("/auth/login", json=data)

    def register_user(self, username: str, password: str) -> requests.Response:
        return self.register({"username": username, "password": password})

    def login_user(self, username: str, password: str) -> requests.Response:
        return self.login({"username": username, "password": password})
