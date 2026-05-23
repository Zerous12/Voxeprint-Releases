"""
Diálogo para notificación y descarga de actualizaciones
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTextEdit, QProgressBar, QMessageBox, QCheckBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon
from pathlib import Path
from typing import Dict, Optional

from core.services.auto_update_service import UPDATE_SERVICE
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from core.utils.logger import logger
from core.managers.theme_manager import PaletteManager
from presentation.common.icon_utils import IconUtils


class DownloadThread(QThread):
    """Thread para descargar actualización en background"""
    progress = Signal(int)
    finished = Signal(Path)
    error = Signal(str)
    
    def __init__(self, download_url: str, save_path: Path):
        super().__init__()
        self.download_url = download_url
        self.save_path = save_path
        self._cancelled = False
    
    def run(self):
        """Ejecuta la descarga"""
        try:
            import urllib.request
            
            def report_progress(block_num, block_size, total_size):
                if self._cancelled:
                    raise RuntimeError("Descarga cancelada por el usuario")
                if total_size > 0:
                    downloaded = block_num * block_size
                    percent = int((downloaded / total_size) * 100)
                    self.progress.emit(min(percent, 100))
            
            urllib.request.urlretrieve(
                self.download_url, 
                self.save_path,
                reporthook=report_progress
            )
            
            if not self._cancelled:
                self.finished.emit(self.save_path)
            
        except Exception as e:
            if not self._cancelled:
                self.error.emit(str(e))


class UpdateDialog(QDialog):
    """Diálogo para mostrar información de actualización"""
    
    # Señal emitida cuando el usuario marca "No recordar esta versión"
    version_ignored = Signal(str)
    
    def __init__(self, update_info: Dict, parent=None, is_manual_check: bool = False):
        super().__init__(parent)
        self.update_info = update_info
        self.installer_path: Optional[Path] = None
        self.download_thread: Optional[DownloadThread] = None
        self.is_manual_check = is_manual_check
        
        # Detectar tema actual
        self.theme_manager = PaletteManager()
        self.is_dark_mode = self.theme_manager.is_dark_mode
        
        self._setup_ui()
        self._populate_data()
        self._check_if_already_ignored()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle("Actualización Disponible")
        self.setFixedSize(550, 420)  # Tamaño fijo, no redimensionable
        self.setModal(True)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        title = QLabel(tr(I18N.Update.DIALOG_HEADER))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Información de versiones
        version_layout = QHBoxLayout()
        
        current_label = QLabel(tr(I18N.Update.LABEL_CURRENT_VERSION))
        self.current_version = QLabel()
        version_layout.addWidget(current_label)
        version_layout.addWidget(self.current_version)
        version_layout.addStretch()
        
        new_label = QLabel(tr(I18N.Update.LABEL_NEW_VERSION))
        self.new_version = QLabel()
        new_version_font = QFont()
        new_version_font.setBold(True)
        self.new_version.setFont(new_version_font)
        version_layout.addWidget(new_label)
        version_layout.addWidget(self.new_version)
        
        layout.addLayout(version_layout)
        
        # Notas de la versión con botón Ver en GitHub
        notes_header_layout = QHBoxLayout()
        
        notes_label = QLabel("Notas de la versión:")
        notes_label_font = QFont()
        notes_label_font.setBold(True)
        notes_label.setFont(notes_label_font)
        notes_header_layout.addWidget(notes_label)
        
        notes_header_layout.addStretch()
        
        # Botón Ver en GitHub (mismo nivel que el label)
        self.btn_view_online = QPushButton(tr(I18N.Update.BTN_VIEW_GITHUB))
        self.btn_view_online.setFixedSize(130, 25)  # Un poco más pequeño
        
        # Usar el mismo ícono de GitHub que About
        from PySide6.QtGui import QIcon
        from PySide6.QtCore import QSize
        github_icon = QIcon()
        github_icon.addFile(":/resources/resources/icons/sys_github_icon.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_view_online.setIcon(github_icon)
        self.btn_view_online.clicked.connect(self._on_view_online_clicked)
        notes_header_layout.addWidget(self.btn_view_online)
        
        layout.addLayout(notes_header_layout)
        
        self.release_notes = QTextEdit()
        self.release_notes.setReadOnly(True)
        self.release_notes.setMaximumHeight(200)
        layout.addWidget(self.release_notes)
        
        # Barra de progreso (oculta inicialmente)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Label de estado
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Checkbox para no recordar esta versión (antes de los botones)
        self.chk_ignore_version = QCheckBox(tr(I18N.Update.CHK_IGNORE_VERSION))
        self.chk_ignore_version.setStyleSheet("QCheckBox { padding: 5px; }")
        self.chk_ignore_version.stateChanged.connect(self._on_ignore_version_changed)
        layout.addWidget(self.chk_ignore_version)
        
        # Botones reorganizados
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.btn_download = QPushButton(tr(I18N.Update.BTN_DOWNLOAD_INSTALL))
        self.btn_download.setFixedSize(150, 30)
        
        # Agregar ícono de descarga con recoloreo según tema
        icon_path = ":/resources/resources/icons/sys_progress_download.svg"
        if self.is_dark_mode:
            # En tema oscuro, cargar directamente (SVG ya es blanco)
            download_icon = QIcon()
            download_icon.addFile(icon_path, QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        else:
            # En tema claro, recolorear a negro para que sea visible
            try:
                download_icon = IconUtils.recolor_icon_svg(icon_path, "#000000")
            except Exception:
                # Fallback: cargar icono sin recolorear
                download_icon = QIcon()
                download_icon.addFile(icon_path, QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        
        self.btn_download.setIcon(download_icon)
        self.btn_download.clicked.connect(self._on_download_clicked)
        button_layout.addWidget(self.btn_download)
        
        # Espaciador para empujar botones de la derecha
        button_layout.addStretch()
        
        # Botón Cerrar a la derecha
        self.btn_close = QPushButton(tr(I18N.Buttons.CLOSE))
        self.btn_close.setFixedSize(100, 30)
        self.btn_close.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_close)
        
        layout.addLayout(button_layout)
    
    def _populate_data(self):
        """Puebla el diálogo con los datos de actualización"""
        current = f"v{self.update_info['current_version']}"
        if self.update_info['current_build']:
            current += f" (Build {self.update_info['current_build']})"
        self.current_version.setText(current)
        
        new = f"v{self.update_info['version']}"
        if self.update_info['build']:
            new += f" (Build {self.update_info['build']})"
        self.new_version.setText(new)
        
        # Mostrar notas de la versión
        notes = self.update_info.get('release_notes', tr(I18N.Update.NOTES_NOT_AVAILABLE))
        self.release_notes.setMarkdown(notes)
    
    def _check_if_already_ignored(self):
        """Verifica si esta versión ya está ignorada y marca el checkbox"""
        try:
            from core.managers.app_preferences_manager import AppPreferencesManager
            prefs = AppPreferencesManager()
            ignored_version = prefs.get_ignored_version()
            current_version = self.update_info.get('version', '')
            
            # Si esta versión ya está ignorada, marcar el checkbox
            if ignored_version and ignored_version == current_version:
                # Desconectar temporalmente para evitar trigger de señal
                self.chk_ignore_version.blockSignals(True)
                self.chk_ignore_version.setChecked(True)
                self.chk_ignore_version.blockSignals(False)
                logger.info("UpdateDialog", f"Versión {current_version} ya está en lista de ignoradas")
                
        except Exception as e:
            logger.error("UpdateDialog", f"Error verificando versión ignorada: {e}")
    
    def _on_ignore_version_changed(self, state):
        """Maneja el cambio de estado del checkbox para ignorar/reactivar versión"""
        try:
            from core.managers.app_preferences_manager import AppPreferencesManager
            from PySide6.QtCore import Qt
            
            prefs = AppPreferencesManager()
            version = self.update_info.get('version', '')
            
            if state == Qt.CheckState.Checked.value:
                # Marcar versión como ignorada
                success = prefs.set_ignored_version(version)
                if success:
                    logger.info("UpdateDialog", f"Versión {version} marcada como ignorada")
                    self.version_ignored.emit(version)
            else:
                # Desmarcar - limpiar versión ignorada
                success = prefs.clear_ignored_version()
                if success:
                    logger.info("UpdateDialog", f"Versión {version} reactivada (no ignorada)")
                    
        except Exception as e:
            logger.error("UpdateDialog", f"Error al cambiar estado de ignorar versión: {e}")
    
    def _on_download_clicked(self):
        """Maneja el clic en el botón de descarga"""
        try:
            # Deshabilitar botones
            self.btn_download.setEnabled(False)
            self.btn_close.setEnabled(False)
            
            # Mostrar progress bar y estado
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText(tr(I18N.Update.STATUS_DOWNLOADING))
            self.status_label.setVisible(True)
            
            # Preparar ruta de descarga según sistema operativo
            import tempfile
            from core.services.auto_update_service import get_installer_info
            
            _, installer_name = get_installer_info()
            save_path = Path(tempfile.gettempdir()) / installer_name
            
            # Iniciar descarga en thread separado
            self.download_thread = DownloadThread(
                self.update_info['download_url'],
                save_path
            )
            
            # Conectar señales
            self.download_thread.progress.connect(self._on_download_progress)
            self.download_thread.finished.connect(self._on_download_finished)
            self.download_thread.error.connect(self._on_download_error)
            
            # Iniciar thread
            self.download_thread.start()
            
        except Exception as e:
            logger.error("UpdateDialog", f"Error al iniciar descarga: {e}")
            self._show_error(tr(I18N.Update.MSG_ERROR_START_DOWNLOAD))
    
    def _on_download_progress(self, percent: int):
        """Actualiza el progreso de descarga"""
        self.progress_bar.setValue(percent)
        self.status_label.setText(tr(I18N.Update.STATUS_DOWNLOADING_PERCENT, percent=percent))
    
    def _on_download_finished(self, installer_path: Path):
        """Maneja la finalización de la descarga"""
        self.installer_path = installer_path
        self.status_label.setText(tr(I18N.Update.STATUS_DOWNLOAD_COMPLETE))
        self.progress_bar.setValue(100)
        
        # Preguntar si instalar ahora
        reply = QMessageBox.question(
            self,
            tr(I18N.Update.MSG_INSTALL_READY_TITLE),
            tr(I18N.Update.MSG_INSTALL_READY_TEXT),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self._install_update()
        else:
            self.accept()
    
    def _on_download_error(self, error_msg: str):
        """Maneja errores de descarga"""
        logger.error("UpdateDialog", f"Error en descarga: {error_msg}")
        self._show_error(tr(I18N.Update.MSG_ERROR_DOWNLOAD, error_msg=error_msg))
        
        # Rehabilitar botones
        self.btn_download.setEnabled(True)
        self.btn_close.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
    
    def _install_update(self):
        """Instala la actualización descargada"""
        try:
            if self.installer_path and self.installer_path.exists():
                # Usar el servicio de actualización para instalar
                success = UPDATE_SERVICE.install_update(self.installer_path)
                
                if success:
                    # Cerrar aplicación
                    from PySide6.QtWidgets import QApplication
                    QApplication.quit()
                else:
                    self._show_error(tr(I18N.Update.MSG_INSTALLER_FAILED))
            else:
                self._show_error(tr(I18N.Update.MSG_INSTALLER_NOT_FOUND))
                
        except Exception as e:
            logger.error("UpdateDialog", f"Error al instalar: {e}")
            self._show_error(tr(I18N.Update.MSG_ERROR_INSTALL))
    
    def _on_view_online_clicked(self):
        """Abre la página de releases en GitHub"""
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        from config.build_config import BUILD_CONFIG
        
        # Usar la URL base de releases desde la configuración
        url = BUILD_CONFIG.release.download_url
        QDesktopServices.openUrl(QUrl(url))
    
    def _show_error(self, message: str):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, tr(I18N.Dialogs.ERROR_TITLE), message)
    
    def reject(self):
        """Maneja el cierre con 'Más tarde' o botón X"""
        # No es necesario guardar aquí porque ya se guardó en _on_ignore_version_changed
        super().reject()
    
    def closeEvent(self, event):
        """Maneja el cierre del diálogo"""
        # Cancelar descarga cooperativamente
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread._cancelled = True
            self.download_thread.wait(5000)
        
        super().closeEvent(event)
