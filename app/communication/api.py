from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.communication.email.models import EmailDraftRequest


router = APIRouter(
    prefix="/communication",
    tags=["Communication"],
)


class MeetingRequest(BaseModel):
    audio_path: str
    title: str = "Meeting"


@router.post("/email/gmail/draft")
def create_gmail_draft(request: EmailDraftRequest):
    try:
        from app.communication.email.workflow import (
            EmailWorkflowService,
        )

        service = EmailWorkflowService()

        return service.create_gmail_draft(request)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post("/email/outlook/draft")
def create_outlook_draft(request: EmailDraftRequest):
    try:
        from app.communication.email.outlook_workflow import (
            OutlookEmailWorkflowService,
        )

        service = OutlookEmailWorkflowService()

        return service.create_draft(request)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post("/meeting/analyze")
def analyze_meeting(request: MeetingRequest):
    try:
        # Heavy Whisper/pyannote imports happen only
        # when this endpoint is actually used.
        from app.communication.meeting.workflow import (
            MeetingWorkflowService,
        )

        service = MeetingWorkflowService()

        return service.analyze_audio(
            audio_path=request.audio_path,
            title=request.title,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc