import sys

from app.communication.meeting.transcription import (
    MeetingTranscriptionService,
)


if len(sys.argv) < 2:
    print(
        "Usage: python -m tests.test_meeting_transcription "
        '"C:\\path\\to\\audio.mp3"'
    )
    raise SystemExit(0)


audio_path = sys.argv[1]

service = MeetingTranscriptionService()

result = service.transcribe(audio_path)

print("Meeting transcription successful")
print("Language:", result["language"])
print(
    "Language probability:",
    round(result["language_probability"], 3),
)
print()
print("Transcript:")
print(result["transcript"])