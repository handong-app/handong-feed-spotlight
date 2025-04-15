from pydantic import BaseModel, field_validator
from typing import Optional, List


class FeedDto:
    class ReadReqDto(BaseModel):
        start: Optional[int] = None
        end: Optional[int] = None
        isFilterNew: bool = False
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