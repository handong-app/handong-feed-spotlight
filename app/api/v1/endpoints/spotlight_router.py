from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.spotlight_dto import SpotlightDto
from app.services.spotlight_service import SpotlightService


class SpotlightRouter:

    def __init__(self):
        self.router = APIRouter()

        self.router.add_api_route("/{target_date}", self.get_spotlight, methods=["GET"])

    @staticmethod
    def get_spotlight(target_date: str, db: Session = Depends(get_db)) -> SpotlightDto.GetSpotlightRespDto:
        """target_date 의 spotlight 를 get"""
        service = SpotlightService(db)
        get_spotlight_resp_dto = service.get_spotlight(SpotlightDto.GetSpotlightReqDto(target_date=target_date))
        return  get_spotlight_resp_dto



spotlight_router = SpotlightRouter().router
