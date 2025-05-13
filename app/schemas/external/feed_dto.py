from pydantic import BaseModel, field_validator
from typing import Optional, List

from app.schemas.tag_labeling_dto import AssignTagsToMessageServDto
from app.util.date_utils import convert_unix_to_date_str


class FeedDto:
    class ReadReqDto(BaseModel):
        start: Optional[int] = None
        end: Optional[int] = None
        isFilterNew: int = 1
        onlyUnassignedFeeds: int = 1
        limit: Optional[int] = None

    class ReadRespDto(BaseModel):
        subjectId: int
        id: str
        sentAt: int
        message: str
        files: List[str] = []
        like: bool
        messageCount: int

        @field_validator("files", mode="before")
        def default_files(cls, value):
            return value or []

        def to_assign_tags_to_message_serv_dto(self) -> AssignTagsToMessageServDto:
            return AssignTagsToMessageServDto(
                subject_id=str(self.subjectId),
                for_date=convert_unix_to_date_str(self.sentAt),
                message=self.message,
            )
