import allure
import pytest

from src.utils.validations import validate_response
from http import HTTPStatus

pytestmark = [
    allure.epic("Edge Cases и безопасность"),
    allure.feature("Граничные случаи и тестирование безопасности"),
    allure.story("Тестирование нестандартных сценариев"),
]


@allure.title("Тест на SQL инъекцию в username")
def test_sql_injection_username(shop_service):
    malicious_usernames = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "admin'--",
        "'; SELECT * FROM users; --",
    ]

    shop_service.validate_malicious_usernames_rejected(malicious_usernames)


@allure.title("Тест на XSS в username")
def test_xss_username(shop_service):
    malicious_usernames = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "onload=alert('xss')",
        "<img src=x onerror=alert('xss')>",
    ]

    shop_service.validate_malicious_usernames_rejected(malicious_usernames)


@allure.title("Тест на специальные символы в username")
def test_special_characters_username(shop_service):
    special_chars = [
        "user\n123",
        "user\t123",
        "user\r123",
        "user\0123",
    ]

    shop_service.validate_malicious_usernames_rejected(special_chars)
