"""
Script de inicialización de la base de datos SQLite
"""

def get_database_schema() -> str:
    """
    Retorna el esquema completo de la base de datos (ESPEJO de voxeprint.db)
    """
    return """
    PRAGMA foreign_keys = ON;

    -- Configuraciones del sistema
    CREATE TABLE IF NOT EXISTS system_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_key TEXT UNIQUE NOT NULL,
        config_value TEXT NOT NULL,
        config_type TEXT DEFAULT 'string',
        description TEXT,
        category TEXT DEFAULT 'general',
        is_editable BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT (datetime('now', 'localtime')),
        updated_at DATETIME DEFAULT (datetime('now', 'localtime'))
    );

    -- Monedas del sistema
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
    );

    -- Tasas de cambio
    CREATE TABLE IF NOT EXISTS exchange_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        base_currency TEXT NOT NULL,
        target_currency TEXT NOT NULL,
        rate REAL NOT NULL,
        updated_at DATETIME DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (base_currency) REFERENCES currencies(code) ON DELETE CASCADE,
        FOREIGN KEY (target_currency) REFERENCES currencies(code) ON DELETE CASCADE,
        UNIQUE(base_currency, target_currency)
    );

    -- Clientes
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        ruc_ci TEXT,
        email TEXT,
        phone_number TEXT,
        is_default BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT (datetime('now', 'localtime')),
        updated_at DATETIME DEFAULT (datetime('now', 'localtime'))
    );

    -- Impresoras 3D (ESPEJO del esquema actual)
    CREATE TABLE IF NOT EXISTS printers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        brand TEXT,
        model TEXT,
        power_consumption_watts REAL DEFAULT 0.0,      -- NUEVO en DB actual
        purchase_cost REAL DEFAULT 0.0,
        maintenance_cost REAL DEFAULT 0.0,
        maintenance_interval_hours REAL DEFAULT 0.0,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT (datetime('now', 'localtime')),
        updated_at DATETIME DEFAULT (datetime('now', 'localtime')),
        useful_life_hours REAL DEFAULT 10000.0,        -- NUEVO en DB actual
        currency_code TEXT DEFAULT 'PYG',
        FOREIGN KEY (currency_code) REFERENCES currencies(code) ON DELETE SET DEFAULT
    );

    -- Filamentos
    CREATE TABLE IF NOT EXISTS filaments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        brand TEXT,
        color TEXT,
        weight_grams REAL DEFAULT 0.0,
        price_per_unit REAL DEFAULT 0.0,
        price_per_gram REAL DEFAULT 0.0,
        quantity_rolls INTEGER DEFAULT 0,
        current_stock_grams REAL DEFAULT 0.0,
        minimum_stock_grams REAL DEFAULT 0.0,
        is_active BOOLEAN DEFAULT 1,
        notes TEXT,
        created_at DATETIME DEFAULT (datetime('now', 'localtime')),
        updated_at DATETIME DEFAULT (datetime('now', 'localtime')),
        currency_code TEXT DEFAULT 'PYG',
        FOREIGN KEY (currency_code) REFERENCES currencies(code) ON DELETE SET DEFAULT
    );

    -- Rollos individuales de filamento
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

    -- Presupuestos
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quote_number TEXT UNIQUE NOT NULL,
        customer_id INTEGER,
        printer_id INTEGER,
        filament_id INTEGER,
        project_name TEXT,
        print_time_hours REAL DEFAULT 0.0,
        filament_weight_grams REAL DEFAULT 0.0,
        final_price REAL DEFAULT 0.0,
        file_path TEXT,
        notes TEXT,
        created_at DATETIME DEFAULT (datetime('now', 'localtime')),
        updated_at DATETIME DEFAULT (datetime('now', 'localtime')),
        currency_code TEXT DEFAULT 'PYG',
        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
        FOREIGN KEY (printer_id) REFERENCES printers(id) ON DELETE SET NULL,
        FOREIGN KEY (filament_id) REFERENCES filaments(id) ON DELETE SET NULL,
        FOREIGN KEY (currency_code) REFERENCES currencies(code) ON DELETE SET DEFAULT
    );

    -- Índices
    CREATE INDEX IF NOT EXISTS idx_customers_ruc_ci ON customers(ruc_ci);
    CREATE INDEX IF NOT EXISTS idx_customers_is_default ON customers(is_default);
    CREATE INDEX IF NOT EXISTS idx_printers_is_active ON printers(is_active);
    CREATE INDEX IF NOT EXISTS idx_printers_currency ON printers(currency_code);
    CREATE INDEX IF NOT EXISTS idx_filaments_type ON filaments(type);
    CREATE INDEX IF NOT EXISTS idx_filaments_is_active ON filaments(is_active);
    CREATE INDEX IF NOT EXISTS idx_filaments_currency ON filaments(currency_code);
    CREATE INDEX IF NOT EXISTS idx_filament_rolls_filament_id ON filament_rolls(filament_id);
    CREATE INDEX IF NOT EXISTS idx_filament_rolls_is_active ON filament_rolls(is_active);
    CREATE INDEX IF NOT EXISTS idx_quotes_customer_id ON quotes(customer_id);
    CREATE INDEX IF NOT EXISTS idx_quotes_created_at ON quotes(created_at);
    CREATE INDEX IF NOT EXISTS idx_quotes_currency ON quotes(currency_code);
    CREATE INDEX IF NOT EXISTS idx_currencies_is_active ON currencies(is_active);
    CREATE INDEX IF NOT EXISTS idx_exchange_rates_base ON exchange_rates(base_currency);
    CREATE INDEX IF NOT EXISTS idx_system_configs_key ON system_configs(config_key);
    CREATE INDEX IF NOT EXISTS idx_system_configs_category ON system_configs(category);

    -- Triggers updated_at
    CREATE TRIGGER IF NOT EXISTS customers_updated_at 
            AFTER UPDATE ON customers
            BEGIN
                UPDATE customers SET updated_at = datetime('now', 'localtime') WHERE id = NEW.id;
            END;
    CREATE TRIGGER IF NOT EXISTS printers_updated_at 
                AFTER UPDATE ON printers
            BEGIN
                UPDATE printers SET updated_at = datetime('now', 'localtime') WHERE id = NEW.id;
            END;
    CREATE TRIGGER IF NOT EXISTS quotes_updated_at 
            AFTER UPDATE ON quotes
            BEGIN
                UPDATE quotes SET updated_at = datetime('now', 'localtime') WHERE id = NEW.id;
            END;
    CREATE TRIGGER IF NOT EXISTS currencies_updated_at
            AFTER UPDATE ON currencies
            BEGIN
                UPDATE currencies SET updated_at = datetime('now', 'localtime') WHERE code = NEW.code;
            END;
    CREATE TRIGGER IF NOT EXISTS exchange_rates_updated_at
            AFTER UPDATE ON exchange_rates
            BEGIN
                UPDATE exchange_rates SET updated_at = datetime('now', 'localtime') WHERE id = NEW.id;
            END;
    CREATE TRIGGER IF NOT EXISTS system_configs_updated_at 
            AFTER UPDATE ON system_configs
            BEGIN
                UPDATE system_configs SET updated_at = datetime('now', 'localtime') WHERE id = NEW.id;
            END;
    CREATE TRIGGER IF NOT EXISTS filaments_updated_at 
            AFTER UPDATE ON filaments
            FOR EACH ROW
            WHEN NEW.updated_at = OLD.updated_at  -- Solo si no se cambió manualmente
            BEGIN
                UPDATE filaments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
    CREATE TRIGGER IF NOT EXISTS filaments_calculate_price_per_gram_insert
            AFTER INSERT ON filaments
            FOR EACH ROW
            WHEN NEW.weight_grams > 0 AND NEW.price_per_unit > 0
            BEGIN
                UPDATE filaments 
                SET price_per_gram = NEW.price_per_unit / NEW.weight_grams
                WHERE id = NEW.id;
            END;
    CREATE TRIGGER IF NOT EXISTS filaments_calculate_price_per_gram_update
            AFTER UPDATE ON filaments
            FOR EACH ROW
            WHEN (NEW.weight_grams <> OLD.weight_grams OR NEW.price_per_unit <> OLD.price_per_unit)
            AND NEW.weight_grams > 0 AND NEW.price_per_unit > 0
            BEGIN
                UPDATE filaments 
                SET price_per_gram = NEW.price_per_unit / NEW.weight_grams,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.id;
        END;

    -- Triggers para filament_rolls: auto-calcular price_per_gram
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


def get_initial_data() -> str:
    """
    Retorna los datos iniciales para la base de datos (coherentes con el esquema actual)
    """
    return """
    -- Cliente predeterminado (solo insertar si no existe ninguno)
    INSERT INTO customers (full_name, ruc_ci, is_default) 
    SELECT 'Sin Nombre', 'X', 1
    WHERE NOT EXISTS (SELECT 1 FROM customers LIMIT 1);

    -- Monedas por defecto
    INSERT OR IGNORE INTO currencies (code, symbol, name, decimals, thousands_sep, decimal_sep, symbol_position, space_between, is_active) VALUES
    ('PYG', '₲', 'Guaraní Paraguayo', 0, '.', '', 'prefix', 1, 1),
    ('USD', '$', 'Dólar Estadounidense', 2, ',', '.', 'prefix', 0, 1),
    ('EUR', '€', 'Euro', 2, '.', ',', 'suffix', 1, 1),
    ('ARS', '$', 'Peso Argentino', 2, '.', ',', 'prefix', 1, 1),
    ('BRL', 'R$', 'Real Brasileño', 2, '.', ',', 'prefix', 1, 1),
    ('CAD', 'C$', 'Dólar Canadiense', 2, ',', '.', 'prefix', 0, 0),
    ('COP', '$', 'Peso Colombiano', 0, '.', ',', 'prefix', 1, 0),
    ('NIO', 'C$', 'Córdoba Nicaragüense', 2, ',', '.', 'prefix', 0, 0),
    ('MXN', '$', 'Peso Mexicano', 2, ',', '.', 'prefix', 0, 0),
    ('PEN', 'S/', 'Sol Peruano', 2, ',', '.', 'prefix', 0, 0),
    ('HNL', 'L', 'Lempira Hondureño', 2, ',', '.', 'prefix', 0, 0),
    ('CLP', '$', 'Peso Chileno', 0, '.', ',', 'prefix', 0, 0),
    ('BOB', 'Bs.', 'Boliviano', 2, ',', '.', 'prefix', 0, 0),
    ('UYU', '$U', 'Peso Uruguayo', 2, '.', ',', 'prefix', 0, 0);

    -- Tasas de cambio por defecto - Sistema Pivote USD
    -- Solo se almacenan conversiones desde USD, las demás se calculan automáticamente
    INSERT OR IGNORE INTO exchange_rates (base_currency, target_currency, rate) VALUES
    ('USD', 'PYG', 6709.36),
    ('USD', 'EUR', 0.87),
    ('USD', 'ARS', 1451.50),
    ('USD', 'BRL', 5.52),
    ('USD', 'CAD', 1.38),
    ('USD', 'COP', 4260.0),
    ('USD', 'NIO', 36.75),
    ('USD', 'MXN', 17.20),
    ('USD', 'PEN', 3.77),
    ('USD', 'HNL', 25.85),
    ('USD', 'CLP', 957.0),
    ('USD', 'BOB', 6.91),
    ('USD', 'UYU', 40.50);

    -- Configuraciones iniciales del sistema
    INSERT OR IGNORE INTO system_configs (config_key, config_value, config_type, description, category) VALUES
    ('base_currency', 'PYG', 'string', 'Moneda base del sistema', 'currency'),
    ('electricity_rate', '435.0', 'float', 'Tarifa eléctrica por kWh', 'costs'),
    ('default_profit_margin', '35.0', 'float', 'Margen de ganancia por defecto (%)', 'costs'),
    ('default_failure_margin', '5.0', 'float', 'Margen de error/fallos por defecto (%)', 'costs'),
    ('tax_rate', '10.0', 'float', 'Tasa de impuesto (%)', 'costs'),
    ('currency_symbol', 'Gs.', 'string', 'Símbolo de moneda', 'general'),
    ('company_name', 'VoxePrint', 'string', 'Nombre de la empresa', 'general'),
    ('company_address', 'Direccion', 'string', 'Dirección de la empresa', 'general'),
    ('company_phone', '+595981234567', 'string', 'Teléfono de la empresa', 'general'),
    ('company_email', 'Voxeprint@mail.com', 'string', 'Email de la empresa', 'general'),
    ('company_city', 'Ciudad', 'string', 'Ciudad de la empresa', 'general'),
    ('company_website', 'Voxeprint.com', 'string', 'Sitio web de la empresa', 'general'),
    ('include_iva', 'True', 'bool', 'Si los totales incluyen IVA', 'costs'),
    ('auto_save_interval', '300', 'int', 'Intervalo de guardado automático (segundos)', 'system'),
    ('backup_enabled', 'True', 'bool', 'Habilitar respaldos automáticos', 'system'),
    ('backup_frequency', '7', 'int', 'Frecuencia de respaldo (días)', 'system'),
    ('pivot_currency', 'USD', 'string', 'Moneda pivote para conversiones (sistema FinTech)', 'currency');

    -- Alias opcional (si quisieras que convivan ambos nombres)
    INSERT OR IGNORE INTO system_configs (config_key, config_value, config_type, description, category)
    SELECT 'electricity_rate_per_kwh', config_value, 'float', 'Alias de tarifa eléctrica por kWh', 'costs'
    FROM system_configs WHERE config_key = 'electricity_rate' LIMIT 1;
    """
