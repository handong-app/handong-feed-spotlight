import logging
from typing import List
from datetime import date
from sqlalchemy.orm import Session

from app.clients.handong_feed_app_client import HandongFeedAppClient
from app.schemas.external.feed_dto import FeedDto
from app.schemas.external.subject_tag_dto import SubjectTagDto
from app.schemas.external.tag_dto import TagDto
from app.schemas.tag_assign_fail_log_dto import TagAssignFailLogDto
from app.schemas.tag_labeling_dto import MessageTagLabelingRespDto, AssignTagsToMessageServDto
from app.services.llm_service import LLMService
from app.services.tag_fail_log_service import TagFailLogService
from app.util.date_utils import convert_start_date_to_unix, convert_end_date_to_unix, convert_unix_to_date_str
from app.util.pii_cleaner import mask_all_ppi
from app.util.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)

class TagLabelingService:
    def __init__(self, db: Session):
        self.db = db
        self.cleaner = TextCleaner()
        self.llm_service = LLMService()
        self.handong_feed_app_client = HandongFeedAppClient()
        self.tag_fail_log_service = TagFailLogService(db)

    def process_feeds_with_date(self, start_date, end_date, is_filter_new, limit) -> MessageTagLabelingRespDto:
        """
        start_date 와 end_date 사이에 생성됝 피드를 assign 시도합니다.

        Returns:
            MessageTagLabelingRespDto: 각 메시지의 subject_id와 할당된 태그 코드 배열을 포함하는 DTO.
        """

        # 날짜 문자열을 Unix timestamp로 변환
        start_ts = convert_start_date_to_unix(start_date)
        end_ts = convert_end_date_to_unix(end_date)

        assign_tags_to_messages_serv_dto_list = [
            dto.to_assign_tags_to_message_serv_dto() for dto in self.handong_feed_app_client.get_feeds(
                FeedDto.ReadReqDto(
                    start=start_ts,
                    end=end_ts,
                    isFilterNew=is_filter_new,
                    limit=limit
                )
            )
        ]

        return self.assign_tags_to_messages_iterative(assign_tags_to_messages_serv_dto_list)


    def process_failed_feeds(self) -> MessageTagLabelingRespDto:
        """
        실패한 피드를 tag_assign_fail_log 테이블에서 가져와서 다시 assign 을 시도합니다.

        Returns:
            MessageTagLabelingRespDto: 각 메시지의 subject_id와 할당된 태그 코드 배열을 포함하는 DTO.
        """

        assign_tags_to_messages_serv_dto_list = self.tag_fail_log_service.get_unprocessed_fail_feeds().to_assign_tags_to_message_serv_dto_list()

        return self.assign_tags_to_messages_iterative(assign_tags_to_messages_serv_dto_list)


    def assign_tags_to_messages_iterative(self, feeds: List[AssignTagsToMessageServDto]) -> MessageTagLabelingRespDto:
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

        tag_codes = TagDto.extract_tag_codes(self.handong_feed_app_client.get_all_tags())

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
            subject_id = feed.subject_id
            for_date = feed.for_date

            if not subject_id:
                logger.warning("Message without subject_id found, skipping")
                continue

            raw_text = feed.message

            masked_text = mask_all_ppi(raw_text)

            cleaned_message = self.cleaner.clean(masked_text)

            try:
                # 실패한 피드를 process 하는 것 이라면, 해당 row 의 is_processed 를 True 로 변경
                if feed.fail_id:
                    self.tag_fail_log_service.mark_as_processed(feed.fail_id)

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
            except Exception as e:
                logger.error(f"[FAIL] Tag assignment failed for subject_id={subject_id}: {e}")

                # 중복 저장 실패인 경우 로그를 남기지 않음
                if "중복으로 인해 저장 실패한" not in str(e):
                    self.tag_fail_log_service.save_fail_log(
                        TagAssignFailLogDto.CreateReqDto(
                            subject_id=int(subject_id),
                            message=cleaned_message,
                            for_date=date.fromisoformat(for_date),
                            error_message=str(e)
                        )
                    )
                continue

        self.update_subject_tag_assignment(assign_resp_dtos_list)

        return MessageTagLabelingRespDto(assign_resp_dtos_list= assign_resp_dtos_list)

    def update_subject_tag_assignment(self, assign_resp_dtos_list):
        """
        주제 태그 할당 완료 처리를 위한 헬퍼 메서드.

        Args:
            client: HandongFeedAppClient 인스턴스
            assign_resp_dtos_list: 태그 할당 응답 DTO 리스트
        """
        for dto in assign_resp_dtos_list:
            if dto and hasattr(dto[0], 'tbSubjectId') and dto[0].tbSubjectId:
                print(f"[CRON] Updating subject tag assignment for tbSubjectId={dto[0].tbSubjectId}")
                self.handong_feed_app_client.update_is_tag_assigned_true(dto[0].tbSubjectId)
