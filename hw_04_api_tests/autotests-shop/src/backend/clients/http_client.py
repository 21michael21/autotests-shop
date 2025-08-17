from typing import Optional, Dict
import requests
import allure
from urllib.parse import urljoin
import json


class HTTPClient:

    def __init__(
        self, host: str, default_headers: Optional[Dict[str, str]] = None
    ) -> None:
        self._host = host
        self._default_headers = default_headers or {}
        with allure.step("Инициализация HTTP клиента"):
            allure.attach(
                f"Базовый URL: {host}",
                "Конфигурация клиента",
                allure.attachment_type.TEXT,
            )
            if default_headers:
                allure.attach(
                    json.dumps(default_headers, indent=2),
                    "Заголовки по умолчанию",
                    allure.attachment_type.JSON,
                )

    def get(
        self, route: str, headers: Optional[Dict] = None, params: Optional[Dict] = None
    ) -> requests.Response:
        return self._request("GET", route, headers, params=params)

    def post(
        self, route: str, headers: Optional[Dict] = None, json: Optional[Dict] = None
    ) -> requests.Response:
        return self._request("POST", route, headers, json=json)

    def _request(
        self, method: str, route: str, headers: Optional[Dict] = None, **kwargs
    ) -> requests.Response:
        url = urljoin(self._host, route)
        req_headers = {**self._default_headers, **(headers or {})}
        with allure.step(f"{method} {url}"):
            request_details = {
                "method": method,
                "url": url,
                "headers": req_headers,
                "base_url": self._host,
                "route": route,
            }
            if "params" in kwargs:
                request_details["query_params"] = kwargs["params"]
            if "json" in kwargs:
                request_details["json_body"] = kwargs["json"]
            if "data" in kwargs:
                request_details["form_data"] = kwargs["data"]
            allure.attach(
                json.dumps(request_details, indent=2, ensure_ascii=False),
                "Детали HTTP запроса",
                allure.attachment_type.JSON,
            )
            try:
                response = requests.request(method, url, headers=req_headers, **kwargs)
                response_details = {
                    "status_code": response.status_code,
                    "status_text": response.reason,
                    "headers": dict(response.headers),
                    "url": response.url,
                    "elapsed_time": str(response.elapsed),
                    "encoding": response.encoding,
                    "cookies": dict(response.cookies),
                }
                allure.attach(
                    json.dumps(response_details, indent=2, ensure_ascii=False),
                    "Детали HTTP ответа",
                    allure.attachment_type.JSON,
                )
                try:
                    response_json = response.json()
                    allure.attach(
                        json.dumps(response_json, indent=2, ensure_ascii=False),
                        "JSON ответ",
                        allure.attachment_type.JSON,
                    )
                except (ValueError, json.JSONDecodeError):
                    allure.attach(
                        response.text, "Текстовый ответ", allure.attachment_type.TEXT
                    )
                if response.status_code < 400:
                    allure.attach(
                        f"Успешный ответ: {response.status_code}",
                        "Результат запроса",
                        allure.attachment_type.TEXT,
                    )
                else:
                    allure.attach(
                        f"Ошибка: {response.status_code}",
                        "Результат запроса",
                        allure.attachment_type.TEXT,
                    )
                return response
            except requests.exceptions.RequestException as e:
                error_details = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "request_url": url,
                    "request_method": method,
                }
                allure.attach(
                    json.dumps(error_details, indent=2, ensure_ascii=False),
                    "Ошибка HTTP запроса",
                    allure.attachment_type.JSON,
                )
                raise
