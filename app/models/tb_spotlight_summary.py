from sqlalchemy import Column, String, DateTime, Text, Date
from app.util.date_utils import get_seoul_time
from app.core.database import Base

class TbSpotlightSummary(Base):
    __tablename__ = "TbSpotlightSummary"

    id = Column(String(32), primary_key=True)
    summary = Column(Text, nullable=False)
    for_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=get_seoul_time)
