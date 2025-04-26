from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

class SubjectTagDto:
    class AssignReqDto(BaseModel):
        tagCode: str
        forDate: Optional[str] = None
        confidentValue: Optional[float] = -1.0

    class AssignRespDto(BaseModel):
        id: int
        tbSubjectId: int
        tagCode: str
        confidentValue: float
        forDate: Optional[str] = None
        createdAt: datetime

    class GetLatestForDateResDto(BaseModel):
        latestForDate: Optional[date]