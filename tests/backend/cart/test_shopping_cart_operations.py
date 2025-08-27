import allure
import pytest

from src.utils.validations import validate_response, validate_cart_response
from src.utils.constants import CART_MESSAGES
from http import HTTPStatus


@allure.title("Добавление товара в корзину")
def test_add_item_to_cart(shop_service, random_item, user):
    resp = shop_service.add_item_to_cart(user["token"], random_item["item_id"], random_item["quantity"])
    validate_response(resp, 200)
    resp_data = resp.json()
    assert resp_data.get("message") in CART_MESSAGES["item_added"]
    
    cart = shop_service.get_cart(user["token"])
    shop_service.validate_item_in_cart(cart, random_item["item_id"])


@allure.title("Получение содержимого корзины")
def test_get_cart_contents(shop_service, user, random_item_in_cart):
    resp = shop_service.get_cart(user["token"])
    validate_cart_response(resp.model_dump())
    
    assert len(resp.items) > 0, "Корзина должна содержать товары после добавления"


@allure.title("Удаление товара из корзины")
def test_remove_item_from_cart(shop_service, random_item_in_cart, user):
    item_to_remove = random_item_in_cart
    
    resp = shop_service.remove_item_from_cart(user["token"], item_to_remove["item_id"])
    validate_response(resp, 200)
    resp_data = resp.json()
    assert resp_data.get("message") in CART_MESSAGES["item_removed"]
    
    cart = shop_service.get_cart(user["token"])
    shop_service.validate_item_not_in_cart(cart, item_to_remove["item_id"])


@pytest.mark.skip(reason="БАГ: API принимает несуществующий товар и возвращает успешный ответ, ожидался 400 Bad Request")
@allure.title("Попытка добавления несуществующего товара")
def test_add_invalid_item(shop_service, user):
    resp = shop_service.add_item_to_cart(user["token"], 99999, 1)
    validate_response(resp, HTTPStatus.BAD_REQUEST)


@pytest.mark.skip(reason="БАГ: API принимает некорректное количество и возвращает успешный ответ, ожидался 400 Bad Request")
@allure.title("Попытка добавления товара с невалидным количеством")
@pytest.mark.parametrize(
    "quantity,expected_status",
    [
        (0, HTTPStatus.BAD_REQUEST),
        (-1, HTTPStatus.BAD_REQUEST),
    ],
)
def test_add_item_invalid_quantity(shop_service, random_item, user, quantity, expected_status):
    resp = shop_service.add_item_to_cart(user["token"], random_item["item_id"], quantity)
    validate_response(resp, expected_status)


@pytest.mark.skip(reason="БАГ: API возвращает успешный ответ при удалении несуществующего товара, ожидался 400 Bad Request")
@allure.title("Попытка удаления несуществующего товара из корзины")
def test_remove_nonexistent_item(shop_service, user):
    resp = shop_service.remove_item_from_cart(user["token"], 99999)
    validate_response(resp, HTTPStatus.BAD_REQUEST)
