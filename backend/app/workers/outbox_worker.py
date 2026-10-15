import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.templates.email_templates import render_template
from app.integrations.resend_client import (
    resend_client,
    ResendTransientError,
    ResendFatalError,
)
from app.core.calendar import generate_ics_calendar

logger = logging.getLogger("outbox_worker")


async def process_single_notification(
    db: AsyncSession,
    notification: Notification
) -> bool:
    """
    Renders template and dispatches a single outbox notification via Resend.
    Updates notification status transactionally.
    """
    now = datetime.now(timezone.utc)
    try:
        subject, html, text = render_template(
            notification.template_name,
            notification.template_data
        )

        attachments = None
        # If interview is scheduled, generate and attach ICS calendar
        if notification.template_name in ("interview_scheduled", "interview_rescheduled"):
            data = notification.template_data
            if "start_time_iso" in data and "end_time_iso" in data and "meeting_url" in data:
                try:
                    start_dt = datetime.fromisoformat(data["start_time_iso"])
                    end_dt = datetime.fromisoformat(data["end_time_iso"])
                    ics_data = generate_ics_calendar(
                        uid=f"interview-{notification.interview_request_id or notification.id}",
                        summary=f"Technical Mock Interview: {data.get('category_name', 'Tech Session')}",
                        description=f"45-60 min technical mock interview.\\nBooking Ref: {data.get('booking_reference')}\\nJoining link: {data.get('meeting_url')}",
                        location_url=data["meeting_url"],
                        start_time_utc=start_dt,
                        end_time_utc=end_dt,
                        organizer_email=data.get("organizer_email", "interviews@mockinterviews.dev"),
                        organizer_name="Interviewer",
                        attendee_email=notification.recipient_email,
                        attendee_name=notification.recipient_name,
                    )
                    attachments = [{
                        "filename": "mock-interview-invitation.ics",
                        "content": ics_data.encode("utf-8").decode("latin-1"),
                    }]
                except Exception as ics_err:
                    logger.warning(f"Could not generate ICS attachment: {ics_err}")

        # Send via Resend client
        result = await resend_client.send_email(
            to=notification.recipient_email,
            subject=subject,
            html=html,
            text=text,
            attachments=attachments,
            idempotency_key=notification.idempotency_key,
        )

        notification.status = "SENT"
        notification.sent_at = now
        notification.resend_email_id = result.get("id")
        notification.last_error = None
        await db.commit()
        logger.info(f"Notification {notification.id} dispatched successfully (SENT)")
        return True

    except ResendTransientError as exc:
        notification.retry_count += 1
        if notification.retry_count >= notification.max_retries:
            notification.status = "DEAD"
            notification.last_error = f"Max retries exceeded: {str(exc)}"
            logger.error(f"Notification {notification.id} marked DEAD after {notification.retry_count} retries")
        else:
            backoff_sec = min(3600, (2 ** notification.retry_count) * 30)
            notification.scheduled_for = now + timedelta(seconds=backoff_sec)
            notification.status = "PENDING"
            notification.last_error = f"Transient error (retry {notification.retry_count}): {str(exc)}"
            logger.warning(f"Notification {notification.id} rescheduled in {backoff_sec}s")

        await db.commit()
        return False

    except ResendFatalError as exc:
        notification.status = "FAILED"
        notification.last_error = f"Fatal error: {str(exc)}"
        logger.error(f"Notification {notification.id} marked FAILED: {str(exc)}")
        await db.commit()
        return False

    except Exception as exc:
        logger.exception(f"Unexpected error processing notification {notification.id}: {str(exc)}")
        notification.retry_count += 1
        if notification.retry_count >= notification.max_retries:
            notification.status = "DEAD"
            notification.last_error = f"Max retries exceeded with unexpected error: {str(exc)}"
        else:
            backoff_sec = min(3600, (2 ** notification.retry_count) * 30)
            notification.scheduled_for = now + timedelta(seconds=backoff_sec)
            notification.status = "PENDING"
            notification.last_error = f"Unexpected error: {str(exc)}"

        await db.commit()
        return False


async def process_pending_outbox(db: AsyncSession, limit: int = 50) -> int:
    """
    Polls and processes pending outbox notifications that are due.
    Safe for concurrent execution with SKIP LOCKED on PostgreSQL.
    """
    now = datetime.now(timezone.utc)
    
    # Query pending notifications
    stmt = (
        select(Notification)
        .where(
            Notification.status == "PENDING",
            Notification.scheduled_for <= now,
        )
        .order_by(Notification.scheduled_for.asc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    notifications = result.scalars().all()

    processed_count = 0
    for notif in notifications:
        success = await process_single_notification(db, notif)
        if success:
            processed_count += 1

    return processed_count
