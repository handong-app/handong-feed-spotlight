from sqlalchemy.orm import Session
from app.models.tag_assign_fail_log import TagAssignFailLog
from app.repositories.tag_assign_fail_log_repository import TagAssignFailLogRepository
from app.schemas.tag_assign_fail_log_dto import TagAssignFailLogDto
from app.schemas.tag_fail_feed_dto import FailFeedResp


class TagFailLogService:
    def __init__(self, db: Session):
        self.db = db
        self.tag_assign_fail_log_repo = TagAssignFailLogRepository(self.db)

    def get_unprocessed_fail_feeds(self) -> FailFeedResp:
        """
        처리되지 않은(즉, is_processed == False) 태그 할당 실패 로그들을 DB 에서 조회 후 해당 feed 의 정보를 리턴합니다.
        """
        fail_logs = self.db.query(TagAssignFailLog).filter(TagAssignFailLog.is_processed == False).all()
        fail_feed_dtos = list(map(lambda fail_log: fail_log.to_fail_feed_detail_dto(), fail_logs))

        return FailFeedResp(fail_feeds=fail_feed_dtos)

    def save_fail_log(self, create_dto: TagAssignFailLogDto.CreateReqDto):
        return self.tag_assign_fail_log_repo.log_failure(
            subject_id = create_dto.subject_id,
            message = create_dto.message,
            for_date = create_dto.for_date,
            error_message = create_dto.error_message
        )

    def mark_as_processed(self, log_id: int) -> None:
        """
        주어진 ID에 해당하는 tag_assign_fail_log 항목의 is_processed 값을 True로 업데이트합니다.

        Args:
            log_id (int): 처리 완료할 실패 로그의 ID.
        """
        self.tag_assign_fail_log_repo.mark_as_processed(log_id)