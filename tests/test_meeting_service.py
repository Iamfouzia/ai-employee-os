from app.communication.meeting.models import MeetingTranscript
from app.communication.meeting.service import MeetingAssistantService


meeting = MeetingTranscript(
    title="Project Planning Meeting",
    transcript="""
Hafiz: We completed the Gmail integration.
Ammar: I will finish the AI routing documentation.
Hafiz: I need to complete the WhatsApp module.
Fouzia: I will update the CRM by 2026-08-15.
Manahil: Follow up with the finance team.
Ammar: Our next review is on 2026-08-18.
""",
)

service = MeetingAssistantService()

result = service.analyze(meeting)

print("Meeting Assistant successful")
print("Summary:", result.summary)
print("Speakers:", result.speakers)
print("Action items:", result.action_items)
print("Deadlines:", result.deadlines)