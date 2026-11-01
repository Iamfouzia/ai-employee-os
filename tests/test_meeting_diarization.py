import sys

from app.communication.meeting.diarization import (
    MeetingDiarizationService,
)


if len(sys.argv) < 2:
    print(
        'Usage: python -m tests.test_meeting_diarization '
        '"C:\\path\\to\\audio.m4a"'
    )
    raise SystemExit(0)


service = MeetingDiarizationService()

result = service.diarize(sys.argv[1])

print("Speaker diarization successful")
print("Speakers:", result["speakers"])
print()

for segment in result["segments"]:
    print(
        f'{segment["speaker"]}: '
        f'{segment["start"]}s -> '
        f'{segment["end"]}s'
    )