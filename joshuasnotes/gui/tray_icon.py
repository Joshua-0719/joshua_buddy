from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt

class TrayIcon(QSystemTrayIcon):
    """The menu bar icon for Joshua's Notes."""
    
    def __init__(self, app, vault_window, engine):
        super().__init__()
        self.app = app
        self.vault_window = vault_window
        self.engine = engine
        
        # Create a minimalist app icon with a cyan accent to match the WhisperFlow aesthetic
        pixmap = QPixmap(22, 22)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#7dd3fc"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(6, 6, 10, 10)
        painter.end()

        self.setIcon(QIcon(pixmap))
        self.setToolTip("WhisperFlow")
        
        # Build the menu
        self.menu = QMenu()

        self.open_action = self.menu.addAction("Open Vault")
        self.open_action.triggered.connect(self.show_vault)

        self.menu.addSeparator()

        self.preload_action = self.menu.addAction("Preload Whisper model")
        self.preload_action.triggered.connect(self.engine.preload_model)

        self.menu.addSeparator()

        self.quit_action = self.menu.addAction("Quit WhisperFlow")
        self.quit_action.triggered.connect(self.quit_app)
        
        self.setContextMenu(self.menu)
        
    def show_vault(self):
        """Show and bring the Vault window to the front."""
        self.vault_window.show()
        self.vault_window.raise_()
        self.vault_window.activateWindow()
        
    def quit_app(self):
        self.engine.stop_listening()
        self.app.quit()
