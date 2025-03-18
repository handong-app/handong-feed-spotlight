from sqlalchemy.orm import Session
from sqlalchemy.sql import text

class TbKaMessageRepository:
    """TbKaMessage 테이블의 데이터 접근을 담당하는 Repository 클래스"""

    def __init__(self, db: Session):
        self.db = db

    def get_messages_by_date(self, target_date: str):
        """last_sent_at 이 target_date인 메세지 데이터를 조회"""

        query = text("""
            SELECT id, message, FROM_UNIXTIME(last_sent_at) AS last_sent_at_datetime
            FROM TbKaMessage
            WHERE deleted != 'Y'
              AND threshold < distance
              AND last_sent_at >= UNIX_TIMESTAMP(:target_date)
              AND last_sent_at < UNIX_TIMESTAMP(DATE_ADD(:target_date_next, INTERVAL 1 DAY))
        """)
        result = self.db.execute(query, {
            "target_date": target_date,
            "target_date_next": target_date
        })

        return result.mappings().all()