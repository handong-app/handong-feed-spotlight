from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

class SubjectTagDto:
    class CreateReqDto(BaseModel):
        tbSubjectId: int
        tagCode: str
        forDate: Optional[date] = None
        confidentValue: Optional[float] = -1.0

    class CreateRespDto(BaseModel):
        id: int
        tbSubjectId: int
        tagCode: str
        confidentValue: float
        forDate: Optional[date] = None
        createdAt: datetime
