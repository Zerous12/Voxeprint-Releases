from pathlib import Path
import sys
# Carpeta base: C:/Users/<usuario>/Documents/Voxeprint3D
BASE_DIR = Path.home() / "Documents" / "Voxeprint3D"

def database_path(db_name: str = None) -> Path:
    """Ruta al archivo de base de datos en Documents/Voxeprint3D/Database/voxeprint_x.x.db"""
    db_dir = BASE_DIR / "Database"
    db_dir.mkdir(parents=True, exist_ok=True)
    if db_name is None:
        from config.app_config import APP_CONFIG
        db_name = APP_CONFIG.database.name
    return db_dir / db_name

def pdfs_dir() -> Path:
    """Carpeta para PDFs en Documents/Voxeprint3D/PDF"""
    d = BASE_DIR / "PDF"
    d.mkdir(parents=True, exist_ok=True)
    return d

def logs_dir() -> Path:
    """Carpeta para logs en Documents/Voxeprint3D/Logs"""
    d = BASE_DIR / "Logs"
    d.mkdir(parents=True, exist_ok=True)
    return d

def backups_dir() -> Path:
    """Carpeta para respaldos en Documents/Voxeprint3D/Backups"""
    d = BASE_DIR / "Backups"
    d.mkdir(parents=True, exist_ok=True)
    return d

def logos_dir() -> Path:
    """Carpeta para logos en Documents/Voxeprint3D/Logos"""
    d = BASE_DIR / "Logos"
    d.mkdir(parents=True, exist_ok=True)
    return d

def config_dir() -> Path:
    """Carpeta para la configuración en Documents/Voxeprint3D/Config"""
    d = BASE_DIR / "Config"
    d.mkdir(parents=True, exist_ok=True)
    return d

def app_root() -> Path:
    """Devuelve la raíz del proyecto o del ejecutable"""
    if getattr(sys, 'frozen', False):
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