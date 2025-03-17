from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


def get_seoul_time():
    return datetime.now(ZoneInfo("Asia/Seoul"))

def convert_to_kst_datetime(timestamp: float) -> datetime:
    """UTC 타임스탬프를 KST(한국 시간) datetime으로 변환"""
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc) + timedelta(hours=9)