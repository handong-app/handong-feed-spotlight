import logging
import requests

from app.core.config import EnvVariables
from app.schemas.tag_dto import TagDto

logger = logging.getLogger(__name__)


class HandongFeedAppClient:
    """
    Handong Feed App 외부 API 호출 클라이언트 서비스
    """

    @staticmethod
    def get_all_tags():
        """
        GET /api/external/tag 호출을 통해 모든 태그 정보를 가져옵니다.

        Returns:
            List[TagDto]

        Raises:
            Exception: 호출 실패 시 예외 발생
        """
        url = f"{EnvVariables.BASE_URL}/api/external/tag"
        try:
            response = requests.get(url)
            response.raise_for_status()
            tags_json = response.json()
            tag_read_res_dto_list = [TagDto.ReadResDto(**item) for item in tags_json]
            logger.info("Successfully retrieved and parsed tags from HanDongFeed App")
            return tag_read_res_dto_list
        except Exception as e:
            logger.error(f"Failed to retrieve tags: {e}")
            raise Exception(f"Failed to get all tags: {e}") from e
