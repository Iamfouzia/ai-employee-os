import sys

from app.communication.meeting.workflow import MeetingWorkflowService


if len(sys.argv) < 2:
    print(
        'Usage: python -m tests.test_meeting_workflow '
        '"C:\\path\\to\\audio.m4a"'
    )
    raise SystemExit(0)


workflow = MeetingWorkflowService()

result = workflow.analyze_audio(
    audio_path=sys.argv[1],
    title="AI Employee OS Test Meeting",
)

print("Meeting workflow successful")
print("Language:", result["language"])

print()
print("Transcript:")
print(result["transcript"])

print()
print("Summary:")
print(result["summary"])

print()
print("Speakers:", result["speakers"])

print()
print("Speaker segments:")

for segment in result["speaker_segments"]:
    print(
        f'{segment["speaker"]}: '
        f'{segment["start"]}s -> '
        f'{segment["end"]}s'
    )

print()
print("Action items:", result["action_items"])
print("Deadlines:", result["deadlines"])