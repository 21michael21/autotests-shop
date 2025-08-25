
import pytest
import random
import string
import os
import allure
import json
from src.backend.clients.http_client.client import HTTPClient
from src.backend.services.shop.adapter import ShopAdapter
from src.backend.services.shop.service import ShopService
from src.utils.allure_utils import attach_test_data, attach_response_data


@pytest.fixture
def http_client():
    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    return HTTPClient(base_url)

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
    import secrets
    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice("!@#$%^&*()_+-=")
    rest = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(4))
    password = upper + lower + digit + special + rest
    
    reg_resp = shop_service.register_user(username, password)
    attach_response_data(reg_resp.model_dump(), "Ответ регистрации")
    
    login_resp = shop_service.login_user(username, password)
    attach_response_data(login_resp.model_dump(), "Ответ логина")
    
    return {"username": username, "password": password, "token": login_resp.token}

@pytest.fixture
def random_item(shop_service: ShopService, user: dict) -> dict:
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
            raise Exception("Каталог пуст")
            
    except Exception as e:
        from src.utils.allure_utils import attach_error_details
        attach_error_details(
            error_type=type(e).__name__,
            error_message=str(e),
            operation="get_random_item"
        )
        raise

@pytest.fixture
def add_random_item(shop_service: ShopService, random_item: dict, user: dict):
    add_resp = shop_service.add_item_to_cart(user["token"], random_item["item_id"], random_item["quantity"])
    
    attach_response_data(add_resp, "Ответ добавления товара в корзину")
    
    return random_item

@pytest.fixture
def created_order_id(shop_service: ShopService, user: dict, add_random_item):
    order_resp = shop_service.create_order(user["token"])
    order_id = order_resp["order_id"]
    
    attach_response_data(order_resp, "Ответ создания заказа")
    
    return order_id

