import sys

from app.communication.whatsapp.voice_service import (
    WhatsAppVoiceService,
)


if len(sys.argv) < 2:
    print(
        'Usage: python -m tests.test_whatsapp_voice '
        '"C:\\path\\to\\audio.m4a"'
    )
    raise SystemExit(0)


service = WhatsAppVoiceService()

result = service.process_voice_message(
    audio_path=sys.argv[1],
    sender="test-user",
)

print("WhatsApp voice processing successful")
print("Language:", result["language"])
print("Transcript:", result["transcript"])
print("Intent:", result["intent"])
print("Reply:", result["reply"])