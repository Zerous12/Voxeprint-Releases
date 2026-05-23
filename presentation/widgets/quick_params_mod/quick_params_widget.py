"""Widget flotante de Parámetros Rápidos (Param).

Estado: DESACTIVADO — disponible a partir de la versión 1.2.3.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QDoubleSpinBox, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPainterPath, QPen
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


_VERSION_RELEASE = "1.3.0"  # Versión en la que se habilitarán los parámetros rápidos

_STYLE_BANNER = """
QFrame#banner_frame {
    background-color: #2b2b2b;
    border-radius: 6px;
    border: 1px solid #555;
}
QLabel#banner_title {
    color: #FFD54F;
    font-weight: bold;
    font-size: 12px;
}
QLabel#banner_body {
    color: #BBBBBB;
    font-size: 10px;
}
"""

_STYLE_OVERLAY = """
QWidget#overlay {
    background-color: rgba(0, 0, 0, 160);
    border-radius: 6px;
}
"""


class QuickParamsWidget(QWidget):
    """Panel flotante de configuración rápida y temporal del presupuesto.

    Permite ajustar delivery, margen de ganancia, descuento, etc. sin
    modificar la configuración permanente del sistema.

    Actualmente los controles están desactivados hasta la versión 1.2.3.
    """

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setObjectName("QuickParamsWidget")
        self.setFixedWidth(300)
        self._build_ui()

    # ── Construcción de UI ───────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)

        # Fondo
        painter.setBrush(self.palette().window())
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 8, 8)

        # Borde (dibujado correctamente dentro del mask)
        pen = QPen(self.palette().mid().color())
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, 8, 8)
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # Título
        title = QLabel(tr(I18N.Ui.QUICK_PARAMS_TITLE))
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        root.addWidget(title)

        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        root.addWidget(line)

        # Controles (desactivados)
        self._controls_container = QWidget()
        controls_layout = QVBoxLayout(self._controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)

        self._spin_delivery   = self._add_row(controls_layout, tr(I18N.Quote.LABEL_DELIVERY),    "Gs.", 0, 999999)
        self._spin_discount   = self._add_row(controls_layout, tr(I18N.Quote.LABEL_DISCOUNT),           "%",  0, 100,    decimals=0)
        self._spin_extra_margin = self._add_row(controls_layout, tr(I18N.Quote.LABEL_EXTRA_MARGIN),      "%",  0, 100,    decimals=0)
        self._check_urgent    = self._add_check(controls_layout, tr(I18N.Quote.CHECKBOX_URGENT_ORDER))
        self._check_pickup    = self._add_check(controls_layout, tr(I18N.Quote.CHECKBOX_LOCAL_PICKUP))

        self._controls_container.setEnabled(False)
        root.addWidget(self._controls_container)

        # Banner "Próximamente"
        root.addWidget(self._build_coming_soon_banner())

        # Botón cerrar
        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.close)
        root.addWidget(btn_close)

    def _add_row(self, layout, label_text, suffix, min_val, max_val, decimals=0):
        row = QHBoxLayout()
        row.setSpacing(6)
        lbl = QLabel(label_text)
        lbl.setMinimumWidth(130)
        spin = QDoubleSpinBox()
        spin.setSuffix(f" {suffix}")
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        spin.setDecimals(decimals)
        spin.setFixedWidth(110)
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(spin)
        layout.addLayout(row)
        return spin

    def _add_check(self, layout, label_text):
        chk = QCheckBox(label_text)
        layout.addWidget(chk)
        return chk

    def _build_coming_soon_banner(self):
        frame = QFrame()
        frame.setObjectName("banner_frame")
        frame.setStyleSheet(_STYLE_BANNER)
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(10, 8, 10, 8)
        fl.setSpacing(4)

        title = QLabel("🔒  Función no disponible")
        title.setObjectName("banner_title")

        body = QLabel(
            f"Los parámetros rápidos estarán activos\n"
            f"a partir de la versión {_VERSION_RELEASE}.\n"
            f"Por ahora esta sección está desactivada."
        )
        body.setObjectName("banner_body")
        body.setWordWrap(True)

        fl.addWidget(title)
        fl.addWidget(body)
        return frame

    # ── API pública (para uso futuro) ────────────────────────────────────────

    def get_params(self) -> dict:
        """Retorna los parámetros configurados (siempre vacío hasta v1.2.3)."""
        return {}
