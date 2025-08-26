import allure
import pytest

from src.builders.user_builder import UserBuilder
from src.utils.validations import validate_response, validate_order_response
from src.utils.constants import HTTP_STATUSES

pytestmark = [
    allure.epic("Система управления заказами"),
    allure.feature("Создание и просмотр заказов"),
    allure.story("Оформление заказов и получение деталей"),
]


@allure.title("Создание заказа")
def test_create_order(shop_service, user, random_item_in_cart):
    resp = shop_service.create_order(user["token"])
    validate_response(resp, 200)
    resp_data = resp.json()
    assert "order_id" in resp_data
    assert resp_data["order_id"] > 0


@allure.title("Получение деталей заказа")
def test_get_order_details(shop_service, user, order_id):
    resp = shop_service.get_order_details(user["token"], order_id)
    validate_response(resp, 200)
    validate_order_response(resp.json(), expected_order_id=order_id)


@allure.title("Попытка получения несуществующего заказа")
def test_get_nonexistent_order(shop_service, user):
    nonexistent_order_id = 9999999999999999999999999
    resp = shop_service.get_order_details(user["token"], nonexistent_order_id)
    validate_response(resp, HTTP_STATUSES["not_found"])


@allure.title("Попытка создания заказа без авторизации")
def test_create_order_unauthorized(shop_service):
    invalid_token = "Bearer invalid_token"
    resp = shop_service.create_order(invalid_token)
    validate_response(resp, HTTP_STATUSES["unauthorized"])


@allure.title("Попытка создания заказа с пустой корзиной")
def test_create_order_empty_cart(shop_service, user):
    shop_service.clear_cart(user["token"])

    resp = shop_service.create_order(user["token"])
    validate_response(resp, HTTP_STATUSES["bad_request"])


@allure.title("Попытка получения заказа другого пользователя")
def test_get_other_user_order(shop_service, user, order_id):
    new_user = UserBuilder().build()
    reg_resp = shop_service.register_user(new_user["username"], new_user["password"])
    validate_response(reg_resp, 200)
    login_resp = shop_service.login_user(new_user["username"], new_user["password"])
    validate_response(login_resp, 200)
    second_user_token = login_resp.json()["token"]

    resp = shop_service.get_order_details(second_user_token, order_id)
    validate_response(resp, HTTP_STATUSES["not_found"])


@allure.title("Проверка очистки корзины после создания заказа")
def test_cart_cleared_after_order(shop_service, user, random_item_in_cart):
    order_resp = shop_service.create_order(user["token"])
    validate_response(order_resp, 200)
    order_data = order_resp.json()
    order_id = order_data["order_id"]

    cart = shop_service.get_cart(user["token"])
    assert len(cart.items) == 0, "Корзина должна быть очищена после создания заказа"
