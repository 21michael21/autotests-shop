import json
from typing import Any, Optional, Mapping, List
import allure
import requests
import http

def assert_eq(
    actual_value: Any,
    expected_value: Any,
    allure_title: str,
    error_msg: Optional[str] = None
) -> None:
    with allure.step(allure_title):
        try:
            assert actual_value == expected_value, error_msg or "Сравниваемые значения не равны"
        except AssertionError:
            error_details = {
                "actual_value": actual_value,
                "expected_value": expected_value,
                "actual_repr": repr(actual_value),
                "expected_repr": repr(expected_value),
                "error_message": error_msg or "Сравниваемые значения не равны"
            }
            allure.attach(
                json.dumps(error_details, indent=2, ensure_ascii=False),
                "Ошибка сравнения",
                allure.attachment_type.JSON,
            )
            raise

def _allure_attach_error(attach_response: dict, error_name: str):
    allure.attach(
        json.dumps(
            attach_response,
            indent=2,
            ensure_ascii=False,
        ),
        error_name,
        attachment_type=allure.attachment_type.JSON,
    )


def _dict_contains(superset: Mapping[str, Any], subset: Mapping[str, Any]) -> bool:
    for key, expected_value in subset.items():
        if key not in superset:
            return False
        actual_value = superset[key]
        if isinstance(expected_value, Mapping) and isinstance(actual_value, Mapping):
            if not _dict_contains(actual_value, expected_value):
                return False
        else:
            if actual_value != expected_value:
                return False
    return True


def assert_json_contains(
    actual_json: dict,
    expected_subset: dict,
    allure_title: str,
) -> None:
    with allure.step(allure_title):
        attach_data = {
            "actual_json": actual_json,
            "expected_subset": expected_subset
        }
        allure.attach(
            json.dumps(attach_data, indent=2, ensure_ascii=False),
            "Сравнение JSON",
            allure.attachment_type.JSON,
        )
        for key, value in expected_subset.items():
            assert key in actual_json, f"Ключ '{key}' отсутствует в ответе"
            if isinstance(value, dict):
                assert_json_contains(actual_json[key], value, allure_title)
            else:
                assert actual_json[key] == value, f"Значение ключа '{key}' не совпадает"


def validate_response(
    response: requests.Response,
    expected_status_code: http.HTTPStatus,
    expected_json: Optional[dict] = None,
    expected_json_partial: Optional[dict] = None,
) -> None:
    assert response.status_code == expected_status_code, (
        f"Получен некорректный код ответа: ожидаемый={expected_status_code}, фактический={response.status_code}"
    )
    if expected_json is not None:
        actual_json = response.json()
        assert_eq(actual_json, expected_json, "Проверка полного JSON ответа")
    if expected_json_partial is not None:
        actual_json = response.json()
        assert_json_contains(actual_json, expected_json_partial, "Проверка частичного совпадения JSON")


def validate_json_structure(
    response_data: dict,
    required_fields: List[str],
    allure_title: str = "Проверка структуры JSON",
) -> None:
    missing_fields = [field for field in required_fields if field not in response_data]
    if missing_fields:
        error_details = {
            "missing_fields": missing_fields,
            "available_fields": list(response_data.keys()),
            "response_data": response_data
        }
        allure.attach(
            json.dumps(error_details, indent=2, ensure_ascii=False),
            "Ошибка структуры JSON",
            allure.attachment_type.JSON,
        )
        raise AssertionError(f"Отсутствуют обязательные поля: {missing_fields}")


def validate_catalog_response(response_data: List[dict], min_items: int = 0) -> None:
    assert isinstance(response_data, list), "Ответ должен быть списком"
    assert len(response_data) >= min_items, f"Каталог должен содержать минимум {min_items} товар(ов)"

    if response_data:
        item = response_data[0]
        required_item_fields = ["id", "name", "brand", "price"]
        validate_json_structure(item, required_item_fields, "Проверка структуры товара")

        assert isinstance(item["id"], int), "ID товара должен быть числом"
        assert isinstance(item["price"], (int, float)), "Цена должна быть числом"
        assert item["price"] > 0, "Цена должна быть положительной"


def validate_cart_response(response_data: dict) -> None:
    validate_json_structure(response_data, ["items"], "Проверка структуры корзины")
    assert isinstance(response_data["items"], list), "Поле items должно быть списком"

    if response_data["items"]:
        item = response_data["items"][0]
        required_item_fields = ["item_id", "name", "price", "quantity"]
        validate_json_structure(item, required_item_fields, "Проверка структуры товара в корзине")

        assert isinstance(item["item_id"], int), "ID товара должен быть числом"
        assert isinstance(item["quantity"], int), "Количество должно быть числом"
        assert item["quantity"] > 0, "Количество должно быть положительным"


def validate_order_response(
    response_data: dict, expected_order_id: Optional[int] = None
) -> None:
    required_fields = ["order_id", "total_price", "created_at", "items"]
    validate_json_structure(response_data, required_fields, "Проверка структуры заказа")

    assert isinstance(response_data["order_id"], int), "ID заказа должен быть числом"
    assert isinstance(response_data["total_price"], (int, float)), "Общая стоимость должна быть числом"
    assert response_data["total_price"] > 0, "Общая стоимость должна быть положительной"
    assert isinstance(response_data["created_at"], str), "Дата создания должна быть строкой"
    assert isinstance(response_data["items"], list), "Список товаров должен быть списком"
    assert len(response_data["items"]) > 0, "Заказ должен содержать товары"

    if expected_order_id is not None:
        assert response_data["order_id"] == expected_order_id, f"ID заказа должен быть {expected_order_id}"

    if response_data["items"]:
        item = response_data["items"][0]
        required_item_fields = ["item_id", "name", "brand", "price", "quantity"]
        validate_json_structure(item, required_item_fields, "Проверка структуры товара в заказе")
