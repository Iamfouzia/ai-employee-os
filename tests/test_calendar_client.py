from datetime import datetime, timedelta, timezone

from app.communication.integrations.calendar_client import (
    GoogleCalendarClient,
)


calendar = GoogleCalendarClient()

start_at = (
    datetime.now(timezone.utc)
    + timedelta(minutes=10)
)

event = calendar.create_follow_up_event(
    title="AI Employee OS - Follow-up Test",
    start_at=start_at,
    description=(
        "Test follow-up event created by "
        "the AI Employee OS Communication Module."
    ),
    duration_minutes=30,
)

print("Calendar event created successfully")
print("Event ID:", event.get("id"))
print("Event link:", event.get("htmlLink"))