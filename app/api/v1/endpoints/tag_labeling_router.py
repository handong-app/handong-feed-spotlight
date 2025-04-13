from fastapi import APIRouter

from app.core.config import EnvVariables
from app.services.tag_labeling_service import TagLabelingService
from app.schemas.tag_labeling_dto import MessageTagLabelingRespDto

tag_labeling_router = APIRouter()

@tag_labeling_router.get("", response_model=MessageTagLabelingRespDto)
def assign_tags():
    service = TagLabelingService()
    return service.assign_tags_to_messages_iterative(EnvVariables.SAMPLE_MESSAGES, EnvVariables.SAMPLE_TAGS)
