import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.tb_spotlight_summary import TbSpotlightSummary
from app.util.date_utils import get_seoul_time
from app.core.database import Base

class SpotlightSummaryRepository:
    def __init__(self, db: Session):
        self.db = db
        Base.metadata.create_all(bind=self.db.get_bind())


    def save_summary(self, summary: str, target_date: str) -> None:
        """
        주어진 summary 텍스트를 TbSpotlightSummary 테이블에 저장합니다.
        target_date는 문자열 (예: "2025-03-17") 형식으로 전달되며, 이를 date 객체로 변환하여 저장합니다.
        """

        for_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()

        new_summary = TbSpotlightSummary(
            id=str(uuid.uuid4()).replace("-", "")[:32],
            summary=summary,
            for_date=for_date_obj,
            created_at=get_seoul_time()
        )
        self.db.add(new_summary)
        self.db.commit()