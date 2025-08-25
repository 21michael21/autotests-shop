import random
import string
from typing import Dict
import allure
import json


class UserBuilder:
    def __init__(self):
        pass

    def build(self) -> Dict[str, str]:
        username = self._generate_username()
        password = self._generate_password()
        user_data = {"username": username, "password": password}
        allure.attach(
            json.dumps(user_data, indent=2),
            "Итоговые данные пользователя",
            allure.attachment_type.JSON,
        )
        return user_data

    def _generate_username(self) -> str:
        username = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        return username

    def _generate_password(self) -> str:
        uppercase = random.choice(string.ascii_uppercase)
        lowercase = random.choice(string.ascii_lowercase)
        random_chars = "".join(
            random.choices(string.ascii_letters + string.digits, k=5)
        )
        special_char = random.choice("!@#$%^&*")
        password = uppercase + lowercase + random_chars + special_char
        return password

    def _validate_password(self, password: str) -> bool:
        has_uppercase = any((c.isupper() for c in password))
        has_lowercase = any((c.islower() for c in password))
        has_special = any((not c.isalnum() for c in password))
        has_min_length = len(password) >= 8
        is_valid = has_uppercase and has_lowercase and has_special and has_min_length
        return is_valid
