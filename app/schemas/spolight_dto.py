from typing import Dict, List
from pydantic import BaseModel

from app.schemas.feed_message_dto import FeedMessageDto


class SpotlightDto:
    class GetSpotlightReqDto(BaseModel):
        target_date: str

    class GetSpotlightRespDto(BaseModel):
        target_date: str
        # summary: str
        # spotlights: List[Dict[str, str]]
        scores: List[int]

    class FetchFeedMessagesByDateServDto(BaseModel):
        target_date: str
        messages:  List[FeedMessageDto]

    class GenerateSpotlightScoreServDto(BaseModel):
