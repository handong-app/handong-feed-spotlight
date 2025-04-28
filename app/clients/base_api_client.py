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

    def _send_request(self, method, url, **kwargs):
        """
        HTTP 요청을 보내고 공통적으로 예외를 처리하는 private 메서드

        Args:
            method (str): HTTP 메서드 ('GET', 'POST', 'PATCH' 등)
            url (str): 요청할 URL
            kwargs: 추가 요청 옵션

        Returns:
            requests.Response: 요청 결과 응답
        """
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            logging.error(f"{method} 요청 실패 (HTTP 오류) - URL: {url}, 상태 코드: {e.response.status_code}, 오류: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"{method} 요청 실패 (네트워크 오류) - URL: {url}, 오류: {e}")
            raise

    def get(self, url, **kwargs):
        return self._send_request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self._send_request('POST', url, **kwargs)

    def patch(self, url, **kwargs):
        return self._send_request('PATCH', url, **kwargs)