"""
Migración: Agregar monedas LATAM adicionales

Fecha: mayo 2026
Versión: 1.4.0

Agrega las siguientes monedas al sistema:
  CAD - Dólar Canadiense
  COP - Peso Colombiano
  NIO - Córdoba Nicaragüense
  MXN - Peso Mexicano
  PEN - Sol Peruano
  HNL - Lempira Hondureño
  CLP - Peso Chileno
  BOB - Boliviano
  UYU - Peso Uruguayo

También agrega la tasa de cambio USD→X para cada moneda nueva
(las inversas y cruces se calculan automáticamente por el sistema pivote).

NOTA: Las tasas son valores de referencia. El usuario debe actualizarlas
en Configuraciones → Tasas de Cambio antes de usarlas en producción.
"""
import sqlite3
from pathlib import Path


NEW_CURRENCIES = [
    # (code, symbol, name, decimals, thousands_sep, decimal_sep, symbol_position, space_between, is_active)
    ('CAD', 'C$',   'Dólar Canadiense',       2, ',', '.', 'prefix', 0, 0),
    ('COP', '$',    'Peso Colombiano',         0, '.', ',', 'prefix', 1, 0),
    ('NIO', 'C$',   'Córdoba Nicaragüense',    2, ',', '.', 'prefix', 0, 0),
    ('MXN', '$',    'Peso Mexicano',           2, ',', '.', 'prefix', 0, 0),
    ('PEN', 'S/',   'Sol Peruano',             2, ',', '.', 'prefix', 0, 0),
    ('HNL', 'L',    'Lempira Hondureño',       2, ',', '.', 'prefix', 0, 0),
    ('CLP', '$',    'Peso Chileno',            0, '.', ',', 'prefix', 0, 0),
    ('BOB', 'Bs.',  'Boliviano',               2, ',', '.', 'prefix', 0, 0),
    ('UYU', '$U',   'Peso Uruguayo',           2, '.', ',', 'prefix', 0, 0),
]

# Solo tasas USD → nueva moneda (el sistema calcula cruces e inversas)
# Valores de referencia — actualizar en el diálogo de Tasas de Cambio
NEW_EXCHANGE_RATES = [
    ('USD', 'CAD', 1.38),
    ('USD', 'COP', 4260.0),
    ('USD', 'NIO', 36.75),
    ('USD', 'MXN', 17.20),
    ('USD', 'PEN', 3.77),
    ('USD', 'HNL', 25.85),
    ('USD', 'CLP', 957.0),
    ('USD', 'BOB', 6.91),
    ('USD', 'UYU', 40.50),
]


def check_if_needed(conn: sqlite3.Connection) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM currencies WHERE code IN ('CAD','COP','NIO','MXN','PEN','HNL','CLP','BOB','UYU')")
    existing = cursor.fetchone()[0]
    if existing == len(NEW_CURRENCIES):
        print("ℹ️  Las monedas LATAM ya existen — migración no necesaria")
        return False
    return True


def add_currencies(conn: sqlite3.Connection):
    cursor = conn.cursor()
    print("🔄 Insertando monedas LATAM...")
    cursor.executemany("""
        INSERT OR IGNORE INTO currencies
        (code, symbol, name, decimals, thousands_sep, decimal_sep, symbol_position, space_between, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, NEW_CURRENCIES)
    conn.commit()
    print(f"✅ {cursor.rowcount} monedas nuevas insertadas (inactivas por defecto)")


def add_exchange_rates(conn: sqlite3.Connection):
    cursor = conn.cursor()
    print("🔄 Insertando tasas de cambio USD → monedas LATAM...")
    cursor.executemany("""
        INSERT OR IGNORE INTO exchange_rates (base_currency, target_currency, rate)
        VALUES (?, ?, ?)
    """, NEW_EXCHANGE_RATES)
    conn.commit()
    print(f"✅ {cursor.rowcount} tasas de cambio insertadas")


def migrate():
    import sys
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

    from core.utils.path_helper import database_path
    db_path = database_path()

    if not db_path.exists():
        print("❌ Base de datos no encontrada")
        return False

    conn = None
    try:
        conn = sqlite3.connect(str(db_path))

        if not check_if_needed(conn):
            conn.close()
            return True

        print("\n🚀 Iniciando migración: Monedas LATAM...")
        add_currencies(conn)
        add_exchange_rates(conn)

        conn.close()
        print("\n✅ MIGRACIÓN COMPLETADA — Activá las monedas en Configuraciones → Tasas de Cambio")
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Monedas LATAM adicionales")
    print("=" * 60)
    migrate()
