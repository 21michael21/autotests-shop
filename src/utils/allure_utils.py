import allure
import json
from typing import Any, Dict, Optional


def attach_response_data(response_data: Any, title: str = "Ответ API") -> None:
    """
    Прикрепляет данные ответа к allure отчету
    
    Args:
        response_data: Данные для прикрепления
        title: Заголовок для attach
    """
    if isinstance(response_data, (dict, list)):
        allure.attach(
            json.dumps(response_data, indent=2, ensure_ascii=False),
            title,
            allure.attachment_type.JSON,
        )
    else:
        allure.attach(
            str(response_data),
            title,
            allure.attachment_type.TEXT,
        )


def attach_error_details(error_type: str, error_message: str, operation: str, **kwargs) -> None:
    """
    Прикрепляет детали ошибки к allure отчету
    
    Args:
        error_type: Тип ошибки
        error_message: Сообщение об ошибке
        operation: Операция, при которой произошла ошибка
        **kwargs: Дополнительные данные для прикрепления
    """
    error_details = {
        "error_type": error_type,
        "error_message": error_message,
        "operation": operation,
        **kwargs
    }
    
    allure.attach(
        json.dumps(error_details, indent=2, ensure_ascii=False),
        "Детали ошибки",
        allure.attachment_type.JSON,
    )


def attach_test_data(data: Any, title: str = "Тестовые данные") -> None:
    """
    Прикрепляет тестовые данные к allure отчету
    
    Args:
        data: Данные для прикрепления
        title: Заголовок для attach
    """
    if isinstance(data, (dict, list)):
        allure.attach(
            json.dumps(data, indent=2, ensure_ascii=False),
            title,
            allure.attachment_type.JSON,
        )
    else:
        allure.attach(
            str(data),
            title,
            allure.attachment_type.TEXT,
        )


def attach_request_info(method: str, url: str, headers: Optional[Dict] = None, 
                       params: Optional[Dict] = None, data: Optional[Any] = None) -> None:
    """
    Прикрепляет информацию о запросе к allure отчету
    
    Args:
        method: HTTP метод
        url: URL запроса
        headers: Заголовки запроса
        params: Параметры запроса
        data: Тело запроса
    """
    request_info = {
        "method": method,
        "url": url,
        "headers": headers,
        "params": params,
        "data": data
    }
    
    allure.attach(
        json.dumps(request_info, indent=2, ensure_ascii=False),
        "Информация о запросе",
        allure.attachment_type.JSON,
    )
