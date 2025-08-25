import json
from datetime import datetime

import allure
import curlify
from allure_commons.types import AttachmentType
from requests import Response

from src.backend.clients.http_client.constants import BINARY_TYPES


def attach_request_data(response: Response, request_time: float, response_time: float) -> None:
    method = response.request.method
    request_url = response.request.url

    allure.attach(body=curlify.to_curl(request=response.request).encode("utf-8").decode("utf-8"), name="curl",
                  attachment_type=AttachmentType.TEXT)

    request_body = response.request.body.decode("utf-8") if isinstance(response.request.body,
                                                                       bytes) else response.request.body
    attach_request = {
        "URL": request_url,
        "HEADERS": str(response.request.headers),
        "BODY": request_body
    }

    allure.attach(body=json.dumps(attach_request, indent=4, separators=(",", ": "), ensure_ascii=False),
                  name="Request",
                  attachment_type=AttachmentType.JSON)

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
        "REQUEST-TIME": datetime.fromtimestamp(request_time).strftime("%Y-%m-%d %H:%M:%S.%f"),
        "RESPONSE-TIME": datetime.fromtimestamp(response_time).strftime("%Y-%m-%d %H:%M:%S.%f"),
        "PROCESSING-DURATION": f"{(response_time - request_time):.2f} milliseconds"
    }

    allure.attach(
        body=json.dumps(attach_response, indent=4, separators=(",", ": "), ensure_ascii=False),
        name="Response",
        attachment_type=allure.attachment_type.JSON
    )
