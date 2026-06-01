import platform
import subprocess
import sys
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication
import threading
import os
from pathlib import Path
from resources.theme import ThemeMode, ThemeColors, ColorRole
from core.utils.path_helper import get_light_style_path, get_dark_style_path, get_qss_file_path
from core.utils.logger import logger
from core.managers.system_type_manager import SystemTypeManager

# Import condicional de winreg (solo Windows)
if sys.platform == 'win32':
    import winreg

class PaletteManager:
    """Clase Singleton para gestionar la configuración de la paleta de colores."""

    _instance = None
    _lock = threading.Lock()

    """Clase para gestionar la configuración de la paleta de colores en función del modo oscuro/claro."""
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PaletteManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa la clase con el sistema de paletas integrado."""
        if self._initialized:   # evita inicializar más de una vez
            return
        
        # Detectar información del sistema
        self.system_version = self._detect_system_version()
        logger.info("ThemeManager", f"Sistema detectado: {self.system_version}")
        
        # Detectar el tema del sistema automáticamente
        self.is_dark_mode = self.detect_dark_mode()
        logger.info("ThemeManager", f"Tema detectado automáticamente: {'Oscuro' if self.is_dark_mode else 'Claro'}")
        
        # Mostrar información de archivos QSS disponibles
        theme_info = self.get_current_theme_info()
        logger.info("ThemeManager", f"QSS disponibles: Light={theme_info['light_qss_available']}, Dark={theme_info['dark_qss_available']}")
        
        self._initialized = True
    
    def _detect_system_version(self):
        """Detecta la versión del sistema operativo de manera multiplataforma."""
        try:
            system = platform.system()
            
            if system == "Darwin":
                # macOS
                mac_ver = platform.mac_ver()[0]
                return f"macOS {mac_ver}" if mac_ver else "macOS"
            
            elif system == "Linux":
                # Linux - leer /etc/os-release (estándar en distros modernas)
                try:
                    with open('/etc/os-release', 'r') as f:
                        os_info = {}
                        for line in f:
                            if '=' in line:
                                key, value = line.strip().split('=', 1)
                                os_info[key] = value.strip('"')
                        name = os_info.get('PRETTY_NAME') or os_info.get('NAME', 'Linux')
                        return name
                except (FileNotFoundError, PermissionError):
                    return f"Linux {platform.release()}"
            
            elif system == "Windows":
                # Windows - usar registro si está disponible
                if sys.platform == 'win32':
                    try:
                        key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as reg_key:
                            current_build, _ = winreg.QueryValueEx(reg_key, "CurrentBuild")
                            build_number = int(current_build)
                            
                            if build_number >= 22000:
                                return "Windows 11"
                            elif build_number >= 10240:
                                return "Windows 10"
                            else:
                                return f"Windows (build {current_build})"
                    except Exception:
                        pass
                
                # Fallback usando platform
                version = platform.version()
                release = platform.release()
                
                if "10.0." in version:
                    version_parts = version.split('.')
                    if len(version_parts) >= 3:
                        try:
                            build = int(version_parts[2])
                            if build >= 22000:
                                return "Windows 11"
                            elif build >= 10240:
                                return "Windows 10"
                        except ValueError:
                            pass
                    return "Windows 10"
                elif release == "8.1":
                    return "Windows 8.1"
                elif release == "8":
                    return "Windows 8"
                elif release == "7":
                    return "Windows 7"
                else:
                    return f"Windows {release}"
            
            return f"{system} {platform.release()}"
                
        except Exception as e:
            logger.warning("ThemeManager", f"Error detectando sistema: {e}")
            return platform.system()
    
    def is_windows_10(self):
        """Retorna True si el sistema es Windows 10."""
        return "Windows 10" in self.system_version
    
    def is_windows_11(self):
        """Retorna True si el sistema es Windows 11."""
        return "Windows 11" in self.system_version
    
    def get_recommended_style_for_system(self):
        """Sugiere el mejor estilo según el sistema operativo."""
        return SystemTypeManager.get_recommended_qt_style()
    
    def detect_dark_mode(self):
        """Detecta si el sistema está en modo oscuro (multiplataforma)."""
        system = platform.system()
        
        try:
            if system == "Windows" and sys.platform == 'win32':
                # Windows: usar registro
                try:
                    key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as reg_key:
                        value, _ = winreg.QueryValueEx(reg_key, "AppsUseLightTheme")    
                        is_dark = value == 0
                        logger.debug("ThemeManager", f"Windows AppsUseLightTheme: {value}, is_dark: {is_dark}")
                        return is_dark
                except FileNotFoundError:
                    logger.warning("ThemeManager", "Clave de registro no encontrada")
                    return False
            
            elif system == "Darwin":
                # macOS: usar defaults read
                try:
                    result = subprocess.run(
                        ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                        capture_output=True, text=True, timeout=5
                    )
                    is_dark = result.stdout.strip().lower() == 'dark'
                    logger.debug("ThemeManager", f"macOS AppleInterfaceStyle: {result.stdout.strip()}, is_dark: {is_dark}")
                    return is_dark
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    return False
                except subprocess.CalledProcessError:
                    # Si falla, probablemente está en modo claro
                    return False
            
            elif system == "Linux":
                # Linux: intentar detectar tema GTK o usar Qt
                try:
                    # Intentar con gsettings (GNOME)
                    result = subprocess.run(
                        ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                        capture_output=True, text=True, timeout=5
                    )
                    is_dark = 'dark' in result.stdout.lower()
                    logger.debug("ThemeManager", f"Linux GNOME color-scheme: {result.stdout.strip()}, is_dark: {is_dark}")
                    return is_dark
                except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                    # Fallback: usar Qt para detectar
                    try:
                        from PySide6.QtGui import QGuiApplication
                        app = QGuiApplication.instance()
                        if app:
                            palette = app.palette()
                            # Si el fondo es más oscuro que el texto, es modo oscuro
                            bg_lightness = palette.color(QPalette.ColorRole.Window).lightness()
                            return bg_lightness < 128
                    except Exception:
                        pass
                    return False
        
        except Exception as e:
            logger.log_exception("ThemeManager", e, "detect_dark_mode")
            return False
        
        return False

    def force_dark_mode(self, force_dark=True):
        """Fuerza el modo oscuro/claro independientemente de la configuración del sistema."""
        self.is_dark_mode = force_dark
        logger.info("ThemeManager", f"Tema forzado a: {'Oscuro' if force_dark else 'Claro'}")

    def refresh_theme(self):
        """Re-detecta el tema del sistema y actualiza la configuración."""
        old_mode = self.is_dark_mode
        self.is_dark_mode = self.detect_dark_mode()
        if old_mode != self.is_dark_mode:
            logger.info("ThemeManager", f"Tema cambiado de {'Oscuro' if old_mode else 'Claro'} a {'Oscuro' if self.is_dark_mode else 'Claro'}")
        return self.is_dark_mode != old_mode  # Retorna True si cambió

    def get_available_styles(self):
        """Devuelve lista de estilos disponibles en el sistema."""
        try:
            from PySide6.QtWidgets import QStyleFactory
            return QStyleFactory.keys()
        except Exception as e:
            logger.error("ThemeManager", f"Error obteniendo estilos disponibles: {e}")
            return []

    def apply_complete_theme(self, app: QApplication, theme_mode=None):
        """
        Aplica el tema completo (paleta + QSS) a la aplicación.
        
        Args:
            app: Instancia de QApplication
            theme_mode: 'light', 'dark', 'auto' o None (usa el actual)
        """
        # Determinar el modo de tema
        if theme_mode == "auto":
            self.is_dark_mode = self.detect_dark_mode()
            logger.info("ThemeManager", f"Modo AUTO detectado: {'Oscuro' if self.is_dark_mode else 'Claro'}")
        elif theme_mode == "light":
            self.is_dark_mode = False
            logger.info("ThemeManager", "Forzando tema claro")
        elif theme_mode == "dark":
            self.is_dark_mode = True
            logger.info("ThemeManager", "Forzando tema oscuro")
        # Si theme_mode es None, usar el modo actual
        
        # Aplicar paleta
        palette = self.load_palette()
        app.setPalette(palette)
        logger.info("ThemeManager", f"Paleta aplicada: {'Oscura' if self.is_dark_mode else 'Clara'}")
        
        # Aplicar QSS
        qss_content = self.load_qss_stylesheet()
        if qss_content:
            app.setStyleSheet(qss_content)
            logger.info("ThemeManager", f"QSS aplicado: {'dark_style.qss' if self.is_dark_mode else 'light_style.qss'}")
        else:
            logger.warning("ThemeManager", "No se pudo cargar el archivo QSS, usando solo la paleta")
        
        logger.info("ThemeManager", f"Tema completo aplicado: {'Oscuro' if self.is_dark_mode else 'Claro'}")
        return True

    def load_qss_stylesheet(self):
        """
        Carga el archivo QSS correspondiente al tema actual.
        
        Returns:
            str: Contenido del archivo QSS o cadena vacía si hay error
        """
        try:
            # Determinar el archivo QSS según el tema usando path helper
            qss_path = get_dark_style_path() if self.is_dark_mode else get_light_style_path()
            
            # Verificar que el archivo existe
            if not qss_path.exists():
                logger.error("ThemeManager", f"Archivo QSS no encontrado: {qss_path}")
                return ""
            
            # Leer el contenido del archivo
            with open(qss_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
                
        except Exception as e:
            logger.error("ThemeManager", f"Error cargando QSS: {e}")
            return ""

    def get_qss_file_path(self):
        """
        Obtiene la ruta del archivo QSS para el tema actual.
        
        Returns:
            Path: Ruta al archivo QSS correspondiente
        """
        return get_dark_style_path() if self.is_dark_mode else get_light_style_path()

    def apply_palette_only(self, app, dark_mode=None):
        """Aplica solo la paleta de colores sin cambiar el estilo del sistema."""
        if dark_mode is not None:
            # Si se especifica un modo, aplicarlo temporalmente
            original_mode = self.is_dark_mode
            self.is_dark_mode = dark_mode
            palette = self.load_palette()
            self.is_dark_mode = original_mode  # Restaurar el modo original
        else:
            # Usar el modo actual
            palette = self.load_palette()
            
        app.setPalette(palette)
        current_mode = dark_mode if dark_mode is not None else self.is_dark_mode
        logger.info("ThemeManager", f"Paleta aplicada: {'Oscura' if current_mode else 'Clara'}, estilo: {app.style().objectName()}")

    def refresh_and_apply_theme(self, app: QApplication):
        """
        Detecta el tema del sistema y aplica el tema completo si cambió.
        
        Args:
            app: Instancia de QApplication
            
        Returns:
            bool: True si el tema cambió y se aplicó
        """
        old_mode = self.is_dark_mode
        self.is_dark_mode = self.detect_dark_mode()
        
        if old_mode != self.is_dark_mode:
            logger.info("ThemeManager", f"Tema del sistema cambió de {'Oscuro' if old_mode else 'Claro'} a {'Oscuro' if self.is_dark_mode else 'Claro'}")
            self.apply_complete_theme(app)
            return True
        return False

    def get_current_theme_info(self):
        """Devuelve información detallada sobre el tema actual."""
        try:
            detected_mode = self.detect_dark_mode()
            light_qss_path = get_light_style_path()
            dark_qss_path = get_dark_style_path()
            current_qss_path = self.get_qss_file_path()
            
            return {
                'detected_dark_mode': detected_mode,
                'current_dark_mode': self.is_dark_mode,
                'is_forced': detected_mode != self.is_dark_mode,
                'theme_name': 'Oscuro' if self.is_dark_mode else 'Claro',
                'system_version': self.system_version,
                'recommended_style': self.get_recommended_style_for_system(),
                'is_windows_10': self.is_windows_10(),
                'is_windows_11': self.is_windows_11(),
                'current_qss_file': current_qss_path.name if current_qss_path else "N/A",
                'light_qss_available': light_qss_path.exists(),
                'dark_qss_available': dark_qss_path.exists(),
                'qss_files_status': {
                    'light_style.qss': light_qss_path.exists(),
                    'dark_style.qss': dark_qss_path.exists()
                }
            }
        except Exception as e:
            logger.error("ThemeManager", f"Error obteniendo info del tema: {e}")
            return {
                'detected_dark_mode': False,
                'current_dark_mode': self.is_dark_mode if hasattr(self, 'is_dark_mode') else False,
                'is_forced': False,
                'theme_name': 'Error',
                'system_version': getattr(self, 'system_version', 'Desconocido'),
                'recommended_style': 'fusion',
                'is_windows_10': False,
                'is_windows_11': False,
                'current_qss_file': 'Error',
                'light_qss_available': False,
                'dark_qss_available': False,
                'qss_files_status': {}
            }
    
    def get_available_theme_modes(self):
        """
        Devuelve los modos de tema disponibles según los archivos QSS existentes.
        
        Returns:
            list: Lista de modos disponibles
        """
        available_modes = ["auto"]  # AUTO siempre está disponible
        
        light_qss = get_light_style_path()
        dark_qss = get_dark_style_path()
        
        if light_qss.exists():
            available_modes.append("light")
        if dark_qss.exists():
            available_modes.append("dark")
            
        return available_modes
    
    def set_theme_mode(self, app: QApplication, theme_mode="auto"):
        """
        Configura y aplica el tema completo de la aplicación.
        
        Args:
            app: Instancia de QApplication
            theme_mode: "light", "dark" o "auto" (por defecto)
        
        Returns:
            bool: True si el tema cambió
        """
        old_mode = self.is_dark_mode
        
        if theme_mode == "auto":
            self.is_dark_mode = self.detect_dark_mode()
            logger.info("ThemeManager", f"Siguiendo tema del sistema: {'Oscuro' if self.is_dark_mode else 'Claro'}")
        elif theme_mode == "light":
            self.is_dark_mode = False
            logger.info("ThemeManager", "Tema establecido manualmente: Claro")
        elif theme_mode == "dark":
            self.is_dark_mode = True
            logger.info("ThemeManager", "Tema establecido manualmente: Oscuro")
        else:
            logger.warning("ThemeManager", f"Modo de tema desconocido: {theme_mode}, usando 'auto'")
            self.is_dark_mode = self.detect_dark_mode()
        
        # Aplicar el tema completo si cambió o si es la primera vez
        theme_changed = old_mode != self.is_dark_mode
        if theme_changed or theme_mode != "auto":
            self.apply_complete_theme(app)
        
        return theme_changed
    
    def toggle_theme(self, app: QApplication):
        """
        Alterna entre modo oscuro y claro, aplicando el tema completo.
        
        Args:
            app: Instancia de QApplication
            
        Returns:
            bool: True (siempre cambia el tema)
        """
        old_mode = self.is_dark_mode
        self.is_dark_mode = not self.is_dark_mode
        logger.info("ThemeManager", f"Tema alternado de {'Oscuro' if old_mode else 'Claro'} a {'Oscuro' if self.is_dark_mode else 'Claro'}")
        
        # Aplicar el tema completo
        self.apply_complete_theme(app)
        return True

    def load_palette(self):
        """Carga la paleta usando el sistema integrado de colores desde domain."""
        theme_mode = ThemeMode.DARK if self.is_dark_mode else ThemeMode.LIGHT
        logger.debug("ThemeManager", f"is_dark_mode: {self.is_dark_mode}, cargando paleta {theme_mode.value}")
        
        try:
            # Crear paleta usando lógica de negocio en el manager
            palette = self._create_qpalette_from_theme(theme_mode)
            return palette
        except Exception as e:
            logger.error("ThemeManager", f"Error al cargar la paleta: {e}")
            return QPalette()

    def _create_qpalette_from_theme(self, theme_mode: ThemeMode) -> QPalette:
        """
        Crea una QPalette basada en el modo de tema (lógica de negocio)
        
        Args:
            theme_mode: Modo de tema deseado
            
        Returns:
            QPalette configurada
        """
        palette = QPalette()
        
        # Lógica de selección de colores (movida desde domain)
        normal_colors, disabled_colors = self._get_colors_for_theme(theme_mode)
        
        # Mapeo de ColorRole del domain a QPalette.ColorRole (lógica de infraestructura)
        qt_color_role_mapping = ThemeColors.QT_COLOR_ROLE_MAPPING
        
        # Aplicar colores normales (lógica de negocio)
        for color_role, color_value in normal_colors.items():
            qt_role = qt_color_role_mapping.get(color_role)
            if qt_role:
                palette.setColor(QPalette.ColorGroup.Active, qt_role, QColor(color_value))
                palette.setColor(QPalette.ColorGroup.Inactive, qt_role, QColor(color_value))
        
        # Aplicar colores disabled (lógica de negocio)
        for color_role, color_value in disabled_colors.items():
            qt_role = qt_color_role_mapping.get(color_role)
            if qt_role:
                palette.setColor(QPalette.ColorGroup.Disabled, qt_role, QColor(color_value))
        
        return palette
    
    def _get_colors_for_theme(self, theme_mode: ThemeMode):
        """
        Obtiene los colores para un modo de tema específico (lógica de negocio)
        
        Args:
            theme_mode: Modo de tema (LIGHT, DARK o AUTO)
            
        Returns:
            tuple: (colores_normales, colores_disabled)
        """
        if theme_mode == ThemeMode.DARK:
            return ThemeColors.DARK_THEME, ThemeColors.DARK_THEME_DISABLED
        elif theme_mode == ThemeMode.AUTO:
            # Lógica adicional: AUTO sigue la detección del sistema
            system_dark = self.detect_dark_mode()
            if system_dark:
                return ThemeColors.DARK_THEME, ThemeColors.DARK_THEME_DISABLED
            else:
                return ThemeColors.LIGHT_THEME, ThemeColors.LIGHT_THEME_DISABLED
        else:  # LIGHT
            return ThemeColors.LIGHT_THEME, ThemeColors.LIGHT_THEME_DISABLED
        
