"""Voice Activity Detection using Silero VAD."""
import logging
import numpy as np
import torch
from silero_vad import load_silero_vad, get_speech_timestamps
from . import config

logger = logging.getLogger(__name__)

# Silero VAD works best single-threaded
torch.set_num_threads(1)


class VoiceActivityDetector:
    """Detects and trims silence from audio using Silero VAD."""

    def __init__(
        self,
        threshold: float = config.VAD_THRESHOLD,
        min_silence_ms: int = config.MIN_SILENCE_MS,
        min_speech_ms: int = config.MIN_SPEECH_MS,
        sample_rate: int = config.SAMPLE_RATE,
    ):
        self.threshold = threshold
        self.min_silence_ms = min_silence_ms
        self.min_speech_ms = min_speech_ms
        self.sample_rate = sample_rate
        self._model = None

    def _load_model(self):
        """Lazy-load the Silero VAD model from the pip package (no network needed)."""
        if self._model is None:
            logger.info("Loading Silero VAD model...")
            self._model = load_silero_vad()
            logger.info("Silero VAD loaded")

    def contains_speech(self, audio: np.ndarray) -> bool:
        """Check if the audio contains any speech."""
        self._load_model()
        if len(audio) == 0:
            return False
        tensor = torch.from_numpy(audio).float()
        timestamps = get_speech_timestamps(
            tensor,
            self._model,
            threshold=self.threshold,
            sampling_rate=self.sample_rate,
            min_silence_duration_ms=self.min_silence_ms,
            min_speech_duration_ms=self.min_speech_ms,
        )
        return len(timestamps) > 0

    def trim_silence(self, audio: np.ndarray) -> np.ndarray:
        """Remove leading and trailing silence from audio."""
        self._load_model()
        if len(audio) == 0:
            return audio

        tensor = torch.from_numpy(audio).float()
        timestamps = get_speech_timestamps(
            tensor,
            self._model,
            threshold=self.threshold,
            sampling_rate=self.sample_rate,
            min_silence_duration_ms=self.min_silence_ms,
            min_speech_duration_ms=self.min_speech_ms,
        )

        if not timestamps:
            logger.info("No speech detected in audio")
            return np.array([], dtype=np.float32)

        # Keep from first speech start to last speech end
        start = timestamps[0]["start"]
        end = timestamps[-1]["end"]
        trimmed = audio[start:end]
        
        original_dur = len(audio) / self.sample_rate
        trimmed_dur = len(trimmed) / self.sample_rate
        logger.info(
            "Trimmed audio: %.2fs → %.2fs (removed %.2fs silence)",
            original_dur, trimmed_dur, original_dur - trimmed_dur
        )
        return trimmed
