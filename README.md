# Autotests Shop - API Testing Framework

## Описание проекта

Данный проект представляет собой автоматизированный фреймворк для тестирования API магазина, созданный согласно архитектуре ментора @dmievlev.

## Архитектура проекта

```
src/
├── backend/
│   ├── clients/
│   │   └── http_client/          # HTTP клиент согласно архитектуре ментора
│   │       ├── client.py         # Основной HTTP клиент
│   │       ├── utils.py          # Утилиты для allure
│   │       └── constants.py      # Константы
│   ├── services/
│   │   └── shop/                 # Единый shop сервис
│   │       ├── service.py        # Основной сервис
│   │       ├── adapter.py        # Адаптер для HTTP
│   │       └── models/           # Модели данных
│   └── models/                   # Старые модели (можно удалить)
├── utils/
│   ├── validations.py            # Оптимизированные валидации
│   ├── constants.py              # Константы сообщений
│   └── allure_utils.py           # Утилиты для allure
└── builders/
    └── user_builder.py           # Упрощенный UserBuilder

tests/
└── backend/                      # Все тесты обновлены для shop сервиса
    ├── auth/                     # Тесты авторизации
    ├── cart/                     # Тесты корзины
    ├── catalog/                  # Тесты каталога
    └── orders/                   # Тесты заказов
```

## Установка и настройка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd hw_04_api_tests/autotests-shop
```

### 2. Создание виртуального окружения
```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
# На macOS/Linux:
source venv/bin/activate
# На Windows:
venv\Scripts\activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

## Запуск тестов

### Основные команды
```bash
# Запуск всех тестов
pytest tests/backend/ -v

# Запуск с allure отчетом
pytest tests/backend/ --alluredir=allure-results
allure serve allure-results

# Запуск конкретных тестов
pytest tests/backend/auth/ -v
pytest tests/backend/cart/ -v
pytest tests/backend/catalog/ -v
pytest tests/backend/orders/ -v
```

### Использование Makefile
```bash
# Установка зависимостей
make install

# Запуск всех тестов
make test

# Запуск с allure отчетом
make test-allure

# Запуск конкретных тестов
make test-auth
make test-cart
make test-catalog
make test-orders


# Очистка временных файлов
make clean
```

## Особенности реализации

### 1. Единый Shop сервис
- Все операции (auth, cart, catalog, orders) объединены в один сервис
- Следует архитектуре ментора для лучшей поддерживаемости

### 2. Оптимизированные Allure отчеты
- Убраны избыточные `allure.step` и `allure.severity`
- Созданы утилиты для централизованного управления allure attach
- Отчеты содержат только полезную для дебага информацию

### 3. Константы сообщений
- Все сообщения API вынесены в `src/utils/constants.py`
- Убраны дублирования в тестах
- Улучшена читаемость и поддерживаемость

### 4. Правильная обработка ошибок
- Тесты с 500 статусом помечаются как skip с указанием бага
- Конкретные проверки вместо проверки "всё подряд"
- Четкие assert с понятными сообщениями

## Структура тестов

### Авторизация (`tests/backend/auth/`)
- Регистрация пользователя
- Вход пользователя
- Попытки входа с неверными данными (параметризованные тесты)

### Корзина (`tests/backend/cart/`)
- Добавление товара в корзину
- Получение содержимого корзины
- Удаление товара из корзины
- Попытка добавления несуществующего товара

### Каталог (`tests/backend/catalog/`)
- Получение каталога товаров
- Фильтрация товаров по цене
- Сортировка товаров по цене
- Проверка невалидных параметров

### Заказы (`tests/backend/orders/`)
- Создание заказа
- Получение деталей заказа
- Попытка получения несуществующего заказа
- Попытка создания заказа без авторизации

## Конфигурация

### Переменные окружения
```bash
# Базовый URL API
export API_BASE_URL="http://localhost:5050"
```

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## Устранение неполадок

### 1. Проблемы с импортами
```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate

# Проверьте, что зависимости установлены
pip list | grep pytest
```

### 2. Проблемы с allure
```bash
# Установите allure командную строку
# На macOS:
brew install allure

# На Ubuntu:
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update
sudo apt-get install allure
```

### 3. Очистка кэша
```bash
make clean
# или вручную:
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
```

## Вклад в проект

Все исправления выполнены согласно замечаниям ментора @dmievlev:

1. ✅ Архитектурные изменения - единый shop сервис
2. ✅ Реструктуризация HTTP клиента
3. ✅ Оптимизация allure отчетов
4. ✅ Убраны дублирования и избыточности
5. ✅ Созданы утилиты для allure
6. ✅ Исправлены все тесты
7. ✅ Добавлены недостающие тесты
8. ✅ Правильная обработка ошибок

## Контакты

Проект готов к ревью и дальнейшему использованию.
Все вопросы по архитектуре и реализации решены согласно рекомендациям ментора.
