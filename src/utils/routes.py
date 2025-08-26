from enum import Enum


class Routes(Enum):
    AUTH_REGISTER = "/auth/register"
    AUTH_LOGIN = "/auth/login"
    AUTH_LOGOUT = "/auth/logout"
    
    USERS = "/users"
    USER_BY_ID = "/users/{user_id}"
    
    PRODUCTS = "/catalog"
    PRODUCT_BY_ID = "/catalog/{product_id}"
    
    CARTS = "/cart"
    CART_ADD = "/cart/add"
    CART_REMOVE = "/cart/remove"
    
    ORDERS = "/orders"
    ORDER_BY_ID = "/orders/{order_id}"
    
    HEALTH = "/health"
