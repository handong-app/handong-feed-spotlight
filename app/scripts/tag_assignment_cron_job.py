from datetime import date, timedelta
from fastapi import HTTPException

from app.clients.handong_feed_app_client import HandongFeedAppClient
from app.services.tag_labeling_service import TagLabelingService
from app.core.database import SessionLocal


def update_subject_tag_assignment(client, assign_resp_dtos_list):
    """
    주제 태그 할당 완료 처리를 위한 헬퍼 메서드.

    Args:
        client: HandongFeedAppClient 인스턴스
        assign_resp_dtos_list: 태그 할당 응답 DTO 리스트
    """
    for dto in assign_resp_dtos_list:
        if dto and hasattr(dto[0], 'tbSubjectId') and dto[0].tbSubjectId:
            print(f"[CRON] Updating subject tag assignment for tbSubjectId={dto[0].tbSubjectId}")
            client.update_is_tag_assigned_true(dto[0].tbSubjectId)


def run():
    db = SessionLocal()
    service = TagLabelingService(db)
    client = HandongFeedAppClient()

    try:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        latest_for_date = str(client.get_latest_for_date().latestForDate + timedelta(days=1))

        print(f"[CRON] Assigning tags to new feeds for {latest_for_date} ~ {yesterday}")
        try:
            resp = service.process_feeds_with_date(
                start_date=latest_for_date,
                end_date=yesterday,
                is_filter_new=1,
                limit=100
            )
            print(
                f"[CRON] Number of new feeds added yesterday that were successfully assigned: {len(resp.assign_resp_dtos_list)}")

            update_subject_tag_assignment(client, resp.assign_resp_dtos_list)

        except HTTPException as e:
            if e.status_code == 204:
                print(f"[CRON] No new feeds to process for {yesterday}.")
            else:
                raise e


        print("\n[CRON] Retrying failed tag assignments...")
        try:
            resp =  service.process_failed_feeds()
            print(f"[CRON] Number of failed feeds that were successfully assigned by retry: {len(resp.assign_resp_dtos_list)}")

            update_subject_tag_assignment(client, resp.assign_resp_dtos_list)

        except HTTPException as e:
            if e.status_code == 204:
                print("[CRON] No failed feeds to process.")
            else:
                raise e

    except Exception as e:
        import logging
        logging.error(f"[CRON] Error during tag assignment: {e}", exc_info=True)

    finally:
        db.close()

if __name__ == "__main__":
    run()