import re
from datetime import date, datetime, timedelta

from app.communication.meeting.models import (
    MeetingAnalysis,
    MeetingTranscript,
)


class MeetingAssistantService:
    def analyze(
        self,
        meeting: MeetingTranscript,
    ) -> MeetingAnalysis:

        lines = [
            line.strip()
            for line in meeting.transcript.splitlines()
            if line.strip()
        ]

        speakers = self._extract_speakers(lines)
        action_items = self._extract_action_items(lines)
        deadlines = self._extract_deadlines(meeting.transcript)
        summary = self._create_summary(lines)

        return MeetingAnalysis(
            summary=summary,
            speakers=speakers,
            action_items=action_items,
            deadlines=deadlines,
        )

    def _extract_speakers(
        self,
        lines: list[str],
    ) -> list[str]:

        speakers = []

        for line in lines:
            if ":" not in line:
                continue

            speaker = line.split(":", 1)[0].strip()

            if (
                speaker
                and len(speaker) < 50
                and speaker not in speakers
            ):
                speakers.append(speaker)

        return speakers

    def _extract_action_items(
        self,
        lines: list[str],
    ) -> list[str]:

        indicators = [
            "will ",
            "need to ",
            "needs to ",
            "action item",
            "todo",
            "follow up",
        ]

        results = []

        for line in lines:
            lowered = line.lower()

            if any(
                indicator in lowered
                for indicator in indicators
            ):
                results.append(line)

        return results

    def _extract_deadlines(
        self,
        transcript: str,
    ) -> list[str]:

        deadlines = []
        text = transcript.lower()
        today = datetime.now().date()

        # Explicit YYYY-MM-DD dates
        for match in re.findall(
            r"\b\d{4}-\d{2}-\d{2}\b",
            transcript,
        ):
            if match not in deadlines:
                deadlines.append(match)

        # Explicit DD/MM/YYYY or MM/DD/YYYY dates
        for match in re.findall(
            r"\b\d{1,2}/\d{1,2}/\d{4}\b",
            transcript,
        ):
            if match not in deadlines:
                deadlines.append(match)

        # Relative dates
        if re.search(r"\btoday\b", text):
            value = today.isoformat()

            if value not in deadlines:
                deadlines.append(value)

        if re.search(r"\btomorrow\b", text):
            value = (
                today + timedelta(days=1)
            ).isoformat()

            if value not in deadlines:
                deadlines.append(value)

        # Weekdays
        weekdays = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        for weekday_name, weekday_number in weekdays.items():
            if not re.search(
                rf"\b{weekday_name}\b",
                text,
            ):
                continue

            days_ahead = (
                weekday_number - today.weekday()
            ) % 7

            # "Friday" means the next upcoming Friday.
            if days_ahead == 0:
                days_ahead = 7

            resolved_date = (
                today + timedelta(days=days_ahead)
            ).isoformat()

            if resolved_date not in deadlines:
                deadlines.append(resolved_date)

        return deadlines

    def _create_summary(
        self,
        lines: list[str],
    ) -> str:

        text = " ".join(lines)

        if len(text) <= 300:
            return text

        return text[:300].rstrip() + "..."