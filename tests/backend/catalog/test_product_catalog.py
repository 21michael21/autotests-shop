import http

import allure
import pytest

from src.utils.validations import validate_catalog_response
from src.utils.allure_utils import attach_response_data, attach_error_details


@allure.title("Получение каталога товаров")
def test_get_catalog(shop_service, user):
    resp = shop_service.get_catalog(user["token"])
    
    # shop_service возвращает Pydantic модель, проверяем структуру
    catalog_data = resp.model_dump()
    validate_catalog_response(catalog_data["items"])
    
    attach_response_data(catalog_data, "Каталог товаров")


@allure.title("Фильтрация товаров по цене")
def test_filter_by_price(shop_service, user):
    resp = shop_service.get_catalog(user["token"], min_price=100, max_price=500)
    items = resp.model_dump()["items"]
    validate_catalog_response(items, min_items=0)
    
    for item in items:
        assert 100 <= item["price"] <= 500, f'Цена товара {item["id"]} не в диапазоне 100-500'
    
    attach_response_data(items, "Отфильтрованные товары по цене")


@allure.title("Сортировка товаров по цене")
def test_sort_by_price(shop_service, user):
    resp = shop_service.get_catalog(user["token"], sort_by="price", sort_order="asc")
    
    # shop_service возвращает Pydantic модель, проверяем структуру
    catalog_data = resp.model_dump()
    validate_catalog_response(catalog_data["items"])
    
    prices = [item["price"] for item in catalog_data["items"] if "price" in item]
    assert prices == sorted(prices), "Товары не отсортированы по возрастанию цены"
    
    attach_response_data(catalog_data, "Отсортированные товары по цене")


@allure.title("Попытка фильтрации с невалидными параметрами")
def test_invalid_filter_params(shop_service, user):
    try:
        resp = shop_service.get_catalog(user["token"], min_price=-100, max_price="invalid")
        # Если API принял некорректные параметры - это баг
        pytest.fail("БАГ: API принимает отрицательные цены и возвращает успешный ответ, ожидался 400 Bad Request")
    except Exception as e:
        # API корректно обработал ошибку
        attach_response_data({"error": str(e)}, "Ответ при невалидных параметрах фильтрации")


@allure.title("Фильтрация товаров по бренду")
def test_filter_by_brand(shop_service, user):
    resp = shop_service.get_catalog(user["token"], brand="Apple")
    
    # shop_service возвращает Pydantic модель, проверяем структуру
    catalog_data = resp.model_dump()
    validate_catalog_response(catalog_data["items"], min_items=0)
    
    # Проверяем, что все товары имеют указанный бренд
    for item in catalog_data["items"]:
        if "brand" in item:
            assert item["brand"] == "Apple", f'Товар {item["id"]} имеет неверный бренд'
    
    attach_response_data(catalog_data, "Товары отфильтрованные по бренду")


@allure.title("Проверка структуры товара")
def test_item_structure(shop_service, user):
    resp = shop_service.get_catalog(user["token"])
    
    # shop_service возвращает Pydantic модель, проверяем структуру
    catalog_data = resp.model_dump()
    validate_catalog_response(catalog_data["items"], min_items=1)
    
    # Проверяем конкретную структуру первого товара
    first_item = catalog_data["items"][0]
    required_fields = ["id", "name", "price"]
    
    for field in required_fields:
        assert field in first_item, f"Товар должен содержать поле {field}"
    
    attach_response_data(first_item, "Структура товара")
