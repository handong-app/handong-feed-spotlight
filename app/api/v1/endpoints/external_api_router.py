from typing import List

from fastapi import APIRouter

from app.schemas.external.feed_dto import FeedDto
from app.schemas.external.tag_dto import TagDto
from app.clients.handong_feed_app_client import HandongFeedAppClient

external_api_router = APIRouter()

@external_api_router.get("/get-all-tags", response_model=List[TagDto.ReadResDto])
def get_all_tags():
    service = HandongFeedAppClient()
    return service.get_all_tags()

@external_api_router.post("/get-feeds", response_model=List[FeedDto.ReadRespDto])
def get_feeds(req: FeedDto.ReadReqDto):
    service = HandongFeedAppClient()
    return service.get_feeds(req)