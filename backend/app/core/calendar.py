import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional


def generate_ics_calendar(
    uid: str,
    summary: str,
    description: str,
    location_url: str,
    start_time_utc: datetime,
    end_time_utc: datetime,
    organizer_email: str,
    organizer_name: str,
    attendee_email: str,
    attendee_name: str,
    sequence: int = 0,
) -> str:
    """
    Generates an RFC 5545 iCalendar (.ics) string for mock interview scheduling.
    Uses UTC datetime format (YYYYMMDDTHHMMSSZ).
    """
    dtstamp = datetime.now(ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")
    dtstart = start_time_utc.strftime("%Y%m%dT%H%M%SZ")
    dtend = end_time_utc.strftime("%Y%m%dT%H%M%SZ")

    # Sanitize multiline description for ICS (CRLF + spaces or \n escaped)
    escaped_description = description.replace("\r\n", "\\n").replace("\n", "\\n")
    escaped_summary = summary.replace("\n", " ").strip()

    ics_content = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//MockInterviewPlatform//EN\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:REQUEST\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{uid}\r\n"
        f"DTSTAMP:{dtstamp}\r\n"
        f"DTSTART:{dtstart}\r\n"
        f"DTEND:{dtend}\r\n"
        f"SUMMARY:{escaped_summary}\r\n"
        f"DESCRIPTION:{escaped_description}\r\n"
        f"LOCATION:{location_url}\r\n"
        f"ORGANIZER;CN={organizer_name}:mailto:{organizer_email}\r\n"
        f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;CN={attendee_name}:mailto:{attendee_email}\r\n"
        f"SEQUENCE:{sequence}\r\n"
        "STATUS:CONFIRMED\r\n"
        "TRANSP:OPAQUE\r\n"
        "BEGIN:VALARM\r\n"
        "TRIGGER:-PT15M\r\n"
        "ACTION:DISPLAY\r\n"
        f"DESCRIPTION:Reminder: {escaped_summary}\r\n"
        "END:VALARM\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    return ics_content
