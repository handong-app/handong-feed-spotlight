from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class TagDto:
    class ReadResDto(BaseModel):
        code: str
        label: str
        userDesc: Optional[str] = None
        llmDesc: Optional[str] = None
        colorHex: Optional[str] = None
        priorityWeight: float
        createdAt: datetime
        updatedAt: datetime

    @staticmethod
    def extract_tag_codes(tags: List["TagDto.ReadResDto"]) -> List[str]:
        """주어진 TagDto.ReadResDto 리스트에서 각 태그의 'code' 필드만 추출하여 문자열 배열로 반환"""
        return [tag.code for tag in tags]