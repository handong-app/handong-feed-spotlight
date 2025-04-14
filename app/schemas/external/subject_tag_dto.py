from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

class SubjectTagDto:
    class CreateReqDto(BaseModel):
        tbSubjectId: int
        tagCode: str
        confidentValue: float
        forDate: Optional[date] = None
        updatedBy: Optional[str] = None
        updatedByType: Optional[str] = None

    class CreateRespDto(BaseModel):
        id: int
        tbSubjectId: int
        tagCode: str
        confidentValue: float
        forDate: Optional[date] = None
        createdAt: datetime