import logging
from typing import List

from app.clients.base_api_client import BaseAPIClient
from app.core.config import EnvVariables
from app.schemas.tag_dto import TagDto

logger = logging.getLogger(__name__)


class HandongFeedAppClient(BaseAPIClient):
    """
    Handong Feed App 외부 API 호출 클라이언트 서비스
    """

    def __init__(self):
        feed_api_key = EnvVariables.FEED_API_KEY
        super().__init__(api_key=feed_api_key)
        self.feed_base_api_url = EnvVariables.FEED_API_BASE_URL


    def get_all_tags(self) -> List[TagDto.ReadResDto]:
        """
        GET /api/external/tag 호출을 통해 모든 태그 정보를 가져옵니다.

        Returns:
            List[TagDto]

        Raises:
            Exception: 호출 실패 시 예외 발생
        """
        url = f"{self.feed_base_api_url}/tag"
        try:
            response = self.get(url)
            response.raise_for_status()
            tags_json = response.json()
            tag_read_res_dto_list = [TagDto.ReadResDto(**item) for item in tags_json]
            logger.info("Successfully retrieved and parsed tags from HanDongFeed App")
            return tag_read_res_dto_list
        except Exception as e:
            logger.error(f"Failed to retrieve tags: {e}")
            raise Exception(f"Failed to get all tags: {e}") from e
