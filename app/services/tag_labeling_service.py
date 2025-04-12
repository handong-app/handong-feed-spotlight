import logging
from app.schemas.tag_labeling_dto import MessageTagAssignment, MessageTagLabelingRespDto
from app.services.llm_service import LLMService
from app.util.pii_cleaner import mask_all_ppi
from app.util.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)

class TagLabelingService:
    def __init__(self):
        self.cleaner = TextCleaner()
        self.llm_service = LLMService()

    def assign_tags_to_messages_iterative(self, messages, tags) -> MessageTagLabelingRespDto:
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

        Args:
            messages (list): 각 메시지는 딕셔너리 형태로, 최소한 'subject_id'와 'message' 키를 포함해야 합니다.
            tags (list): 할당 가능한 태그 목록. 각 태그는 딕셔너리 형태(예: {"code": "...", "label": "...", "llm_desc": "..."})로 제공됩니다.

        Returns:
            MessageTagLabelingRespDto: 각 메시지의 subject_id와 할당된 태그 코드 배열을 포함하는 DTO.
    """

        if not messages:
            logger.warning("Empty messages list provided")
            return MessageTagLabelingRespDto(assignments=[])

        if not tags:
            logger.warning("Empty tags list provided")
            return MessageTagLabelingRespDto(assignments=[])

        assignments = []

        for msg in messages:
            subject_id = msg.get("subject_id")

            if not subject_id:
                logger.warning("Message without subject_id found, skipping")
                continue

            raw_text = msg.get("message", "")

            masked_text = mask_all_ppi(raw_text)

            cleaned_message = self.cleaner.clean(masked_text)

            assignment = self.llm_service.assign_tag_to_message(subject_id, cleaned_message, tags)
            if assignment:
                assignments.append(assignment)

        return MessageTagLabelingRespDto(assignments=assignments)
