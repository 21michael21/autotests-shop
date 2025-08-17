import json
from typing import Any, Optional, Mapping, List
import allure
import requests
import http


@allure.step("Сравнение значений: {allure_title}")
def assert_eq(
    actual_value: Any,
    expected_value: Any,
    allure_title: str,
    error_msg: Optional[str] = None,
) -> None:
    with allure.step(allure_title):
        try:
            allure.attach(
                json.dumps(
                    {
                        "actual": actual_value,
                        "expected": expected_value,
                        "type_actual": str(type(actual_value)),
                        "type_expected": str(type(expected_value)),
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                "Детали сравнения",
                allure.attachment_type.JSON,
            )
            assert actual_value == expected_value, error_msg or "Значения не равны"
            allure.attach("Сравнение успешно", "Результат", allure.attachment_type.TEXT)
        except AssertionError as e:
            error_details = {
                "actual": actual_value,
                "expected": expected_value,
                "error_message": str(e),
                "comparison_type": "equality",
            }
            allure.attach(
                json.dumps(error_details, indent=2, ensure_ascii=False),
                "Ошибка сравнения",
                allure.attachment_type.JSON,
            )
            allure.attach(
                f"Фактическое значение: {repr(actual_value)}",
                "Фактическое значение",
                allure.attachment_type.TEXT,
            )
            allure.attach(
                f"Ожидаемое значение: {repr(expected_value)}",
                "Ожидаемое значение",
                allure.attachment_type.TEXT,
            )
            raise


@allure.step("Утверждение истинности: {allure_title}")
def assert_true(
    condition: bool, allure_title: str, error_msg: Optional[str] = None
) -> None:
    with allure.step(allure_title):
        assert condition, error_msg or "Условие ложно"
        allure.attach("Условие истинно", "Результат", allure.attachment_type.TEXT)


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


@allure.step("Частичная проверка JSON: {allure_title}")
def assert_json_contains(
    actual_json: Mapping[str, Any],
    expected_subset: Mapping[str, Any],
    allure_title: str,
) -> None:
    with allure.step(allure_title):
        allure.attach(
            json.dumps(actual_json, indent=2, ensure_ascii=False),
            "Фактический JSON",
            allure.attachment_type.JSON,
        )
        allure.attach(
            json.dumps(expected_subset, indent=2, ensure_ascii=False),
            "Ожидаемый фрагмент",
            allure.attachment_type.JSON,
        )
        assert _dict_contains(
            actual_json, expected_subset
        ), "JSON не содержит ожидаемые поля/значения"
        allure.attach(
            "JSON содержит ожидаемые поля/значения",
            "Результат",
            allure.attachment_type.TEXT,
        )


@allure.step("Валидация HTTP ответа")
def validate_response(
    response: requests.Response,
    expected_status_code: http.HTTPStatus,
    expected_json: Optional[dict] = None,
    expected_json_partial: Optional[dict] = None,
) -> None:
    with allure.step("Детали HTTP запроса"):
        request_details = {
            "method": response.request.method,
            "url": response.request.url,
            "headers": dict(response.request.headers),
            "body": (
                response.request.body.decode("utf-8")
                if isinstance(response.request.body, bytes)
                else response.request.body
            ),
        }
        allure.attach(
            json.dumps(request_details, indent=2, ensure_ascii=False),
            "HTTP запрос",
            allure.attachment_type.JSON,
        )
    with allure.step("Детали HTTP ответа"):
        response_details = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "url": response.url,
            "elapsed_time": str(response.elapsed),
        }
        allure.attach(
            json.dumps(response_details, indent=2, ensure_ascii=False),
            "HTTP ответ",
            allure.attachment_type.JSON,
        )
    with allure.step(f"Проверка статус-кода (ожидается: {expected_status_code})"):
        assert_eq(
            response.status_code,
            expected_status_code,
            "Проверка статус-кода",
            f"Ожидаемый код: {expected_status_code}, получен: {response.status_code}",
        )

    if expected_json is not None or expected_json_partial is not None:
        try:
            actual_json = response.json()
            allure.attach(
                json.dumps(actual_json, indent=2, ensure_ascii=False),
                "Фактический JSON ответ",
                allure.attachment_type.JSON,
            )
        except json.JSONDecodeError:
            allure.attach(
                response.text, "Текстовый ответ (не JSON)", allure.attachment_type.TEXT
            )
            raise AssertionError("Ожидался JSON ответ, но сервер вернул не-JSON")

        if expected_json is not None:
            allure.attach(
                json.dumps(expected_json, indent=2, ensure_ascii=False),
                "Ожидаемый JSON ответ",
                allure.attachment_type.JSON,
            )
            assert_eq(actual_json, expected_json, "Проверка полного JSON ответа")

        if expected_json_partial is not None:
            assert_json_contains(
                actual_json,
                expected_json_partial,
                "Проверка частичного совпадения JSON",
            )

    with allure.step("Валидация завершена успешно"):
        allure.attach(
            "Все проверки пройдены успешно",
            "Результат валидации",
            allure.attachment_type.TEXT,
        )


@allure.step("Валидация структуры JSON ответа")
def validate_json_structure(
    response_data: dict,
    required_fields: List[str],
    allure_title: str = "Проверка структуры JSON",
) -> None:
    with allure.step(allure_title):
        missing_fields = [
            field for field in required_fields if field not in response_data
        ]
        if missing_fields:
            allure.attach(
                json.dumps(
                    {
                        "missing_fields": missing_fields,
                        "available_fields": list(response_data.keys()),
                    },
                    indent=2,
                ),
                "Отсутствующие поля",
                allure.attachment_type.JSON,
            )
            raise AssertionError(f"Отсутствуют обязательные поля: {missing_fields}")
        allure.attach(
            "Все обязательные поля присутствуют",
            "Результат",
            allure.attachment_type.TEXT,
        )


@allure.step("Валидация ответа каталога")
def validate_catalog_response(response_data: List[dict], min_items: int = 0) -> None:
    with allure.step("Проверка каталога товаров"):
        assert isinstance(response_data, list), "Ответ должен быть списком"
        assert (
            len(response_data) >= min_items
        ), f"Каталог должен содержать минимум {min_items} товар(ов)"

        if response_data:
            item = response_data[0]
            required_item_fields = ["id", "name", "brand", "price"]
            validate_json_structure(
                item, required_item_fields, "Проверка структуры товара"
            )

            assert isinstance(item["id"], int), "ID товара должен быть числом"
            assert isinstance(item["price"], (int, float)), "Цена должна быть числом"
            assert item["price"] > 0, "Цена должна быть положительной"

        allure.attach(
            "Каталог товаров валиден", "Результат", allure.attachment_type.TEXT
        )


@allure.step("Валидация ответа корзины")
def validate_cart_response(response_data: dict) -> None:
    with allure.step("Проверка корзины"):
        validate_json_structure(response_data, ["items"], "Проверка структуры корзины")
        assert isinstance(
            response_data["items"], list
        ), "Поле items должно быть списком"

        if response_data["items"]:
            item = response_data["items"][0]
            required_item_fields = ["item_id", "name", "price", "quantity"]
            validate_json_structure(
                item, required_item_fields, "Проверка структуры товара в корзине"
            )

            assert isinstance(item["item_id"], int), "ID товара должен быть числом"
            assert isinstance(item["quantity"], int), "Количество должно быть числом"
            assert item["quantity"] > 0, "Количество должно быть положительным"

        allure.attach("Корзина валидна", "Результат", allure.attachment_type.TEXT)


@allure.step("Валидация ответа заказа")
def validate_order_response(
    response_data: dict, expected_order_id: Optional[int] = None
) -> None:
    with allure.step("Проверка заказа"):
        required_fields = ["order_id", "total_price", "created_at", "items"]
        validate_json_structure(
            response_data, required_fields, "Проверка структуры заказа"
        )

        assert isinstance(
            response_data["order_id"], int
        ), "ID заказа должен быть числом"
        assert isinstance(
            response_data["total_price"], (int, float)
        ), "Общая стоимость должна быть числом"
        assert (
            response_data["total_price"] > 0
        ), "Общая стоимость должна быть положительной"
        assert isinstance(
            response_data["created_at"], str
        ), "Дата создания должна быть строкой"
        assert isinstance(
            response_data["items"], list
        ), "Список товаров должен быть списком"
        assert len(response_data["items"]) > 0, "Заказ должен содержать товары"

        if expected_order_id is not None:
            assert (
                response_data["order_id"] == expected_order_id
            ), f"ID заказа должен быть {expected_order_id}"

        if response_data["items"]:
            item = response_data["items"][0]
            required_item_fields = ["item_id", "name", "brand", "price", "quantity"]
            validate_json_structure(
                item, required_item_fields, "Проверка структуры товара в заказе"
            )

        allure.attach("Заказ валиден", "Результат", allure.attachment_type.TEXT)
