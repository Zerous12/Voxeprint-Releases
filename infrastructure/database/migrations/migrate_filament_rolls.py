"""
Migración: Inventario de rollos individuales de filamento

VERSIÓN: 1.2.0
CAMBIOS:
- Crea tabla `filament_rolls` para tracking individual de rollos
- Migra datos existentes de `filaments` → genera N rollos por filamento
- Registra versión de migración en `system_configs`

COMPATIBILIDAD:
- La tabla `filaments` sigue existiendo como "tipo de material" (padre)
- Los campos agregados (quantity_rolls, current_stock_grams, price_per_gram)
  ahora se calculan desde filament_rolls como fuente de verdad
- BDs sin filamentos no generan rollos (solo tabla + versión)
"""
from core.utils.logger import logger


MIGRATION_VERSION = "1.2.0"
MIGRATION_KEY = "db_schema_version"


def check_migration_needed(db_connection) -> bool:
    """Verifica si la migración es necesaria comprobando system_configs"""
    try:
        # Verificar si la versión de migración ya está registrada en system_configs
        rows = db_connection.execute_query(
            "SELECT config_value FROM system_configs WHERE config_key = ?",
            (MIGRATION_KEY,)
        )
        if rows:
            registered_version = rows[0]['config_value']
            if registered_version >= MIGRATION_VERSION:
                return False  # Migración ya fue aplicada

        return True
    except Exception:
        return True


def run_migration(db_connection) -> bool:
    """
    Ejecuta la migración de inventario de rollos.
    
    Returns:
        True si se ejecutó, False si no era necesaria
    """
    if not check_migration_needed(db_connection):
        logger.debug("Migration", f"Migración {MIGRATION_VERSION} ya aplicada - omitiendo")
        return False

    logger.info("Migration", f"Ejecutando migración {MIGRATION_VERSION}: Inventario de rollos individuales")

    try:
        # 1. Crear tabla filament_rolls con columna sku incluida
        db_connection.execute_script(_get_create_table_sql())
        logger.info("Migration", "Tabla filament_rolls verificada/creada")

        # 2. Migrar datos existentes (cada rollo recibe su SKU)
        migrated = _migrate_existing_filaments(db_connection)
        logger.info("Migration", f"Migrados {migrated} rollos desde filamentos existentes")

        # 3. Registrar versión de migración
        _register_migration_version(db_connection)
        logger.info("Migration", f"Migración {MIGRATION_VERSION} completada exitosamente")

        return True

    except Exception as e:
        logger.error("Migration", f"Error en migración {MIGRATION_VERSION}: {e}")
        raise


def _get_create_table_sql() -> str:
    return """
    CREATE TABLE IF NOT EXISTS filament_rolls (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        filament_id           INTEGER NOT NULL,
        sku                   TEXT UNIQUE,
        initial_weight_grams  REAL NOT NULL DEFAULT 0.0,
        current_weight_grams  REAL NOT NULL DEFAULT 0.0,
        purchase_price        REAL NOT NULL DEFAULT 0.0,
        price_per_gram        REAL DEFAULT 0.0,
        purchase_date         DATE DEFAULT (date('now','localtime')),
        is_active             BOOLEAN DEFAULT 1,
        notes                 TEXT,
        created_at            DATETIME DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (filament_id) REFERENCES filaments(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_filament_rolls_filament_id ON filament_rolls(filament_id);
    CREATE INDEX IF NOT EXISTS idx_filament_rolls_is_active ON filament_rolls(is_active);

    CREATE TRIGGER IF NOT EXISTS filament_rolls_calc_ppg_insert
        AFTER INSERT ON filament_rolls
        FOR EACH ROW
        WHEN NEW.initial_weight_grams > 0 AND NEW.purchase_price > 0
        BEGIN
            UPDATE filament_rolls
            SET price_per_gram = NEW.purchase_price / NEW.initial_weight_grams
            WHERE id = NEW.id;
        END;

    CREATE TRIGGER IF NOT EXISTS filament_rolls_calc_ppg_update
        AFTER UPDATE ON filament_rolls
        FOR EACH ROW
        WHEN (NEW.initial_weight_grams <> OLD.initial_weight_grams OR NEW.purchase_price <> OLD.purchase_price)
        AND NEW.initial_weight_grams > 0 AND NEW.purchase_price > 0
        BEGIN
            UPDATE filament_rolls
            SET price_per_gram = NEW.purchase_price / NEW.initial_weight_grams
            WHERE id = NEW.id;
        END;
    """


def _migrate_existing_filaments(db_connection) -> int:
    """
    Migra filamentos existentes: por cada filament con quantity_rolls > 0,
    crea N registros en filament_rolls distribuyendo el stock equitativamente.
    """
    rows = db_connection.execute_query(
        "SELECT * FROM filaments WHERE quantity_rolls > 0 AND current_stock_grams > 0"
    )

    total_rolls_created = 0

    for row in rows:
        filament_id = row['id']
        qty = int(row['quantity_rolls'])
        total_stock = float(row['current_stock_grams'])
        price_per_gram = float(row['price_per_gram'] or 0)
        weight_per_roll = float(row['weight_grams'] or 0)
        created_at = row['created_at']

        if qty <= 0:
            continue

        # Distribuir stock equitativamente entre rollos
        stock_per_roll = total_stock / qty
        # Precio de compra por rollo basado en promedio ponderado
        price_per_roll = stock_per_roll * price_per_gram if price_per_gram > 0 else 0

        for i in range(qty):
            # El último rollo absorbe la diferencia de redondeo
            if i == qty - 1:
                roll_stock = total_stock - (stock_per_roll * (qty - 1))
            else:
                roll_stock = stock_per_roll

            roll_initial = weight_per_roll if weight_per_roll > 0 else roll_stock

            sku = f"VX-{filament_id:05d}-{i+1:02d}"

            db_connection.execute_command(
                """INSERT INTO filament_rolls 
                   (filament_id, sku, initial_weight_grams, current_weight_grams, 
                    purchase_price, price_per_gram, purchase_date, is_active, 
                    notes, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""",
                (
                    filament_id,
                    sku,
                    roll_initial,
                    round(roll_stock, 2),
                    round(price_per_roll, 2),
                    price_per_gram,
                    created_at[:10] if created_at else None,
                    f"Migrado automáticamente (rollo {i+1}/{qty})",
                    created_at
                )
            )
            total_rolls_created += 1

    return total_rolls_created


def _register_migration_version(db_connection):
    """Registra la versión de migración en system_configs"""
    db_connection.execute_command(
        """INSERT OR REPLACE INTO system_configs 
           (config_key, config_value, config_type, description, category)
           VALUES (?, ?, 'string', 'Versión del esquema de base de datos', 'system')""",
        (MIGRATION_KEY, MIGRATION_VERSION)
    )
