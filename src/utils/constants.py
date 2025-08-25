


CART_MESSAGES = {
    "item_added": ["Item added to cart", "Товар добавлен в корзину"],
    "item_removed": ["Item removed from cart", "Товар удалён из корзины", "Товар удален из корзины"]
}


AUTH_MESSAGES = {
    "registration_successful": "Registration successful",
    "user_already_exists": "User already exists",
    "username_criteria": "Username does not match the criteria",
    "password_criteria": "Password does not match the criteria",
    "invalid_credentials": "Invalid credentials"
}


ORDER_MESSAGES = {
    "order_created": "Order created successfully",
    "order_created_ru": "Заказ оформлен"
}


HTTP_STATUSES = {
    "unauthorized": 401,
    "not_found": 404,
    "bad_request": 400,
    "internal_server_error": 500
}


VALIDATION_REQUIREMENTS = {
    "username": {
        "min_length": 6,
        "allowed_chars": "латинские буквы и цифры"
    },
    "password": {
        "min_length": 8,
        "requirements": ["заглавная буква", "строчная буква", "спецсимвол"]
    }
}
