from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QToolTip
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


_STYLE_GREEN = """
QPushButton {
    color: #e6fdff;
    border: 1px solid #bcbcbc;
    border-radius: 5px;
    background-color: #6cb86c;
    font-weight: bold;
    padding: 0 10px;
}
QPushButton:hover {
    color: #ffffff;
    background-color: #00aa00;
    border: 1px solid #00aaff;
}
QPushButton:pressed {
    color: #ffffff;
    background-color: #ffaa00;
    border: 1px solid #69cdff;
}
"""

_STYLE_BLUE = """
QPushButton {
    color: #e6fdff;
    border: 1px solid #bcbcbc;
    border-radius: 5px;
    background-color: #46aac4;
    font-weight: bold;
    padding: 0 10px;
}
QPushButton:hover {
    color: #ffffff;
    background-color: #009dc4;
    border: 1px solid #00aaff;
}
QPushButton:pressed {
    color: #ffffff;
    background-color: #ffaa00;
    border: 1px solid #69cdff;
}
"""

_STYLE_RED = """
QPushButton {
    color: #e6fdff;
    border: 1px solid #bcbcbc;
    border-radius: 5px;
    background-color: #f09292;
    font-weight: bold;
    padding: 0 10px;
}
QPushButton:hover {
    color: #ffffff;
    background-color: #be0000;
    border: 1px solid #00aaff;
}
QPushButton:pressed {
    color: #ffffff;
    background-color: #ff0000;
    border: 1px solid #69cdff;
}
"""


class QuoteNoteDialog(QDialog):
    """Vista del diálogo de Nota de Precios.

    Recibe el pixmap ya renderizado del QuoteNotePresenter y delega
    las acciones de copiar/guardar de vuelta al presenter.
    """

    def __init__(self, pixmap: QPixmap, presenter, parent=None, on_status=None):
        super().__init__(parent)
        self.setWindowTitle(tr(I18N.Quote.DIALOG_NOTE_TITLE))
        self.setModal(True)
        self._pixmap     = pixmap
        self._presenter  = presenter
        self._on_status  = on_status  # callable(str) opcional para el panel de resumen
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Vista previa — tamaño lógico fijo (DPR=2 → físico/2)
        dpr       = self._pixmap.devicePixelRatioF() or 1.0
        logical_w = int(self._pixmap.width()  / dpr)
        logical_h = int(self._pixmap.height() / dpr)

        preview = QLabel()
        preview.setPixmap(self._pixmap)
        preview.setFixedSize(logical_w, logical_h)
        preview.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(preview)

        # ── Botones ───────────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self._btn_copy = QPushButton(tr(I18N.QuoteNote.BTN_COPY))
        self._btn_copy.setIcon(QIcon(":/resources/resources/icons/sys_copy_v1.svg"))
        self._btn_copy.setFixedHeight(36)
        self._btn_copy.setStyleSheet(_STYLE_GREEN)
        self._btn_copy.setToolTip(tr(I18N.Quote.TOOLTIP_COPY_NOTE))
        self._btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_copy.clicked.connect(self._handle_copy)

        btn_save = QPushButton(tr(I18N.QuoteNote.BTN_SAVE_AS))
        btn_save.setIcon(QIcon(":/resources/resources/icons/sys_file_download.svg"))
        btn_save.setFixedHeight(36)
        btn_save.setStyleSheet(_STYLE_BLUE)
        btn_save.setToolTip(tr(I18N.Quote.TOOLTIP_SAVE_NOTE))
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self._handle_save)

        btn_close = QPushButton(tr(I18N.Buttons.CLOSE))
        btn_close.setFixedHeight(36)
        btn_close.setStyleSheet(_STYLE_RED)
        btn_close.setToolTip(tr(I18N.Quote.TOOLTIP_CLOSE_DIALOG))
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self._btn_copy)
        btn_layout.addWidget(btn_save)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

        # Tamaño fijo: imagen + márgenes + barra de botones
        self.setFixedSize(self.sizeHint())

    def _handle_copy(self):
        """Copia al portapapeles y muestra tooltip de confirmación flotante."""
        self._presenter.copy_to_clipboard(self._pixmap)
        rect       = self._btn_copy.rect()
        global_pos = self._btn_copy.mapToGlobal(rect.center())
        QToolTip.showText(global_pos, tr(I18N.QuoteNote.TOOLTIP_COPIED_CONFIRM), self._btn_copy)
        if self._on_status:
            self._on_status(tr(I18N.QuoteNote.STATUS_COPIED))

    def _handle_save(self):
        """Guarda la nota como imagen y notifica al panel de resumen."""
        ok = self._presenter.save_to_file(self._pixmap, self)
        if ok and self._on_status:
            self._on_status(tr(I18N.QuoteNote.STATUS_SAVED))

