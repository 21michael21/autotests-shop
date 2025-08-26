import allure
import pytest

from src.utils.validations import validate_catalog_response, validate_response
from src.utils.constants import HTTP_STATUSES


@allure.title("Получение каталога товаров")
def test_get_catalog(shop_service, user):
    resp = shop_service.get_catalog(user["token"])
    
    catalog_data = resp.model_dump()
    validate_catalog_response(catalog_data["items"])
    



@allure.title("Фильтрация товаров по цене")
def test_filter_by_price(shop_service, user):
    resp = shop_service.get_catalog(user["token"], min_price=100, max_price=500)
    items = resp.model_dump()["items"]
    validate_catalog_response(items, min_items=0)
    
    shop_service.validate_items_price_range(items, 100, 500)


@allure.title("Сортировка товаров по цене")
def test_sort_by_price(shop_service, user):
    resp = shop_service.get_catalog(user["token"], sort_by="price", sort_order="asc")
    
    catalog_data = resp.model_dump()
    validate_catalog_response(catalog_data["items"])
    
    shop_service.validate_items_sorted_by_price(catalog_data["items"], "asc")


@pytest.mark.skip(reason="БАГ: API принимает отрицательные цены и возвращает успешный ответ, ожидался 400 Bad Request")
@allure.title("Попытка фильтрации с невалидными параметрами")
def test_invalid_filter_params(shop_service, user):
    resp = shop_service.get_catalog(user["token"], min_price=-100, max_price="invalid")
    validate_response(resp, HTTP_STATUSES["bad_request"])


@allure.title("Фильтрация товаров по бренду")
def test_filter_by_brand(shop_service, user):
    resp = shop_service.get_catalog(user["token"], brand="Apple")
    
    catalog_data = resp.model_dump()
    validate_catalog_response(catalog_data["items"], min_items=0)
    
    shop_service.validate_items_brand(catalog_data["items"], "Apple")


@allure.title("Проверка структуры товара")
def test_item_structure(shop_service, user):
    resp = shop_service.get_catalog(user["token"])
    
    catalog_data = resp.model_dump()
    validate_catalog_response(catalog_data["items"], min_items=1)
    
    first_item = catalog_data["items"][0]
    required_fields = ["id", "name", "price"]
    
    shop_service.validate_item_has_required_fields(first_item, required_fields)
