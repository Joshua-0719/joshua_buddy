"""Text injection into the active application."""
import logging
import time
import subprocess
import pyperclip
from . import config

logger = logging.getLogger(__name__)


class TextInjector:
    """Injects transcribed text into the currently focused application."""

    def __init__(self, mode: str = config.INJECTION_MODE):
        self.mode = mode

    def inject(self, text: str):
        """Inject text into the active application.
        
        Args:
            text: The text to inject.
        """
        if not text:
            logger.warning("Empty text, nothing to inject")
            return

        if self.mode == "clipboard":
            self._inject_clipboard(text)
        elif self.mode == "typing":
            self._inject_typing(text)
        else:
            logger.error("Unknown injection mode: %s", self.mode)

    def _inject_clipboard(self, text: str):
        """Copy text to clipboard and simulate Cmd+V."""
        # Save current clipboard (best effort)
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            old_clipboard = None

        # Set new clipboard content
        pyperclip.copy(text)
        time.sleep(config.PASTE_DELAY)

        # Simulate Cmd+V using pynput (avoids macOS System Events permission block)
        from pynput.keyboard import Controller, Key
        kb = Controller()
        try:
            with kb.pressed(Key.cmd):
                kb.press('v')
                kb.release('v')
            logger.info("Text injected via clipboard paste (%d chars)", len(text))
        except Exception as e:
            logger.error("Failed to simulate Cmd+V: %s", e)

        # Restore old clipboard after a brief delay
        if old_clipboard is not None:
            time.sleep(0.3)
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                pass

    def _inject_typing(self, text: str):
        """Type text character by character using pynput."""
        from pynput.keyboard import Controller
        kb = Controller()
        for char in text:
            kb.type(char)
            time.sleep(0.01)  # Small delay for reliability
        logger.info("Text injected via simulated typing (%d chars)", len(text))
