from typing import List
from pydantic import BaseModel
from datetime import date

from app.schemas.tag_labeling_dto import AssignTagsToMessageServDto


class FailFeedDetail(BaseModel):
    """
    태그 할당 실패 피드의 상세 정보를 담는 DTO.

    Attributes:
        subject_id (int): 실패한 메시지의 subject_id.
        message (str): 실패한 메시지의 내용.
        for_date (date): 실패한 메시지의 날짜.
    """
    fail_id: int
    subject_id: int
    message: str
    for_date: date

    def to_assign_tags_to_message_serv_dto(self) -> AssignTagsToMessageServDto:
        return AssignTagsToMessageServDto(
            fail_id=self.fail_id,
            subject_id=str(self.subject_id),
            for_date=str(self.for_date),
            message=self.message,
        )


class FailFeedResp(BaseModel):
    """
    태그 할당 실패 피드 목록을 담는 응답 DTO.

    Attributes:
        fail_feeds (List[FailFeedDetail]): 각 실패 피드의 상세 정보를 포함하는 리스트.
    """
    fail_feeds: List[FailFeedDetail]

    def to_assign_tags_to_message_serv_dto_list(self) -> List[AssignTagsToMessageServDto]:
        return [
            dto.to_assign_tags_to_message_serv_dto() for dto in self.fail_feeds
        ]