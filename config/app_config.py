"""
Configuración global de la aplicación Voxeprint.
Centraliza todos los parámetros de negocio, cálculos y comportamiento de la aplicación.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CalculationParameters:   
    electricity_rate_multiplier: float = 1.6
    default_electricity_rate: float = 435.0    
    # Fallback si no se encuentra configuración en la base de datos
    fallback_electricity_rate: float = 465.0     
    default_failure_margin: float = 5.0    
    # Margen de ganancia sobre los costos (%)
    default_profit_margin: float = 35.0    
    # Tasa de IVA Paraguay (%)
    default_tax_rate: float = 10.0 
    round_to_integer: bool = True
    
    @property
    def effective_electricity_rate(self) -> float:
        return self.default_electricity_rate * self.electricity_rate_multiplier
    
@dataclass(frozen=True)
class DatabaseParameters:
    """
    Parámetros de configuración de la base de datos.
    """
    # Versión actual de la base de datos
    current_version: str = "1.2"    
    # Versión del schema (cambios estructurales)
    schema_version: int = 2    
    # Versión anterior (para migraciones)
    previous_version: Optional[str] = "1.1"    
    # ¿Requiere migración al actualizar?
    migration_required: bool = False    
    # ¿Crear backup antes de migrar?
    backup_before_migration: bool = True    
    # Timeout para operaciones de migración (segundos)
    migration_timeout: int = 30    
    # Número máximo de archivos de backup a mantener
    max_backup_files: int = 5
    
    @property
    def name(self) -> str:
        """
        Nombre del archivo de base de datos según la versión.        
        Returns:
            str: Nombre del archivo (ej: "voxeprint_1.1.db")
        """
        return f"voxeprint_{self.current_version}.db"
    
@dataclass(frozen=True)
class UIParameters:
    """
    Parámetros de configuración de la interfaz de usuario.
    """
    # Tema por defecto (light, dark, auto)
    default_theme: str = "light"    
    # Idioma por defecto (es, en)
    default_language: str = "es"    
    # Símbolo de moneda
    currency_symbol: str = "Gs."    
    # Formato de fecha (dd/mm/yyyy, yyyy-mm-dd, etc.)
    date_format: str = "dd/MM/yyyy"    
    # Separador de miles
    thousands_separator: str = "."    
    # Separador decimal
    decimal_separator: str = ","    
    # Número de decimales para mostrar en la UI
    display_decimals: int = 2    
    # Tamaño de fuente por defecto
    default_font_size: int = 10    
    # Mostrar tooltips
    show_tooltips: bool = True    
    # Animaciones habilitadas
    animations_enabled: bool = True


@dataclass(frozen=True)
class BusinessParameters:
    """
    Parámetros de configuración del negocio/empresa.
    """
    # Nombre de la empresa
    company_name: str = "ZeroLab"    
    # Dirección
    company_address: str = "Calle Paraiso 242 c/ Calle 5 de Marzo"    
    # Ciudad
    company_city: str = "Capiata"    
    # Teléfono
    company_phone: str = ""
    # Email
    company_email: str = "Zerous_12@hotmail.com"    
    # Sitio web
    company_website: str = "Web"
    
    # RUC (Registro Único del Contribuyente)
    company_ruc: Optional[str] = None    
    # Logo path (relativo a resources/)
    company_logo_path: str = "images/logo.png"


@dataclass(frozen=True)
class SystemParameters:
    """
    Parámetros de configuración del sistema.
    """
    # Intervalo de guardado automático (segundos)
    auto_save_interval: int = 300    
    # Habilitar respaldos automáticos
    backup_enabled: bool = True    
    # Frecuencia de respaldo automático (días)
    backup_frequency: int = 7    
    # Número máximo de respaldos a mantener
    max_backup_files: int = 10    
    # Verificar actualizaciones al iniciar
    check_updates_on_startup: bool = True    
    # Intervalo de verificación de actualizaciones (horas)
    update_check_interval: int = 24    
    # Habilitar logs de debug
    debug_logging_enabled: bool = False    
    # Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log_level: str = "INFO"    
    # Días para mantener logs antiguos
    log_retention_days: int = 30

@dataclass(frozen=True)
class PDFParameters:
    """
    Parámetros de configuración para generación de PDFs.
    """
    # Incluir logo de empresa en PDFs
    include_company_logo: bool = True    
    # Incluir información de contacto en PDFs
    include_contact_info: bool = True    
    # Incluir desglose detallado de costos
    include_cost_breakdown: bool = True    
    # Incluir términos y condiciones
    include_terms_and_conditions: bool = False    
    # Texto de términos y condiciones
    terms_and_conditions_text: str = ""    
    # Incluir firma digital
    include_digital_signature: bool = False    
    # Marca de agua (watermark)
    watermark_text: Optional[str] = None    
    # Tamaño de página (A4, Letter, Legal)
    page_size: str = "A4"    
    # Orientación (portrait, landscape)
    page_orientation: str = "portrait"


class AppConfig:
    """
    Gestor principal de configuración de la aplicación.
    Proporciona acceso centralizado a todos los parámetros de la aplicación.    
    Uso:
        from config.app_config import APP_CONFIG
        
        # Obtener multiplicador eléctrico
        multiplier = APP_CONFIG.calculation.electricity_rate_multiplier
        
        # Obtener tarifa efectiva
        rate = APP_CONFIG.calculation.effective_electricity_rate
        
        # Obtener nombre de base de datos
        db_name = APP_CONFIG.database.name
    """
    
    def __init__(self):
        self._calculation = CalculationParameters()
        self._ui = UIParameters()
        self._business = BusinessParameters()
        self._system = SystemParameters()
        self._database = DatabaseParameters()
        self._pdf = PDFParameters()
    
    @property
    def calculation(self) -> CalculationParameters:
        """Parámetros de cálculo de costos"""
        return self._calculation
    
    @property
    def ui(self) -> UIParameters:
        """Parámetros de interfaz de usuario"""
        return self._ui
    
    @property
    def business(self) -> BusinessParameters:
        """Parámetros del negocio/empresa"""
        return self._business
    
    @property
    def system(self) -> SystemParameters:
        """Parámetros del sistema"""
        return self._system
    
    @property
    def database(self) -> DatabaseParameters:
        """Parámetros de base de datos"""
        return self._database
    
    @property
    def pdf(self) -> PDFParameters:
        """Parámetros de generación de PDFs"""
        return self._pdf   

# instancia global - Usar esta en toda la aplicación
APP_CONFIG = AppConfig()

# Cálculos
ELECTRICITY_MULTIPLIER = APP_CONFIG.calculation.electricity_rate_multiplier
EFFECTIVE_ELECTRICITY_RATE = APP_CONFIG.calculation.effective_electricity_rate
DEFAULT_FAILURE_MARGIN = APP_CONFIG.calculation.default_failure_margin
DEFAULT_PROFIT_MARGIN = APP_CONFIG.calculation.default_profit_margin
DEFAULT_TAX_RATE = APP_CONFIG.calculation.default_tax_rate

# UI
CURRENCY_SYMBOL = APP_CONFIG.ui.currency_symbol
DATE_FORMAT = APP_CONFIG.ui.date_format

# Negocio
COMPANY_NAME = APP_CONFIG.business.company_name
COMPANY_EMAIL = APP_CONFIG.business.company_email

# FUNCIONES DE UTILIDAD
def get_electricity_multiplier() -> float:
    """Obtiene el multiplicador de tarifa eléctrica"""
    return APP_CONFIG.calculation.electricity_rate_multiplier


def get_effective_electricity_rate() -> float:
    """Obtiene la tarifa eléctrica efectiva (con multiplicador aplicado)"""
    return APP_CONFIG.calculation.effective_electricity_rate


def get_default_margins() -> dict:
    """Obtiene todos los márgenes por defecto"""
    return {
        "failure_margin": APP_CONFIG.calculation.default_failure_margin,
        "profit_margin": APP_CONFIG.calculation.default_profit_margin,
        "tax_rate": APP_CONFIG.calculation.default_tax_rate
    }


def get_currency_symbol() -> str:
    """Obtiene el símbolo de moneda"""
    return APP_CONFIG.ui.currency_symbol


def get_company_info() -> dict:
    """Obtiene información completa de la empresa"""
    return {
        "name": APP_CONFIG.business.company_name,
        "address": APP_CONFIG.business.company_address,
        "city": APP_CONFIG.business.company_city,
        "phone": APP_CONFIG.business.company_phone,
        "email": APP_CONFIG.business.company_email,
        "website": APP_CONFIG.business.company_website,
        "ruc": APP_CONFIG.business.company_ruc
    }
