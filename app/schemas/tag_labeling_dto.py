from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from app.schemas.external.subject_tag_dto import SubjectTagDto


class MessageTagAssignment(BaseModel):
    subject_id: str
    tag_codes: List[str]

class MessageTagLabelingRespDto(BaseModel):
    assign_resp_dtos_list: List[List[SubjectTagDto.AssignRespDto]]

class AssignTagsToMessageServDto(BaseModel):
    fail_id: Optional[int] = None
    subject_id: str
    for_date: str
    message: str
    