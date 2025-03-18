from sqlalchemy import Column, String, Integer, DateTime, Date
from app.util.date_utils import get_seoul_time
from app.core.database import Base

class TbSpotlightRank(Base):
    __tablename__ = "TbSpotlightRank"

    id = Column(String(32), primary_key=True)
    tb_ka_message_id = Column(String(32), nullable=False)
    rank = Column(Integer, nullable=False)
    for_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=get_seoul_time)
