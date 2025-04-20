from sqlalchemy.orm import Session
from app.models.tag_assign_fail_log import TagAssignFailLog
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
        fail_feed_dtos = list(map(lambda fail_log: fail_log.to_dto(), fail_logs))

        return FailFeedResp(fail_feeds=fail_feed_dtos)