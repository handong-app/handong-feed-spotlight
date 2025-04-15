from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

class SubjectTagDto:
    class AssignReqDto(BaseModel):
        tbSubjectId: int
        tagCode: str
        forDate: Optional[date] = None
        confidentValue: Optional[float] = -1.0

    class AssignRespDto(BaseModel):
        id: int
        tbSubjectId: int
        tagCode: str
        confidentValue: float
        forDate: Optional[date] = None
        createdAt: datetime
