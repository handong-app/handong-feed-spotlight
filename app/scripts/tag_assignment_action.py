import logging
from datetime import date, timedelta
from fastapi import HTTPException

from app.clients.handong_feed_app_client import HandongFeedAppClient
from app.services.tag_labeling_service import TagLabelingService
from app.core.database import SessionLocal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)


def run():
    db = SessionLocal()
    service = TagLabelingService(db)
    client = HandongFeedAppClient()

    try:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        latest_for_date = str(client.get_latest_for_date().latestForDate + timedelta(days=1))

        print(f"[ACTION] Assigning tags to new feeds for {latest_for_date} ~ {yesterday}")
        try:
            resp = service.process_feeds_with_date(
                start_date=latest_for_date,
                end_date=yesterday,
                is_filter_new=1,
                limit=100
            )
            print(
                f"[ACTION] Number of new feeds added yesterday that were successfully assigned: {len(resp.assign_resp_dtos_list)}")


        except HTTPException as e:
            if e.status_code == 204:
                print(f"[ACTION] No new feeds to process for {yesterday}.")
            else:
                raise e


        print("\n[ACTION] Retrying failed tag assignments...")
        try:
            resp =  service.process_failed_feeds()
            print(f"[ACTION] Number of failed feeds that were successfully assigned by retry: {len(resp.assign_resp_dtos_list)}")


        except HTTPException as e:
            if e.status_code == 204:
                print("[ACTION] No failed feeds to process.")
            else:
                raise e

    except Exception as e:
        logging.error(f"[ACTION] Error during tag assignment: {e}", exc_info=True)

    finally:
        db.close()

if __name__ == "__main__":
    run()