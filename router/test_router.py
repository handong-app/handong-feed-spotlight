import ollama
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.sql import text

from schema.test_dto import GenerateTestReqDTO
from util.database import get_db
from sqlalchemy.orm import Session

test_router = APIRouter()

@test_router.get("/db_connection")
def test_db_connection(db: Session = Depends(get_db)):
    """
    DB 에 간단한 쿼리를 보내 DB 연결상태 확인
    :param db:
    :return:
    """
    try:
        db.execute(text("SELECT 1"))  # 간단한 쿼리 실행
        return {"message": "Database connected successfully!"}
    except Exception as e:
        return {"error": str(e)}
