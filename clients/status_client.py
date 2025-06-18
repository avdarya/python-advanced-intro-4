from requests import Response

from config import Server
from utils.base_session import BaseSession

class StatusApiClient:
    def __init__(self, env: str) -> None:
        self.session = BaseSession(base_url=Server(env).base_url)

    def get_status(self) -> Response:
        return self.session.get(f"/status")