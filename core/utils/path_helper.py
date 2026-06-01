import os
import platform
import sys
import logging
from pathlib import Path

from config.build_config import DATA_DIR_NAME

_LEGACY_DIR_NAMES = ["Voxeprint3D", "voxeprint3d"]


def _migrate_legacy_dir(new_dir: Path) -> None:
    """Renombra un directorio legacy a new_dir si existe y new_dir no."""
    for legacy_name in _LEGACY_DIR_NAMES:
        legacy_dir = new_dir.parent / legacy_name
        if legacy_dir.exists() and not new_dir.exists():
            try:
                legacy_dir.rename(new_dir)
                logging.getLogger("PathHelper").info(
                    "Directorio migrado: %s -> %s", legacy_dir, new_dir
                )
            except Exception as e:
                logging.getLogger("PathHelper").warning(
                    "Error migrando %s: %s", legacy_dir, e
                )


def _get_base_dir() -> Path:
    """
    Determina el directorio base de datos de usuario según la plataforma.

    El nombre del directorio se obtiene de ``BUILD_CONFIG.app.data_dir_name``
    (fuente única de verdad). Usuarios Windows con el directorio legacy
    ``Voxeprint3D`` se migran automáticamente al nuevo nombre.
    """
    system = platform.system()
    dir_name = DATA_DIR_NAME

    if system in ("Windows", "Darwin"):
        base = Path.home() / "Documents" / dir_name
        if system == "Windows":
            _migrate_legacy_dir(base)
        return base

    # Linux
    documents_path = Path.home() / "Documents" / dir_name
    if documents_path.exists():
        return documents_path

    xdg_data_home = os.environ.get("XDG_DATA_HOME", "")
    if xdg_data_home:
        return Path(xdg_data_home) / dir_name
    return Path.home() / ".local" / "share" / dir_name


BASE_DIR = _get_base_dir()

def database_path(db_name: str = None) -> Path:
    """Ruta al archivo de base de datos en BASE_DIR/Database/voxeprint_x.x.db"""
    db_dir = BASE_DIR / "Database"
    db_dir.mkdir(parents=True, exist_ok=True)
    if db_name is None:
        from config.app_config import APP_CONFIG
        db_name = APP_CONFIG.database.name
    return db_dir / db_name

def pdfs_dir() -> Path:
    """Carpeta para PDFs en BASE_DIR/PDF"""
    d = BASE_DIR / "PDF"
    d.mkdir(parents=True, exist_ok=True)
    return d

def logs_dir() -> Path:
    """Carpeta para logs en BASE_DIR/Logs"""
    d = BASE_DIR / "Logs"
    d.mkdir(parents=True, exist_ok=True)
    return d

def backups_dir() -> Path:
    """Carpeta para respaldos en BASE_DIR/Backups"""
    d = BASE_DIR / "Backups"
    d.mkdir(parents=True, exist_ok=True)
    return d

def logos_dir() -> Path:
    """Carpeta para logos en BASE_DIR/Logos"""
    d = BASE_DIR / "Logos"
    d.mkdir(parents=True, exist_ok=True)
    return d

def config_dir() -> Path:
    """Carpeta para la configuración en BASE_DIR/Config"""
    d = BASE_DIR / "Config"
    d.mkdir(parents=True, exist_ok=True)
    return d

def app_root() -> Path:
    """Devuelve la raíz del proyecto o del ejecutable"""
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent.parent.parent

def app_lib_root() -> Path:
    """Devuelve la raíz de los módulos (lib/ en cx_Freeze, raíz en desarrollo)"""
    if getattr(sys, 'frozen', False):
        # cx_Freeze: los módulos están en lib/
        exe_dir = Path(sys.executable).parent
        lib_dir = exe_dir / "lib"
        if lib_dir.exists():
            return lib_dir
        return exe_dir
    else:
        return Path(__file__).resolve().parent.parent.parent

def styles_dir() -> Path:
    """Carpeta para estilos QSS en la aplicación"""
    return app_root() / "resources" / "style"

def get_qss_file_path(filename: str) -> Path:
    """Devuelve la ruta al archivo QSS especificado"""
    return styles_dir() / filename

def get_light_style_path() -> Path:
    """Ruta al archivo de estilo claro"""
    return get_qss_file_path("light_style.qss")

def get_dark_style_path() -> Path:
    """Ruta al archivo de estilo oscuro"""
    return get_qss_file_path("dark_style.qss")

def build_resource_path(relative_path: str) -> str:
    """Devuelve la ruta absoluta a partir de la raíz y una ruta relativa"""
    return str(app_root() / relative_path)

def get_user_start_dir() -> str:
    """Devuelve el directorio inicial para diálogos de archivo.

    Prioridad: Descargas → Escritorio → Home.
    Compatible con Windows y Linux.
    """
    home = Path.home()
    for candidate in (home / "Downloads", home / "Descargas", home / "Desktop", home / "Escritorio", home):
        if candidate.exists():
            return str(candidate)
    return str(home)