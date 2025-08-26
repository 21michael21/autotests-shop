import http
import os

import allure
import pytest

from src.backend.clients.http_client.client import HTTPClient
from src.backend.services.shop.adapter import ShopAdapter
from src.utils.validations import validate_response
from tests.backend.conftest import create_test_adapter

pytestmark = [
    allure.epic("Edge Cases и безопасность"),
    allure.feature("Граничные случаи и тестирование безопасности"),
    allure.story("Тестирование нестандартных сценариев"),
]


@allure.title("Тест на SQL инъекцию в username")
def test_sql_injection_username(shop_service):
    adapter = create_test_adapter()

    malicious_usernames = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "admin'--",
        "'; SELECT * FROM users; --",
    ]

    for username in malicious_usernames:
        resp = adapter.register_user(username, "ValidPass123!")
        assert resp.status_code in [
            400,
            500,
        ], f"SQL инъекция {username} должна быть отклонена"


@allure.title("Тест на XSS в username")
def test_xss_username(shop_service):
    adapter = create_test_adapter()

    malicious_usernames = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "onload=alert('xss')",
        "<img src=x onerror=alert('xss')>",
    ]

    for username in malicious_usernames:
        resp = adapter.register_user(username, "ValidPass123!")
        assert resp.status_code in [400, 500], f"XSS {username} должен быть отклонен"


@allure.title("Тест на очень длинные значения")
def test_very_long_values(shop_service):
    adapter = create_test_adapter()

    long_username = "a" * 1000
    resp = adapter.register_user(long_username, "ValidPass123!")
    assert resp.status_code in [400, 500], "Очень длинный username должен быть отклонен"

    long_password = "A" + "a" * 998 + "1!"
    resp = adapter.register_user("validuser123", long_password)
    assert resp.status_code == 400, "Очень длинный password должен быть отклонен"


@allure.title("Тест на специальные символы в username")
def test_special_characters_username(shop_service):
    adapter = create_test_adapter()

    special_chars = [
        "user\n123",
        "user\t123",
        "user\r123",
        "user\0123",
    ]

    for username in special_chars:
        resp = adapter.register_user(username, "ValidPass123!")
        assert resp.status_code in [
            400,
            500,
        ], f"Username с спецсимволом {repr(username)} должен быть отклонен"
