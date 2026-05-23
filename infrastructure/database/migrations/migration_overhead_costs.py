"""
Migración: Gastos Operativos del Negocio (Overhead)

VERSIÓN: 1.2.1
CAMBIOS:
- Inserta 9 claves en system_configs (category='overhead') para configurar
  los gastos fijos mensuales del negocio y los parámetros de operación.
- INSERT OR IGNORE: instalaciones existentes no pierden valores ya configurados.
"""
from core.utils.logger import logger

MIGRATION_VERSION = "1.2.1"
MIGRATION_KEY = "db_overhead_version"


def check_migration_needed(db_connection) -> bool:
    """Verifica si la migración es necesaria comprobando system_configs"""
    try:
        rows = db_connection.execute_query(
            "SELECT config_value FROM system_configs WHERE config_key = ?",
            (MIGRATION_KEY,)
        )
        if rows:
            registered_version = rows[0]['config_value']
            if registered_version >= MIGRATION_VERSION:
                return False
        return True
    except Exception:
        return True


def run_migration(db_connection) -> bool:
    """
    Ejecuta la migración de gastos operativos.

    Returns:
        True si se ejecutó, False si no era necesaria.
    """
    if not check_migration_needed(db_connection):
        logger.debug("Migration", f"Migración {MIGRATION_VERSION} ya aplicada - omitiendo")
        return False

    logger.info("Migration", f"Ejecutando migración {MIGRATION_VERSION}: Gastos Operativos del Negocio")

    try:
        db_connection.execute_script(_get_insert_sql())
        logger.info("Migration", "Claves de overhead insertadas en system_configs")

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
        ('overhead_rent',          '0.0',  'float', 'Alquiler mensual',            'overhead', 1),
        ('overhead_water',         '0.0',  'float', 'Agua mensual',                'overhead', 1),
        ('overhead_internet',      '0.0',  'float', 'Internet mensual',            'overhead', 1),
        ('overhead_accounting',    '0.0',  'float', 'Gestoria mensual',            'overhead', 1),
        ('overhead_salary',        '0.0',  'float', 'Salario / Autonomos mensual', 'overhead', 1),
        ('overhead_transport',     '0.0',  'float', 'Transporte mensual',          'overhead', 1),
        ('overhead_other',         '0.0',  'float', 'Otros gastos mensuales',      'overhead', 1),
        ('overhead_hours_per_day', '12.0', 'float', 'Horas de operacion por dia',  'overhead', 1),
        ('overhead_days_per_month','30.0', 'float', 'Dias de operacion por mes',   'overhead', 1);
    """


def _register_version(db_connection):
    """Registra la versión de esta migración en system_configs"""
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
            "VALUES (?, ?, 'string', 'Version de migracion overhead', 'system', 0)",
            (MIGRATION_KEY, MIGRATION_VERSION)
        )
