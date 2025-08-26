import allure
import pytest
import http
from src.utils.validations import validate_response, validate_order_response
from src.backend.services.shop.adapter import ShopAdapter
from src.backend.clients.http_client.client import HTTPClient
import os

pytestmark = [
    allure.epic("Система управления заказами"),
    allure.feature("Создание и просмотр заказов"),
    allure.story("Оформление заказов и получение деталей"),
]


@allure.title("Создание заказа")
def test_create_order(shop_service, user, add_random_item):
    resp = shop_service.create_order(user["token"])
    assert "order_id" in resp
    assert resp["order_id"] > 0


@allure.title("Получение деталей заказа")
def test_get_order_details(shop_service, user, created_order_id):
    order_id = created_order_id
    resp = shop_service.get_order_details(user["token"], order_id)
    validate_order_response(resp, expected_order_id=order_id)


@allure.title("Попытка получения несуществующего заказа")
def test_get_nonexistent_order(shop_service, user):

    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)

    nonexistent_order_id = 9999999999999999999999999
    resp = adapter.get_order_details(user["token"], nonexistent_order_id)
    validate_response(resp, http.HTTPStatus.NOT_FOUND)


@allure.title("Попытка создания заказа без авторизации")
def test_create_order_unauthorized(shop_service):
    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os

    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)

    invalid_token = "Bearer invalid_token"
    resp = adapter.create_order(invalid_token)
    validate_response(resp, http.HTTPStatus.UNAUTHORIZED)


@allure.title("Попытка создания заказа с пустой корзиной")
def test_create_order_empty_cart(shop_service, user):
    try:
        cart = shop_service.get_cart(user["token"])
        if cart.items:
            for item in cart.items:
                shop_service.remove_item_from_cart(user["token"], item.item_id)
    except Exception:
        pass

    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os

    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)

    resp = adapter.create_order(user["token"])
    validate_response(resp, http.HTTPStatus.BAD_REQUEST)


@allure.title("Попытка получения заказа другого пользователя")
def test_get_other_user_order(shop_service, user, created_order_id):
    from src.builders.user_builder import UserBuilder

    new_user = UserBuilder().build()
    reg_resp = shop_service.register_user(new_user["username"], new_user["password"])
    login_resp = shop_service.login_user(new_user["username"], new_user["password"])
    second_user_token = login_resp.token

    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os

    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)

    resp = adapter.get_order_details(second_user_token, created_order_id)
    validate_response(resp, http.HTTPStatus.NOT_FOUND)


@allure.title("Проверка очистки корзины после создания заказа")
def test_cart_cleared_after_order(shop_service, user, add_random_item):
    order_resp = shop_service.create_order(user["token"])
    order_id = order_resp["order_id"]

    cart = shop_service.get_cart(user["token"])
    assert len(cart.items) == 0, "Корзина должна быть очищена после создания заказа"
