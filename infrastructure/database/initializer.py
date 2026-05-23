"""
Inicializador de la base de datos
"""
from .connection import DatabaseConnection
from .schema import get_database_schema, get_initial_data
from core.utils.logger import logger

from PySide6.QtCore import QStandardPaths
import os, shutil
from core.utils.path_helper import database_path

class DatabaseInitializer:
    """Inicializa y configura la base de datos"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(database_path())

        self.db_connection = DatabaseConnection(db_path)
        self.db_path = str(db_path)
    
    def initialize_database(self) -> None:
        """
        Inicializa la base de datos creando tablas y datos iniciales
        """
        try:
            schema_script = get_database_schema()
            self.db_connection.execute_script(schema_script)
            
            initial_data_script = get_initial_data()
            self.db_connection.execute_script(initial_data_script)
            
        except Exception as e:
            logger.error("Database", f"Error al inicializar la base de datos: {e}")
            raise
    
    def database_exists(self) -> bool:
        """
        Verifica si la base de datos existe
        
        Returns:
            bool: True si existe, False si no
        """
        return os.path.exists(self.db_path)
    
    def reset_database(self) -> None:
        """
        Reinicia la base de datos eliminando el archivo y recreándolo
        """
        if self.database_exists():
            os.remove(self.db_path)
            logger.info("Database", "Base de datos anterior eliminada")
        
        self.initialize_database()
    
    def backup_database(self, backup_path: str) -> None:
        """
        Crea un respaldo de la base de datos
        
        Args:
            backup_path: Ruta donde guardar el respaldo
        """
        if not self.database_exists():
            raise FileNotFoundError("La base de datos no existe")                
        shutil.copy2(self.db_path, backup_path)


def setup_database(db_path: str = None) -> DatabaseInitializer:
    """
    Configura la base de datos para la aplicación
    Args:
        db_path: Ruta al archivo de base de datos
    Returns:
        DatabaseInitializer: Inicializador configurado
    """
    if db_path is None:
        db_path = str(database_path())

    initializer = DatabaseInitializer(db_path)

    if not initializer.database_exists():
        logger.info("Database", "Base de datos no encontrada - creando nueva base de datos")
        initializer.initialize_database()
        logger.info("Database", f"Base de datos creada en: {db_path}")
    else:
        logger.debug("Database", "Base de datos encontrada - verificando esquema")
        initializer.initialize_database()

    # Ejecutar migraciones pendientes
    _run_pending_migrations(initializer.db_connection)

    return initializer


def _run_pending_migrations(db_connection):
    """Ejecuta migraciones pendientes de forma ordenada"""
    try:
        from infrastructure.database.migrations.migrate_filament_rolls import run_migration
        run_migration(db_connection)
    except Exception as e:
        logger.error("Database", f"Error ejecutando migración filament_rolls: {e}")

    try:
        from infrastructure.database.migrations.migration_overhead_costs import run_migration as run_overhead_migration
        run_overhead_migration(db_connection)
    except Exception as e:
        logger.error("Database", f"Error ejecutando migración overhead_costs: {e}")

    try:
        from infrastructure.database.migrations.migration_overhead_printers import run_migration as run_overhead_printers_migration
        run_overhead_printers_migration(db_connection)
    except Exception as e:
        logger.error("Database", f"Error ejecutando migración overhead_printers: {e}")
