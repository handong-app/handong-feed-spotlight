import logging
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
        else:
            logging.warning("API 키가 제공되지 않았습니다. 인증이 필요한 API 호출은 실패할 수 있습니다.")
        # 타임아웃 설정 (connect=5초, read=30초)
        self.session.timeout = (5, 30)

    def get(self, url, **kwargs):
        try:
            response = self.session.get(url, **kwargs)
            response.raise_for_status()  # 4xx, 5xx 응답에 대해 예외 발생
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"GET 요청 실패: {url}, 오류: {str(e)}")
            raise

    def post(self, url, **kwargs):
        try:
            response = self.session.post(url, **kwargs)
            response.raise_for_status()  # 4xx, 5xx 응답에 대해 예외 발생
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"POST 요청 실패: {url}, 오류: {str(e)}")
            raise