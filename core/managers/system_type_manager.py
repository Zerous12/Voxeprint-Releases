import platform
import sys
from pathlib import Path
from typing import Optional


class SystemTypeManager:
    """
    Centraliza la detección del sistema operativo y provee utilidades
    multiplataforma (ruta de icono, estilo Qt, DPI, directorio de datos, etc.)
    """

    @staticmethod
    def current_os() -> str:
        """Retorna 'Windows', 'Linux' o 'Darwin' (macOS)"""
        return platform.system()

    @staticmethod
    def is_windows() -> bool:
        return SystemTypeManager.current_os() == "Windows"

    @staticmethod
    def is_linux() -> bool:
        return SystemTypeManager.current_os() == "Linux"

    @staticmethod
    def is_macos() -> bool:
        return SystemTypeManager.current_os() == "Darwin"

    @staticmethod
    def get_os_display_name() -> str:
        """Retorna un nombre legible del SO (ej: 'Windows 11', 'Ubuntu 24.04', 'macOS 14.5')"""
        system = SystemTypeManager.current_os()
        if system == "Windows":
            return SystemTypeManager._windows_display_name()
        elif system == "Darwin":
            mac_ver = platform.mac_ver()[0]
            return f"macOS {mac_ver}" if mac_ver else "macOS"
        elif system == "Linux":
            try:
                with open('/etc/os-release', 'r') as f:
                    info = {}
                    for line in f:
                        if '=' in line:
                            k, v = line.strip().split('=', 1)
                            info[k] = v.strip('"')
                    return info.get('PRETTY_NAME') or info.get('NAME', 'Linux')
            except Exception:
                return f"Linux {platform.release()}"
        return system

    @staticmethod
    def _windows_display_name() -> str:
        """Detecta la versión de Windows"""
        try:
            if sys.platform == 'win32':
                import winreg
                key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as reg_key:
                    build = int(winreg.QueryValueEx(reg_key, "CurrentBuild")[0])
                    if build >= 22000:
                        return "Windows 11"
                    elif build >= 10240:
                        return "Windows 10"
        except Exception:
            pass
        release = platform.release()
        return f"Windows {release}" if release else "Windows"

    @staticmethod
    def is_windows_10() -> bool:
        """Retorna True si el sistema es Windows 10"""
        return "Windows 10" in SystemTypeManager.get_os_display_name()

    @staticmethod
    def is_windows_11() -> bool:
        """Retorna True si el sistema es Windows 11"""
        return "Windows 11" in SystemTypeManager.get_os_display_name()

    @staticmethod
    def get_icon_filename() -> str:
        """
        Retorna el nombre del archivo de icono según la plataforma:
        - Windows: icon.ico
        - Linux/macOS: icon.png
        """
        if SystemTypeManager.is_windows():
            return "icon.ico"
        return "icon.png"

    @staticmethod
    def get_icon_path(exe_dir: Path) -> Path:
        """Retorna la ruta completa al archivo de icono"""
        return exe_dir / SystemTypeManager.get_icon_filename()

    @staticmethod
    def get_font_dpi_env() -> Optional[str]:
        """
        Retorna el valor para QT_FONT_DPI según la plataforma.
        Solo Windows necesita override de DPI.
        """
        if SystemTypeManager.is_windows():
            return "108"
        return None

    @staticmethod
    def get_recommended_qt_style() -> str:
        """
        Sugiere el mejor estilo Qt según el sistema operativo.
        - Windows 10/11 → 'windows11'
        - macOS → 'macos' (estilo nativo)
        - Linux → detecta GTK nativo si está disponible, sino 'fusion'
        """
        system = SystemTypeManager.current_os()
        if system == "Windows":
            if SystemTypeManager.is_windows_11() or SystemTypeManager.is_windows_10():
                return "windows11"
            return "fusion"
        elif system == "Darwin":
            return "macos"
        else:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app is not None:
                native = app.style().name()
                if native not in ("windows", "windows11", "windowsvista"):
                    return native
            return "fusion"

    @staticmethod
    def get_recommended_data_dir(dir_name: str) -> Path:
        """
        Retorna el directorio de datos recomendado según la plataforma:
        - Windows: ~/Documents/{dir_name}
        - macOS: ~/Library/Application Support/{dir_name}
        - Linux: $XDG_DATA_HOME/{dir_name} o ~/.local/share/{dir_name}
        """
        system = SystemTypeManager.current_os()
        if system == "Windows":
            return Path.home() / "Documents" / dir_name
        elif system == "Darwin":
            return Path.home() / "Library" / "Application Support" / dir_name
        else:
            xdg = __import__('os').environ.get("XDG_DATA_HOME", "")
            if xdg:
                return Path(xdg) / dir_name
            return Path.home() / ".local" / "share" / dir_name

    @staticmethod
    def should_disable_qtwebengine_sandbox() -> bool:
        """En Linux/macOS se deshabilita el sandbox de QtWebEngine si no está disponible"""
        return not SystemTypeManager.is_windows()

    @staticmethod
    def get_qtwebengine_env_vars(frozen: bool = False, meipass: str = None) -> dict:
        """
        Retorna un dict con variables de entorno necesarias para QtWebEngine
        según la plataforma y el estado de empaquetado.
        """
        env = {}
        if not SystemTypeManager.is_windows():
            env["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
            env["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"
        if frozen and meipass:
            qe_res = Path(meipass) / "PySide6" / "Qt" / "resources"
            if qe_res.is_dir():
                env["QTWEBENGINE_RESOURCES_PATH"] = str(qe_res)
            qe_locales = Path(meipass) / "PySide6" / "Qt" / "translations" / "qtwebengine_locales"
            if qe_locales.is_dir():
                env["QTWEBENGINE_LOCALES_PATH"] = str(qe_locales)
        return env

    @staticmethod
    def check_windows_compatibility() -> tuple:
        """
        Verifica compatibilidad de Windows.
        Returns: (es_compatible, mensaje_error)
        """
        if not SystemTypeManager.is_windows():
            return True, None
        try:
            release = platform.release()
            if release == "7":
                return False, "WIN7"
            if release in ["Vista", "XP", "2000", "NT"]:
                return False, "WIN_LEGACY"
        except Exception:
            pass
        return True, None

    @staticmethod
    def check_macos_compatibility() -> tuple:
        """
        Verifica compatibilidad de macOS (mínimo 10.14).
        Returns: (es_compatible, mensaje_error, version_str)
        """
        if not SystemTypeManager.is_macos():
            return True, None, None
        try:
            mac_ver = platform.mac_ver()[0]
            if mac_ver:
                parts = mac_ver.split('.')
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
                if major == 10 and minor < 14:
                    return False, "MACOS", mac_ver
        except Exception:
            pass
        return True, None, None
