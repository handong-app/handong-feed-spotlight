from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.core.database import get_db

from app.services.test_service import TestService


class TestRouter:

    def __init__(self):
        self.router = APIRouter()

        self.router.add_api_route("/db_connection", self.test_db_connection, methods=["GET"])
        self.router.add_api_route("/feed/{target_date}", self.fetch_feed_messages, methods=["GET"])

    def test_db_connection(self, db: Session = Depends(get_db)):
        """DB 연결 확인"""
        try:
            db.execute(text("SELECT 1"))
            return {"message": "Database connected successfully!"}
        except Exception as e:
            return {"error": str(e)}

    def fetch_feed_messages(self, target_date: str, db: Session = Depends(get_db)):
        """특정 날짜의 메시지를 조회"""
        service = TestService(db)
        messages = service.fetch_feed_messages_by_date(target_date)
        return messages



test_router = TestRouter().router
