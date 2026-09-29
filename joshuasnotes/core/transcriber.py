"""Speech-to-text transcription using mlx-whisper."""
import logging
import numpy as np
from . import config

logger = logging.getLogger(__name__)


class Transcriber:
    """Transcribes audio using mlx-whisper (Apple Silicon optimized)."""

    def __init__(self, model_name: str = config.MODEL_NAME, language: str | None = config.LANGUAGE):
        self.model_name = model_name
        self.language = language
        self._loaded = False

    def _ensure_loaded(self):
        """Trigger lazy model download/load on first use."""
        if not self._loaded:
            logger.info("Loading Whisper model: %s (first run may download ~3GB)...", self.model_name)
            import mlx_whisper
            self._mlx_whisper = mlx_whisper
            # Warm up with a tiny silent audio to force model load
            # Pass numpy array directly — no ffmpeg needed!
            silent = np.zeros(config.SAMPLE_RATE, dtype=np.float32)
            self._mlx_whisper.transcribe(
                silent,
                path_or_hf_repo=self.model_name,
                language=self.language,
            )
            self._loaded = True
            logger.info("Whisper model loaded and ready")

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe a numpy float32 audio array to text.
        
        Args:
            audio: 1-D float32 numpy array at 16kHz sample rate.
            
        Returns:
            Transcribed text string, stripped of leading/trailing whitespace.
        """
        self._ensure_loaded()

        if len(audio) == 0:
            logger.warning("Empty audio passed to transcriber")
            return ""

        logger.info("Transcribing %.2f seconds of audio...", len(audio) / config.SAMPLE_RATE)

        # Pass numpy array directly to mlx-whisper — no temp file or ffmpeg needed!
        result = self._mlx_whisper.transcribe(
            audio,
            path_or_hf_repo=self.model_name,
            language=self.language,
        )

        text = result.get("text", "").strip()
        logger.info("Transcription: %s", text[:100])
        return text
