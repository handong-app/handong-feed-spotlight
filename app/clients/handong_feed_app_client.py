import logging
from typing import List

from app.clients.base_api_client import BaseAPIClient
from app.core.config import EnvVariables
from app.schemas.external.feed_dto import FeedDto
from app.schemas.external.subject_tag_dto import SubjectTagDto
from app.schemas.external.tag_dto import TagDto

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

    def get_feeds(self, feed_req: FeedDto.ReadReqDto) -> List[FeedDto.ReadRespDto]:
        """
        GET /api/external/feed API를 호출하여 피드 데이터를 가져오고,
        JSON 배열을 Detail 모델 리스트로 변환하여 반환합니다.

        Args:
            feed_req (FeedReqDto): 시작 시간, 종료 시간, isFilterNew, limit 등의 쿼리 파라미터 정보.

        Returns:
            List[Detail]: 외부 API에서 반환된 피드 상세 정보를 Detail DTO 리스트로 매핑한 결과.

        Raises:
            Exception: API 호출 실패 또는 JSON 파싱 에러 발생 시 예외 전달.
        """
        url = f"{self.feed_base_api_url}/feed"
        # FeedReqDto를 사전(dictionary)로 변환하여 query parameters로 전달 (unset된 값은 제외)
        params = feed_req.model_dump(exclude_unset=True)
        # if "isFilterNew" in params:
        #     params["isFilterNew"] = "1" if params["isFilterNew"] else "0"
        try:
            response = self.get(url, params=params)
            response.raise_for_status()
            feed_json = response.json()
            feed_read_resp_dtos = [FeedDto.ReadRespDto(**item) for item in feed_json]
            logger.info("Successfully retrieved and parsed feed details from HanDongFeed App")
            return feed_read_resp_dtos
        except Exception as e:
            logger.error(f"Failed to retrieve feed: {e}")
            raise Exception(f"Failed to get feed: {e}") from e


    def assign_tags_batch(self, subject_id: str, assign_reqs: List[SubjectTagDto.AssignReqDto]) -> List[SubjectTagDto.AssignRespDto]:
        """
        POST /api/external/subject-tag/:subjectId/tag-assign-batch를 호출하여 여러 태그 배정 요청을 보냅니다.

        요청 예시:
        [
          {
            "tagCode": "club",
            "forDate": "2025-01-01",    // "2025-01-01" 혹은 null,
            "confidentValue": 0.33
          },
          {
            "tagCode": "event",
            "forDate": "2025-01-01",    // "2025-01-01" 혹은 null,
            "confidentValue": 0.33
          }
        ]

        주의:
          저장 시 응답 배열 내 개별 객체의 id 값이 -1이면, 중복으로 인한 저장 실패입니다.

        Args:
            subject_id (str): 태그 배정 대상의 subject ID
            assign_reqs (List[CreateReqDto]): 태그 배정 요청 데이터 목록

        Returns:
            SubjectTagAssignBatchRespDto: 각 태그 배정 결과를 담은 DTO (assignments: List[CreateResDto])
        Raises:
            Exception: API 호출 실패 또는 저장 실패 시 예외 발생
        """
        url = f"{self.feed_base_api_url}/subject-tag/{subject_id}/tag-assign-batch"
        payload = [assignment.model_dump() for assignment in assign_reqs]
        try:
            response = self.post(url, json=payload)
            response.raise_for_status()
            result_json = response.json()
            # 중복 저장 실패 검사
            for item in result_json:
                if item.get("id", 0) == -1:
                    raise Exception(f"중복으로 인해 저장 실패한 태그 배정: {item}")
            logger.info(f"Successfully assigned tags batch for subject_id {subject_id}")
            return [SubjectTagDto.AssignRespDto(**item) for item in result_json]
        except Exception as e:
            logger.error(f"Failed to assign tags batch for subject_id {subject_id}: {e}")
            raise Exception(f"Failed to assign tags batch for subject_id {subject_id}: {e}") from e


    def assign_tag(self, subject_id: str, assign_req: SubjectTagDto.AssignReqDto) -> SubjectTagDto.AssignRespDto:
        """
        POST /api/external/subject-tag/:subjectId/tag-assign를 호출하여 단일 태그 배정 요청을 보냅니다.

        요청 예시:
        {
          "tagCode": "club",
          "forDate": "2025-01-01",    // "2025-01-01" 혹은 null,
          "confidentValue": 0.33
        }

        주의:
          저장 시 반환 결과의 id 값이 -1이면 중복으로 인한 저장 실패로 간주합니다.

        Args:
            subject_id (str): 단일 태그 배정 대상의 subject ID
            assign_req (CreateReqDto): 단일 태그 배정 요청 데이터

        Returns:
            CreateResDto: 단일 태그 배정 결과 DTO

        Raises:
            Exception: API 호출 실패 또는 저장 실패 시 예외 발생
        """
        url = f"{self.feed_base_api_url}/subject-tag/{subject_id}/tag-assign"
        payload = assign_req.model_dump()
        try:
            response = self.post(url, json=payload)
            response.raise_for_status()
            result_json = response.json()
            if result_json.get("id", 0) == -1:
                raise Exception(f"중복으로 인해 저장 실패한 단일 태그 배정: {result_json}")
            logger.info(f"Successfully assigned tag for subject_id {subject_id}")
            return SubjectTagDto.AssignRespDto(**result_json)
        except Exception as e:
            logger.error(f"Failed to assign tag for subject_id {subject_id}: {e}")
            raise Exception(f"Failed to assign tag for subject_id {subject_id}: {e}") from e


    def get_latest_for_date(self) -> SubjectTagDto.GetLatestForDateResDto:
        """
        GET /api/external/subject-tag/latest-for-date 를 호출하여 최신 for_date 를 받습니다.

        Returns:
            ReadLatestForDateResDto: 최신 for_date 응답 DTO

        Raises:
            Exception: API 호출 실패 시 예외 발생
        """
        url = f"{self.feed_base_api_url}/subject-tag/latest-for-date"
        try:
            response = self.get(url)
            response.raise_for_status()

            # 204 No Content 응답 처리
            if response.status_code == 204:
                logger.info("No latest for_date found (204 No Content)")
                return SubjectTagDto.GetLatestForDateResDto(latestForDate=None)

            result_json = response.json()
            logger.info(f"Successfully get latest for_date: {result_json.get('latestForDate')}")
            return SubjectTagDto.GetLatestForDateResDto(**result_json)
        except Exception as e:
            logger.error(f"Failed to get latest for_date: {e}")
            raise Exception(f"Failed to get latest for_date: {e}") from e