import random
import string
from typing import Dict
import allure
import json


class UserBuilder:

    def __init__(self):
        with allure.step("Инициализация UserBuilder"):
            allure.attach(
                "UserBuilder готов к генерации тестовых данных пользователей",
                "Статус инициализации",
                allure.attachment_type.TEXT,
            )

    def build(self) -> Dict[str, str]:
        with allure.step("Генерация тестовых данных пользователя"):
            with allure.step("Генерация username"):
                username = self._generate_username()
                allure.attach(
                    username, "Сгенерированный username", allure.attachment_type.TEXT
                )
                username_validation = {
                    "username": username,
                    "length": len(username),
                    "min_length_required": 6,
                    "is_valid": len(username) >= 6,
                    "contains_only_alphanumeric": username.isalnum(),
                }
                allure.attach(
                    json.dumps(username_validation, indent=2),
                    "Валидация username",
                    allure.attachment_type.JSON,
                )
            with allure.step("Генерация password"):
                password = self._generate_password()
                allure.attach(
                    password, "Сгенерированный password", allure.attachment_type.TEXT
                )
                password_validation = {
                    "password": password,
                    "length": len(password),
                    "min_length_required": 8,
                    "has_uppercase": any((c.isupper() for c in password)),
                    "has_lowercase": any((c.islower() for c in password)),
                    "has_special_char": any((not c.isalnum() for c in password)),
                    "is_valid": self._validate_password(password),
                }
                allure.attach(
                    json.dumps(password_validation, indent=2),
                    "Валидация password",
                    allure.attachment_type.JSON,
                )
            user_data = {"username": username, "password": password}
            with allure.step("Формирование итоговых данных"):
                allure.attach(
                    json.dumps(user_data, indent=2),
                    "Итоговые данные пользователя",
                    allure.attachment_type.JSON,
                )
                allure.attach(
                    "Тестовые данные пользователя успешно сгенерированы",
                    "Результат генерации",
                    allure.attachment_type.TEXT,
                )
            return user_data

    def _generate_username(self) -> str:
        username = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        with allure.step(f"Генерация username: {username}"):
            generation_details = {
                "method": "random.choices",
                "characters": "ascii_letters + digits",
                "length": 8,
                "result": username,
            }
            allure.attach(
                json.dumps(generation_details, indent=2),
                "Детали генерации username",
                allure.attachment_type.JSON,
            )
        return username

    def _generate_password(self) -> str:
        uppercase = random.choice(string.ascii_uppercase)
        lowercase = random.choice(string.ascii_lowercase)
        random_chars = "".join(
            random.choices(string.ascii_letters + string.digits, k=5)
        )
        special_char = random.choice("!@#$%^&*")
        password = uppercase + lowercase + random_chars + special_char
        with allure.step(f"Генерация password: {password}"):
            generation_details = {
                "method": "component_based",
                "components": {
                    "uppercase": uppercase,
                    "lowercase": lowercase,
                    "random_chars": random_chars,
                    "special_char": special_char,
                },
                "total_length": len(password),
                "result": password,
            }
            allure.attach(
                json.dumps(generation_details, indent=2),
                "Детали генерации password",
                allure.attachment_type.JSON,
            )
        return password

    def _validate_password(self, password: str) -> bool:
        has_uppercase = any((c.isupper() for c in password))
        has_lowercase = any((c.islower() for c in password))
        has_special = any((not c.isalnum() for c in password))
        has_min_length = len(password) >= 8
        is_valid = has_uppercase and has_lowercase and has_special and has_min_length
        with allure.step(f"Валидация password: {password}"):
            validation_result = {
                "password": password,
                "criteria": {
                    "min_length_8": has_min_length,
                    "has_uppercase": has_uppercase,
                    "has_lowercase": has_lowercase,
                    "has_special_char": has_special,
                },
                "is_valid": is_valid,
            }
            allure.attach(
                json.dumps(validation_result, indent=2),
                "Результат валидации password",
                allure.attachment_type.JSON,
            )
        return is_valid
