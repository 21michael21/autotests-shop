import json
from typing import Any, Dict, List, Mapping, Optional

import allure
import requests

from src.utils.allure_utils import attach_error_details, attach_response_data


def _create_error_details(actual_value: Any, expected_value: Any, error_msg: str, operation: str) -> Dict[str, Any]:
    return {
        "actual_value": actual_value,
        "expected_value": expected_value,
        "actual_repr": repr(actual_value),
        "expected_repr": repr(expected_value),
        "error_message": error_msg,
        "operation": operation
    }


def _attach_and_raise_error(error_type: str, error_msg: str, operation: str, error_details: Dict[str, Any]):
    attach_error_details(error_type, error_msg, operation, **error_details)
    raise AssertionError(error_msg)


def validate_equality(actual_value: Any, expected_value: Any, error_msg: str = None) -> None:
    if actual_value != expected_value:
        error_message = error_msg or "Сравниваемые значения не равны"
        error_details = _create_error_details(actual_value, expected_value, error_message, "validate_equality")
        _attach_and_raise_error("AssertionError", error_message, "validate_equality", error_details)


def validate_dict_contains(superset: Mapping[str, Any], subset: Mapping[str, Any]) -> bool:
    for key, expected_value in subset.items():
        if key not in superset:
            return False
        actual_value = superset[key]
        if isinstance(expected_value, Mapping) and isinstance(actual_value, Mapping):
            if not validate_dict_contains(actual_value, expected_value):
                return False
        else:
            if actual_value != expected_value:
                return False
    return True


def validate_json_contains(
    actual_json: dict,
    expected_subset: dict,
    allure_title: str,
) -> None:
    with allure.step(allure_title):
        attach_data = {
            "actual_json": actual_json,
            "expected_subset": expected_subset
        }
        attach_response_data(attach_data, "Сравнение JSON")
        for key, value in expected_subset.items():
            if key not in actual_json:
                error_msg = f"Ключ '{key}' отсутствует в ответе"
                error_details = {"missing_key": key, "available_keys": list(actual_json.keys())}
                _attach_and_raise_error("ValidationError", error_msg, "validate_json_contains", error_details)
            
            if isinstance(value, dict):
                validate_json_contains(actual_json[key], value, allure_title)
            else:
                if actual_json[key] != value:
                    error_msg = f"Значение ключа '{key}' не совпадает"
                    error_details = {
                        "key": key,
                        "actual_value": actual_json[key],
                        "expected_value": value
                    }
                    _attach_and_raise_error("ValidationError", error_msg, "validate_json_contains", error_details)


def validate_response_status(response: requests.Response, expected_status_code: int) -> None:
    if response.status_code != expected_status_code:
        error_msg = f"Получен некорректный код ответа: ожидаемый={expected_status_code}, фактический={response.status_code}"
        error_details = {
            "expected_status": expected_status_code,
            "actual_status": response.status_code,
            "response_url": response.url
        }
        _attach_and_raise_error("ResponseValidationError", error_msg, "validate_response_status", error_details)


def validate_response(
    response: requests.Response,
    expected_status_code: int,
    expected_json: Optional[dict] = None,
    expected_json_partial: Optional[dict] = None,
) -> None:
    validate_response_status(response, expected_status_code)
    
    if expected_json is not None:
        actual_json = response.json()
        validate_equality(actual_json, expected_json, "Проверка полного JSON ответа")
    
    if expected_json_partial is not None:
        actual_json = response.json()
        validate_json_contains(actual_json, expected_json_partial, "Проверка частичного совпадения JSON")


def validate_json_structure(
    response_data: dict,
    required_fields: List[str],
    allure_title: str = "Проверка структуры JSON",
) -> None:
    missing_fields = [field for field in required_fields if field not in response_data]
    if missing_fields:
        error_msg = f"Отсутствуют обязательные поля: {missing_fields}"
        error_details = {
            "missing_fields": missing_fields,
            "available_fields": list(response_data.keys()),
            "response_data": response_data
        }
        _attach_and_raise_error("ValidationError", error_msg, "validate_json_structure", error_details)


def validate_field_type(data: dict, field_name: str, expected_type: type, error_msg: str = None) -> None:
    if field_name not in data:
        return
    
    if not isinstance(data[field_name], expected_type):
        error_message = error_msg or f"Поле '{field_name}' должно быть типа {expected_type.__name__}"
        error_details = {
            "field_name": field_name,
            "expected_type": expected_type.__name__,
            "actual_type": type(data[field_name]).__name__,
            "actual_value": data[field_name]
        }
        _attach_and_raise_error("TypeValidationError", error_message, "validate_field_type", error_details)


def validate_field_value(data: dict, field_name: str, validation_func, error_msg: str) -> None:
    if field_name not in data:
        return
    
    if not validation_func(data[field_name]):
        error_details = {
            "field_name": field_name,
            "field_value": data[field_name],
            "validation_rule": error_msg
        }
        _attach_and_raise_error("ValidationError", error_msg, "validate_field_value", error_details)


def validate_catalog_response(response_data: List[dict], min_items: int = 0) -> None:
    if not isinstance(response_data, list):
        error_details = {"actual_type": type(response_data).__name__, "expected_type": "list"}
        _attach_and_raise_error("TypeValidationError", "Ответ должен быть списком", "validate_catalog_response", error_details)
    
    if len(response_data) < min_items:
        error_msg = f"Каталог должен содержать минимум {min_items} товар(ов)"
        error_details = {"actual_count": len(response_data), "min_required": min_items}
        _attach_and_raise_error("ValidationError", error_msg, "validate_catalog_response", error_details)

    if response_data:
        item = response_data[0]
        required_item_fields = ["id", "name", "brand", "price"]
        validate_json_structure(item, required_item_fields, "Проверка структуры товара")

        validate_field_type(item, "id", int, "ID товара должен быть числом")
        validate_field_type(item, "price", (int, float), "Цена должна быть числом")
        validate_field_value(item, "price", lambda x: x > 0, "Цена должна быть положительной")


def validate_cart_response(response_data: dict) -> None:
    validate_json_structure(response_data, ["items"], "Проверка структуры корзины")
    
    if not isinstance(response_data["items"], list):
        error_details = {"field_name": "items", "expected_type": "list", "actual_type": type(response_data["items"]).__name__}
        _attach_and_raise_error("TypeValidationError", "Поле items должно быть списком", "validate_cart_response", error_details)

    if response_data["items"]:
        item = response_data["items"][0]
        required_item_fields = ["item_id", "name", "price", "quantity"]
        validate_json_structure(item, required_item_fields, "Проверка структуры товара в корзине")

        validate_field_type(item, "item_id", int, "ID товара должен быть числом")
        validate_field_type(item, "quantity", int, "Количество должно быть числом")
        validate_field_value(item, "quantity", lambda x: x > 0, "Количество должно быть положительным")


def validate_order_response(
    response_data: dict, expected_order_id: Optional[int] = None
) -> None:
    required_fields = ["order_id", "total_price", "created_at", "items"]
    validate_json_structure(response_data, required_fields, "Проверка структуры заказа")

    validate_field_type(response_data, "order_id", int, "ID заказа должен быть числом")
    validate_field_type(response_data, "total_price", (int, float), "Общая стоимость должна быть числом")
    validate_field_value(response_data, "total_price", lambda x: x > 0, "Общая стоимость должна быть положительной")
    validate_field_type(response_data, "created_at", str, "Дата создания должна быть строкой")
    validate_field_type(response_data, "items", list, "Список товаров должен быть списком")
    validate_field_value(response_data, "items", lambda x: len(x) > 0, "Заказ должен содержать товары")

    if expected_order_id is not None:
        validate_equality(response_data["order_id"], expected_order_id, f"ID заказа должен быть {expected_order_id}")

    if response_data["items"]:
        item = response_data["items"][0]
        required_item_fields = ["item_id", "name", "brand", "price", "quantity"]
        validate_json_structure(item, required_item_fields, "Проверка структуры товара в заказе")
