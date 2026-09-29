from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

class HUDWindow(QWidget):
    """The floating translucent 'pill' overlay shown during dictation."""
    
    def __init__(self):
        super().__init__()
        
        # Native macOS frameless tool window, always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        self.init_ui()
        
        # Opacity effect for fade in/out
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main container with a premium glass-like dark surface
        self.container = QWidget()
        self.container.setObjectName("HudContainer")
        self.container.setStyleSheet("""
            #HudContainer {
                background-color: rgba(255, 255, 255, 245);
                border: 1px solid #d7e3e4;
                border-radius: 999px;
            }
            QLabel {
                color: #20383e;
                font-family: "Montserrat", sans-serif;
            }
        """)

        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(18, 10, 18, 10)
        container_layout.setSpacing(10)

        self.icon_label = QLabel("●")
        self.icon_label.setStyleSheet(
            "font-size: 12px; color: #159889; font-weight: 700;"
        )

        self.text_label = QLabel("Ready")
        self.text_label.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #20383e;"
        )

        container_layout.addWidget(self.icon_label)
        container_layout.addWidget(self.text_label)

        layout.addWidget(self.container)
        self.resize(185, 52)
        
    def showEvent(self, event):
        """Center at the bottom of the screen when shown."""
        super().showEvent(event)
        screen = self.screen().availableGeometry()
        x = screen.center().x() - self.width() // 2
        y = screen.bottom() - self.height() - 80
        self.move(x, y)
        
    def update_state(self, state: str):
        """Update the HUD visually based on the engine state."""
        if state == "idle":
            self.fade_out()
        elif state == "recording":
            self.icon_label.setText("●")
            self.icon_label.setStyleSheet("font-size: 12px; color: #dc5c5c; font-weight: 700;")
            self.text_label.setText("Listening...")
            self.fade_in()
        elif state == "processing":
            self.icon_label.setText("◔")
            self.icon_label.setStyleSheet("font-size: 12px; color: #159889; font-weight: 700;")
            self.text_label.setText("Processing...")
            self.fade_in()
            
    def fade_in(self):
        if not self.isVisible():
            self.opacity_effect.setOpacity(0.0)
            self.show()
        self.animation.stop()
        self.animation.setEndValue(1.0)
        self.animation.start()
        
    def fade_out(self):
        if self.isVisible():
            self.animation.stop()
            self.animation.setEndValue(0.0)
            self.animation.finished.connect(self._on_fade_out_done)
            self.animation.start()
            
    def _on_fade_out_done(self):
        self.animation.finished.disconnect(self._on_fade_out_done)
        self.hide()
