"""Audio recording using sounddevice."""
import logging
import threading
import numpy as np
import sounddevice as sd
from . import config

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Captures microphone audio into a buffer.
    
    Usage:
        recorder = AudioRecorder()
        recorder.start()
        # ... user speaks ...
        recorder.stop()
        audio = recorder.get_audio()  # numpy float32 array
    """

    def __init__(
        self,
        sample_rate: int = config.SAMPLE_RATE,
        channels: int = config.CHANNELS,
        dtype: str = config.DTYPE,
        blocksize: int = config.BLOCKSIZE,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.blocksize = blocksize

        self._buffer: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()
        self._recording = False

    # ── Audio callback (runs on a sounddevice thread) ──────────
    def _callback(self, indata: np.ndarray, frames: int, time_info, status):
        if status:
            logger.warning("Audio status: %s", status)
        if self._recording:
            with self._lock:
                self._buffer.append(indata.copy())

    # ── Public API ─────────────────────────────────────────────
    def start(self):
        """Start recording from the default microphone."""
        with self._lock:
            self._buffer.clear()
        self._recording = True

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            blocksize=self.blocksize,
            callback=self._callback,
        )
        self._stream.start()
        logger.info("Recording started")

    def stop(self):
        """Stop recording and close the stream."""
        self._recording = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        logger.info("Recording stopped")

    def get_audio(self) -> np.ndarray:
        """Return recorded audio as a 1-D float32 numpy array."""
        with self._lock:
            if not self._buffer:
                return np.array([], dtype=np.float32)
            audio = np.concatenate(self._buffer, axis=0).flatten()
        logger.info("Captured %.2f seconds of audio", len(audio) / self.sample_rate)
        return audio

    @property
    def is_recording(self) -> bool:
        return self._recording
