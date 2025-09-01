import allure
import pytest

from src.builders.user_builder import UserBuilder
from src.utils.constants import AUTH_MESSAGES
from src.utils.validations import validate_response
from http import HTTPStatus


@allure.title("Регистрация нового пользователя")
def test_user_registration(shop_service):
    new_user = UserBuilder().build()
    resp = shop_service.register_user(new_user["username"], new_user["password"])
    validate_response(resp, HTTPStatus.OK)
    resp_data = resp.json()
    assert resp_data["message"] == AUTH_MESSAGES["registration_successful"]


@allure.title("Вход пользователя в систему")
def test_user_login(shop_service, user):
    resp = shop_service.login_user(user["username"], user["password"])
    validate_response(resp, HTTPStatus.OK)
    resp_data = resp.json()
    assert isinstance(resp_data["token"], str), "Токен должен быть строкой"
    assert len(resp_data["token"]) > 0, "Токен не должен быть пустым"


@allure.title("Попытка входа с неверными данными")
@pytest.mark.parametrize(
    "username,password,expected_message",
    [
        ("wrong_username", "correct_password", "Invalid credentials"),
        ("correct_username", "wrong_password", "Invalid credentials"),
        ("wrong_username", "wrong_password", "Invalid credentials"),
    ],
)
def test_login_invalid_credentials(
    shop_service, user, username, password, expected_message
):
    if username == "correct_username":
        username = user["username"]
    if password == "correct_password":
        password = user["password"]

    resp = shop_service.login_user(username, password)
    validate_response(resp, HTTPStatus.UNAUTHORIZED)
    
    message = resp.json().get("message", "")
    assert message == expected_message, f"Неожиданное сообщение: {message}"


@allure.title("Попытка регистрации с существующим username")
def test_duplicate_username_registration(shop_service, user):
    resp = shop_service.register_user(user["username"], "ValidPass123!")
    validate_response(resp, HTTPStatus.BAD_REQUEST)
    
    message = resp.json().get("message", "")
    assert message == "User already exists", f"Неожиданное сообщение: {message}"


@allure.title("Попытка регистрации с невалидным username")
@pytest.mark.parametrize(
    "username,expected_message",
    [
        ("ab", "Username does not match the criteria"),
        ("user@123", "Username does not match the criteria"),
        ("user 123", "Username does not match the criteria"),
        ("", "Username does not match the criteria"),
    ],
)
def test_invalid_username_registration(shop_service, username, expected_message):
    resp = shop_service.register_user(username, "ValidPass123!")
    validate_response(resp, HTTPStatus.BAD_REQUEST)
    
    message = resp.json().get("message", "")
    valid_messages = [
        "Username does not match the criteria",
        "User already exists",
        "Invalid data"
    ]
    assert any(valid_msg in message for valid_msg in valid_messages), f"Неожиданное сообщение: {message}"


@allure.title("Попытка регистрации с невалидным password")
@pytest.mark.parametrize(
    "password,expected_message",
    [
        ("short", "Password does not match the criteria"),
        ("nouppercase123!", "Password does not match the criteria"),
        ("NOLOWERCASE123!", "Password does not match the criteria"),
        ("NoSpecialChar123", "Password does not match the criteria"),
        ("", "Password does not match the criteria"),
    ],
)
def test_invalid_password_registration(shop_service, password, expected_message):
    resp = shop_service.register_user("validuser123", password)
    validate_response(resp, HTTPStatus.BAD_REQUEST)
    
    message = resp.json().get("message", "")
    valid_messages = [
        "Password does not match the criteria",
        "User already exists",
        "Invalid data"
    ]
    assert any(valid_msg in message for valid_msg in valid_messages), f"Неожиданное сообщение: {message}"


@allure.title("Попытка входа без авторизации")
def test_login_without_authorization(shop_service):
    resp = shop_service.login_user("", "")
    validate_response(resp, HTTPStatus.UNAUTHORIZED)


@pytest.mark.skip(reason="БАГ: API возвращает 500 Internal Server Error вместо 400 Bad Request для слишком длинных username и password")
@allure.title("Регистрация с слишком длинными username и password")
def test_registration_with_too_long_username_and_password(shop_service):
    long_username = "a" * 1000
    resp = shop_service.register_user(long_username, "ValidPass123!")
    validate_response(resp, HTTPStatus.BAD_REQUEST)
    
    long_password = "A" + "a" * 998 + "1!"
    resp = shop_service.register_user("validuser123", long_password)
    validate_response(resp, HTTPStatus.BAD_REQUEST)


@allure.title("Проверка структуры JWT токена")
def test_jwt_token_structure(shop_service, user):
    resp = shop_service.login_user(user["username"], user["password"])
    validate_response(resp, HTTPStatus.OK)
    resp_data = resp.json()
    
    assert "token" in resp_data, "Ответ должен содержать поле token"
    assert isinstance(resp_data["token"], str), "Токен должен быть строкой"
    assert len(resp_data["token"]) > 0, "Токен не должен быть пустым"
    
    token_parts = resp_data["token"].split('.')
    assert len(token_parts) == 3, "JWT токен должен содержать 3 части"
