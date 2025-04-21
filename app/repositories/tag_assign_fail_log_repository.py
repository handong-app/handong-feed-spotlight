from datetime import date
from sqlalchemy.orm import Session
from app.models.tag_assign_fail_log import TagAssignFailLog
from app.schemas.tag_assign_fail_log_dto import TagAssignFailLogDto


class TagAssignFailLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_failure(self, subject_id: int, message: str, for_date: date, error_message: str) -> TagAssignFailLogDto.CreateRespDto:
        """
        태깅 실패 시, 해당 메시지의 subject_id, message, for_date 및 발생한 error_message를
        tag_assign_fail_log 테이블에 기록합니다.

        Args:
            subject_id (int): 태깅 실패한 feed 의 subject_id.
            message (str): 태깅 실패한 feed 의 메시지 내용.
            for_date (date): 태깅 실패한 feed 의 subject 신규 생성 날짜.
            error_message (str): 태깅 실패 시 발생한 에러 메시지.

        Returns:
            TagAssignFailLog: 저장된 실패 로그 엔티티.
        """
        log_entry = TagAssignFailLog(
            subject_id=subject_id,
            message=message,
            for_date=for_date,
            error_message=error_message,
            is_processed=False
        )
        self.db.add(log_entry)
        self.db.commit()
        return log_entry.to_create_resp_dto()

    def mark_as_processed(self, log_id: int) -> None:
        """
        주어진 ID에 해당하는 tag_assign_fail_log 항목의 is_processed 값을 True로 업데이트합니다.

        Args:
            log_id (int): 처리 완료할 실패 로그의 ID.
        """
        log_entry = self.db.query(TagAssignFailLog).filter(TagAssignFailLog.id == log_id).first()
        if log_entry:
            log_entry.is_processed = True
            self.db.commit()
