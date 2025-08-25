import allure
import pytest
import http
from src.utils.validations import validate_response, validate_json_structure
from src.builders.user_builder import UserBuilder
from src.utils.constants import AUTH_MESSAGES

pytestmark = [
    allure.epic("Система аутентификации"),
    allure.feature("Регистрация и вход пользователей"),
    allure.story("Базовые операции аутентификации"),
]


@allure.title("Регистрация нового пользователя")
def test_user_registration(shop_service):
    new_user = UserBuilder().build()
    resp = shop_service.register_user(new_user["username"], new_user["password"])
    assert resp.message == AUTH_MESSAGES["registration_successful"]


@allure.title("Вход пользователя в систему")
def test_user_login(shop_service, user):
    resp = shop_service.login_user(user["username"], user["password"])
    assert isinstance(resp.token, str), "Токен должен быть строкой"
    assert len(resp.token) > 0, "Токен не должен быть пустым"


@allure.title("Попытка входа с неверными данными")
@pytest.mark.parametrize("username,password,expected_status", [
    ("wrong_username", "correct_password", http.HTTPStatus.UNAUTHORIZED),
    ("correct_username", "wrong_password", http.HTTPStatus.UNAUTHORIZED),
    ("wrong_username", "wrong_password", http.HTTPStatus.UNAUTHORIZED),
])
def test_login_invalid_credentials(shop_service, user, username, password, expected_status):
    if username == "correct_username":
        username = user["username"]
    if password == "correct_password":
        password = user["password"]
    
    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)
    
    resp = adapter.login_user(username, password)
    validate_response(resp, expected_status)


@allure.title("Попытка регистрации с существующим username")
def test_duplicate_username_registration(shop_service, user):
    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)
    
    resp = adapter.register_user(user["username"], "newpassword123")
    validate_response(resp, http.HTTPStatus.BAD_REQUEST)
    assert "User already exists" in resp.json().get("message", "")


@allure.title("Попытка регистрации с невалидным username")
@pytest.mark.parametrize("username,expected_status", [
    ("ab", http.HTTPStatus.BAD_REQUEST),
    ("user@123", http.HTTPStatus.BAD_REQUEST),
    ("user 123", http.HTTPStatus.BAD_REQUEST),
    ("", http.HTTPStatus.BAD_REQUEST),
])
def test_invalid_username_registration(shop_service, username, expected_status):
    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)
    
    resp = adapter.register_user(username, "ValidPass123!")
    validate_response(resp, expected_status)
    assert "Username does not match the criteria" in resp.json().get("message", "")


@allure.title("Попытка регистрации с невалидным password")
@pytest.mark.parametrize("password,expected_status", [
    ("short", http.HTTPStatus.BAD_REQUEST),
    ("nouppercase123!", http.HTTPStatus.BAD_REQUEST),
    ("NOLOWERCASE123!", http.HTTPStatus.BAD_REQUEST),
    ("NoSpecialChar123", http.HTTPStatus.BAD_REQUEST),
    ("", http.HTTPStatus.BAD_REQUEST),
])
def test_invalid_password_registration(shop_service, password, expected_status):
    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)
    
    resp = adapter.register_user("validuser123", password)
    validate_response(resp, expected_status)
    assert "Password does not match the criteria" in resp.json().get("message", "")


@allure.title("Попытка входа без авторизации")
def test_login_without_authorization(shop_service):
    from src.backend.services.shop.adapter import ShopAdapter
    from src.backend.clients.http_client.client import HTTPClient
    import os
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:5050")
    http_client = HTTPClient(base_url)
    adapter = ShopAdapter(http_client)
    
    resp = adapter.login_user("", "")
    validate_response(resp, http.HTTPStatus.BAD_REQUEST)


@allure.title("Проверка JWT токена")
def test_jwt_token_structure(shop_service, user):
    resp = shop_service.login_user(user["username"], user["password"])
    token = resp.token
    
    parts = token.split('.')
    assert len(parts) == 3, "JWT токен должен содержать 3 части"
    
    assert len(token) > 50, "JWT токен должен быть достаточно длинным"
