"""
Parámetros de construcción y versión de Voxeprint.
Centraliza información de builds, releases y metadatos del proyecto.
"""

import platform
from dataclasses import dataclass
from typing import Optional
import datetime

# Importar DatabaseParameters desde app_config para centralización
from config.app_config import DatabaseParameters


@dataclass(frozen=True)
class ApplicationParameters:
    """Parámetros básicos de la aplicación"""
    name: str = "Voxeprint"
    data_dir_name: str = "voxeprint"
    display_name: str = "Voxeprint - Tu Asistente generador de Cotizaciones"
    description: str = "Calculadora profesional para impresión 3D"
    version: str = "1.2.8"
    build_number: int = 136
    release_date: str = "2026.05.31"
    
    # Información del desarrollador/organización
    author: str = "Richard Mequert"
    organization: str = "ZeroLab"
    contact_email: str = "Zerous_12@hotmail.com"
    github_profile: str = "https://github.com/Zerous12"
    
    # Licencia y copyright
    license: str = "VoxePrint Community License (VCL) 1.0"
    license_short: str = "Source-available · Free for community use"
    copyright: str = f"© 2025–2026 Richard Mequert — VoxePrint"


@dataclass(frozen=True)
class TeamParameters:
    """Información del equipo de desarrollo"""
    # Lista de desarrolladores (expandible)
    developers: tuple = ("• Richard Mequert",)
    
    # Lista de diseñadores (expandible)
    designers: tuple = ("• Richard Mequert",)
    
    # Lista de testers (expandible)
    testers: tuple = ("• Paolo Olmedo",
                      "• Ivan Sekatcheff",)
    
    # Características principales del software
    features: tuple = (
        "• Automatic cost calculation",
        "• Customer management",
        "• Inventory management",
        "• PDF generation",
        "• Multi-currency system",
        "• Modern and intuitive interface",
    )
    
    # Stack tecnológico
    technologies: tuple = (
        "Python • PySide6 • SQLite",
        "ReportLab • PDF.js • Qt"
    )
    
    # Agradecimientos
    acknowledgments: tuple = (
        "Qt Foundation",
        "Python Software Foundation", 
        "Comunidad OpenSource",
        "Usuarios de Voxeprint"
    )


# Nota: DatabaseParameters ahora se importa desde app_config.py
# para mantener toda la configuración de la aplicación centralizada


@dataclass(frozen=True)
class BuildParameters:
    """Parámetros de construcción y compilación"""
    python_version: str = "3.11+"
    qt_framework: str = "PySide6"
    build_type: str = "Release"  # Debug, Release, Beta, Alpha
    target_platform: str = "Windows"  # Windows, Linux, macOS
    architecture: str = "x64"  # x86, x64, arm64
    
    # Configuraciones de compilación
    include_debug_info: bool = False
    enable_console: bool = False  # Para builds en Windows
    compression_enabled: bool = True
    obfuscate_code: bool = False
    
    # Información de build
    build_date: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    build_machine: str = "Build Server"
    compiler: str = "cx_Freeze 6.14+"
    
    # Dependencias principales
    dependencies: dict = None
    
    def __post_init__(self):
        if self.dependencies is None:
            object.__setattr__(self, 'dependencies', {
                "PySide6": "6.5+",               
                "SQLite": "3.40+",
                "Python": self.python_version
            })


@dataclass(frozen=True)
class ReleaseParameters:
    """Parámetros de release y distribución"""
    channel: str = "stable"  # stable, beta, alpha, dev
    distribution_type: str = "standalone"  # standalone, installer, portable
    auto_update_enabled: bool = True
    update_check_interval: int = 24  # horas
    
    # URLs de distribución (Repo público para releases)
    download_url: str = "https://github.com/Zerous12/Voxeprint---3DPrint-Quote-Generator/releases"
    update_server: str = "https://api.github.com/repos/Zerous12/Voxeprint---3DPrint-Quote-Generator/releases"
    documentation_url: str = "https://github.com/Zerous12/Voxeprint---3DPrint-Quote-Generator"
    
    # Configuración de telemetría
    telemetry_enabled: bool = False
    crash_reporting_enabled: bool = True


class BuildConfig:
    """
    Gestor principal de configuración de construcción.
    Proporciona acceso centralizado a toda la configuración de build.
    """
    
    def __init__(self):
        self._app = ApplicationParameters()
        self._team = TeamParameters()
        self._database = DatabaseParameters()
        self._build = BuildParameters()
        object.__setattr__(self._build, 'target_platform', platform.system())
        self._release = ReleaseParameters()
    
    @property
    def app(self) -> ApplicationParameters:
        """Parámetros de la aplicación"""
        return self._app
    
    @property
    def team(self) -> TeamParameters:
        """Información del equipo"""
        return self._team
    
    @property
    def database(self) -> DatabaseParameters:
        """Parámetros de la base de datos"""
        return self._database
    
    @property
    def build(self) -> BuildParameters:
        """Parámetros de construcción"""
        return self._build
    
    @property
    def release(self) -> ReleaseParameters:
        """Parámetros de release"""
        return self._release
    
    def get_full_version(self) -> str:
        """Retorna versión completa con build number"""
        return f"{self.app.version}.{self.app.build_number}"
    
    def get_build_identifier(self) -> str:
        """Retorna identificador único del build"""
        return f"{self.get_full_version()}-{self.build.build_type.lower()}-{self.build.architecture}"
    
    def get_version_info(self) -> dict:
        """Retorna información completa de versión y build"""
        return {
            "app_version": self.app.version,
            "build_number": self.app.build_number,
            "full_version": self.get_full_version(),
            "build_identifier": self.get_build_identifier(),
            "database_version": self.database.current_version,
            "release_date": self.app.release_date,
            "build_type": self.build.build_type,
            "platform": self.build.target_platform,
            "architecture": self.build.architecture,
            "channel": self.release.channel
        }
    
    def get_about_info(self) -> dict:
        """Retorna información para ventana 'Acerca de'"""
        return {
            "name": self.app.display_name,
            "version": self.get_full_version(),
            "build_id": self.get_build_identifier(),
            "description": self.app.description,
            "author": self.app.author,
            "organization": self.app.organization,
            "contact": self.app.contact_email,
            "github_profile": self.app.github_profile,
            "license": self.app.license,
            "copyright": self.app.copyright,
            "release_date": self.app.release_date,
            "build_date": self.build.build_date,
            "platform": f"{self.build.target_platform} {self.build.architecture}",
            "framework": self.build.qt_framework,
            # Información del equipo
            "developers": list(self.team.developers),
            "designers": list(self.team.designers),
            "testers": list(self.team.testers),
            "features": list(self.team.features),
            "technologies": list(self.team.technologies),
            "acknowledgments": list(self.team.acknowledgments)
        }
    
    def get_team_info(self) -> dict:
        """Retorna información específica del equipo"""
        return {
            "developers": list(self.team.developers),
            "designers": list(self.team.designers),
            "testers": list(self.team.testers),
            "features": list(self.team.features),
            "technologies": list(self.team.technologies),
            "acknowledgments": list(self.team.acknowledgments)
        }
    
    def needs_database_migration(self) -> bool:
        """Verifica si se necesita migración de base de datos"""
        return self.database.migration_required
    
    def is_debug_build(self) -> bool:
        """Verifica si es una compilación de debug"""
        return self.build.build_type.lower() == "debug"
    
    def is_development_mode(self) -> bool:
        """Verifica si está en modo desarrollo"""
        import sys
        return not getattr(sys, 'frozen', False)
    
    def is_pre_release(self) -> bool:
        """Verifica si es una pre-release (alpha/beta)"""
        return self.release.channel.lower() in ["alpha", "beta", "dev"]
    
    def get_dependencies_info(self) -> dict:
        """Retorna información de dependencias"""
        return self.build.dependencies.copy()


# Instancia global del gestor de build
BUILD_CONFIG = BuildConfig()

# Variables de acceso directo (estilo parámetros)
APP_NAME = BUILD_CONFIG.app.name
APP_VERSION = BUILD_CONFIG.app.version
APP_FULL_VERSION = BUILD_CONFIG.get_full_version()
BUILD_IDENTIFIER = BUILD_CONFIG.get_build_identifier()
DATABASE_NAME = BUILD_CONFIG.database.name
DATABASE_VERSION = BUILD_CONFIG.database.current_version
AUTHOR = BUILD_CONFIG.app.author
ORGANIZATION = BUILD_CONFIG.app.organization
BUILD_TYPE = BUILD_CONFIG.build.build_type
TARGET_PLATFORM = BUILD_CONFIG.build.target_platform
DATA_DIR_NAME = BUILD_CONFIG.app.data_dir_name

# Variables dunder para compatibilidad con estándares Python
__version__ = BUILD_CONFIG.app.version
__author__ = BUILD_CONFIG.app.author
__email__ = BUILD_CONFIG.app.contact_email
__license__ = BUILD_CONFIG.app.license


# Funciones de utilidad para builds
def get_version() -> str:
    """Obtiene la versión de la aplicación"""
    return BUILD_CONFIG.app.version


def get_version_with_v() -> str:
    """Obtiene la versión con prefijo 'v'"""
    return f"v{BUILD_CONFIG.app.version}"


def get_build_number() -> int:
    """Obtiene el número de build"""
    return BUILD_CONFIG.app.build_number


def get_formatted_version_build() -> str:
    """Obtiene la versión formateada como 'v1.1.5, build 109'"""
    return f"v{BUILD_CONFIG.app.version}, build {BUILD_CONFIG.app.build_number}"


def get_main_window_version() -> str:
    """Obtiene la versión formateada para el main window como 'v1.1.5 (109)'"""
    return f"v{BUILD_CONFIG.app.version} ({BUILD_CONFIG.app.build_number})"


def get_full_version() -> str:
    """Obtiene la versión completa con build number"""
    return BUILD_CONFIG.get_full_version()


def get_build_identifier() -> str:
    """Obtiene el identificador único del build"""
    return BUILD_CONFIG.get_build_identifier()


def get_app_title() -> str:
    """Obtiene el título completo de la aplicación"""
    return f"{BUILD_CONFIG.app.display_name}"


def get_window_title(subtitle: str = "") -> str:
    """Obtiene título para ventanas con subtítulo opcional"""
    base_title = f"{BUILD_CONFIG.app.name} v{BUILD_CONFIG.app.version}"
    return f"{base_title} - {subtitle}" if subtitle else base_title


def get_about_info() -> dict:
    """Obtiene información completa 'Acerca de'"""
    return BUILD_CONFIG.get_about_info()


def get_build_info() -> dict:
    """Obtiene información técnica del build"""
    return BUILD_CONFIG.get_version_info()


def is_debug() -> bool:
    """Verifica si es un build de debug"""
    return BUILD_CONFIG.is_debug_build()


def is_development() -> bool:
    """Verifica si está en modo desarrollo"""
    return BUILD_CONFIG.is_development_mode()


def open_github_profile():
    """Abre el perfil de GitHub del desarrollador en el navegador"""
    import webbrowser
    try:
        webbrowser.open(BUILD_CONFIG.app.github_profile)
        return True
    except Exception as e:
        print(f"Error abriendo perfil de GitHub: {e}")
        return False


def get_build_info_text() -> str:
    """Obtiene la información de build como texto formateado para mostrar en diálogos"""
    info = BUILD_CONFIG.get_version_info()
    about = BUILD_CONFIG.get_about_info()
    
    text = f"""
{BUILD_CONFIG.app.display_name} - Información de Build

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INFORMACIÓN GENERAL:
   • Versión: {info['full_version']}
   • Build ID: {info['build_identifier']}
   • Fecha de Release: {info['release_date']}
   • Fecha de Build: {about['build_date']}

CONFIGURACIÓN TÉCNICA:
   • Tipo de Build: {info['build_type']} ({info['channel']})
   • Plataforma: {info['platform']}
   • Framework: {about['framework']}
   • Base de Datos: {info['database_version']}

INFORMACIÓN DEL DESARROLLADOR:
   • Autor: {BUILD_CONFIG.app.author}
   • Organización: {BUILD_CONFIG.app.organization}
   • Contacto: {BUILD_CONFIG.app.contact_email}
   • GitHub: {BUILD_CONFIG.app.github_profile}

DEPENDENCIAS:
"""
    for dep, version in BUILD_CONFIG.get_dependencies_info().items():
        text += f"   • {dep}: {version}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    return text
