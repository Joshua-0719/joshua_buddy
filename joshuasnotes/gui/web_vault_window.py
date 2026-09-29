from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView


class WebVaultWindow(QWebEngineView):
    def __init__(self, bridge):
        super().__init__()
        self.setWindowTitle("WhisperFlow")
        self.resize(1180, 760)
        self.setMinimumSize(760, 560)

        self.channel = QWebChannel(self.page())
        self.channel.registerObject("desktop", bridge)
        self.page().setWebChannel(self.channel)
        self.bridge = bridge

        frontend = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "index.html"
        self.load(QUrl.fromLocalFile(str(frontend)))