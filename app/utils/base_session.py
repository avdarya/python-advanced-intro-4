import logging

import curlify
from requests import Session, Response


class BaseSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.base_url = kwargs.get("base_url", None)

    def request(self, method: str, path: str, **kwargs) -> Response:
        url = self.base_url + path

        response = super().request(method, url, **kwargs)

        curl = curlify.to_curl(response.request)
        logging.info(curl)

        return response

