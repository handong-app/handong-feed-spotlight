from datetime import date, timedelta
from fastapi import HTTPException

from app.services.tag_labeling_service import TagLabelingService
from app.core.database import SessionLocal

def run():
    db = SessionLocal()
    service = TagLabelingService(db)

    try:
        yesterday = (date.fromisoformat("2025-01-21") - timedelta(days=1)).isoformat()
        print(f"[CRON] Assigning tags to new feeds for {yesterday}")
        try:
            resp = service.process_feeds_with_date(
                start_date=yesterday,
                end_date=yesterday,
                is_filter_new=1,
                limit=100
            )
            print(
                f"[CRON] Number of new feeds added yesterday that were successfully assigned: {len(resp.assign_resp_dtos_list)}")
        except HTTPException as e:
            if e.status_code == 204:
                print(f"[CRON] No new feeds to process for {yesterday}.")
            else:
                raise e


        print(f"\n[CRON] Retrying failed tag assignments...")
        try:
            resp =  service.process_failed_feeds()
            print(f"[CRON] Number of failed feeds that were successfully assigned by retry: {len(resp.assign_resp_dtos_list)}")
        except HTTPException as e:
            if e.status_code == 204:
                print(f"[CRON] No failed feeds to process.")
            else:
                raise e

    except Exception as e:
        print(f"[CRON ERROR] {e}")

    finally:
        db.close()

if __name__ == "__main__":
    run()