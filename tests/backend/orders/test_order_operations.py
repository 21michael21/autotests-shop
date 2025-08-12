import allure
import pytest
import http
from src.utils.validations import validate_response, validate_order_response
pytestmark = [allure.epic('Система управления заказами'), allure.feature('Создание и просмотр заказов'), allure.story('Оформление заказов и получение деталей')]

@pytest.fixture
def created_order_id(orders_adapter, add_random_item, user):
    resp = orders_adapter.create_order(user['token'])
    validate_response(resp, http.HTTPStatus.OK)
    return resp.json()['order_id']

@allure.title('Получение деталей заказа')
@allure.severity(allure.severity_level.NORMAL)
def test_get_order_details(orders_adapter, user, created_order_id):
    order_id = created_order_id
    with allure.step('Получение деталей заказа'):
        resp = orders_adapter.get_order_details(user['token'], order_id)
        allure.attach(str(resp.json()), 'Детали заказа', allure.attachment_type.JSON)
    validate_response(resp, http.HTTPStatus.OK)
    validate_order_response(resp.json(), expected_order_id=order_id)

@allure.title('Попытка получения несуществующего заказа')
@allure.severity(allure.severity_level.NORMAL)
def test_get_nonexistent_order(orders_adapter, user):
    nonexistent_order_id = 999999
    with allure.step('Попытка получения несуществующего заказа'):
        resp = orders_adapter.get_order_details(user['token'], nonexistent_order_id)
    validate_response(resp, http.HTTPStatus.NOT_FOUND)

@allure.title('Попытка создания заказа без авторизации')
@allure.severity(allure.severity_level.NORMAL)
def test_create_order_unauthorized(orders_adapter):
    invalid_token = 'Bearer invalid_token'
    with allure.step('Попытка создания заказа с невалидным токеном'):
        resp = orders_adapter.create_order(invalid_token)
    validate_response(resp, http.HTTPStatus.UNAUTHORIZED)
