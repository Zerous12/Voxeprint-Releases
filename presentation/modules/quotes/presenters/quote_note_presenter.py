from __future__ import annotations

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication
from core.managers.quote_note_manager import QuoteNoteManager
from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class QuoteNotePresenter:
    """Presenter para la Nota de Precios.

    Construye el QPixmap con diseño profesional a partir de company_info y
    document_settings del QuoteConfigManager (compartidos con el PDF de
    presupuesto: logo, colores primarios, datos de empresa).

    La vista (QuoteNoteDialog) recibe el pixmap listo y delega las acciones
    de copiar/guardar a este presenter.
    """

    def __init__(self):
        self.manager = QuoteNoteManager()

    def build_pixmap(self, data: dict):
        return self.manager.generate(data)

    def copy_to_clipboard(self, pixmap):
        """Copia el pixmap al portapapeles del sistema."""
        QApplication.clipboard().setPixmap(pixmap)
        logger.info("QuoteNotePresenter", "Nota de Precios copiada al portapapeles")

    def save_to_file(self, pixmap: QPixmap, parent=None) -> bool:
        """Abre el diálogo de guardado y guarda el pixmap en disco."""
        from PySide6.QtWidgets import QFileDialog
        from core.utils.path_helper import get_user_start_dir
        from datetime import datetime
        import os
        note_number = datetime.now().strftime("%d%m%y%H%M%S")
        default_name = tr(I18N.QuoteNote.FILE_DEFAULT_NAME, number=note_number) + ".png"
        path, _ = QFileDialog.getSaveFileName(
            parent,
            tr(I18N.QuoteNote.DIALOG_SAVE_TITLE),
            os.path.join(get_user_start_dir(), default_name),
            tr(I18N.QuoteNote.DIALOG_SAVE_FILTER)
        )
        if not path:
            return False
        ok = pixmap.save(path)
        if ok:
            logger.info("QuoteNotePresenter", f"Nota guardada en: {path}")
        else:
            logger.error("QuoteNotePresenter", f"Error al guardar nota en: {path}")
        return ok
