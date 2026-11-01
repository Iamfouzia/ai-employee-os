from pathlib import Path

import av
import numpy as np
import torch
from pyannote.audio import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[3]

TOKEN_FILE = (
    PROJECT_ROOT
    / ".secrets"
    / "huggingface"
    / "token.txt"
)


class MeetingDiarizationService:
    def __init__(self):
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None:
            if not TOKEN_FILE.exists():
                raise FileNotFoundError(
                    f"Hugging Face token not found: {TOKEN_FILE}"
                )

            token = TOKEN_FILE.read_text(
                encoding="utf-8"
            ).strip()

            if not token:
                raise ValueError(
                    "Hugging Face token file is empty."
                )

            print("Loading speaker diarization model...")

            self._pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-community-1",
                token=token,
            )

        return self._pipeline

    def _load_audio(self, audio_path: str) -> dict:
        path = Path(audio_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        container = av.open(str(path))

        audio_stream = container.streams.audio[0]

        resampler = av.audio.resampler.AudioResampler(
            format="fltp",
            layout="mono",
            rate=16000,
        )

        chunks = []

        for frame in container.decode(audio_stream):
            resampled_frames = resampler.resample(frame)

            for resampled in resampled_frames:
                samples = resampled.to_ndarray()

                if samples.ndim == 2:
                    samples = samples[0]

                chunks.append(
                    samples.astype(
                        np.float32,
                        copy=False,
                    )
                )

        container.close()

        if not chunks:
            raise ValueError(
                "No audio samples could be decoded."
            )

        waveform = np.concatenate(chunks)

        waveform_tensor = (
            torch
            .from_numpy(waveform)
            .unsqueeze(0)
        )

        return {
            "waveform": waveform_tensor,
            "sample_rate": 16000,
        }

    def diarize(self, audio_path: str) -> dict:
        pipeline = self._get_pipeline()

        audio = self._load_audio(audio_path)

        output = pipeline(audio)

        segments = []
        speakers = set()

        diarization = output.speaker_diarization

        for turn, _, speaker in diarization.itertracks(
            yield_label=True
        ):
            speakers.add(speaker)

            segments.append(
                {
                    "speaker": speaker,
                    "start": round(turn.start, 2),
                    "end": round(turn.end, 2),
                }
            )

        return {
            "speakers": sorted(speakers),
            "segments": segments,
        }