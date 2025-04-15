import logging

from app.clients.handong_feed_app_client import HandongFeedAppClient
from app.schemas.external.feed_dto import FeedDto
from app.schemas.external.subject_tag_dto import SubjectTagDto
from app.schemas.external.tag_dto import TagDto
from app.schemas.tag_labeling_dto import MessageTagLabelingRespDto
from app.services.llm_service import LLMService
from app.util.date_utils import convert_start_date_to_unix, convert_end_date_to_unix, convert_unix_to_date_str
from app.util.pii_cleaner import mask_all_ppi
from app.util.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)

class TagLabelingService:
    def __init__(self):
        self.cleaner = TextCleaner()
        self.llm_service = LLMService()
        self.handong_feed_app_client = HandongFeedAppClient()

    def assign_tags_to_messages_iterative(self, start_date, end_date, is_filter_new, limit) -> MessageTagLabelingRespDto:
        """
        주어진 메시지 리스트와 태그 목록을 기반으로 각 메시지에 적합한 태그 코드를 할당합니다.

        이 메서드는 다음의 작업을 수행합니다:
          1. 메시지 리스트가 비어있는 경우 경고 로그를 남기고 빈 결과를 반환합니다.
          2. 태그 목록이 비어있는 경우 경고 로그를 남기고 빈 결과를 반환합니다.
          3. 각 메시지에 대해 다음을 수행합니다:
             - 메시지에서 subject_id가 존재하지 않으면 건너뜁니다.
             - 원본 메시지(raw_text)를 가져와서 개인정보 및 링크 등 민감 정보를 `mask_all_ppi`를 사용하여 마스킹합니다.
             - TextCleaner를 적용하여 텍스트를 정규화합니다.
             - 정제된 메시지(cleaned_message)를 이용해 LLMService의 assign_tag_to_message 메서드를 호출하여 태그 코드를 할당합니다.
             - LLM 응답이 유효하면, 해당 메시지에 대한 할당 결과(MessageTagAssignment)를 수집합니다.
          4. 모든 메시지에 대한 할당 결과를 MessageTagLabelingRespDto에 담아 반환합니다.

            messages (list): 각 메시지는 딕셔너리 형태로, 최소한 'subject_id'와 'message' 키를 포함해야 합니다.
            tags (list): 할당 가능한 태그 목록. 각 태그는 딕셔너리 형태(예: {"code": "...", "label": "...", "llm_desc": "..."})로 제공됩니다.

        Returns:
            MessageTagLabelingRespDto: 각 메시지의 subject_id와 할당된 태그 코드 배열을 포함하는 DTO.
    """
        # 날짜 문자열을 Unix timestamp로 변환
        start_ts = convert_start_date_to_unix(start_date)
        end_ts = convert_end_date_to_unix(end_date)

        tag_codes = TagDto.extract_tag_codes(self.handong_feed_app_client.get_all_tags())

        feeds = self.handong_feed_app_client.get_feeds(
            FeedDto.ReadReqDto(
                start = start_ts,
                end = end_ts,
                isFilterNew = is_filter_new,
                limit = limit
            )
        )

        # 해당 조건에 부합하는 피드가 없다면, status 204 반환
        if not feeds:
            logger.warning("Empty feed list provided")
            from fastapi import HTTPException
            raise HTTPException(status_code=204, detail="해당 조건에 부합하는 피드가 없습니다.")

        if not tag_codes:
            logger.warning("Empty tag code list provided")
            return MessageTagLabelingRespDto(assign_resp_dtos_list=[])

        assign_resp_dtos_list = []

        for feed in feeds:
            subject_id = feed.subjectId
            for_date = convert_unix_to_date_str(feed.sentAt)

            if not subject_id:
                logger.warning("Message without subject_id found, skipping")
                continue

            raw_text = feed.message

            masked_text = mask_all_ppi(raw_text)

            cleaned_message = self.cleaner.clean(masked_text)

            assignment = self.llm_service.assign_tag_to_message(str(subject_id), cleaned_message, tag_codes)
            if assignment:
                assign_req_dtos = []
                for tag_code in assignment.tag_codes:
                    assign_req_dto = SubjectTagDto.AssignReqDto(
                        tagCode=tag_code,
                        forDate=for_date,
                    )
                    assign_req_dtos.append(assign_req_dto)

                assign_resp_dtos = self.handong_feed_app_client.assign_tags_batch(str(subject_id), assign_req_dtos)
                assign_resp_dtos_list.append(assign_resp_dtos)
            else:
                logger.debug(f"No valid assignment returned for subject_id={subject_id}")

        return MessageTagLabelingRespDto(assign_resp_dtos_list= assign_resp_dtos_list)
