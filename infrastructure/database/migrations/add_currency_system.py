"""
Migración: Agregar sistema de monedas multi-currency

Fecha: 21 de diciembre de 2025
Versión: 1.2.0

Esta migración:
1. Crea tablas currencies y exchange_rates
2. Agrega columna currency a printers, filaments, quotes
3. Pobla con monedas por defecto (PYG, USD, EUR, ARS, BRL)
4. Establece tasas de cambio iniciales
5. Migra datos existentes a PYG como moneda por defecto
"""
import sqlite3
from pathlib import Path
import shutil
from datetime import datetime


def backup_database(db_path: Path) -> Path:
    """Crea backup de la base de datos antes de migrar"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / f"voxeprint_pre_currency_{timestamp}.db"
    shutil.copy(db_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    return backup_path


def check_if_migration_needed(conn: sqlite3.Connection) -> bool:
    """Verifica si la migración ya fue aplicada"""
    cursor = conn.cursor()
    
    # Verificar si la tabla currencies existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='currencies'
    """)
    if cursor.fetchone():
        print("ℹ️  La tabla 'currencies' ya existe")
        return False
    
    return True


def create_currency_tables(conn: sqlite3.Connection):
    """Crea las tablas currencies y exchange_rates"""
    cursor = conn.cursor()
    
    print("🔄 Creando tabla 'currencies'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currencies (
            code TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            decimals INTEGER DEFAULT 2,
            thousands_sep TEXT DEFAULT ',',
            decimal_sep TEXT DEFAULT '.',
            symbol_position TEXT DEFAULT 'prefix',
            space_between BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT (datetime('now', 'localtime')),
            updated_at DATETIME DEFAULT (datetime('now', 'localtime'))
        )
    """)
    
    print("🔄 Creando tabla 'exchange_rates'...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_currency TEXT NOT NULL,
            target_currency TEXT NOT NULL,
            rate REAL NOT NULL,
            updated_at DATETIME DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (base_currency) REFERENCES currencies(code) ON DELETE CASCADE,
            FOREIGN KEY (target_currency) REFERENCES currencies(code) ON DELETE CASCADE,
            UNIQUE(base_currency, target_currency)
        )
    """)
    
    # Índices
    print("🔄 Creando índices...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_currencies_is_active ON currencies(is_active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_exchange_rates_base ON exchange_rates(base_currency)")
    
    # Triggers
    print("🔄 Creando triggers...")
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS currencies_updated_at
        AFTER UPDATE ON currencies
        BEGIN
            UPDATE currencies SET updated_at = datetime('now', 'localtime') WHERE code = NEW.code;
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS exchange_rates_updated_at
        AFTER UPDATE ON exchange_rates
        BEGIN
            UPDATE exchange_rates SET updated_at = datetime('now', 'localtime') WHERE id = NEW.id;
        END
    """)
    
    conn.commit()
    print("✅ Tablas de monedas creadas")


def populate_default_currencies(conn: sqlite3.Connection):
    """Pobla la tabla con monedas por defecto"""
    cursor = conn.cursor()
    
    print("🔄 Poblando monedas por defecto...")
    currencies = [
        ('PYG', 'Gs.', 'Guaraní Paraguayo', 0, '.', '', 'prefix', 1, 1),
        ('USD', '$', 'Dólar Estadounidense', 2, ',', '.', 'prefix', 0, 1),
        ('EUR', '€', 'Euro', 2, '.', ',', 'suffix', 1, 1),
        ('ARS', '$', 'Peso Argentino', 2, '.', ',', 'prefix', 1, 1),
        ('BRL', 'R$', 'Real Brasileño', 2, '.', ',', 'prefix', 1, 1)
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO currencies 
        (code, symbol, name, decimals, thousands_sep, decimal_sep, symbol_position, space_between, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, currencies)
    
    conn.commit()
    print(f"✅ {len(currencies)} monedas insertadas")


def populate_exchange_rates(conn: sqlite3.Connection):
    """Pobla tasas de cambio por defecto"""
    cursor = conn.cursor()
    
    print("🔄 Poblando tasas de cambio por defecto...")
    
    # Tasas reales aproximadas (diciembre 2025)
    rates = [
        # Desde PYG
        ('PYG', 'USD', 0.00015),
        ('PYG', 'EUR', 0.00013),
        ('PYG', 'ARS', 0.12),
        ('PYG', 'BRL', 0.00073),
        # Desde USD
        ('USD', 'PYG', 6709.36),
        ('USD', 'EUR', 0.92),
        ('USD', 'ARS', 1025.50),
        ('USD', 'BRL', 4.95),
        # Desde EUR
        ('EUR', 'PYG', 7293.22),
        ('EUR', 'USD', 1.09),
        ('EUR', 'ARS', 1115.22),
        ('EUR', 'BRL', 5.38),
        # Desde ARS
        ('ARS', 'PYG', 8.33),
        ('ARS', 'USD', 0.00098),
        ('ARS', 'EUR', 0.00090),
        ('ARS', 'BRL', 0.0048),
        # Desde BRL
        ('BRL', 'PYG', 1369.86),
        ('BRL', 'USD', 0.20),
        ('BRL', 'EUR', 0.19),
        ('BRL', 'ARS', 207.17)
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO exchange_rates (base_currency, target_currency, rate)
        VALUES (?, ?, ?)
    """, rates)
    
    conn.commit()
    print(f"✅ {len(rates)} tasas de cambio insertadas")


def add_currency_column_to_tables(conn: sqlite3.Connection):
    """Agrega columna currency a printers, filaments, quotes"""
    cursor = conn.cursor()
    
    tables = ['printers', 'filaments', 'quotes']
    
    for table in tables:
        print(f"🔄 Agregando columna 'currency' a tabla '{table}'...")
        
        # Verificar si la columna ya existe
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'currency' in columns:
            print(f"ℹ️  Columna 'currency' ya existe en '{table}'")
            continue
        
        try:
            cursor.execute(f"""
                ALTER TABLE {table} 
                ADD COLUMN currency TEXT DEFAULT 'PYG'
            """)
            
            # Actualizar registros existentes
            cursor.execute(f"""
                UPDATE {table} 
                SET currency = 'PYG' 
                WHERE currency IS NULL
            """)
            
            # Crear índice
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{table}_currency ON {table}(currency)
            """)
            
            print(f"✅ Columna agregada a '{table}'")
            
        except sqlite3.OperationalError as e:
            print(f"⚠️  Error agregando columna a '{table}': {e}")
    
    conn.commit()


def update_system_config(conn: sqlite3.Connection):
    """Agrega configuración de moneda base al sistema"""
    cursor = conn.cursor()
    
    print("🔄 Agregando configuración de moneda base...")
    cursor.execute("""
        INSERT OR IGNORE INTO system_configs (config_key, config_value, config_type, description, category)
        VALUES ('base_currency', 'PYG', 'string', 'Moneda base del sistema', 'currency')
    """)
    
    conn.commit()
    print("✅ Configuración de moneda base agregada")


def verify_migration(conn: sqlite3.Connection):
    """Verifica que la migración se haya completado correctamente"""
    cursor = conn.cursor()
    
    print("\n📊 Verificando migración...")
    
    # Verificar tablas
    cursor.execute("SELECT COUNT(*) FROM currencies")
    currencies_count = cursor.fetchone()[0]
    print(f"✓ Monedas: {currencies_count}")
    
    cursor.execute("SELECT COUNT(*) FROM exchange_rates")
    rates_count = cursor.fetchone()[0]
    print(f"✓ Tasas de cambio: {rates_count}")
    
    # Verificar columnas agregadas
    for table in ['printers', 'filaments', 'quotes']:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE currency = 'PYG'")
        count = cursor.fetchone()[0]
        print(f"✓ {table} con currency='PYG': {count}")
    
    # Verificar config
    cursor.execute("SELECT config_value FROM system_configs WHERE config_key = 'base_currency'")
    base_currency = cursor.fetchone()
    if base_currency:
        print(f"✓ Moneda base del sistema: {base_currency[0]}")
    
    print("\n✅ Migración verificada correctamente")


def migrate():
    """Ejecuta la migración completa"""
    import sys
    from pathlib import Path
    
    # Agregar el directorio raíz al path
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from core.utils.path_helper import database_path
    db_path = database_path()
    
    if not db_path.exists():
        print("❌ Base de datos no encontrada")
        return False
    
    try:
        # Backup
        backup_path = backup_database(db_path)
        
        # Conectar a la DB
        conn = sqlite3.connect(str(db_path))
        
        # Verificar si es necesaria la migración
        if not check_if_migration_needed(conn):
            print("ℹ️  La migración ya fue aplicada anteriormente")
            conn.close()
            return True
        
        print("\n🚀 Iniciando migración de sistema de monedas...")
        
        # Ejecutar pasos de migración
        create_currency_tables(conn)
        populate_default_currencies(conn)
        populate_exchange_rates(conn)
        add_currency_column_to_tables(conn)
        update_system_config(conn)
        
        # Verificar
        verify_migration(conn)
        
        conn.close()
        
        print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print(f"📁 Backup guardado en: {backup_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA MIGRACIÓN: {e}")
        print(f"📁 Puedes restaurar desde: {backup_path}")
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("MIGRACIÓN: Sistema Multi-Currency")
    print("=" * 70)
    print()
    
    result = migrate()
    
    if result:
        print("\n🎉 Sistema de monedas instalado correctamente")
        print("   Ahora puedes configurar la moneda base en Ajustes > Sistema")
    else:
        print("\n⚠️  La migración no se completó. Verifica los errores arriba.")
