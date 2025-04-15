from fastapi import APIRouter, Query

from app.services.tag_labeling_service import TagLabelingService
from app.schemas.tag_labeling_dto import MessageTagLabelingRespDto

tag_labeling_router = APIRouter()

@tag_labeling_router.get("", response_model=MessageTagLabelingRespDto)
def assign_tags(
        start_date: str = Query(..., description="조회 시작 날짜 (yyyy-mm-dd)"),
        end_date: str = Query(..., description="조회 종료 날짜 (yyyy-mm-dd)"),
        is_filter_new: bool = Query(False, description="신규 메시지 필터링 여부 (true 또는 false)"),
        limit: int = Query(100, description="조회할 최대 메시지 수")
):
    """
    주어진 날짜 범위와 필터, 제한 정보를 기반으로 각 메시지에 적합한 태그 코드를 할당합니다.

    - start_date, end_date: yyyy-mm-dd 형식의 문자열 (예: "2025-01-01")
    - is_filter_new: 신규 메시지 필터링 여부 (true/false)
    - limit: 조회할 메시지 최대 개수

    Returns:
        MessageTagLabelingRespDto: 각 메시지에 할당된 태그 정보를 포함하는 DTO.
    """
    service = TagLabelingService()
    return service.assign_tags_to_messages_iterative(start_date, end_date, is_filter_new, limit)