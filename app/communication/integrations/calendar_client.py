from datetime import datetime, timedelta

from googleapiclient.discovery import build

from app.communication.integrations.gmail_auth import (
    get_google_credentials,
)


class GoogleCalendarClient:
    def __init__(self):
        credentials = get_google_credentials()

        self.service = build(
            "calendar",
            "v3",
            credentials=credentials,
        )

    def create_follow_up_event(
        self,
        title: str,
        start_at: datetime,
        description: str = "",
        duration_minutes: int = 30,
    ) -> dict:
        if start_at.tzinfo is None:
            raise ValueError(
                "start_at must include timezone information."
            )

        end_at = start_at + timedelta(
            minutes=duration_minutes
        )

        event = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_at.isoformat(),
            },
            "end": {
                "dateTime": end_at.isoformat(),
            },
            "reminders": {
                "useDefault": True,
            },
        }

        return (
            self.service.events()
            .insert(
                calendarId="primary",
                body=event,
            )
            .execute()
        )