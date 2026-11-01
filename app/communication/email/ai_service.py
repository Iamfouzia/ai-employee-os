import os

from openai import OpenAI

from app.communication.email.models import (
    EmailDraftRequest,
    EmailDraftResponse,
    EmailMessage,
)


class EmailAIService:
    MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    @staticmethod
    def generate_draft(
        request: EmailDraftRequest,
    ) -> EmailDraftResponse:

        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            try:
                client = OpenAI(api_key=api_key)

                prompt = f"""
Write a {request.tone} business email.

Subject:
{request.subject}

Recipients:
{", ".join(request.recipients)}

Context:
{request.context}

Return only the email body.
""".strip()

                response = client.responses.create(
                    model=EmailAIService.MODEL,
                    input=prompt,
                    store=False,
                )

                body = response.output_text.strip()

                if body:
                    return EmailDraftResponse(
                        subject=request.subject,
                        body=body,
                    )

            except Exception as exc:
                print(
                    f"OpenAI unavailable, using fallback: {exc}"
                )

        return EmailDraftResponse(
            subject=request.subject,
            body=EmailAIService._generate_fast_draft(
                request
            ),
        )

    @staticmethod
    def generate_reply(
        email: EmailMessage,
        tone: str = "professional",
    ) -> EmailDraftResponse:

        subject = email.subject.strip()

        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            try:
                client = OpenAI(api_key=api_key)

                prompt = f"""
Write a {tone} reply to this customer email.

From:
{email.sender}

Subject:
{email.subject}

Email:
{email.body}

Return only the reply body.
""".strip()

                response = client.responses.create(
                    model=EmailAIService.MODEL,
                    input=prompt,
                    store=False,
                )

                body = response.output_text.strip()

                if body:
                    return EmailDraftResponse(
                        subject=subject,
                        body=body,
                    )

            except Exception as exc:
                print(
                    f"OpenAI unavailable, using fallback: {exc}"
                )

        return EmailDraftResponse(
            subject=subject,
            body=EmailAIService._generate_fast_reply(
                email=email,
                tone=tone,
            ),
        )

    @staticmethod
    def _generate_fast_draft(
        request: EmailDraftRequest,
    ) -> str:

        return (
            "Dear Customer,\n\n"
            f"{request.context}\n\n"
            "Please let us know if you have any further questions.\n\n"
            "Best regards,\n"
            "AI Employee OS"
        )

    @staticmethod
    def _generate_fast_reply(
        email: EmailMessage,
        tone: str,
    ) -> str:

        opening = (
            "Hello"
            if tone.lower() == "friendly"
            else "Dear Customer"
        )

        return (
            f"{opening},\n\n"
            f"Thank you for your message regarding "
            f"\"{email.subject}\".\n\n"
            "We have received your request and will review it. "
            "We will get back to you with the relevant information "
            "as soon as possible.\n\n"
            "Best regards,\n"
            "AI Employee OS"
        )