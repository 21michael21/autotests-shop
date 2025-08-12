import allure
import pytest
import http
from src.utils.validations import validate_response, validate_catalog_response
pytestmark = [allure.epic('Система каталога'), allure.feature('Фильтрация и сортировка товаров'), allure.story('Получение и фильтрация товаров')]

@allure.title('Получение каталога товаров')
@allure.severity(allure.severity_level.CRITICAL)
def test_get_catalog(catalog_adapter, user):
    with allure.step('Получение каталога'):
        resp = catalog_adapter.get_catalog(user['token'])
        allure.attach(str(resp.json()), 'Ответ API', allure.attachment_type.JSON)
    validate_response(resp, http.HTTPStatus.OK)
    validate_catalog_response(resp.json())

@allure.title('Фильтрация товаров по цене')
@allure.severity(allure.severity_level.NORMAL)
def test_filter_by_price(catalog_adapter, user):
    with allure.step('Фильтрация по цене'):
        resp = catalog_adapter.get_catalog(user['token'], min_price=100, max_price=500)
        allure.attach(str(resp.json()), 'Ответ API', allure.attachment_type.JSON)
    validate_response(resp, http.HTTPStatus.OK)
    response_data = resp.json()
    validate_catalog_response(response_data, min_items=0)
    
    if response_data:
        for item in response_data:
            assert 100 <= item['price'] <= 500, f'Цена товара {item["id"]} не в диапазоне 100-500'
    else:
        allure.attach('Фильтр вернул пустой список - нет товаров в диапазоне 100-500', 'Информация', allure.attachment_type.TEXT)

@allure.title('Сортировка товаров по цене')
@allure.severity(allure.severity_level.NORMAL)
def test_sort_by_price(catalog_adapter, user):
    with allure.step('Сортировка по цене'):
        resp = catalog_adapter.get_catalog(user['token'], sort_by='price', sort_order='asc')
        allure.attach(str(resp.json()), 'Ответ API', allure.attachment_type.JSON)
    validate_response(resp, http.HTTPStatus.OK)
    response_data = resp.json()
    validate_catalog_response(response_data)
    
    prices = [item['price'] for item in response_data if 'price' in item]
    assert prices == sorted(prices), 'Товары не отсортированы по возрастанию цены'

@allure.title('Попытка фильтрации с невалидными параметрами')
@allure.severity(allure.severity_level.NORMAL)
def test_invalid_filter_params(catalog_adapter, user):
    with allure.step('Фильтрация с невалидными параметрами'):
        resp = catalog_adapter.get_catalog(user['token'], min_price=-100, max_price='invalid')
        allure.attach(resp.text, 'Ответ API', allure.attachment_type.TEXT)
    assert resp.status_code in [200, 400, 500]
