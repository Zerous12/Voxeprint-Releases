"""
Migración: Número de Impresoras Activas para Overhead

VERSIÓN: 1.2.2
CAMBIOS:
- Añade overhead_active_printers_mode ('auto' | 'manual') para elegir si el
  número de impresoras activas se toma automáticamente de la BD o se indica
  de forma manual.
- Añade overhead_active_printers (int) usado cuando el modo es 'manual'.
"""
from core.utils.logger import logger

MIGRATION_VERSION = "1.2.2"
MIGRATION_KEY = "db_overhead_printers_version"


def check_migration_needed(db_connection) -> bool:
    try:
        rows = db_connection.execute_query(
            "SELECT config_value FROM system_configs WHERE config_key = ?",
            (MIGRATION_KEY,)
        )
        if rows:
            return rows[0]['config_value'] < MIGRATION_VERSION
        return True
    except Exception:
        return True


def run_migration(db_connection) -> bool:
    if not check_migration_needed(db_connection):
        logger.debug("Migration", f"Migración {MIGRATION_VERSION} ya aplicada - omitiendo")
        return False

    logger.info("Migration", f"Ejecutando migración {MIGRATION_VERSION}: Impresoras activas para overhead")

    try:
        db_connection.execute_script(_get_insert_sql())
        logger.info("Migration", "Claves overhead_active_printers insertadas en system_configs")
        _register_version(db_connection)
        logger.info("Migration", f"Migración {MIGRATION_VERSION} completada")
        return True
    except Exception as e:
        logger.log_exception("Migration", e, f"ejecutar migración {MIGRATION_VERSION}")
        return False


def _get_insert_sql() -> str:
    return """
    INSERT OR IGNORE INTO system_configs
        (config_key, config_value, config_type, description, category, is_editable)
    VALUES
        ('overhead_active_printers_mode', 'auto',  'string',
         'Modo de impresoras activas: auto (BD) o manual', 'overhead', 1),
        ('overhead_active_printers',      '1',     'integer',
         'Numero manual de impresoras activas (usado cuando modo=manual)', 'overhead', 1);
    """


def _register_version(db_connection):
    rows = db_connection.execute_query(
        "SELECT id FROM system_configs WHERE config_key = ?",
        (MIGRATION_KEY,)
    )
    if rows:
        db_connection.execute_query(
            "UPDATE system_configs SET config_value = ? WHERE config_key = ?",
            (MIGRATION_VERSION, MIGRATION_KEY)
        )
    else:
        db_connection.execute_query(
            "INSERT INTO system_configs (config_key, config_value, config_type, description, category, is_editable) "
            "VALUES (?, ?, 'string', 'Version de migracion overhead printers', 'system', 0)",
            (MIGRATION_KEY, MIGRATION_VERSION)
        )
