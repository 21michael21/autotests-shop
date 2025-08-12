from typing import Dict, Optional
import allure
from src.backend.clients.http_client import HTTPClient

class OrdersAdapter:

    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
        with allure.step('🔧 Инициализация OrdersAdapter'):
            allure.attach('OrdersAdapter готов к работе с API заказов', 'Статус инициализации', allure.attachment_type.TEXT)

    def create_order(self, token: str) -> 'requests.Response':
        with allure.step('📦 Создание заказа из корзины'):
            headers = {'Authorization': token}
            allure.attach(f'Заголовки: {headers}', 'Детали запроса', allure.attachment_type.TEXT)
            response = self.http_client.post('/orders/', headers=headers)
            allure.attach(f'Статус ответа: {response.status_code}', 'Результат создания заказа', allure.attachment_type.TEXT)
            return response

    def get_order_details(self, token: str, order_id: int) -> 'requests.Response':
        with allure.step(f'📋 Получение деталей заказа {order_id}'):
            headers = {'Authorization': token}
            allure.attach(f'Заголовки: {headers}', 'Детали запроса', allure.attachment_type.TEXT)
            response = self.http_client.get(f'/orders/{order_id}', headers=headers)
            allure.attach(f'Статус ответа: {response.status_code}', 'Результат получения заказа', allure.attachment_type.TEXT)
            return response
