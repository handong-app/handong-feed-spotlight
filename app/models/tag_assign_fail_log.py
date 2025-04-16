from sqlalchemy import Column, Integer, Text, Date, DateTime, Boolean, func
from app.core.database import Base
from app.schemas.tag_fail_feed_dto import FailFeedDetail


class TagAssignFailLog(Base):
    __tablename__ = "tag_assign_fail_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, nullable=False)                                                    # 태깅 실패한 메시지의 subject_id
    message = Column(Text, nullable=False)                                                           # 실패한 메시지 내용
    for_date = Column(Date, nullable=False)                                                          # 실패한 메시지의 날짜
    error_message = Column(Text, nullable=True)                                                     # 태깅 실패 시 발생한 에러 메시지
    is_processed = Column(Boolean, nullable=False, default=False)                                   # 재처리 여부. False이면 아직 처리되지 않음.
    created_at = Column(DateTime, nullable=False, server_default=func.now())                        # 로그 생성 시각
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())   # 로그 갱신 시각

    def __repr__(self):
        """문자열 표현 정의하는 특수 메서드"""
        return (f"<TagAssignFailLog(id={self.id}, subject_id={self.subject_id}, "
                f"for_date={self.for_date}, is_processed={self.is_processed})>")

    def to_dto(self):
        return FailFeedDetail(
            subject_id=self.subject_id,
            message=self.message,
            for_date=self.for_date,
        )