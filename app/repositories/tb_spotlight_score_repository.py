import uuid
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from app.models.tb_spotlight_score import TbSpotlightScore
from app.util.date_utils import get_seoul_time
from app.schemas.spotlight_dto import SpotlightDto
from app.core.database import Base


class SpotlightScoreRepository:
    def __init__(self, db: Session):
        self.db = db
        Base.metadata.create_all(bind=self.db.get_bind())

    def save_scores(self, scores: List[SpotlightDto.GenerateSpotlightScoreServDto], target_date: str) -> None:
        """
        주어진 스코어 DTO들을 TbSpotlightScore 테이블에 저장.
        target_date는 문자열 (예: "2025-03-17") 형식으로 전달되며, 이를 date 객체로 변환하여 저장.
        """

        for_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()

        for score_dto in scores:
            new_score = TbSpotlightScore(
                id=str(uuid.uuid4()).replace("-", "")[:32],
                tb_ka_message_id=score_dto.tb_ka_message_id,
                score=score_dto.score,
                for_date=for_date_obj,
                created_at=get_seoul_time()
            )
            self.db.add(new_score)

        self.db.commit()