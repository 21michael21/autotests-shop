import json
import random
import secrets
import string

import allure
import pytest

from config import BASE_URL
from src.backend.clients.http_client.client import HTTPClient
from src.backend.services.shop.adapter import ShopAdapter
from src.backend.services.shop.service import ShopService
from src.utils.allure_utils import attach_test_data, attach_response_data, attach_error_details
from src.utils.validations import validate_response


def _get_random_item_with_error_handling(shop_service, user):
    """
    Получает случайный товар из каталога с обработкой ошибок.
    Try-except используется для корректной обработки ситуаций когда каталог пуст
    или API недоступен, что позволяет тестам продолжить выполнение с информативными сообщениями.
    """
    try:
        catalog = shop_service.get_catalog(user["token"])
        if catalog.items:
            item = random.choice(catalog.items)
            item_data = {
                "item_id": item.id,
                "name": item.name,
                "brand": item.brand,
                "price": item.price,
                "quantity": random.randint(1, 3)
            }
            
            attach_test_data(item_data, "Полученный случайный товар")
            
            return item_data
        else:
            raise ValueError("Каталог пуст - нет доступных товаров для тестирования")
            
    except Exception as e:
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "operation": "get_random_item",
            "user_token": user["token"][:10] + "..." if user["token"] else "None"
        }
        attach_error_details(
            error_type=type(e).__name__,
            error_message=str(e),
            operation="get_random_item",
            **error_details
        )
        raise


@pytest.fixture
def http_client():
    return HTTPClient(BASE_URL)

@pytest.fixture
def shop_adapter(http_client: HTTPClient) -> ShopAdapter:
    adapter = ShopAdapter(http_client)
    return adapter

@pytest.fixture
def shop_service(shop_adapter: ShopAdapter) -> ShopService:
    service = ShopService(shop_adapter)
    return service

@pytest.fixture
def user(shop_service):
    username = "user" + ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice("!@#$%^&*()_+-=")
    rest = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(4))
    password = upper + lower + digit + special + rest
    
    reg_resp = shop_service.register_user(username, password)
    validate_response(reg_resp, 200)
    attach_response_data(reg_resp.json(), "Ответ регистрации")
    
    login_resp = shop_service.login_user(username, password)
    validate_response(login_resp, 200)
    attach_response_data(login_resp.json(), "Ответ логина")
    
    return {"username": username, "password": password, "token": login_resp.json()["token"]}

@pytest.fixture
def random_item(shop_service: ShopService, user: dict) -> dict:
    return _get_random_item_with_error_handling(shop_service, user)

@pytest.fixture
def random_item_in_cart(shop_service: ShopService, random_item: dict, user: dict):
    add_resp = shop_service.add_item_to_cart(user["token"], random_item["item_id"], random_item["quantity"])
    validate_response(add_resp, 200)
    
    attach_response_data(add_resp.json(), "Ответ добавления товара в корзину")
    
    return random_item

@pytest.fixture
def order_id(shop_service: ShopService, user: dict, random_item_in_cart):
    order_resp = shop_service.create_order(user["token"])
    validate_response(order_resp, 200)
    order_data = order_resp.json()
    order_id = order_data["order_id"]
    
    attach_response_data(order_data, "Ответ создания заказа")
    
    return order_id

