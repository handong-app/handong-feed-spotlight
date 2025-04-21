from datetime import date

from pydantic import BaseModel


class TagAssignFailLogDto:
    class CreateReqDto(BaseModel):
        subject_id: int
        message: str
        for_date: date
        error_message: str

    class CreateRespDto(BaseModel):
        id: int
        subject_id: int
        message: str
        for_date: date
        error_message: str