import allure
import pytest
import http
from src.utils.validations import validate_response, validate_cart_response

pytestmark = [
    allure.epic("Система корзины"),
    allure.feature("Операции с корзиной"),
    allure.story("Добавление и удаление товаров"),
]


@allure.title("Добавление товара в корзину")
@allure.severity(allure.severity_level.CRITICAL)
def test_add_item_to_cart(cart_adapter, add_random_item, user):
    with allure.step("Добавление товара в корзину"):
        resp = cart_adapter.add_item(
            user["token"], add_random_item["item_id"], add_random_item["quantity"]
        )
        allure.attach(str(resp.json()), "Ответ API", allure.attachment_type.JSON)
    validate_response(resp, http.HTTPStatus.OK)

    response_data = resp.json()
    assert "message" in response_data
    assert response_data["message"] in [
        "Item added to cart",
        "Товар добавлен в корзину",
    ]


@allure.title("Получение содержимого корзины")
@allure.severity(allure.severity_level.NORMAL)
def test_get_cart_contents(cart_adapter, user):
    with allure.step("Получение корзины"):
        resp = cart_adapter.get_cart(user["token"])
        allure.attach(str(resp.json()), "Ответ API", allure.attachment_type.JSON)
    validate_response(resp, http.HTTPStatus.OK)
    validate_cart_response(resp.json())


@allure.title("Удаление товара из корзины")
@allure.severity(allure.severity_level.NORMAL)
def test_remove_item_from_cart(cart_adapter, add_random_item, user):
    with allure.step("Удаление товара из корзины"):
        resp = cart_adapter.remove_item(user["token"], add_random_item["item_id"])
        allure.attach(str(resp.json()), "Ответ API", allure.attachment_type.JSON)
    validate_response(resp, http.HTTPStatus.OK)

    response_data = resp.json()
    assert "message" in response_data
    assert response_data["message"] in [
        "Item removed from cart",
        "Товар удалён из корзины",
        "Товар удален из корзины",
    ]


@allure.title("Попытка добавления несуществующего товара")
@allure.severity(allure.severity_level.NORMAL)
def test_add_invalid_item(cart_adapter, user):
    with allure.step("Добавление несуществующего товара"):
        resp = cart_adapter.add_item(user["token"], 99999, 1)
        allure.attach(resp.text, "Ответ API", allure.attachment_type.TEXT)
    assert resp.status_code in [400, 500]
