import os, gc
from PySide6.QtWidgets import QMessageBox, QFileDialog, QDialog
from PySide6.QtCore import Qt
from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QShortcut, QKeySequence

from presentation.modules.visualizer.designs.pdf_viewer_ui import Ui_Dialog_Preview_Pdf
from presentation.modules.visualizer.components.pdf_viewer_loader import PdfViewerLoader
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class PDFViewer(QDialog):
    """
    Visor PDF como ventana independiente para evitar parpadeo de la ventana principal
    """
    def __init__(self, pdf_path: str, quote_number: str, save_callback=None, parent=None):
        # NO pasar parent para evitar que afecte a la ventana principal
        super().__init__(None)  # Sin parent
        self._is_closing = False
        self._saved = False  # Para rastrear si el usuario guardó
        self._confirmed_action = None  # 'save' o 'cancel'
        self.pdf_path = pdf_path
        self.quote_number = quote_number
        self.save_callback = save_callback  # Callback para ejecutar el guardado
        
        # Configurar como ventana independiente
        self.setWindowFlags(
            Qt.WindowType.Window| 
            Qt.WindowType.WindowMaximizeButtonHint | 
            Qt.WindowType.WindowCloseButtonHint
        )
        self.ui = Ui_Dialog_Preview_Pdf()
        
        # Agregar un método setModal dummy para evitar errores
        self.setModal = lambda x: None
        
        self.ui.setupUi(self)
        
        # Quitar el método dummy después del setup
        if hasattr(self, 'setModal'):
            delattr(self, 'setModal')
        
        self.setWindowTitle(tr(I18N.Pdf.VIEWER_TITLE_SIMPLE, quote_number=quote_number))
        dlg_geom = self.geometry()
        frame_geom = self.ui.frame_view.geometry()
        self._frame_margins = {
            "left": frame_geom.left(),
            "top": frame_geom.top(),
            "right": dlg_geom.width() - frame_geom.right(),
            "bottom": dlg_geom.height() - frame_geom.bottom()
        }
        lq_geom = self.ui.label_quote_num.geometry()
        self._label_quote_right_margin = dlg_geom.width() - lq_geom.right()
        
       
        # Instanciar el visor PDF
        self.pdf_viewer_loader = PdfViewerLoader(self.ui.container_pdf_view)
        
        # Configurar tema inicial (puedes conectar esto con tu ThemeManager)
        self.pdf_viewer_loader.set_theme("auto")  # Por defecto auto
       
        # Configurar botones
        self.configure_buttons()
        
        # Configurar atajos de teclado
        self.setup_shortcuts()
        
        # Conectar señales
        self.connect_signals()
        
        # Cargar el PDF inmediatamente como en la versión que funcionaba
        self.load_pdf()
    
    def configure_buttons(self):       
        # Sobreescribir textos de retranslateUi con traducciones del sistema i18n
        self.ui.btn_save_doc.setText(tr(I18N.Pdf.BTN_SAVE_TEXT))
        self.ui.btn_out_viewer.setText(tr(I18N.Dialogs.CANCEL))
        self.ui.groupbox_preview.setTitle(tr(I18N.Pdf.GROUP_PREVIEW_TITLE))
        self.ui.print_pdf.setToolTip(tr(I18N.Pdf.TOOLTIP_PRINT))
        self.ui.save_us_pdf.setToolTip(tr(I18N.Pdf.TOOLTIP_SAVE_COPY))

        # Configurar estado inicial - los botones print/download requieren guardado
        self.ui.print_pdf.setVisible(False)
        self.ui.save_us_pdf.setVisible(False)
        
        # Configurar estado inicial del botón guardar
        self.ui.btn_save_doc.setEnabled(True)
    
    def setup_shortcuts(self):
        """Configura los atajos de teclado para el PDF viewer"""
        # Ctrl+S para guardar presupuesto
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self._handle_save_document)
                
        # Escape para cancelar/cerrar
        self.escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.escape_shortcut.activated.connect(self._handle_cancel_and_close)
        
        # F1 para mostrar ayuda de atajos
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self._show_shortcuts_help)
        
        # Actualizar tooltips para incluir información de atajos
        self.ui.btn_save_doc.setToolTip(tr(I18N.Pdf.TOOLTIP_SAVE_DOCUMENT))
        self.ui.btn_out_viewer.setToolTip(tr(I18N.Pdf.TOOLTIP_CANCEL_VIEWER))
        
        # Actualizar título de grupo para incluir información de atajos
        self.ui.groupBox_action.setTitle(tr(I18N.Pdf.GROUP_ACTION_TITLE))
    
    def connect_signals(self):
        """Conecta las señales de los botones y el visor"""
        # Botones principales - nueva mecánica
        self.ui.btn_save_doc.clicked.connect(self._handle_save_document)
        self.ui.btn_out_viewer.clicked.connect(self._handle_cancel_and_close)
        
        # Botones secundarios
        self.ui.print_pdf.clicked.connect(self._handle_print_request)
        self.ui.save_us_pdf.clicked.connect(self._handle_download_request)
    
    def _handle_save_document(self):
        """Maneja el guardado del documento"""
        if self._saved:
            # Ya se guardó, no hacer nada
            return
            
        try:
            # Ejecutar callback de guardado si está disponible
            if self.save_callback and callable(self.save_callback):
                success = self.save_callback()
                if success:
                    self._saved = True
                    self._confirmed_action = 'save'
                    
                    # Mostrar mensaje de éxito
                    QMessageBox.information(
                        self, 
                        tr(I18N.Pdf.MSG_SAVE_SUCCESS_TITLE), 
                        tr(I18N.Pdf.MSG_SAVE_SUCCESS, quote_number=self.quote_number)
                    )
                    
                    # Deshabilitar botón guardar y habilitar print/download
                    self.ui.btn_save_doc.setEnabled(False)
                    self.ui.btn_save_doc.setText(tr(I18N.Pdf.STATUS_SAVED))
                    self.ui.print_pdf.setVisible(True)
                    self.ui.save_us_pdf.setVisible(True)
                    
                    # Cambiar botón cancelar a cerrar
                    self.ui.btn_out_viewer.setText(tr(I18N.Dialogs.CLOSE))
                    self.ui.btn_out_viewer.setToolTip(tr(I18N.Pdf.TOOLTIP_CLOSE_VIEWER))
                    
                    # Actualizar tooltip del botón guardar
                    self.ui.btn_save_doc.setToolTip(tr(I18N.Pdf.TOOLTIP_DOCUMENT_SAVED))
                else:
                    QMessageBox.warning(
                        self, 
                        tr(I18N.Pdf.MSG_SAVE_ERROR_TITLE), 
                        tr(I18N.Pdf.MSG_SAVE_ERROR)
                    )
            else:
                # Modo básico sin callback - marcar como guardado
                self._saved = True
                self._confirmed_action = 'save'
                self.close()
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                tr(I18N.Dialogs.ERROR_TITLE), 
                tr(I18N.Pdf.MSG_SAVE_EXCEPTION, error=str(e))
            )
    
    def _handle_cancel_and_close(self):
        """Maneja la cancelación/cierre según el estado actual"""
        if self._saved:
            # Documento ya guardado - simplemente cerrar
            self._confirmed_action = 'close'
        else:
            # Documento no guardado - cancelar
            self._confirmed_action = 'cancel'
        self.close()
    
    def was_saved(self):
        """Retorna si el usuario guardó el documento"""
        return self._saved
    
    def get_confirmed_action(self):
        """Retorna la acción confirmada: 'save', 'cancel', 'close' o None"""
        return self._confirmed_action
    
    def _show_shortcuts_help(self):
        """Muestra la ayuda de atajos de teclado"""
        QMessageBox.information(
            self,
            tr(I18N.Pdf.SHORTCUTS_HELP_TITLE),
            tr(I18N.Pdf.SHORTCUTS_HELP_MESSAGE)
        )
    
    def exec_independent(self):
        """
        Simula exec() pero con ventana independiente para evitar parpadeo
        Retorna el resultado de la acción: 'save', 'cancel' o None
        """
        self.show()
        
        # Esperar hasta que la ventana se cierre
        from PySide6.QtCore import QEventLoop
        loop = QEventLoop()
        self.destroyed.connect(loop.quit)
        loop.exec()
        
        return self.get_confirmed_action()
        
    def connect_signals_web_slots(self):
        # Visor PDF
        self.pdf_viewer_loader.pdf_loaded.connect(self.configure_button_visibility)
        self.pdf_viewer_loader.pdf_loaded.connect(self._on_pdf_loaded_apply_theme)  # 🎯 Nueva señal para tema
        self.pdf_viewer_loader.pdf_load_failed.connect(self._on_pdf_load_failed)
        self.pdf_viewer_loader.pdf_print_requested.connect(self._handle_print_request)
        self.pdf_viewer_loader.pdf_download_requested.connect(self._handle_download_request)
    
    def load_pdf(self):
        """Carga el PDF en el visor"""
        if getattr(self, "_is_closing", False):
            return
        try:
            self.connect_signals_web_slots()
            self.pdf_viewer_loader.load_pdf(self.pdf_path)
        except Exception as e:
            self.pdf_viewer_loader.load_error_viewer()
    
    def configure_button_visibility(self):
        """Muestra los botones cuando el PDF se carga correctamente"""
        # Solo mostrar print/download si ya se guardó
        if self._saved:
            self.ui.print_pdf.setVisible(True)
            self.ui.save_us_pdf.setVisible(True)
    
    def _on_pdf_loaded_apply_theme(self):
        """
        🎯 Se ejecuta cuando el PDF está completamente cargado.
        Momento perfecto para aplicar el tema.
        """
        # Aplicar el tema ahora que estamos seguros de que PDF.js está listo
        current_theme = self.pdf_viewer_loader.get_current_theme()
        self.pdf_viewer_loader.set_theme(current_theme)
    
    def _on_pdf_load_failed(self, msg):
        """Maneja el fallo de carga del PDF"""
        QMessageBox.critical(self, tr(I18N.Dialogs.ERROR_TITLE), msg)
    
    def _handle_print_request(self):
        """Maneja la solicitud de impresión"""
        # Verificar que se haya guardado primero
        if not self._saved:
            QMessageBox.warning(
                self, 
                tr(I18N.Pdf.MSG_NOT_SAVED_TITLE), 
                tr(I18N.Pdf.MSG_NOT_SAVED_PRINT)
            )
            return
            
        try:
            import subprocess
            import platform
            
            if not os.path.exists(self.pdf_path):
                QMessageBox.warning(self, tr(I18N.Dialogs.ERROR_TITLE), tr(I18N.Pdf.MSG_FILE_NOT_FOUND))
                return
            
            # Abrir PDF con el programa predeterminado para imprimir
            if platform.system() == "Windows":
                subprocess.run(["start", "", self.pdf_path], shell=True, check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.pdf_path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", self.pdf_path], check=True)
                
            QMessageBox.information(self, tr(I18N.Pdf.MSG_PRINT_TITLE), tr(I18N.Pdf.MSG_PRINT_SUCCESS))
        except Exception as e:
            QMessageBox.critical(self, tr(I18N.Pdf.MSG_PRINT_ERROR_TITLE), tr(I18N.Pdf.MSG_PRINT_ERROR))
    
    def _handle_download_request(self, download):
        """Maneja la solicitud de descarga"""
        # Verificar que se haya guardado primero
        if not self._saved:
            # Cancelar la descarga del navegador INMEDIATAMENTE
            self.pdf_viewer_loader.cancel_pending_download()
            
            # Mostrar advertencia
            QMessageBox.warning(
                self, 
                tr(I18N.Pdf.MSG_NOT_SAVED_TITLE), 
                tr(I18N.Pdf.MSG_NOT_SAVED_DOWNLOAD)
            )
            return
            
        try:
            # Cancelar la descarga automática del navegador
            # Vamos a manejar la descarga manualmente
            self.pdf_viewer_loader.cancel_pending_download()
            
            # Configurar nombre sugerido
            suggested_name = tr(I18N.Pdf.FILE_DEFAULT_NAME, number=self.quote_number) + ".pdf"
            default_path = os.path.join(
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation),
                suggested_name
            )
            
            # Crear diálogo para guardar
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                tr(I18N.Pdf.DIALOG_SAVE_AS_TITLE),
                default_path,
                tr(I18N.Pdf.FILE_FILTER)
            )
            
            if save_path:
                import shutil
                shutil.copy2(self.pdf_path, save_path)
                QMessageBox.information(self, tr(I18N.Pdf.MSG_DOWNLOAD_SUCCESS_TITLE), tr(I18N.Pdf.MSG_DOWNLOAD_SUCCESS, path=save_path))
            else:
                self._cleanup_after_cancel()
                
        except Exception as e:
            QMessageBox.critical(self, tr(I18N.Pdf.MSG_DOWNLOAD_ERROR_TITLE), tr(I18N.Pdf.MSG_DOWNLOAD_ERROR))
    
    def _cleanup_after_cancel(self):
        """Limpieza exhaustiva después de cancelar"""
        # Forzar garbage collection del diálogo
        gc.collect()
        # Limpiar cachés del WebEngine
        self.pdf_viewer_loader.clean_cache()

    def closeEvent(self, event):
        """Maneja el cierre del diálogo"""
        self._is_closing = True
        super().closeEvent(event)

    def resizeEvent(self, event):
        # Calcula el nuevo tamaño del frame_view respetando los márgenes iniciales
        dlg_rect = self.rect()
        margins = self._frame_margins
        new_width = dlg_rect.width() - margins["left"] - margins["right"]
        new_height = dlg_rect.height() - margins["top"] - margins["bottom"]
        self.ui.frame_view.setGeometry(
            margins["left"],
            margins["top"],
            new_width,
            new_height
        )
        # Anclar label_quote_num a la pared derecha
        lq = self.ui.label_quote_num
        lq_geom = lq.geometry()
        new_x = dlg_rect.width() - self._label_quote_right_margin - lq_geom.width()
        lq.move(new_x, 5)
        super().resizeEvent(event)

    def set_pdf_theme(self, theme_mode="auto"):
        """
        Cambia el tema del visor PDF
        
        Args:
            theme_mode: 'auto', 'light', 'dark'
        """
        if hasattr(self, 'pdf_viewer_loader'):
            self.pdf_viewer_loader.set_theme(theme_mode)
            
    def get_pdf_theme(self):
        """Retorna el tema actual del visor PDF"""
        if hasattr(self, 'pdf_viewer_loader'):
            return self.pdf_viewer_loader.get_current_theme()
        return "auto"