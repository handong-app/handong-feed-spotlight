from typing import List
from pydantic import BaseModel

from app.schemas.feed_message_dto import FeedMessageDto


class SpotlightDto:
    class GetSpotlightReqDto(BaseModel):
        target_date: str

    class GetSpotlightRespDto(BaseModel):
        for_date: str
        summary: str
        scores: List["SpotlightDto.GenerateSpotlightScoreServDto"]

    class FetchFeedMessagesByDateServDto(BaseModel):
        target_date: str
        messages:  List[FeedMessageDto]

    class GenerateSpotlightScoreServDto(BaseModel):
        tb_ka_message_id: str
        score: int

SpotlightDto.GetSpotlightRespDto.model_rebuild()