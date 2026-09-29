"""Global hotkey listener using pynput."""
import logging
import threading
from typing import Callable
from pynput import keyboard
from . import config

logger = logging.getLogger(__name__)


class HotkeyListener:
    """Listens for a push-to-talk hotkey combination.
    
    Hold Ctrl+Option+Space to record, release to transcribe.
    """

    def __init__(
        self,
        on_press_callback: Callable[[], None],
        on_release_callback: Callable[[], None],
    ):
        self.on_press_callback = on_press_callback
        self.on_release_callback = on_release_callback
        self._listener: keyboard.Listener | None = None
        self._pressed_keys: set[str] = set()
        self._hotkey_active = False
        self._lock = threading.Lock()

        # Map config modifiers to pynput key objects
        self._modifier_map = {
            "ctrl": {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r},
            "alt": {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r},
            "shift": {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r},
            "cmd": {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r},
        }

    def _key_to_name(self, key) -> str | None:
        """Convert a pynput key to a normalized string name."""
        # Check if it's a modifier
        for name, key_set in self._modifier_map.items():
            if key in key_set:
                return name
        # Check if it's the trigger key
        if key == keyboard.Key.space:
            return "space"
        # Character keys
        if hasattr(key, "char") and key.char:
            return key.char.lower()
        # Named keys
        if hasattr(key, "name") and key.name:
            return key.name.lower()
        return None

    def _check_hotkey(self) -> bool:
        """Check if all hotkey keys are currently pressed."""
        required = config.HOTKEY_MODIFIERS | {config.HOTKEY_TRIGGER}
        return required.issubset(self._pressed_keys)

    def _on_press(self, key):
        """Handle key press events."""
        name = self._key_to_name(key)
        if name is None:
            return

        with self._lock:
            self._pressed_keys.add(name)
            if self._check_hotkey() and not self._hotkey_active:
                self._hotkey_active = True
                logger.info("Hotkey pressed — starting recording")
                threading.Thread(
                    target=self.on_press_callback, daemon=True
                ).start()

    def _on_release(self, key):
        """Handle key release events."""
        name = self._key_to_name(key)
        if name is None:
            return

        with self._lock:
            self._pressed_keys.discard(name)
            if self._hotkey_active and not self._check_hotkey():
                self._hotkey_active = False
                logger.info("Hotkey released — stopping recording")
                threading.Thread(
                    target=self.on_release_callback, daemon=True
                ).start()

    def start(self):
        """Start listening for the hotkey in a daemon thread."""
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()
        logger.info(
            "Hotkey listener started: %s (push-to-talk)",
            config.hotkey_display(),
        )

    def stop(self):
        """Stop the hotkey listener."""
        if self._listener:
            self._listener.stop()
            self._listener = None
        logger.info("Hotkey listener stopped")
