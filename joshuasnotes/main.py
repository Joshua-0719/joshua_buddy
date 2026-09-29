import sys
import logging
import os
import ssl
from PySide6.QtWidgets import QApplication

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
from joshuasnotes.gui.desktop_bridge import DesktopBridge
from joshuasnotes.gui.tray_icon import TrayIcon
from joshuasnotes.gui.web_vault_window import WebVaultWindow

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
    bridge = DesktopBridge(db, engine)
    vault = WebVaultWindow(bridge)
    tray = TrayIcon(app, vault, engine)
    tray.show()
    
    # Show the Vault UI immediately on launch so the user can see it
    vault.show()
    vault.raise_()
    vault.activateWindow()
    
    # 5. Wire Signals -> Slots
    engine.state_changed.connect(hud.update_state)
    engine.note_created.connect(lambda _note: bridge.refreshNotes())

    # 6. Start the app
    engine.start_listening()
    logging.info("Joshua Notes is running. Look for the menu bar icon!")
    
    # Enter the Qt main loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
