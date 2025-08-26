import json
from datetime import datetime

import allure
import curlify
from allure_commons.types import AttachmentType
from requests import Response

from src.backend.clients.http_client.constants import BINARY_TYPES
from src.utils.allure_utils import attach_response_data, attach_request_info


def attach_request_data(
    response: Response, request_time: float, response_time: float
) -> None:
    method = response.request.method
    request_url = response.request.url

    # Прикрепляем cURL команду
    curl_command = curlify.to_curl(request=response.request).encode("utf-8").decode("utf-8")
    attach_request_info(method, request_url, str(response.request.headers), None, curl_command)

    request_body = (
        response.request.body.decode("utf-8")
        if isinstance(response.request.body, bytes)
        else response.request.body
    )
    attach_request = {
        "URL": request_url,
        "HEADERS": str(response.request.headers),
        "BODY": request_body,
    }

    attach_response_data(attach_request, "Request")

    content_type = response.headers.get("Content-Type", "")
    if not any(binary_type in content_type for binary_type in BINARY_TYPES):
        try:
            response_body_json = response.json()
            response_body = json.dumps(response_body_json, ensure_ascii=False)
        except json.JSONDecodeError:
            response_body = response.text
    else:
        response_body = "<BINARY DATA>"

    attach_response = {
        "URL": request_url,
        "HEADERS": str(response.headers),
        "BODY": response_body,
        "STATUS-CODE": f"{response.status_code}",
        "REQUEST-TIME": datetime.fromtimestamp(request_time).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        ),
        "RESPONSE-TIME": datetime.fromtimestamp(response_time).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        ),
        "PROCESSING-DURATION": f"{(response_time - request_time):.2f} milliseconds",
    }

    attach_response_data(attach_response, "Response")
