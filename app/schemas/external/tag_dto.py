from datetime import datetime
from pydantic import BaseModel
from typing import Optional

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