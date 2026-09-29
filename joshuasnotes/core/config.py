"""VoiceType configuration and constants."""
import os
from pathlib import Path

# ── Audio Settings ──────────────────────────────────────────────
SAMPLE_RATE = 16_000          # 16 kHz — required by Whisper
CHANNELS = 1                  # Mono
DTYPE = "float32"             # Audio sample format
BLOCKSIZE = 1024              # Samples per audio callback block

# ── Whisper Model ───────────────────────────────────────────────
MODEL_NAME = "mlx-community/whisper-large-v3-turbo"
# Alternatives:
#   "mlx-community/whisper-small"         ~1 GB RAM, fastest
#   "mlx-community/whisper-medium"        ~2 GB RAM
#   "mlx-community/whisper-large-v3"      ~4 GB RAM, most accurate

LANGUAGE = "en"               # Set to None for auto-detection

# ── Voice Activity Detection ───────────────────────────────────
VAD_THRESHOLD = 0.5           # Speech probability threshold (0-1)
MIN_SILENCE_MS = 700          # Silence duration to end speech (ms)
MIN_SPEECH_MS = 250           # Minimum speech duration to keep (ms)

# ── Hotkey ──────────────────────────────────────────────────────
# Option (⌥) + Space (push-to-talk)
HOTKEY_MODIFIERS = frozenset(["alt"])            # "alt" = Option (⌥) on Mac
HOTKEY_TRIGGER = "space"                         # pynput key name

# Mac-friendly display names (pynput name → display name)
KEY_DISPLAY_NAMES = {
    "alt": "⌥ Option",
    "ctrl": "⌃ Control",
    "cmd": "⌘ Command",
    "shift": "⇧ Shift",
    "space": "Space",
}

def hotkey_display() -> str:
    """Return a human-readable hotkey string for Mac users."""
    parts = [KEY_DISPLAY_NAMES.get(m, m) for m in sorted(HOTKEY_MODIFIERS)]
    parts.append(KEY_DISPLAY_NAMES.get(HOTKEY_TRIGGER, HOTKEY_TRIGGER))
    return " + ".join(parts)

# ── Text Injection ──────────────────────────────────────────────
# "clipboard" = copy + Cmd+V  |  "typing" = simulate keystrokes
INJECTION_MODE = "clipboard"
PASTE_DELAY = 0.05            # Seconds between clipboard set and paste

# ── Paths ───────────────────────────────────────────────────────
DATA_DIR = Path.home() / ".voicetype"
LOG_FILE = DATA_DIR / "voicetype.log"
HISTORY_FILE = DATA_DIR / "history.jsonl"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
