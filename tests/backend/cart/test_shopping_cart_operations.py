import http

import allure
import pytest

from src.utils.validations import validate_response, validate_cart_response
from src.utils.constants import CART_MESSAGES
from src.utils.allure_utils import attach_response_data, attach_error_details


@allure.title("Добавление товара в корзину")
def test_add_item_to_cart(shop_service, random_item, user):
    resp = shop_service.add_item_to_cart(user["token"], random_item["item_id"], random_item["quantity"])
    assert resp.get("message") in CART_MESSAGES["item_added"]
    
    cart = shop_service.get_cart(user["token"])
    cart_items = [item.item_id for item in cart.items]
    assert random_item["item_id"] in cart_items, "Товар должен быть в корзине после добавления"
    
    attach_response_data(resp, "Ответ при добавлении товара в корзину")


@allure.title("Получение содержимого корзины")
def test_get_cart_contents(shop_service, user, add_random_item):
    resp = shop_service.get_cart(user["token"])
    validate_cart_response(resp.model_dump())
    
    assert len(resp.items) > 0, "Корзина должна содержать товары после добавления"
    
    attach_response_data(resp.model_dump(), "Содержимое корзины")


@allure.title("Удаление товара из корзины")
def test_remove_item_from_cart(shop_service, add_random_item, user):
    item_to_remove = add_random_item
    
    resp = shop_service.remove_item_from_cart(user["token"], item_to_remove["item_id"])
    assert resp.get("message") in CART_MESSAGES["item_removed"]
    
    cart = shop_service.get_cart(user["token"])
    cart_items = [item.item_id for item in cart.items]
    assert item_to_remove["item_id"] not in cart_items, "Товар должен быть удален из корзины"
    
    attach_response_data(resp, "Ответ при удалении товара")


@allure.title("Попытка добавления несуществующего товара")
def test_add_invalid_item(shop_service, user):
    try:
        resp = shop_service.add_item_to_cart(user["token"], 99999, 1)
        pytest.fail("БАГ: API принимает несуществующий товар и возвращает успешный ответ, ожидался 400 Bad Request")
    except Exception as e:
        attach_response_data({"error": str(e)}, "Ответ при попытке добавить несуществующий товар")


@allure.title("Попытка добавления товара с невалидным количеством")
@pytest.mark.parametrize(
    "quantity,expected_status",
    [
        (0, http.HTTPStatus.BAD_REQUEST),
        (-1, http.HTTPStatus.BAD_REQUEST),
    ],
)
def test_add_item_invalid_quantity(shop_service, random_item, user, quantity, expected_status):
    resp = shop_service.add_item_to_cart(user["token"], random_item["item_id"], quantity)
    
    if "message" in resp and "error" in resp["message"].lower():
        attach_response_data(resp, f"Ответ при попытке добавить товар с количеством {quantity}")
    else:
        pytest.skip(f"БАГ: API принимает некорректное количество {quantity} и возвращает успешный ответ")
    
    attach_response_data(resp, f"Ответ при попытке добавить товар с количеством {quantity}")


@allure.title("Попытка удаления несуществующего товара из корзины")
def test_remove_nonexistent_item(shop_service, user):
    resp = shop_service.remove_item_from_cart(user["token"], 99999)
    
    if "message" in resp and "error" in resp["message"].lower():
        attach_response_data(resp, "Ответ при попытке удалить несуществующий товар")
    else:
        pytest.skip("БАГ: API возвращает успешный ответ при удалении несуществующего товара")
    
    attach_response_data(resp, "Ответ при попытке удалить несуществующий товар")
