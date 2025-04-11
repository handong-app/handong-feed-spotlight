from pydantic import BaseModel
from typing import List

class MessageTagAssignment(BaseModel):
    subject_id: str
    tag_codes: List[str]

class MessageTagLabelingRespDto(BaseModel):
    assignments: List[MessageTagAssignment]
    