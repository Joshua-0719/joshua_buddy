import sys
import logging
import os
import ssl
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# ── Fix macOS Python SSL certificates ──────────────────────────
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
    ssl._create_default_https_context = ssl.create_default_context
except ImportError:
    pass

from joshuasnotes.core.engine import DictationEngine
from joshuasnotes.database.db_manager import DBManager
from joshuasnotes.gui.hud_window import HUDWindow
from joshuasnotes.gui.vault_window import VaultWindow
from joshuasnotes.gui.tray_icon import TrayIcon

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

def main():
    setup_logging()
    
    # 1. Initialize Qt Application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 2. Initialize Database Layer
    db = DBManager()
    
    # 3. Initialize Core Engine (Audio/AI)
    engine = DictationEngine(db_manager=db)
    
    # 4. Initialize UI Components
    hud = HUDWindow()
    vault = VaultWindow(db, engine=engine)
    tray = TrayIcon(app, vault, engine)
    
    # Show the Vault UI immediately on launch
    vault.show()
    vault.raise_()
    vault.activateWindow()
    tray.show()

    # 5. Wire Signals -> Slots
    engine.state_changed.connect(hud.update_state)
    engine.state_changed.connect(vault.update_status)
    engine.note_created.connect(vault.add_new_note)

    # 5.5 Start UDP listener for external hotkey triggers
    import socket
    import threading
    def udp_listener():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 49999))
        while True:
            try:
                data, _ = sock.recvfrom(1024)
                if b"TOGGLE" in data:
                    if engine._state == "recording":
                        engine.stop_recording()
                    elif engine._state == "idle":
                        engine.start_recording()
            except Exception as e:
                logging.error(f"UDP error: {e}")
    threading.Thread(target=udp_listener, daemon=True).start()

    # 6. Start the app
    engine.start_listening()
    logging.info("Joshua Notes is running. Look for the menu bar icon!")
    
    # Enter the Qt main loop
    sys.exit(app.exec())

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
