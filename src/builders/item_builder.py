import random
from typing import Dict
import allure
import json
from src.backend.services.catalog.adapter import CatalogAdapter

class ItemBuilder:

    def __init__(self, catalog_adapter: CatalogAdapter, token: str) -> None:
        self.catalog_adapter = catalog_adapter
        self.token = token
        with allure.step('🔧 Инициализация ItemBuilder'):
            initialization_details = {'catalog_adapter': str(catalog_adapter), 'token_type': 'JWT', 'token_length': len(token)}
            allure.attach(json.dumps(initialization_details, indent=2), 'Конфигурация ItemBuilder', allure.attachment_type.JSON)
            allure.attach('✅ ItemBuilder готов к работе с каталогом', 'Статус инициализации', allure.attachment_type.TEXT)

    def build(self) -> Dict[str, int]:
        with allure.step('📦 Получение случайного товара из каталога'):
            with allure.step('📚 Запрос каталога товаров'):
                try:
                    resp = self.catalog_adapter.get_catalog(self.token)
                    allure.attach(str(resp.status_code), 'HTTP статус ответа каталога', allure.attachment_type.TEXT)
                    if resp.status_code != 200:
                        error_msg = f'Ошибка получения каталога: {resp.status_code}'
                        allure.attach(error_msg, '❌ Ошибка', allure.attachment_type.TEXT)
                        raise ValueError(error_msg)
                except Exception as e:
                    error_details = {'error_type': type(e).__name__, 'error_message': str(e), 'operation': 'get_catalog'}
                    allure.attach(json.dumps(error_details, indent=2), '❌ Ошибка запроса каталога', allure.attachment_type.JSON)
                    raise
            with allure.step('🔍 Парсинг ответа каталога'):
                try:
                    items = resp.json()
                    allure.attach(json.dumps(items, indent=2), 'Полученный каталог товаров', allure.attachment_type.JSON)
                    allure.attach(str(len(items)), 'Количество товаров в каталоге', allure.attachment_type.TEXT)
                except (ValueError, json.JSONDecodeError) as e:
                    error_details = {'error_type': 'JSONDecodeError', 'error_message': str(e), 'response_text': resp.text[:500]}
                    allure.attach(json.dumps(error_details, indent=2), '❌ Ошибка парсинга JSON', allure.attachment_type.JSON)
                    raise ValueError(f'Не удалось распарсить ответ каталога: {e}')
            with allure.step('🔍 Проверка наличия товаров'):
                if not items:
                    error_msg = 'Каталог пуст - нет товаров для тестирования'
                    allure.attach(error_msg, '❌ Ошибка', allure.attachment_type.TEXT)
                    raise ValueError(error_msg)
                allure.attach(f'✅ В каталоге найдено {len(items)} товаров', 'Результат проверки', allure.attachment_type.TEXT)
            with allure.step('🎲 Выбор случайного товара'):
                selected_item = random.choice(items)
                allure.attach(json.dumps(selected_item, indent=2), 'Выбранный товар', allure.attachment_type.JSON)
                allure.attach(f"Выбран товар: {selected_item.get('name', 'Unknown')} (ID: {selected_item.get('id', 'Unknown')})", 'Информация о выбранном товаре', allure.attachment_type.TEXT)
            with allure.step('🔢 Генерация количества товара'):
                quantity = random.randint(1, 5)
                allure.attach(str(quantity), 'Сгенерированное количество', allure.attachment_type.TEXT)
                allure.attach(f'Количество товара: {quantity} (диапазон: 1-5)', 'Детали генерации количества', allure.attachment_type.TEXT)
            with allure.step('📋 Формирование итоговых данных'):
                item_data = {'item_id': selected_item['id'], 'quantity': quantity}
                allure.attach(json.dumps(item_data, indent=2), 'Итоговые данные товара', allure.attachment_type.JSON)
                validation_result = {'item_id': {'value': item_data['item_id'], 'type': type(item_data['item_id']).__name__, 'is_valid': isinstance(item_data['item_id'], int)}, 'quantity': {'value': item_data['quantity'], 'type': type(item_data['quantity']).__name__, 'is_valid': isinstance(item_data['quantity'], int) and 1 <= item_data['quantity'] <= 5}}
                allure.attach(json.dumps(validation_result, indent=2), 'Валидация данных товара', allure.attachment_type.JSON)
                allure.attach('✅ Тестовые данные товара успешно сформированы', 'Результат формирования', allure.attachment_type.TEXT)
            return item_data
