"""Global hotkey listener using pynput, isolated in a subprocess to avoid Qt runloop conflicts."""
import logging
import threading
import queue
import multiprocessing as mp
from typing import Callable
from pynput import keyboard
from . import config

logger = logging.getLogger(__name__)


def _hotkey_process_worker(event_queue: mp.Queue):
    """Runs in a separate process, completely isolated from PySide6.
    
    This prevents Qt's CFRunLoop on macOS from swallowing the Carbon event taps
    that pynput uses to monitor global keystrokes.
    """
    pressed_keys = set()
    hotkey_active = False

    modifier_map = {
        "ctrl": {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r},
        "alt": {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r},
        "shift": {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r},
        "cmd": {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r},
    }

    def key_to_name(key) -> str | None:
        for name, key_set in modifier_map.items():
            if key in key_set:
                return name
        if key == keyboard.Key.space:
            return "space"
        if hasattr(key, "vk") and key.vk == 49:
            return "space"
        if hasattr(key, "char") and key.char:
            if key.char in (' ', '\xa0'):
                return "space"
            return key.char.lower()
        if hasattr(key, "name") and key.name:
            return key.name.lower()
        return None

    def check_hotkey() -> bool:
        required = config.HOTKEY_MODIFIERS | {config.HOTKEY_TRIGGER}
        return required.issubset(pressed_keys)

    def on_press(key):
        nonlocal hotkey_active
        name = key_to_name(key)
        if name:
            pressed_keys.add(name)
            if check_hotkey() and not hotkey_active:
                hotkey_active = True
                event_queue.put("start")

    def on_release(key):
        nonlocal hotkey_active
        name = key_to_name(key)
        if name:
            pressed_keys.discard(name)
            if hotkey_active and not check_hotkey():
                hotkey_active = False
                event_queue.put("stop")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


class HotkeyListener:
    """Listens for a push-to-talk hotkey combination, safe for Qt."""

    def __init__(
        self,
        on_press_callback: Callable[[], None],
        on_release_callback: Callable[[], None],
    ):
        self.on_press_callback = on_press_callback
        self.on_release_callback = on_release_callback
        self._queue = mp.Queue()
        self._process = None
        self._monitor_thread = None
        self._running = False

    def _monitor_queue(self):
        while self._running:
            try:
                # Use a timeout so we can exit cleanly
                msg = self._queue.get(timeout=0.5)
                if msg == "start":
                    logger.info("Hotkey pressed — starting recording")
                    threading.Thread(target=self.on_press_callback, daemon=True).start()
                elif msg == "stop":
                    logger.info("Hotkey released — stopping recording")
                    threading.Thread(target=self.on_release_callback, daemon=True).start()
            except queue.Empty:
                pass
            except Exception as e:
                if self._running:
                    logger.error(f"Error in hotkey queue monitor: {e}")

    def start(self):
        """Start listening for the hotkey in an isolated process."""
        self._running = True
        self._process = mp.Process(target=_hotkey_process_worker, args=(self._queue,), daemon=True)
        self._process.start()

        self._monitor_thread = threading.Thread(target=self._monitor_queue, daemon=True)
        self._monitor_thread.start()

        logger.info(
            "Isolated Hotkey listener started: %s (push-to-talk)",
            config.hotkey_display(),
        )

    def stop(self):
        """Stop the hotkey listener."""
        self._running = False
        if self._process and self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=1.0)
            self._process = None
        logger.info("Hotkey listener stopped")
