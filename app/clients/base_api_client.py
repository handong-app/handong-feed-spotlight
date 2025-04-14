import requests
from app.core.config import EnvVariables

class BaseAPIClient:
    def __init__(self, api_key: str = None):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
        key = api_key if api_key is not None else EnvVariables.FEED_API_KEY
        if key:
            self.session.headers.update({"X-API-Key": key})

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    def post(self, url, **kwargs):
        return self.session.post(url, **kwargs)