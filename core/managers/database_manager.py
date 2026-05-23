"""
Gestor principal de la base de datos para VoxePrint
"""
from pathlib import Path
import os
from infrastructure.database.initializer import setup_database
from core.utils.path_helper import database_path, backups_dir
from infrastructure.database.connection import DatabaseConnection
from infrastructure.database.repositories import (
    CustomerRepository,
    PrinterRepository,
    FilamentRepository,
    QuoteRepository,
    SystemConfigRepository
)


class DatabaseManager:
    """Gestor centralizado de la base de datos"""
    
    def __init__(self, db_path: str = database_path()):
        """
        Inicializa el gestor de base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos
        """
        self.db_path = db_path
        self.db_connection = None
        self.initializer = None
        
        # Repositorios
        self.customers = None
        self.printers = None
        self.filaments = None
        self.quotes = None
        self.configs = None
        
        self._initialize()
    
    def _initialize(self):
        """Inicializa la conexión y repositorios"""
        # Configurar la base de datos
        self.initializer = setup_database(self.db_path)
        
        # Crear conexión
        self.db_connection = DatabaseConnection(self.db_path)
        
        # Inicializar repositorios
        self.customers = CustomerRepository(self.db_connection)
        self.printers = PrinterRepository(self.db_connection)
        self.filaments = FilamentRepository(self.db_connection)
        self.quotes = QuoteRepository(self.db_connection)
        self.configs = SystemConfigRepository(self.db_connection)
    
    def get_app_config(self):
        """
        Obtiene la configuración principal de la aplicación
        
        Returns:
            dict: Configuración de la aplicación
        """
        return {
            # Preferimos 'electricity_rate' pero usamos 265.0 Gs/kWh por defecto
            'electricity_rate': self.configs.get_float_value('electricity_rate', 435.0),
            'default_profit_margin': self.configs.get_float_value('default_profit_margin', 30.0),
            'default_failure_margin': self.configs.get_float_value('default_failure_margin', 5.0),
            'company_name': self.configs.get_value('company_name', 'VoxePrint'),
            'company_address': self.configs.get_value('company_address', ''),
            'company_phone': self.configs.get_value('company_phone', ''),
            'company_email': self.configs.get_value('company_email', ''),
            'currency_symbol': self.configs.get_value('currency_symbol', 'Gs.'),
            'tax_rate': self.configs.get_float_value('tax_rate', 10.0),
            'auto_save_interval': self.configs.get_int_value('auto_save_interval', 300),
            'backup_enabled': self.configs.get_bool_value('backup_enabled', True),
            'backup_frequency': self.configs.get_int_value('backup_frequency', 7)
        }
    
    def update_config(self, config_key: str, value: str) -> bool:
        """
        Actualiza una configuración
        
        Args:
            config_key: Clave de configuración
            value: Nuevo valor
            
        Returns:
            bool: True si se actualizó correctamente
        """
        return self.configs.update_value(config_key, value)
    
    def backup_database(self, backup_path: str = None) -> str:
        """
        Crea un respaldo de la base de datos
        
        Args:
            backup_path: Ruta del respaldo (opcional)
            
        Returns:
            str: Ruta del archivo de respaldo creado
        """
        if backup_path is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = backups_dir()  # Usar el directorio centralizado
            backup_path = backup_dir / f"voxeprint_backup_{timestamp}.db"
        
        self.initializer.backup_database(backup_path)
        return backup_path
    
    def reset_database(self):
        """Reinicia la base de datos completamente"""
        self.initializer.reset_database()
        self._initialize()
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.db_connection:
            # No necesitamos cerrar explícitamente SQLite en este caso
            # ya que usamos context managers
            pass


# Instancia global del gestor de base de datos (inicialización diferida)
_db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """
    Obtiene la instancia global del gestor de base de datos.
    Se inicializa en la primera llamada (lazy initialization).
    
    Returns:
        DatabaseManager: Gestor de base de datos
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
