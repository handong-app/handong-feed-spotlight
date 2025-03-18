from sqlalchemy.orm import Session
from app.repositories.tb_ka_message_repository import TbKaMessageRepository

class TestService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = TbKaMessageRepository(db)

    def fetch_feed_messages_by_date(self, target_date: str):
        """
        특정 날짜의 피드 메시지를 조회하는 서비스 레이어
        """
        messages = self.repository.get_messages_by_date(target_date)

        return {"target_date": target_date, "messages": messages}