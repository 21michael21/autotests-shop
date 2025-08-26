import requests
from src.backend.services.shop.adapter import ShopAdapter
from src.utils.constants import HTTP_STATUSES

from src.backend.services.shop.models.response_models import (
    RegistrationResponse,
    LoginResponse,
    CartResponse,
    CatalogResponse,
)
from src.utils.validations import validate_response


class ShopService:
    def __init__(self, adapter: ShopAdapter):
        self._adapter = adapter

    def register_user(self, username: str, password: str) -> requests.Response:
        return self._adapter.register_user(username, password)

    def login_user(self, username: str, password: str) -> requests.Response:
        return self._adapter.login_user(username, password)

    def get_catalog(self, token: str = None, **filters) -> CatalogResponse:
        response = self._adapter.get_catalog(token, **filters)
        validate_response(response, 200)
        items = response.json()
        return CatalogResponse(items=items)

    def get_cart(self, token: str) -> CartResponse:
        response = self._adapter.get_cart(token)
        validate_response(response, 200)
        return CartResponse(**response.json())

    def add_item_to_cart(self, token: str, item_id: int, quantity: int) -> requests.Response:
        return self._adapter.add_item_to_cart(token, item_id, quantity)

    def remove_item_from_cart(self, token: str, item_id: int) -> requests.Response:
        return self._adapter.remove_item_from_cart(token, item_id)

    def create_order(self, token: str) -> requests.Response:
        return self._adapter.create_order(token)

    def get_order_details(self, token: str, order_id: int) -> requests.Response:
        return self._adapter.get_order_details(token, order_id)

    def clear_cart(self, token: str):
        cart = self.get_cart(token)
        if cart.items:
            for item in cart.items:
                try:
                    self.remove_item_from_cart(token, item.item_id)
                except Exception:
                    pass

    def validate_items_price_range(self, items, min_price, max_price):
        for item in items:
            assert min_price <= item["price"] <= max_price, f'Цена товара {item["id"]} не в диапазоне {min_price}-{max_price}'

    def validate_items_sorted_by_price(self, items, order):
        prices = [item["price"] for item in items if "price" in item]
        if order == "asc":
            assert prices == sorted(prices), "Товары не отсортированы по возрастанию цены"
        else:
            assert prices == sorted(prices, reverse=True), "Товары не отсортированы по убыванию цены"

    def validate_items_brand(self, items, brand):
        for item in items:
            if "brand" in item:
                assert item["brand"] == brand, f'Товар {item["id"]} имеет неверный бренд'

    def validate_item_has_required_fields(self, item, required_fields):
        for field in required_fields:
            assert field in item, f"Товар должен содержать поле {field}"

    def validate_malicious_usernames_rejected(self, malicious_usernames):
        for username in malicious_usernames:
            resp = self._adapter.register_user(username, "ValidPass123!")
            validate_response(resp, HTTP_STATUSES["bad_request"])

    def validate_item_in_cart(self, cart, item_id):
        cart_items = [item.item_id for item in cart.items]
        assert item_id in cart_items, f"Товар {item_id} должен быть в корзине"

    def validate_item_not_in_cart(self, cart, item_id):
        cart_items = [item.item_id for item in cart.items]
        assert item_id not in cart_items, f"Товар {item_id} должен быть удален из корзины"
