from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTranslator, QLibraryInfo, QStandardPaths, QCoreApplication, Qt
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtCore import QUrl
import sys
import platform
from pathlib import Path
import traceback
import os
import tempfile
import faulthandler

# Import condicional para bloqueo de archivos (multiplataforma)
if sys.platform == 'win32':
    import msvcrt
else:
    import fcntl

from config.build_config import BUILD_CONFIG
from core.managers.theme_manager import PaletteManager
from core.managers.app_preferences_manager import AppPreferencesManager
from core.managers.system_type_manager import SystemTypeManager
from core.utils.path_helper import logs_dir
from core.utils.logger import logger
from core.managers.language_manager import LanguageManager
from core.managers.locale_manager import LocaleManager
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from presentation.modules.intro.presenters.intro_presenter import IntroPresenter
from presentation.modules.resources_rc import *

def _exe_dir() -> Path:
    return Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent

ICON_PATH = SystemTypeManager.get_icon_path(_exe_dir())


def _show_fatal_error_dialog(title: str, message: str, log_dir=None) -> None:
    """Muestra un diálogo de error crítico con botón 'Ver Logs' y botón 'Cerrar'."""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setWindowFlags(msg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

    btn_logs = None
    if log_dir is not None:
        btn_logs = msg.addButton(tr(I18N.Errors.BTN_VIEW_LOGS), QMessageBox.ButtonRole.ActionRole)
    btn_close = msg.addButton(tr(I18N.Dialogs.CLOSE), QMessageBox.ButtonRole.RejectRole)
    msg.setDefaultButton(btn_close)
    msg.exec()

    if btn_logs is not None and msg.clickedButton() == btn_logs:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_dir)))

def excepthook(exc_type, exc, tb):
    """
    Manejador global de excepciones no capturadas
    Usa el sistema de logging centralizado para registrar errores críticos
    """
    try:
        # Crear excepción para el logging
        exception = exc_type(str(exc))
        exception.__traceback__ = tb
        
        # Registrar el error usando el sistema de logging centralizado
        logger.error("GlobalExceptionHandler", f"Excepción no capturada: {exc_type.__name__}: {str(exc)}")
        logger.log_exception("GlobalExceptionHandler", exception, "excepthook global")
        
        # Obtener la ruta del archivo de log para mostrar al usuario
        from datetime import datetime
        log_file = logger.log_dir / f"voxeprint_{datetime.now().strftime('%Y%m')}.log"
        
        # Mostrar mensaje de error al usuario (simplificado, sin detalles técnicos)
        try:
            _show_fatal_error_dialog(
                tr(I18N.Errors.FATAL_TITLE),
                tr(I18N.Errors.FATAL_MSG, path=str(log_file)),
                log_dir=log_file.parent
            )
        except Exception:
            # Si Qt no está disponible, solo imprimir (ya está en consola arriba)
            pass
            
    except Exception as logging_error:  
        log_file = logs_dir() / "error.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"LOGGING SYSTEM ERROR: {logging_error}\n")
            f.write("ORIGINAL ERROR:\n")
            f.write("".join(traceback.format_exception(exc_type, exc, tb)) + "\n")
        
        try:
            _show_fatal_error_dialog(
                tr(I18N.Errors.FATAL_TITLE),
                tr(I18N.Errors.FATAL_MSG_FALLBACK, path=str(log_file)),
                log_dir=log_file.parent
            )
        except Exception:
            pass

    sys.exit(1)
#////////////////////////////////////////////////////////////////////////////////////////////////////////
sys.excepthook = excepthook
font_dpi = SystemTypeManager.get_font_dpi_env()
if font_dpi is not None:
    os.environ["QT_FONT_DPI"] = font_dpi

# QtWebEngine: configurar variables de entorno según plataforma y empaquetado
for key, value in SystemTypeManager.get_qtwebengine_env_vars(
    frozen=getattr(sys, 'frozen', False),
    meipass=getattr(sys, '_MEIPASS', None)
).items():
    os.environ.setdefault(key, value)
# Obligatorio para QtWebEngine: compartir contextos OpenGL antes de crear QApplication
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
#////////////////////////////////////////////////////////////////////////////////////////////////////////


def check_system_compatibility():
    """
    Verifica que el sistema operativo sea compatible con la aplicación.
    Requisitos mínimos:
    - Windows 8 o superior
    - macOS 10.14 (Mojave) o superior
    - Linux: cualquier versión moderna con Qt6 support

    Returns:
        tuple: (es_compatible, mensaje_error)
    """
    if SystemTypeManager.is_windows():
        ok, key = SystemTypeManager.check_windows_compatibility()
        if not ok:
            if key == "WIN_LEGACY":
                return False, tr(I18N.SystemCheck.WIN_LEGACY, release=platform.release())
            return False, tr(getattr(I18N.SystemCheck, key))

    elif SystemTypeManager.is_macos():
        ok, key, ver = SystemTypeManager.check_macos_compatibility()
        if not ok:
            return False, tr(I18N.SystemCheck.MACOS, version=ver)

    return True, None


class AppSentinel:
    """Singleton para evitar múltiples instancias de la aplicación (multiplataforma)"""
    
    def __init__(self, lockfile_name='voxeprint_app.lock'):
        self.lockfile_path = os.path.join(tempfile.gettempdir(), lockfile_name)
        self.filepath = None
        self._released = False
    
    def acquire(self):
        try:
            self.filepath = open(self.lockfile_path, 'w')
            
            if sys.platform == 'win32':
                msvcrt.locking(self.filepath.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(self.filepath.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                
        except (OSError, IOError):
            app = QApplication.instance() or QApplication([])
            QMessageBox.warning(None, tr(I18N.Dialogs.ERROR_TITLE), tr(I18N.SystemCheck.APP_RUNNING))
            sys.exit(1)

    def release(self):
        if self._released or not self.filepath:
            return
        self._released = True
        try:
            if sys.platform != 'win32':
                try:
                    fcntl.flock(self.filepath.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
            self.filepath.close()
            if os.path.exists(self.lockfile_path):
                os.remove(self.lockfile_path)
        except Exception as e:
            logger.log_exception("AppSentinel", e, "release")

class App():
    def __init__(self):
        # Habilitar faulthandler para capturar crashes nativos de C++/PySide6
        try:
            _fh_path = Path(tempfile.gettempdir()) / "voxeprint_crash.log"
            self._faulthandler_file = open(_fh_path, "w", encoding="utf-8")
            faulthandler.enable(file=self._faulthandler_file)
        except Exception:
            pass

        # --- Lógica singleton: archivo de bloqueo ---
        self.applock = AppSentinel()
        self.applock.acquire()
        self.app = QApplication([]) # Inicializa la aplicación Qt  
        
        # Inicializar managers
        self.preferences_manager = AppPreferencesManager()
        self.palette_manager = PaletteManager()
        
        # Configurar estilo del sistema
        self.app.setStyle(self.palette_manager.get_recommended_style_for_system())
        
        # Aplicar tema basado en preferencias del usuario
        self._initialize_theme()
        
        # Guardar referencias para acceso posterior
        self.app.palette_manager = self.palette_manager
        self.app.preferences_manager = self.preferences_manager
              
        # Inicializar managers de i18n/l10n
        self.language_manager = LanguageManager()
        self.locale_manager = LocaleManager()
        self.app.language_manager = self.language_manager
        
        # Leer preferencias de idioma y locale (o usar defaults)
        saved_language = self.preferences_manager.get_preference("appearance", "language", "es")
        saved_locale = self.preferences_manager.get_preference("appearance", "locale", "PY")
        
        # Cargar idioma y locale
        if not self.language_manager.load_language(saved_language):
            # Fallback si el idioma no está disponible
            self.language_manager.load_language("es")
        if not self.locale_manager.load_locale(saved_locale):
            self.locale_manager.load_locale("PY")
        
        # Configurar traductor Qt nativo (para botones de diálogos nativos, etc.)
        translator = QTranslator(self.app) # Crea una instancia del traductor       
        qt_translations = QLibraryInfo.path(QLibraryInfo.TranslationsPath) # Obtenemos el directorio de traducciones
        translator.load(f"qtbase_{self.language_manager.current_language()}", qt_translations) # Cargamos la traducción correspondiente  
        self.app.installTranslator(translator) # Instalamos el traductor en la aplicación
        
        # Configurar icono        
        app_icon = QIcon(str(ICON_PATH))
        self.app.setWindowIcon(app_icon)
        
        # Variables para las ventanas
        self.intro_presenter = None
        self.main_presenter = None
        
        # Inicializar splash screen      
        self.intro_presenter = IntroPresenter()  # Crea una instancia del presenter de introducción
        self.intro_presenter.intro_finished.connect(self.launch_main_panel)
        self.intro_presenter.show()  # Muestra el splash screen a través del presenter         
        
    def _initialize_theme(self):
        """Inicializa el tema basado en las preferencias del usuario"""
        try:
            # Intentar cargar tema desde preferencias
            user_theme = self.preferences_manager.get_theme()
            logger.debug("ThemeManager", f"Tema configurado en preferencias: {user_theme}")
            
            # Validar que el tema configurado sea válido
            valid_themes = ["auto", "light", "dark"]
            if user_theme not in valid_themes:
                logger.warning("ThemeManager", f"Tema inválido '{user_theme}', usando 'dark' por defecto")
                user_theme = "dark"
                # Guardar el tema corregido en preferencias
                self.preferences_manager.set_theme("dark")
                self.preferences_manager.save_preferences()
            
            # Aplicar el tema configurado
            self.palette_manager.set_theme_mode(self.app, user_theme)
            logger.debug("ThemeManager", f"Tema aplicado correctamente: {user_theme}")
            
        except Exception as e:
            logger.error("ThemeManager", f"Error cargando tema desde preferencias: {str(e)}")
            logger.warning("ThemeManager", "Aplicando tema oscuro por defecto como fallback")
            
            try:
                # Si hay error cargando preferencias, usar tema oscuro por defecto
                self.palette_manager.force_dark_mode(True)
                self.palette_manager.apply_complete_theme(self.app)
                
                # Intentar guardar tema por defecto en preferencias
                self.preferences_manager.set_theme("dark")
                self.preferences_manager.save_preferences()
                logger.info("ThemeManager", "Tema oscuro aplicado como fallback exitosamente")
                
            except Exception as fallback_error:
                logger.error("ThemeManager", f"Error crítico aplicando tema por defecto: {str(fallback_error)}")
                logger.log_exception("ThemeManager", fallback_error, "_initialize_theme fallback")
                # En caso extremo, continuar sin tema personalizado         
        
    def launch_main_panel(self):
        """Lanza el panel principal con arquitectura MVP"""
        # Cerrar splash screen PRIMERO, antes de cualquier operación que pueda fallar
        if self.intro_presenter:
            self.intro_presenter.close()
            self.intro_presenter = None

        try:
            # Import diferido para que la carga pesada ocurra durante el splash
            from presentation.modules.main.presenters.main_presenter import MainPresenter

            # Crear presenter con la vista
            self.main_presenter = MainPresenter(parent=self)
            # Mostrar ventana principal
            self.main_presenter.run()

        except Exception as e:
            logger.error("App", f"Error crítico al lanzar panel principal: {str(e)}")
            logger.log_exception("App", e, "launch_main_panel")
            # Asegurar cierre del intro por si acaso (doble seguridad)
            if self.intro_presenter:
                self.intro_presenter.close()
                self.intro_presenter = None
            _show_fatal_error_dialog(
                tr(I18N.Intro.ERROR_TITLE),
                tr(I18N.Intro.ERROR_TEXT),
                log_dir=logs_dir()
            )
            self.app.quit()    

    def apply_theme_from_preferences(self):
        """
        Aplica el tema basado en las preferencias actuales.
        Útil para refrescar el tema después de cambios.
        """
        try:
            self._initialize_theme()
            return True
        except Exception as e:
            logger.error("ThemeManager", f"Error aplicando tema desde preferencias: {str(e)}")
            logger.log_exception("ThemeManager", e, "apply_theme_from_preferences")
            return False
    
    def get_current_theme_info(self) -> dict:
        """
        Obtiene información completa del tema actual.
        
        Returns:
            dict: Información del tema actual
        """
        try:
            theme_info = {
                'user_preference': self.preferences_manager.get_theme(),
                'system_dark_mode': self.palette_manager.detect_dark_mode(),
                'current_dark_mode': self.palette_manager.is_dark_mode,
                'available_modes': self.palette_manager.get_available_theme_modes(),
                'qss_info': self.palette_manager.get_current_theme_info()
            }
            logger.debug("ThemeManager", "Información del tema obtenida correctamente", **theme_info)
            return theme_info
        except Exception as e:
            logger.error("ThemeManager", f"Error obteniendo información del tema: {str(e)}")
            logger.log_exception("ThemeManager", e, "get_current_theme_info")
            return {}

    def run(self):
        try:
            exit_code = self.app.exec()
            sys.exit(exit_code)
        except SystemExit:
            pass
        except Exception as e:
            logger.error("App", f"Error en ejecución principal: {str(e)}")
            logger.log_exception("App", e, "run")
        finally:
            self.applock.release()

    
#////////////////////////////////////////////////Main/////////////////////////////////////////////////////
def _run():
    # Cargar idioma por defecto para que tr() funcione en check_system_compatibility
    lang_mgr = LanguageManager()
    lang_mgr.load_language("es")
    
    # Verificar compatibilidad del sistema ANTES de crear la aplicación
    is_compatible, error_message = check_system_compatibility()
    
    if not is_compatible:
        temp_app = QApplication([])
        
        msg = QMessageBox()
        msg.setWindowTitle(tr(I18N.SystemCheck.TITLE_UNSUPPORTED))
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(f"<b>{tr(I18N.SystemCheck.HEADER_UNSUPPORTED)}</b>")
        msg.setInformativeText(error_message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1e1e2e;
            }
            QMessageBox QLabel {
                color: #cdd6f4;
                font-size: 13px;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                padding: 8px 24px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)
        msg.exec()
        sys.exit(1)
    
    # Configuración usando build_config.py
    QCoreApplication.setOrganizationName(BUILD_CONFIG.app.organization)
    QCoreApplication.setApplicationName(BUILD_CONFIG.app.name)
    QCoreApplication.setApplicationVersion(BUILD_CONFIG.get_full_version())
    application = App()
    application.run()

if __name__ == "__main__":
    try:
        _run()
    except Exception:
        # Cualquier excepción que se escape del run cae aquí
        excepthook(*sys.exc_info())
    
#////////////////////////////////////////////////////////////////////////////////////////////////////////
# Desarrollo de la calculadora de impresiones 3d - Voxeprint:
#   - Desarrollador principal: Richard Mequert (Alias: Zerous)
#
# Detalles adicionales:
#   - Voxeprint es un software de generación de presupuestos para impresiones 3D.
#   - Permite a los usuarios calcular costos y materiales necesarios para sus proyectos de impresión.
#   - Facilita la creación de informes detallados sobre los costos de impresión y los recursos requeridos.
#   - Este comentario proporciona una descripción general de la aplicación y su contexto de desarrollo.
#////////////////////////////////////////////////////////////////////////////////////////////////////////
