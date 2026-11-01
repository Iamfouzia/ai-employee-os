from app.communication.meeting.diarization import (
    MeetingDiarizationService,
)
from app.communication.meeting.models import MeetingTranscript
from app.communication.meeting.service import MeetingAssistantService
from app.communication.meeting.transcription import (
    MeetingTranscriptionService,
)


class MeetingWorkflowService:
    def __init__(self):
        self.transcription = MeetingTranscriptionService()
        self.diarization = MeetingDiarizationService()
        self.assistant = MeetingAssistantService()

    def analyze_audio(
        self,
        audio_path: str,
        title: str = "Meeting",
    ) -> dict:

        transcription_result = self.transcription.transcribe(
            audio_path
        )

        diarization_result = self.diarization.diarize(
            audio_path
        )

        meeting = MeetingTranscript(
            title=title,
            transcript=transcription_result["transcript"],
        )

        analysis = self.assistant.analyze(meeting)

        return {
            "status": "meeting_processed",
            "language": transcription_result["language"],
            "transcript": transcription_result["transcript"],
            "summary": analysis.summary,

            "speakers": diarization_result["speakers"],
            "speaker_segments": diarization_result["segments"],

            "action_items": analysis.action_items,
            "deadlines": analysis.deadlines,
        }