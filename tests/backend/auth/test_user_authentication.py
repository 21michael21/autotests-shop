import allure
import pytest
import http
from src.utils.validations import validate_response, validate_json_structure
from src.builders.user_builder import UserBuilder
pytestmark = [allure.epic('Система аутентификации'), allure.feature('Регистрация и вход пользователей'), allure.story('Базовые операции аутентификации')]

@allure.title('Регистрация нового пользователя')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_registration(auth_adapter):
    new_user = UserBuilder().build()
    with allure.step('Регистрация пользователя'):
        resp = auth_adapter.register_user(new_user['username'], new_user['password'])
        allure.attach(str(resp.text), 'Ответ API', allure.attachment_type.TEXT)
    validate_response(resp, http.HTTPStatus.OK)
    
    response_data = resp.json()
    validate_json_structure(response_data, ['message'], 'Проверка структуры ответа регистрации')
    assert response_data['message'] == 'Registration successful'

@allure.title('Вход пользователя в систему')
@allure.severity(allure.severity_level.CRITICAL)
def test_user_login(auth_adapter, user):
    with allure.step('Вход пользователя'):
        resp = auth_adapter.login_user(user['username'], user['password'])
        allure.attach(str(resp.json()), 'Ответ API', allure.attachment_type.JSON)
    validate_response(resp, http.HTTPStatus.OK)
    
    response_data = resp.json()
    validate_json_structure(response_data, ['token'], 'Проверка структуры ответа входа')
    assert isinstance(response_data['token'], str), 'Токен должен быть строкой'
    assert len(response_data['token']) > 0, 'Токен не должен быть пустым'

@allure.title('Попытка входа с неверными данными')
@allure.severity(allure.severity_level.NORMAL)
def test_login_invalid_credentials(auth_adapter, user):
    with allure.step('Вход с неверным паролем'):
        resp = auth_adapter.login_user(user['username'], 'wrong_password')
        allure.attach(str(resp.json()), 'Ответ API', allure.attachment_type.JSON)
    validate_response(resp, http.HTTPStatus.UNAUTHORIZED)
