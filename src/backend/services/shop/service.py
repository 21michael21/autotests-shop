import http

import allure

from src.backend.services.shop.adapter import ShopAdapter
from src.backend.services.shop.models.request_models import (
    RegisterRequest,
    LoginRequest,
    AddItemToCartRequest,
)
from src.backend.services.shop.models.response_models import (
    RegistrationResponse,
    LoginResponse,
    CartResponse,
    CatalogResponse,
)
from src.utils.validations import validate_response, validate_json_structure


class ShopService:
    def __init__(self, adapter: ShopAdapter):
        self._adapter = adapter

    def register_user(self, username: str, password: str) -> RegistrationResponse:
        request_data = RegisterRequest(username=username, password=password)
        response = self._adapter.register_user(username, password)
        validate_response(response, http.HTTPStatus.OK)
        return RegistrationResponse(**response.json())

    def login_user(self, username: str, password: str) -> LoginResponse:
        request_data = LoginRequest(username=username, password=password)
        response = self._adapter.login_user(username, password)
        validate_response(response, http.HTTPStatus.OK)
        return LoginResponse(**response.json())

    def get_catalog(self, token: str = None, **filters) -> CatalogResponse:
        response = self._adapter.get_catalog(token, **filters)
        validate_response(response, http.HTTPStatus.OK)
        items = response.json()
        return CatalogResponse(items=items)

    def get_cart(self, token: str) -> CartResponse:
        response = self._adapter.get_cart(token)
        validate_response(response, http.HTTPStatus.OK)
        return CartResponse(**response.json())

    def add_item_to_cart(self, token: str, item_id: int, quantity: int):
        request_data = AddItemToCartRequest(item_id=item_id, quantity=quantity)
        response = self._adapter.add_item_to_cart(token, item_id, quantity)
        validate_response(response, http.HTTPStatus.OK)
        return response.json()

    def remove_item_from_cart(self, token: str, item_id: int):
        response = self._adapter.remove_item_from_cart(token, item_id)
        validate_response(response, http.HTTPStatus.OK)
        return response.json()

    def create_order(self, token: str):
        response = self._adapter.create_order(token)
        validate_response(response, http.HTTPStatus.OK)
        return response.json()

    def get_order_details(self, token: str, order_id: int):
        response = self._adapter.get_order_details(token, order_id)
        validate_response(response, http.HTTPStatus.OK)
        return response.json()
