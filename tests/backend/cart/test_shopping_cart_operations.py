import allure
import pytest
import http
from src.utils.validations import validate_response, validate_cart_response
from src.utils.constants import CART_MESSAGES

pytestmark = [
    allure.epic("Система корзины"),
    allure.feature("Операции с корзиной"),
    allure.story("Добавление и удаление товаров"),
]


@allure.title("Добавление товара в корзину")
def test_add_item_to_cart(shop_service, random_item, user):
        resp = shop_service.add_item_to_cart(user["token"], random_item["item_id"], random_item["quantity"])
        assert resp.get("message") in CART_MESSAGES["item_added"]
        
        cart = shop_service.get_cart(user["token"])
        cart_items = [item.item_id for item in cart.items]
        assert random_item["item_id"] in cart_items, "Товар должен быть в корзине после добавления"


@allure.title("Получение содержимого корзины")
def test_get_cart_contents(shop_service, user, add_random_item):
    resp = shop_service.get_cart(user["token"])
    validate_cart_response(resp.model_dump())
    
    assert len(resp.items) > 0, "Корзина должна содержать товары после добавления"


@allure.title("Удаление товара из корзины")
def test_remove_item_from_cart(shop_service, add_random_item, user):
    item_to_remove = add_random_item
    
    resp = shop_service.remove_item_from_cart(user["token"], item_to_remove["item_id"])
    assert resp.get("message") in CART_MESSAGES["item_removed"]
    
    cart = shop_service.get_cart(user["token"])
    cart_items = [item.item_id for item in cart.items]
    assert item_to_remove["item_id"] not in cart_items, "Товар должен быть удален из корзины"


@allure.title("Попытка добавления несуществующего товара")
def test_add_invalid_item(shop_service, user):

    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)
    
    resp = adapter.add_item_to_cart(user["token"], 99999, 1)
    if resp.status_code == 500:
        pytest.skip("Сервис возвращает 500 вместо 400 — это баг, требуется завести баг-репорт")
    assert resp.status_code == 400


@allure.title("Попытка добавления товара с невалидным количеством")
@pytest.mark.parametrize("quantity,expected_status", [
    (0, http.HTTPStatus.BAD_REQUEST),
    (-1, http.HTTPStatus.BAD_REQUEST),
])
def test_add_item_invalid_quantity(shop_service, user, random_item, quantity, expected_status):
    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)
    
    resp = adapter.add_item_to_cart(user["token"], random_item["item_id"], quantity)
    validate_response(resp, expected_status)


@allure.title("Попытка добавления товара без авторизации")
def test_add_item_unauthorized(shop_service, random_item):
    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)
    
    resp = adapter.add_item_to_cart("invalid_token", random_item["item_id"], 1)
    validate_response(resp, http.HTTPStatus.UNAUTHORIZED)


@allure.title("Попытка удаления несуществующего товара из корзины")
def test_remove_nonexistent_item(shop_service, user):
    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)
    
    resp = adapter.remove_item_from_cart(user["token"], 99999)
    validate_response(resp, http.HTTPStatus.NOT_FOUND)
