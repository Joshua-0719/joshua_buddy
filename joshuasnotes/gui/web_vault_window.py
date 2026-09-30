from pathlib import Path
import sys

from PySide6.QtCore import QUrl, Qt
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView


class WebVaultWindow(QWebEngineView):
    def __init__(self, bridge):
        super().__init__()
        self.setWindowTitle("Joshua Notes")
        self.resize(1180, 760)
        self.setMinimumSize(760, 560)
        self.setWindowFlag(Qt.WindowType.Window, True)
        self.setWindowFlag(Qt.WindowType.Sheet, False)

        self.channel = QWebChannel(self.page())
        self.channel.registerObject("desktop", bridge)
        self.page().setWebChannel(self.channel)
        self.bridge = bridge

        if getattr(sys, "frozen", False):
            project_root = Path(sys._MEIPASS)
        else:
            project_root = Path(__file__).resolve().parents[2]
        frontend = project_root / "frontend" / "dist" / "index.html"
        self.load(QUrl.fromLocalFile(str(frontend)))