import pytest
import allure
import json
from src.backend.clients.http_client import HTTPClient
from src.backend.clients.db_client import DbClient
from src.backend.services.auth.adapter import AuthAdapter
from src.backend.services.cart.adapter import CartAdapter
from src.backend.services.catalog.adapter import CatalogAdapter
from src.backend.services.orders.adapter import OrdersAdapter
from config import BASE_URL, DB_CONFIG

# Глобальные метки для всех тестов
pytestmark = [
    allure.epic("Автотесты для Backend API интернет-магазина"),
    allure.feature("Полное покрытие функционала"),
    allure.story("Интеграционное тестирование API")
]

@pytest.fixture(scope="session")
@allure.step("Инициализация HTTP клиента")
def http_client() -> HTTPClient:
    """
    Фикстура для создания HTTP клиента на всю сессию тестов
    
    Returns:
        HTTPClient: Настроенный HTTP клиент для работы с API
    """
    with allure.step(f"Создание HTTP клиента для {BASE_URL}"):
        client = HTTPClient(BASE_URL)
        
        client_info = {
            "base_url": BASE_URL,
            "client_type": "HTTPClient",
            "scope": "session"
        }
        
        allure.attach(
            json.dumps(client_info, indent=2),
            "Информация о HTTP клиенте",
            allure.attachment_type.JSON
        )
        
        allure.attach(
            "HTTP клиент успешно инициализирован",
            "Статус инициализации",
            allure.attachment_type.TEXT
        )
        
        return client

@pytest.fixture(scope="session")
@allure.step("Инициализация DB клиента")
def db_client() -> DbClient:
    """
    Фикстура для создания DB клиента на всю сессию тестов
    
    Returns:
        DbClient: Настроенный клиент для работы с базой данных
    """
    with allure.step(f"Создание DB клиента для {DB_CONFIG['host']}:{DB_CONFIG['port']}"):
        client = DbClient(DB_CONFIG)
        
        db_info = {
            "host": DB_CONFIG["host"],
            "port": DB_CONFIG["port"],
            "database": DB_CONFIG["dbname"],
            "user": DB_CONFIG["user"],
            "client_type": "DbClient",
            "scope": "session"
        }
        
        allure.attach(
            json.dumps(db_info, indent=2),
            "Информация о DB клиенте",
            allure.attachment_type.JSON
        )
        
        allure.attach(
            "DB клиент успешно инициализирован",
            "Статус инициализации",
            allure.attachment_type.TEXT
        )
        
        return client

@pytest.fixture
@allure.step("Создание тестового пользователя")
def user(http_client: HTTPClient, db_client: DbClient) -> dict:
    from src.builders.user_builder import UserBuilder
    auth = AuthAdapter(http_client)
    user_data = UserBuilder().build()
    try:
        db_client.delete_user(user_data["username"])
    except Exception:
        pass
    register_resp = auth.register(user_data)
    login_resp = auth.login(user_data)
    token_data = login_resp.json()
    if "token" not in token_data:
        raise ValueError("JWT токен не получен")
    return {
        "username": user_data["username"],
        "password": user_data["password"],
        "token": f"Bearer {token_data['token']}",
    }

@pytest.fixture
@allure.step("Создание адаптера аутентификации")
def auth_adapter(http_client: HTTPClient) -> AuthAdapter:
    """
    Фикстура для создания адаптера аутентификации
    
    Args:
        http_client: HTTP клиент для API запросов
        
    Returns:
        AuthAdapter: Адаптер для работы с API аутентификации
    """
    with allure.step("Создание AuthAdapter"):
        adapter = AuthAdapter(http_client)
        
        adapter_info = {
            "adapter_type": "AuthAdapter",
            "http_client": str(http_client),
            "endpoints": ["/auth/register", "/auth/login"]
        }
        
        allure.attach(
            json.dumps(adapter_info, indent=2),
            "Информация об AuthAdapter",
            allure.attachment_type.JSON
        )
        
        allure.attach(
            "AuthAdapter успешно создан",
            "Статус создания",
            allure.attachment_type.TEXT
        )
        
        return adapter

@pytest.fixture
@allure.step("Создание адаптера корзины")
def cart_adapter(http_client: HTTPClient) -> CartAdapter:
    """
    Фикстура для создания адаптера корзины
    
    Args:
        http_client: HTTP клиент для API запросов
        
    Returns:
        CartAdapter: Адаптер для работы с API корзины
    """
    with allure.step("Создание CartAdapter"):
        adapter = CartAdapter(http_client)
        
        adapter_info = {
            "adapter_type": "CartAdapter",
            "http_client": str(http_client),
            "endpoints": ["/cart/", "/cart/add", "/cart/remove"]
        }
        
        allure.attach(
            json.dumps(adapter_info, indent=2),
            "Информация о CartAdapter",
            allure.attachment_type.JSON
        )
        
        allure.attach(
            "CartAdapter успешно создан",
            "Статус создания",
            allure.attachment_type.TEXT
        )
        
        return adapter

@pytest.fixture
@allure.step("Создание адаптера каталога")
def catalog_adapter(http_client: HTTPClient) -> CatalogAdapter:
    """
    Фикстура для создания адаптера каталога
    
    Args:
        http_client: HTTP клиент для API запросов
        
    Returns:
        CatalogAdapter: Адаптер для работы с API каталога
    """
    with allure.step("Создание CatalogAdapter"):
        adapter = CatalogAdapter(http_client)
        
        adapter_info = {
            "adapter_type": "CatalogAdapter",
            "http_client": str(http_client),
            "endpoints": ["/catalog/"]
        }
        
        allure.attach(
            json.dumps(adapter_info, indent=2),
            "Информация о CatalogAdapter",
            allure.attachment_type.JSON
        )
        
        allure.attach(
            "CatalogAdapter успешно создан",
            "Статус создания",
            allure.attachment_type.TEXT
        )
        
        return adapter

@pytest.fixture
@allure.step("Получение случайного товара")
def random_item(catalog_adapter: CatalogAdapter, user: dict) -> dict:
    """
    Фикстура для получения случайного товара из каталога
    
    Args:
        catalog_adapter: Адаптер для работы с каталогом
        user: Данные авторизованного пользователя
        
    Returns:
        dict: Данные случайного товара (item_id, quantity)
    """
    with allure.step("Получение случайного товара из каталога"):
        from src.builders.item_builder import ItemBuilder
        
        try:
            item_builder = ItemBuilder(catalog_adapter, user["token"])
            item_data = item_builder.build()
            
            allure.attach(
                json.dumps(item_data, indent=2),
                "Полученный случайный товар",
                allure.attachment_type.JSON
            )
            
            allure.attach(
                "Случайный товар успешно получен",
                "Результат получения",
                allure.attachment_type.TEXT
            )
            
            return item_data
            
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "operation": "get_random_item"
            }
            
            allure.attach(
                json.dumps(error_details, indent=2),
                "Ошибка получения товара",
                allure.attachment_type.JSON
            )
            raise

@pytest.fixture
def add_random_item(cart_adapter: CartAdapter, random_item: dict, user: dict, db_client: DbClient) -> dict:
    """
    Фикстура для добавления товара в корзину
    
    Добавляет товар в корзину и очищает данные после теста
    
    Args:
        cart_adapter: Адаптер для работы с корзиной
        random_item: Данные товара для добавления
        user: Данные авторизованного пользователя
        db_client: DB клиент для очистки данных
        
    Returns:
        dict: Данные добавленного товара
        
    Yields:
        dict: Данные добавленного товара для использования в тестах
    """
    with allure.step("Добавление товара в корзину"):
        try:
            # Добавляем товар в корзину
            add_resp = cart_adapter.add_to_cart(user["token"], random_item)
            
            allure.attach(
                json.dumps(add_resp.json(), indent=2),
                "Ответ на добавление товара",
                allure.attachment_type.JSON
            )
            
            if add_resp.status_code == 200:
                allure.attach(
                    "Товар успешно добавлен в корзину",
                    "Результат добавления",
                    allure.attachment_type.TEXT
                )
            else:
                allure.attach(
                    f"Добавление завершилось со статусом: {add_resp.status_code}",
                    "Результат добавления",
                    allure.attachment_type.TEXT
                )
            
            # Передаём данные товара тесту
            yield random_item
            
        except Exception as e:
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "operation": "add_to_cart",
                "item_data": random_item
            }
            
            allure.attach(
                json.dumps(error_details, indent=2),
                "Ошибка добавления товара",
                allure.attachment_type.JSON
            )
            raise
        
        finally:
            with allure.step("Очистка корзины после теста"):
                try:
                    db_client.delete_cart(user["username"])
                except Exception:
                    pass

@pytest.fixture
@allure.step("Создание адаптера заказов")
def orders_adapter(http_client: HTTPClient) -> OrdersAdapter:
    """
    Фикстура для создания адаптера заказов
    
    Args:
        http_client: HTTP клиент для API запросов
        
    Returns:
        OrdersAdapter: Адаптер для работы с API заказов
    """
    with allure.step("Создание OrdersAdapter"):
        from src.backend.services.orders.adapter import OrdersAdapter
        adapter = OrdersAdapter(http_client)
        
        adapter_info = {
            "adapter_type": "OrdersAdapter",
            "http_client": str(http_client),
            "endpoints": ["/orders/", "/orders/{order_id}"]
        }
        
        allure.attach(
            json.dumps(adapter_info, indent=2),
            "Информация об OrdersAdapter",
            allure.attachment_type.JSON
        )
        
        allure.attach(
            "OrdersAdapter успешно создан",
            "Статус создания",
            allure.attachment_type.TEXT
        )
        
        return adapter