import requests
from http import HTTPStatus
from src.backend.services.shop.adapter import ShopAdapter

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

    def _make_adapter_call(self, method_name: str, *args, **kwargs) -> requests.Response:
        method = getattr(self._adapter, method_name)
        return method(*args, **kwargs)

    def _validate_response_status(self, response: requests.Response, expected_status: int = 200):
        if response.status_code != expected_status:
            raise RuntimeError(f"Unexpected response status: {response.status_code}, expected: {expected_status}")

    def register_user(self, username: str, password: str) -> requests.Response:
        return self._make_adapter_call("register_user", username, password)

    def login_user(self, username: str, password: str) -> requests.Response:
        return self._make_adapter_call("login_user", username, password)

    def get_catalog(self, token: str = None, **filters) -> CatalogResponse:
        response = self._make_adapter_call("get_catalog", token, **filters)
        validate_response(response, 200)
        items = response.json()
        return CatalogResponse(items=items)

    def get_cart(self, token: str) -> CartResponse:
        response = self._make_adapter_call("get_cart", token)
        validate_response(response, 200)
        return CartResponse(**response.json())

    def add_item_to_cart(self, token: str, item_id: int, quantity: int) -> requests.Response:
        return self._make_adapter_call("add_item_to_cart", token, item_id, quantity)

    def remove_item_from_cart(self, token: str, item_id: int) -> requests.Response:
        return self._make_adapter_call("remove_item_from_cart", token, item_id)

    def create_order(self, token: str) -> requests.Response:
        return self._make_adapter_call("create_order", token)

    def get_order_details(self, token: str, order_id: int) -> requests.Response:
        return self._make_adapter_call("get_order_details", token, order_id)

    def clear_cart(self, token: str):
        cart = self.get_cart(token)
        if cart.items:
            for item in cart.items:
                response = self.remove_item_from_cart(token, item.item_id)
                self._validate_response_status(response, 200)

    def _validate_item_field(self, item: dict, field_name: str, expected_value, error_message: str):
        if field_name in item and item[field_name] != expected_value:
            raise AssertionError(error_message)

    def _validate_item_price_range(self, item: dict, min_price: int, max_price: int):
        if "price" in item and not (min_price <= item["price"] <= max_price):
            raise AssertionError(f'Цена товара {item["id"]} не в диапазоне {min_price}-{max_price}')

    def validate_items_price_range(self, items, min_price, max_price):
        for item in items:
            self._validate_item_price_range(item, min_price, max_price)

    def validate_items_sorted_by_price(self, items, order):
        prices = [item["price"] for item in items if "price" in item]
        if order == "asc":
            assert prices == sorted(prices), "Товары не отсортированы по возрастанию цены"
        else:
            assert prices == sorted(prices, reverse=True), "Товары не отсортированы по убыванию цены"

    def check_items_sorted_by_price(self, items, order):
        """
        Проверяет, что товары отсортированы по цене в указанном порядке.
        Вынесен из тестов для переиспользования и лучшей читаемости.
        """
        prices = [item["price"] for item in items if "price" in item]
        if order == "asc":
            return prices == sorted(prices)
        else:
            return prices == sorted(prices, reverse=True)

    def validate_items_brand(self, items, brand):
        for item in items:
            self._validate_item_field(item, "brand", brand, f'Товар {item["id"]} имеет неверный бренд')

    def validate_item_has_required_fields(self, item, required_fields):
        for field in required_fields:
            if field not in item:
                raise AssertionError(f"Товар должен содержать поле {field}")

    def validate_malicious_usernames_rejected(self, malicious_usernames):
        for username in malicious_usernames:
            resp = self._make_adapter_call("register_user", username, "ValidPass123!")
            validate_response(resp, HTTPStatus.BAD_REQUEST)

    def validate_item_in_cart(self, cart, item_id):
        cart_items = [item.item_id for item in cart.items]
        if item_id not in cart_items:
            raise AssertionError(f"Товар {item_id} должен быть в корзине")

    def validate_item_not_in_cart(self, cart, item_id):
        cart_items = [item.item_id for item in cart.items]
        if item_id in cart_items:
            raise AssertionError(f"Товар {item_id} должен быть удален из корзины")
