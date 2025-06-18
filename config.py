class Server:
    def __init__(self, env: str):
        self.base_url = {
            "dev": "http://0.0.0.0:8002",
            "beta": "",
            "rc": "http://0.0.0.0:8002",
        }[env]