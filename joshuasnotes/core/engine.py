import logging
from PySide6.QtCore import QObject, Signal, QThread
from .recorder import AudioRecorder
from .vad import VoiceActivityDetector
from .transcriber import Transcriber
from .hotkey import HotkeyListener
from .injector import TextInjector
from ..database.db_manager import DBManager

logger = logging.getLogger(__name__)

class TranscriptionWorker(QThread):
    """Background thread to handle VAD and Whisper transcription without freezing the UI."""
    finished = Signal(str, float)  # text, duration
    error = Signal(str)
    
    def __init__(self, audio, vad, transcriber):
        super().__init__()
        self.audio = audio
        self.vad = vad
        self.transcriber = transcriber
        
    def run(self):
        try:
            if not self.vad.contains_speech(self.audio):
                self.finished.emit("", 0.0)
                return
                
            trimmed = self.vad.trim_silence(self.audio)
            if len(trimmed) == 0:
                self.finished.emit("", 0.0)
                return
                
            text = self.transcriber.transcribe(trimmed)
            # Sample rate is 16000
            duration = len(self.audio) / 16000.0
            self.finished.emit(text, duration)
        except Exception as e:
            logger.exception("Error in transcription thread")
            self.error.emit(str(e))

class DictationEngine(QObject):
    """Orchestrates audio capture, AI transcription, text injection, and database storage via Qt signals."""
    
    state_changed = Signal(str)  # 'idle', 'recording', 'processing'
    note_created = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, db_manager: DBManager):
        super().__init__()
        self.recorder = AudioRecorder()
        self.vad = VoiceActivityDetector()
        self.transcriber = Transcriber()
        self.injector = TextInjector()
        self.db = db_manager
        
        self.hotkey = HotkeyListener(
            on_press_callback=self._start_recording,
            on_release_callback=self._stop_recording
        )
        self._state = "idle"
        self._worker = None

    def start_listening(self):
        """Start the global hotkey listener."""
        self.hotkey.start()
        
    def stop_listening(self):
        """Stop the global hotkey listener."""
        self.hotkey.stop()
        if self.recorder.is_recording:
            self.recorder.stop()

    def start_recording(self):
        """Start recording from an in-app control."""
        self._start_recording()

    def stop_recording(self):
        """Stop recording from an in-app control."""
        self._stop_recording()

    def preload_model(self):
        """Trigger lazy model load in a background thread."""
        class PreloadWorker(QThread):
            def __init__(self, transcriber):
                super().__init__()
                self.t = transcriber
            def run(self):
                try:
                    self.t._ensure_loaded()
                except Exception:
                    pass
        self._preload_worker = PreloadWorker(self.transcriber)
        self._preload_worker.start()

    def _start_recording(self):
        if self._state != "idle": 
            return
        self._state = "recording"
        self.state_changed.emit(self._state)
        self.recorder.start()

    def _stop_recording(self):
        if self._state != "recording": 
            return
        self.recorder.stop()
        self._state = "processing"
        self.state_changed.emit(self._state)
        
        audio = self.recorder.get_audio()
        if len(audio) == 0:
            self._set_idle()
            return
            
        self._worker = TranscriptionWorker(audio, self.vad, self.transcriber)
        self._worker.finished.connect(self._on_transcription_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_transcription_done(self, text: str, duration: float):
        if text:
            # 1. Inject into active app
            self.injector.inject(text)
            
            # 2. Save to vault
            try:
                note = self.db.add_note(text, duration)
                self.note_created.emit(note.to_dict())
            except Exception as e:
                logger.error(f"Failed to save note to DB: {e}")
                
        self._set_idle()

    def _on_error(self, err: str):
        self.error_occurred.emit(err)
        self._set_idle()

    def _set_idle(self):
        self._state = "idle"
        self.state_changed.emit(self._state)
