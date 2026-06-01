"""
Visor PDF simplificado para presupuestos ya guardados
Solo permite visualizar, imprimir y descargar - no guardar
Usa la misma UI que PDFViewer pero con lógica simplificada
"""

import os
from PySide6.QtWidgets import QMessageBox, QFileDialog, QDialog
from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtGui import QShortcut, QKeySequence

from presentation.modules.visualizer.designs.pdf_viewer_ui import Ui_Dialog_Preview_Pdf
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from presentation.modules.visualizer.components.pdf_viewer_loader import PdfViewerLoader
from core.utils.logger import logger


class SavedQuotePDFViewer(QDialog):
    """
    Visor PDF para presupuestos ya guardados
    Usa la misma UI que PDFViewer pero sin funcionalidad de guardado
    """
    
    def __init__(self, pdf_path: str, quote_number: str, parent=None, is_report: bool = False):
        # NO pasar parent para evitar que afecte a la ventana principal (igual que PDFViewer)
        super().__init__(None)  # Sin parent
        self._is_closing = False
        self.pdf_path = pdf_path
        self.quote_number = quote_number
        self.is_report = is_report
        
        # Configurar como ventana independiente (igual que PDFViewer)
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.WindowMaximizeButtonHint | 
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Usar la misma UI que PDFViewer
        self.ui = Ui_Dialog_Preview_Pdf()
        
        # Agregar un método setModal dummy para evitar errores (igual que PDFViewer)
        self.setModal = lambda x: None
        
        self.ui.setupUi(self)
        
        # Quitar el método dummy después del setup (igual que PDFViewer)
        if hasattr(self, 'setModal'):
            delattr(self, 'setModal')
        
        # Configurar título específico para presupuesto guardado
        self.setWindowTitle(tr(I18N.Pdf.VIEWER_SAVED_TITLE, quote_number=quote_number))
        
        # Configurar márgenes como en PDFViewer
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
        
        # Instanciar el visor PDF usando el mismo loader
        self.pdf_viewer_loader = PdfViewerLoader(self.ui.container_pdf_view)
        
        # Configurar tema inicial (igual que PDFViewer)
        self.pdf_viewer_loader.set_theme("auto")  # Por defecto auto
        
        # Sincronizar con el tema global de la aplicación
        self._sync_with_global_theme()
        
        # Configurar UI para presupuesto guardado
        self._configure_ui_for_saved_quote()
        
        # Configurar atajos de teclado
        self._setup_shortcuts()
        
        # Conectar señales
        self._connect_signals()
        
        # Cargar PDF inmediatamente
        self._load_pdf()
    
    def _configure_ui_for_saved_quote(self):
        """Configura la UI específicamente para presupuestos guardados"""
        # Cambiar textos de la UI
        self.ui.label_quote_num.setText(f"{self.quote_number}")
        self.ui.groupbox_preview.setTitle(tr(I18N.Pdf.GROUP_PREVIEW_TITLE))
        self.ui.groupBox_action.setTitle(tr(I18N.Pdf.GROUP_ACTIONS_SAVED_TITLE))
        
        # 🎯 Ajustar el ancho del groupBox_action para un solo botón
        # Necesita espacio para: botón (120px) + márgenes (25px) = 145px
        self.ui.groupBox_action.setMinimumSize(142, 78)
        self.ui.groupBox_action.setMaximumSize(142, 78)
        
        # Ocultar el botón "Guardar" ya que no es necesario
        self.ui.btn_save_doc.setVisible(False)
        
        # Configurar el botón "Cancelar" como único botón para cerrar
        self.ui.btn_out_viewer.setText(tr(I18N.Dialogs.CLOSE))
        self.ui.btn_out_viewer.setToolTip(tr(I18N.Pdf.TOOLTIP_CLOSE_VIEWER))
        # Mantener los colores originales del btn_out_viewer (rojos)
        
        # Mostrar botones de impresión y descarga desde el inicio
        self.ui.print_pdf.setVisible(True)
        self.ui.save_us_pdf.setVisible(True)
        self.ui.print_pdf.setToolTip(tr(I18N.Pdf.TOOLTIP_PRINT))
        self.ui.save_us_pdf.setToolTip(tr(I18N.Pdf.TOOLTIP_SAVE_COPY))
    
    def _setup_shortcuts(self):
        """Configura los atajos de teclado para el visor"""
        # Ctrl+P para imprimir
        self.print_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.print_shortcut.activated.connect(self._handle_print_request)
        
        # Ctrl+S para guardar como
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self._handle_download_request)
        
        # Escape para cerrar
        self.escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.escape_shortcut.activated.connect(self.close)
    
    def _connect_signals(self):
        """Conecta las señales de los botones"""
        # Botón principal ahora es "Cerrar" (btn_out_viewer)
        self.ui.btn_out_viewer.clicked.connect(self.close)
        
        # Botones de acción
        self.ui.print_pdf.clicked.connect(self._handle_print_request)
        self.ui.save_us_pdf.clicked.connect(self._handle_download_request)
        
        # Conectar señales del loader PDF como en PDFViewer
        self._connect_pdf_loader_signals()
    
    def _connect_pdf_loader_signals(self):
        """Conecta las señales del loader PDF (igual que PDFViewer)"""
        if hasattr(self.pdf_viewer_loader, 'pdf_loaded'):
            self.pdf_viewer_loader.pdf_loaded.connect(self._on_pdf_loaded)
            # 🎯 Conectar señal para aplicar tema cuando el PDF esté cargado
            self.pdf_viewer_loader.pdf_loaded.connect(self._on_pdf_loaded_apply_theme)
        if hasattr(self.pdf_viewer_loader, 'pdf_load_failed'):
            self.pdf_viewer_loader.pdf_load_failed.connect(self._on_pdf_load_failed)
        if hasattr(self.pdf_viewer_loader, 'pdf_print_requested'):
            self.pdf_viewer_loader.pdf_print_requested.connect(self._handle_print_request)
        if hasattr(self.pdf_viewer_loader, 'pdf_download_requested'):
            self.pdf_viewer_loader.pdf_download_requested.connect(self._handle_download_request)
    
    def _load_pdf(self):
        """Carga el PDF en el visor usando la misma lógica que PDFViewer"""
        if getattr(self, "_is_closing", False):
            return
        try:
            if not os.path.exists(self.pdf_path):
                QMessageBox.critical(
                    self,
                    tr(I18N.Dialogs.ERROR_TITLE),
                    tr(I18N.Pdf.MSG_PDF_NOT_EXISTS, path=self.pdf_path)
                )
                return
            
            # Conectar señales antes de cargar (igual que PDFViewer)
            self._connect_pdf_loader_signals()
            
            # Cargar PDF usando el mismo método que PDFViewer
            self.pdf_viewer_loader.load_pdf(self.pdf_path)
            
            logger.info("SavedQuotePDFViewer", "Iniciando carga de PDF", 
                           quote=self.quote_number,
                           path=self.pdf_path)
        
        except Exception as e:
            logger.error("SavedQuotePDFViewer", "Error en carga de PDF", 
                             quote=self.quote_number,
                             error=str(e))
            # Usar el mismo método de error que PDFViewer
            if hasattr(self.pdf_viewer_loader, 'load_error_viewer'):
                self.pdf_viewer_loader.load_error_viewer()
            else:
                QMessageBox.critical(
                    self,
                    tr(I18N.Dialogs.ERROR_TITLE),
                    tr(I18N.Pdf.MSG_LOAD_ERROR)
                )
    
    def _on_pdf_loaded(self):
        """Se ejecuta cuando el PDF se carga exitosamente"""
        logger.info("SavedQuotePDFViewer", "PDF cargado exitosamente", 
                       quote=self.quote_number)
        
    
    def _on_pdf_load_failed(self, error_msg):
        """Maneja el fallo de carga del PDF"""
        logger.warning("SavedQuotePDFViewer", "Error cargando PDF", 
                          quote=self.quote_number,
                          error=error_msg)
        QMessageBox.critical(self, tr(I18N.Dialogs.ERROR_TITLE), tr(I18N.Pdf.MSG_LOAD_FAILED, error=error_msg))
    
    def _handle_print_request(self):
        """Maneja la impresión del PDF usando lógica similar a PDFViewer"""
        try:
            import subprocess
            import platform
            
            if not os.path.exists(self.pdf_path):
                QMessageBox.warning(self, tr(I18N.Dialogs.ERROR_TITLE), tr(I18N.Pdf.MSG_FILE_NOT_FOUND))
                return
            
            # Usar la misma lógica de impresión que PDFViewer
            if platform.system() == "Windows":
                subprocess.run(["start", "", self.pdf_path], shell=True, check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.pdf_path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", self.pdf_path], check=True)
                
            logger.info("SavedQuotePDFViewer", "PDF enviado a impresión", 
                           quote=self.quote_number)
            QMessageBox.information(self, tr(I18N.Pdf.MSG_PRINT_TITLE), tr(I18N.Pdf.MSG_PRINT_SUCCESS))
            
        except Exception as e:
            logger.error("SavedQuotePDFViewer", "Error en impresión", 
                             quote=self.quote_number,
                             error=str(e))
            QMessageBox.critical(self, tr(I18N.Pdf.MSG_PRINT_ERROR_TITLE), tr(I18N.Pdf.MSG_PRINT_ERROR))
    
    def _handle_download_request(self):
        """Maneja la descarga/guardado del PDF usando lógica similar a PDFViewer"""
        try:
            # Usar la misma lógica de descarga que PDFViewer
            key = I18N.Pdf.FILE_REPORT_NAME if self.is_report else I18N.Pdf.FILE_DEFAULT_NAME
            suggested_name = tr(key, number=self.quote_number) + ".pdf"
            default_path = os.path.join(
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation),
                suggested_name
            )
            
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                tr(I18N.Pdf.DIALOG_SAVE_AS_TITLE),
                default_path,
                tr(I18N.Pdf.FILE_FILTER)
            )
            
            if save_path:
                import shutil
                shutil.copy2(self.pdf_path, save_path)
                
                logger.info("SavedQuotePDFViewer", "PDF guardado como copia", 
                               quote=self.quote_number,
                               original=self.pdf_path,
                               copia=save_path)
                
                QMessageBox.information(self, tr(I18N.Pdf.MSG_DOWNLOAD_SUCCESS_TITLE), tr(I18N.Pdf.MSG_DOWNLOAD_SUCCESS, path=save_path))
                
        except Exception as e:
            logger.error("SavedQuotePDFViewer", "Error guardando copia", 
                             quote=self.quote_number,
                             error=str(e))
            QMessageBox.critical(self, tr(I18N.Pdf.MSG_DOWNLOAD_ERROR_TITLE), tr(I18N.Pdf.MSG_DOWNLOAD_ERROR))
    
    def resizeEvent(self, event):
        """Maneja el redimensionamiento usando la misma lógica que PDFViewer"""
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
        Cambia el tema del visor PDF (igual que PDFViewer)
        
        Args:
            theme_mode: 'auto', 'light', 'dark'
        """
        if hasattr(self, 'pdf_viewer_loader'):
            self.pdf_viewer_loader.set_theme(theme_mode)
            
    def get_pdf_theme(self):
        """Retorna el tema actual del visor PDF (igual que PDFViewer)"""
        if hasattr(self, 'pdf_viewer_loader'):
            return self.pdf_viewer_loader.get_current_theme()
        return "auto"
    
    def _sync_with_global_theme(self):
        """
        Sincroniza el tema del visor PDF con el tema global de la aplicación
        """
        try:
            # Intentar obtener el tema desde el gestor global
            from core.managers.theme_manager import PaletteManager
            
            palette_manager = PaletteManager()
            theme_info = palette_manager.get_current_theme_info()
            
            if theme_info:
                # Convertir el tema de la aplicación al formato del PDF viewer
                if theme_info.get('current_dark_mode', False):
                    pdf_theme = "dark"
                else:
                    pdf_theme = "light"
                
                logger.debug("SavedQuotePDFViewer", "Sincronizando tema global", 
                                app_theme=theme_info.get('theme_name', 'desconocido'),
                                pdf_theme=pdf_theme)
                
                # Aplicar el tema al PDF viewer
                self.pdf_viewer_loader.set_theme(pdf_theme)
            else:
                # Fallback a auto si no se puede obtener el tema
                logger.debug("SavedQuotePDFViewer", "Usando tema automático como fallback")
                self.pdf_viewer_loader.set_theme("auto")
                
        except Exception as e:
            # Si hay algún error, usar tema automático
            logger.warning("SavedQuotePDFViewer", "Error sincronizando tema global, usando auto", 
                              error=str(e))
            self.pdf_viewer_loader.set_theme("auto")
    
    def _on_pdf_loaded_apply_theme(self):
        """
        🎯 Se ejecuta cuando el PDF está completamente cargado.
        Momento perfecto para aplicar el tema sincronizado con la aplicación.
        """
        try:
            # Re-sincronizar con el tema global cuando el PDF esté listo
            self._sync_with_global_theme()
            
            logger.debug("SavedQuotePDFViewer", "Tema aplicado después de cargar PDF", 
                             tema_actual=self.get_pdf_theme())
            
        except Exception as e:
            # Fallback al comportamiento original si hay error
            logger.warning("SavedQuotePDFViewer", "Error aplicando tema, usando método original", 
                              error=str(e))
            current_theme = self.pdf_viewer_loader.get_current_theme()
            self.pdf_viewer_loader.set_theme(current_theme)
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana (igual que PDFViewer)"""
        self._is_closing = True
        try:
            # Limpiar recursos del visor PDF
            if hasattr(self, 'pdf_viewer_loader'):
                if hasattr(self.pdf_viewer_loader, 'cleanup'):
                    self.pdf_viewer_loader.cleanup()
                
            logger.debug("SavedQuotePDFViewer", "Visor cerrado", 
                             quote=self.quote_number)
            
            super().closeEvent(event)
            
        except Exception as e:
            logger.error("SavedQuotePDFViewer", "Error cerrando visor", 
                             error=str(e))
            super().closeEvent(event)