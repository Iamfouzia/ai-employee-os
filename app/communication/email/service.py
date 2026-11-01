from datetime import datetime, timedelta, timezone

from app.communication.email.models import (
    EmailAnalysis,
    EmailCategory,
    EmailMessage,
    EmailPriority,
)


class EmailAssistantService:
    """
    Core business logic for the Email Assistant.

    Responsibilities:
    - classification
    - priority detection
    - reply-needed detection
    - basic summarization
    - smart follow-up recommendation
    """

    def analyze_email(
        self,
        email: EmailMessage,
    ) -> EmailAnalysis:

        category = self._classify_email(email)
        priority = self._detect_priority(email)
        requires_reply = self._requires_reply(email)

        summary = self._create_basic_summary(email)

        follow_up_at = self._suggest_follow_up(
            priority=priority,
            requires_reply=requires_reply,
        )

        return EmailAnalysis(
            summary=summary,
            category=category,
            priority=priority,
            requires_reply=requires_reply,
            suggested_follow_up_at=follow_up_at,
        )

    def _classify_email(
        self,
        email: EmailMessage,
    ) -> EmailCategory:

        text = f"{email.subject} {email.body}".lower()

        billing_keywords = [
            "invoice",
            "payment",
            "billing",
            "refund",
            "receipt",
        ]

        sales_keywords = [
            "price",
            "pricing",
            "quotation",
            "quote",
            "purchase",
            "buy",
            "product",
        ]

        support_keywords = [
            "problem",
            "issue",
            "error",
            "help",
            "support",
            "not working",
        ]

        meeting_keywords = [
            "meeting",
            "appointment",
            "schedule",
            "calendar",
            "call",
        ]

        hr_keywords = [
            "job",
            "candidate",
            "interview",
            "employee",
            "leave",
            "vacation",
        ]

        if any(
            keyword in text
            for keyword in billing_keywords
        ):
            return EmailCategory.BILLING

        if any(
            keyword in text
            for keyword in sales_keywords
        ):
            return EmailCategory.SALES

        if any(
            keyword in text
            for keyword in support_keywords
        ):
            return EmailCategory.SUPPORT

        if any(
            keyword in text
            for keyword in meeting_keywords
        ):
            return EmailCategory.MEETING

        if any(
            keyword in text
            for keyword in hr_keywords
        ):
            return EmailCategory.HR

        return EmailCategory.GENERAL

    def _detect_priority(
        self,
        email: EmailMessage,
    ) -> EmailPriority:

        text = f"{email.subject} {email.body}".lower()

        urgent_keywords = [
            "urgent",
            "immediately",
            "asap",
            "emergency",
            "critical",
        ]

        high_priority_keywords = [
            "important",
            "deadline",
            "today",
            "complaint",
        ]

        if any(
            keyword in text
            for keyword in urgent_keywords
        ):
            return EmailPriority.URGENT

        if any(
            keyword in text
            for keyword in high_priority_keywords
        ):
            return EmailPriority.HIGH

        return EmailPriority.NORMAL

    def _requires_reply(
        self,
        email: EmailMessage,
    ) -> bool:

        text = email.body.lower()

        reply_indicators = [
            "?",
            "please reply",
            "please confirm",
            "let me know",
            "can you",
            "could you",
            "would you",
            "please send",
        ]

        return any(
            indicator in text
            for indicator in reply_indicators
        )

    def _create_basic_summary(
        self,
        email: EmailMessage,
    ) -> str:

        body = " ".join(
            email.body.split()
        )

        max_length = 160

        if len(body) <= max_length:
            return body

        return (
            body[:max_length].rstrip()
            + "..."
        )

    def _suggest_follow_up(
        self,
        priority: EmailPriority,
        requires_reply: bool,
    ) -> datetime | None:
        """
        Recommend when the email should be reviewed again
        if a response/action is required.

        This creates a recommendation only.
        It does not automatically schedule anything.
        """

        if not requires_reply:
            return None

        now = datetime.now(timezone.utc)

        if priority == EmailPriority.URGENT:
            return now + timedelta(hours=4)

        if priority == EmailPriority.HIGH:
            return now + timedelta(days=1)

        return now + timedelta(days=3)