"""
Presenter para manejar verificación de actualizaciones
"""

from PySide6.QtCore import QObject, QThread, Signal, QTimer
from typing import Optional, Dict

from core.services.auto_update_service import AutoUpdateService
from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from core.managers.app_preferences_manager import AppPreferencesManager
from presentation.modules.main.views.update_dialog import UpdateDialog


class UpdateCheckThread(QThread):
    """Thread para verificar actualizaciones sin bloquear la UI"""
    update_available = Signal(dict)
    no_update = Signal()
    error = Signal(str)
    
    def __init__(self, use_cache: bool = True):
        super().__init__()
        self.use_cache = use_cache
    
    def run(self):
        """Ejecuta la verificación de actualizaciones"""
        try:
            service = AutoUpdateService()
            update_info = service.check_for_updates(use_cache=self.use_cache)
            
            # Si no se pudo obtener información (error de conexión, etc.)
            if update_info is None:
                self.error.emit("No se pudo conectar al servidor de actualizaciones")
                return
            
            # Si hay información válida, verificar si es más nueva
            if update_info.get('is_newer'):
                self.update_available.emit(update_info)
            else:
                self.no_update.emit()
                
        except Exception as e:
            logger.error("UpdateCheckThread", f"Error verificando actualizaciones: {e}")
            self.error.emit(str(e))
class UpdateCheckerPresenter(QObject):
    """Presenter para gestionar la verificación de actualizaciones"""
    
    # Señales emitidas
    update_available_signal = Signal(dict)  # Cuando hay actualización disponible
    no_update_signal = Signal()  # Cuando no hay actualización (está actualizado)
    version_ignored_signal = Signal(str)  # Cuando una versión es ignorada
    check_error_signal = Signal(str)  # Cuando hay error al verificar
    checking_started = Signal()  # Cuando inicia la verificación
    checking_finished = Signal()  # Cuando termina la verificación (éxito o error)
    update_check_blocked = Signal(int)  # Cuando la verificación es bloqueada por cooldown (emite segundos restantes)
    
    def __init__(self, parent_view=None):
        super().__init__()
        self.parent_view = parent_view
        self.check_thread: Optional[UpdateCheckThread] = None
        self.update_dialog: Optional[UpdateDialog] = None
        self.preferences = AppPreferencesManager()
        self._is_checking = False  # Flag para evitar múltiples verificaciones simultáneas
        self._last_shown_version: Optional[str] = None  # Versión mostrada recientemente
        self._cooldown_timer = QTimer()  # Timer para limpiar versión mostrada
        self._cooldown_timer.setSingleShot(True)
        self._cooldown_timer.timeout.connect(self._clear_shown_version)
        self._is_manual_check = False  # Flag para saber si es búsqueda manual
        self._cooldown_start_time = None  # Timestamp cuando inicia el cooldown
        self._cooldown_duration = 60  # Duración del cooldown en segundos
    
    def check_for_updates_async(self, silent: bool = True):
        """
        Verifica actualizaciones de forma asíncrona
        
        Args:
            silent: Si es True, solo notifica si hay actualización (verificación automática).
                   Si es False, notifica siempre (búsqueda manual por el usuario)
        """
        try:
            # Evitar múltiples verificaciones simultáneas
            if self._is_checking:
                logger.warning("UpdateChecker", "Ya hay una verificación en curso, ignorando solicitud")
                return
            
            # Si hay un diálogo abierto, traerlo al frente en lugar de crear otro
            if self.update_dialog and not self.update_dialog.isHidden():
                logger.info("UpdateChecker", "Diálogo de actualización ya abierto, trayéndolo al frente")
                self.update_dialog.raise_()
                self.update_dialog.activateWindow()
                return
            
            self._is_checking = True
            logger.info("UpdateChecker", "Verificando actualizaciones...")
            
            # Emitir señal de inicio de verificación
            self.checking_started.emit()
            
            # Guardar si es búsqueda manual
            self._is_manual_check = not silent
            
            # Crear y configurar thread
            # Si silent es True (automático): usar caché
            # Si silent es False (manual): forzar verificación sin caché
            use_cache = silent
            self.check_thread = UpdateCheckThread(use_cache=use_cache)
            
            # Conectar señales según el modo
            if silent:
                # Modo silencioso: solo mostrar si hay actualización Y NO está ignorada
                self.check_thread.update_available.connect(lambda info: self._on_update_available(info, is_manual=False))
                self.check_thread.no_update.connect(self._on_no_update_silent)
            else:
                # Modo explícito: mostrar SIEMPRE, incluso si está ignorada (búsqueda manual)
                self.check_thread.update_available.connect(lambda info: self._on_update_available(info, is_manual=True))
                self.check_thread.no_update.connect(self._on_no_update_explicit)
            
            self.check_thread.error.connect(self._on_check_error)
            
            # Iniciar verificación
            self.check_thread.start()
            
        except Exception as e:
            logger.error("UpdateChecker", f"Error al iniciar verificación: {e}")
            self._is_checking = False
    
    def _on_update_available(self, update_info: Dict, is_manual: bool = False):
        """Maneja cuando hay actualización disponible"""
        try:
            self._is_checking = False  # Liberar flag
            self.checking_finished.emit()  # Notificar fin de verificación
            
            version = update_info.get('version', '')
            
            # Verificar si esta versión ya fue mostrada recientemente (últimos 60 segundos)
            if self._last_shown_version == version:
                # Calcular cuántos segundos quedan del cooldown
                from datetime import datetime
                if self._cooldown_start_time:
                    elapsed = (datetime.now() - self._cooldown_start_time).total_seconds()
                    remaining = max(0, int(self._cooldown_duration - elapsed))
                else:
                    remaining = self._cooldown_duration
                
                logger.info(
                    "UpdateChecker",
                    f"Versión {version} ya fue mostrada recientemente, bloqueando verificación ({remaining}s restantes)"
                )
                # Emitir señal de bloqueo con los segundos realmente restantes
                self.update_check_blocked.emit(remaining)
                return
            
            # Solo verificar versiones ignoradas en modo automático (no manual)
            if not is_manual:
                ignored_version = self.preferences.get_ignored_version()
                if ignored_version and ignored_version == version:
                    logger.info(
                        "UpdateChecker", 
                        f"Versión {version} está siendo ignorada (búsqueda automática)"
                    )
                    # Emitir señal de versión ignorada
                    self.version_ignored_signal.emit(version)
                    return
            else:
                logger.info(
                    "UpdateChecker",
                    f"Búsqueda manual: mostrando actualización aunque esté ignorada"
                )
            
            # Verificar nuevamente si ya hay un diálogo abierto (por si acaso)
            if self.update_dialog and not self.update_dialog.isHidden():
                logger.warning("UpdateChecker", "Diálogo ya visible, no creando duplicado")
                self.update_dialog.raise_()
                self.update_dialog.activateWindow()
                return
            
            logger.info(
                "UpdateChecker", 
                f"Nueva versión disponible: v{version} "
                f"(Build {update_info.get('build', 'N/A')})"
            )
            
            # Emitir señal para que otros componentes actualicen su UI
            self.update_available_signal.emit(update_info)
            
            # Registrar versión que se va a mostrar
            self._last_shown_version = version
            
            # Guardar timestamp de inicio del cooldown
            from datetime import datetime
            self._cooldown_start_time = datetime.now()
            
            self._cooldown_timer.start(self._cooldown_duration * 1000)  # 60 segundos de cooldown
            
            # Mostrar diálogo de actualización
            self.update_dialog = UpdateDialog(update_info, self.parent_view, is_manual_check=is_manual)
            
            # Conectar señal para cuando el usuario marca "ignorar esta versión"
            self.update_dialog.version_ignored.connect(self._on_version_ignored)
            
            self.update_dialog.exec()
            
            # Limpiar referencia al cerrar
            self.update_dialog = None
            
        except Exception as e:
            logger.error("UpdateChecker", f"Error al mostrar diálogo de actualización: {e}")
            self._is_checking = False
    
    def _on_no_update_silent(self):
        """Maneja cuando no hay actualización (modo silencioso)"""
        self._is_checking = False
        self.checking_finished.emit()  # Notificar fin de verificación
        logger.info("UpdateChecker", "No hay actualizaciones disponibles (verificación silenciosa)")
        # Emitir señal de no actualización
        self.no_update_signal.emit()
    
    def _on_no_update_explicit(self):
        """Maneja cuando no hay actualización (modo explícito)"""
        from PySide6.QtWidgets import QMessageBox
        
        self._is_checking = False
        self.checking_finished.emit()  # Notificar fin de verificación
        logger.info("UpdateChecker", "No hay actualizaciones disponibles")
        
        # Emitir señal de no actualización
        self.no_update_signal.emit()
        
        QMessageBox.information(
            self.parent_view,
            tr(I18N.Update.MSG_NO_UPDATE_TITLE),
            tr(I18N.Update.MSG_NO_UPDATE_TEXT)
        )
    
    def _on_check_error(self, error_msg: str):
        """Maneja errores al verificar actualizaciones"""
        self._is_checking = False
        self.checking_finished.emit()  # Notificar fin de verificación
        logger.error("UpdateChecker", f"Error al verificar actualizaciones: {error_msg}")
        
        # Emitir señal de error para que el main presenter lo maneje
        self.check_error_signal.emit(error_msg)
        
        # En modo manual (búsqueda explícita), mostrar mensaje al usuario
        if self._is_manual_check:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self.parent_view,
                tr(I18N.Update.MSG_CHECK_ERROR_TITLE),
                tr(I18N.Update.MSG_CHECK_ERROR_TEXT, error_msg=error_msg)
            )
    
    def _on_version_ignored(self, version: str):
        """Maneja cuando el usuario solicita ignorar una versión"""
        try:
            success = self.preferences.set_ignored_version(version)
            if success:
                logger.info("UpdateChecker", f"Versión {version} será ignorada")
        except Exception as e:
            logger.error("UpdateChecker", f"Error al ignorar versión: {e}")
    
    def _clear_shown_version(self):
        """Limpia el registro de versión mostrada recientemente (después del cooldown)"""
        logger.debug("UpdateChecker", f"Limpiando cooldown de versión {self._last_shown_version}")
        self._last_shown_version = None
        self._cooldown_start_time = None