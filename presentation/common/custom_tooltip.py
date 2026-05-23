from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer, QPoint


class CustomToolTip(QLabel):
    def __init__(self):
        super().__init__(None)
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setWordWrap(True)
        self.setMaximumWidth(320)
        self.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 11px;
            }
        """)
        self.hide()


class SlotToolTipManager:
    def __init__(self):
        self._tooltip = CustomToolTip()
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show)
        self._text = ""
        self._pos = QPoint()

    def show_delayed(self, widget, text: str, delay: int = 400):
        self._text = text
        self._pos = widget.mapToGlobal(QPoint(0, widget.height() + 4))
        self._timer.start(delay)

    def _show(self):
        if not self._text:
            return
        self._tooltip.setText(self._text)
        self._tooltip.adjustSize()
        self._tooltip.move(self._pos)
        self._tooltip.show()
        self._tooltip.raise_()

    def hide(self):
        self._timer.stop()
        self._tooltip.hide()
