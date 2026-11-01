from pathlib import Path

from faster_whisper import WhisperModel


class MeetingTranscriptionService:
    def __init__(self):
        self._model = None

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            print("Loading Whisper base.en model...")

            self._model = WhisperModel(
                "base.en",
                device="cpu",
                compute_type="int8",
            )

        return self._model

    def transcribe(self, audio_path: str) -> dict:
        path = Path(audio_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
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

        transcript = " ".join(text_parts)

        return {
            "transcript": transcript,
            "language": info.language,
            "language_probability": info.language_probability,
        }