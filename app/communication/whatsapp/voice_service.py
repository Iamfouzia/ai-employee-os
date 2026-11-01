from pathlib import Path

from faster_whisper import WhisperModel

from app.communication.whatsapp.models import WhatsAppMessage
from app.communication.whatsapp.service import WhatsAppAssistantService


class WhatsAppVoiceService:
    def __init__(self):
        self._model = None
        self.assistant = WhatsAppAssistantService()

    def _get_model(self):
        if self._model is None:
            print("Loading multilingual Whisper base model...")

            self._model = WhisperModel(
                "base",
                device="cpu",
                compute_type="int8",
            )

        return self._model

    def process_voice_message(
        self,
        audio_path: str,
        sender: str,
    ) -> dict:

        path = Path(audio_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Voice message not found: {audio_path}"
            )

        model = self._get_model()

        segments, info = model.transcribe(
            str(path),
            beam_size=3,
            vad_filter=True,
        )

        text_parts = []

        for segment in segments:
            text = segment.text.strip()

            if text:
                text_parts.append(text)

        transcript = " ".join(text_parts).strip()

        if not transcript:
            raise ValueError(
                "No speech could be detected in the voice message."
            )

        language = info.language or "auto"

        if language not in self.assistant.SUPPORTED_LANGUAGES:
            language = "auto"

        message = WhatsAppMessage(
            sender=sender,
            message=transcript,
            language=language,
        )

        reply = self.assistant.process_message(message)

        return {
            "status": "voice_processed",
            "sender": sender,
            "transcript": transcript,
            "language": info.language,
            "language_probability": round(
                info.language_probability,
                3,
            ),
            "intent": reply.intent,
            "reply": reply.message,
        }