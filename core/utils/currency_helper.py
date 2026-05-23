"""
Helper para formateo, conversión y manejo de monedas

Este módulo proporciona utilidades centralizadas para trabajar con múltiples monedas
en el sistema, incluyendo formateo, validación, conversión entre monedas y manejo
de tasas de cambio.
"""
from typing import Dict, Any, Optional, List
import sqlite3
from pathlib import Path
from core.utils.logger import logger


class CurrencyHelper:
    """Helper para formateo y conversión de valores monetarios"""
    
    # Cache de configuraciones de monedas (se carga desde DB)
    _currency_cache: Dict[str, Dict[str, Any]] = {}
    _exchange_rates_cache: Dict[tuple, float] = {}
    _db_path: Optional[Path] = None
    
    @classmethod
    def _get_db_connection(cls):
        """Obtiene conexión a la base de datos"""
        if cls._db_path is None:
            from core.utils.path_helper import database_path
            cls._db_path = database_path()
        return sqlite3.connect(str(cls._db_path))
    
    @classmethod
    def _load_currency_from_db(cls, currency_code: str) -> Optional[Dict[str, Any]]:
        """Carga configuración de una moneda desde la DB"""
        try:
            conn = cls._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT code, symbol, name, decimals, thousands_sep, decimal_sep, 
                       symbol_position, space_between, is_active
                FROM currencies
                WHERE code = ?
            """, (currency_code,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "code": row[0],
                    "symbol": row[1],
                    "name": row[2],
                    "decimals": row[3],
                    "thousands_sep": row[4],
                    "decimal_sep": row[5],
                    "symbol_position": row[6],
                    "space_between": bool(row[7]),
                    "is_active": bool(row[8])
                }
        except Exception as e:
            logger.error("CurrencyHelper", f"Error cargando moneda {currency_code}: {e}")
            logger.log_exception("CurrencyHelper", e, "_load_currency_from_db")
        return None
    
    @classmethod
    def _get_currency_config(cls, currency_code: str) -> Dict[str, Any]:
        """Obtiene configuración de una moneda (con cache)"""
        if currency_code not in cls._currency_cache:
            config = cls._load_currency_from_db(currency_code)
            if config:
                cls._currency_cache[currency_code] = config
            else:
                # Fallback a PYG por defecto
                return {
                    "code": "PYG",
                    "symbol": "Gs.",
                    "name": "Guaraní Paraguayo",
                    "decimals": 0,
                    "thousands_sep": ".",
                    "decimal_sep": "",
                    "symbol_position": "prefix",
                    "space_between": True,
                    "is_active": True
                }
        return cls._currency_cache[currency_code]
    
    @classmethod
    def clear_cache(cls):
        """Limpia el cache de monedas (útil después de actualizar monedas)"""
        cls._currency_cache.clear()
        cls._exchange_rates_cache.clear()
    
    @staticmethod
    def format(amount: float, currency: str = "PYG", include_symbol: bool = True) -> str:
        """
        Formatea un monto según la moneda especificada
        
        Args:
            amount: Monto a formatear
            currency: Código de moneda (PYG, USD, EUR, etc.)
            include_symbol: Si incluir el símbolo de moneda
            
        Returns:
            String formateado según las reglas de la moneda
            
        Examples:
            >>> CurrencyHelper.format(150000, "PYG")
            'Gs. 150.000'
            >>> CurrencyHelper.format(150.50, "USD")
            '$150.50'
            >>> CurrencyHelper.format(150.50, "EUR")
            '150,50 €'
        """
        config = CurrencyHelper._get_currency_config(currency)
        
        # Formatear número con decimales
        if config["decimals"] == 0:
            formatted_number = f"{int(round(amount))}"
        else:
            formatted_number = f"{amount:.{config['decimals']}f}"
        
        # Separar parte entera y decimal
        parts = formatted_number.split('.')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else ""
        
        # Agregar separador de miles
        if len(integer_part) > 3:
            # Insertar separador cada 3 dígitos desde la derecha
            reversed_int = integer_part[::-1]
            chunks = [reversed_int[i:i+3] for i in range(0, len(reversed_int), 3)]
            integer_part = config["thousands_sep"].join(chunks)[::-1]
        
        # Unir parte entera y decimal
        if decimal_part and config["decimal_sep"]:
            formatted_number = f"{integer_part}{config['decimal_sep']}{decimal_part}"
        else:
            formatted_number = integer_part
        
        # Agregar símbolo si se solicita
        if not include_symbol:
            return formatted_number
        
        symbol = config["symbol"]
        space = " " if config["space_between"] else ""
        
        if config["symbol_position"] == "prefix":
            return f"{symbol}{space}{formatted_number}"
        else:
            return f"{formatted_number}{space}{symbol}"
    
    @staticmethod
    def get_symbol(currency: str = "PYG") -> str:
        """
        Obtiene el símbolo de una moneda
        
        Args:
            currency: Código de moneda
            
        Returns:
            Símbolo de la moneda
        """
        config = CurrencyHelper._get_currency_config(currency)
        return config["symbol"]
    
    @staticmethod
    def get_decimals(currency: str = "PYG") -> int:
        """
        Obtiene la cantidad de decimales para una moneda
        
        Args:
            currency: Código de moneda
            
        Returns:
            Cantidad de decimales (0 para PYG, 2 para USD/EUR)
        """
        config = CurrencyHelper._get_currency_config(currency)
        return config["decimals"]
    
    @staticmethod
    def get_name(currency: str = "PYG") -> str:
        """
        Obtiene el nombre de la moneda
        
        Args:
            currency: Código de moneda
            
        Returns:
            Nombre de la moneda
        """
        config = CurrencyHelper._get_currency_config(currency)
        return config["name"]
    
    @staticmethod
    def get_label_with_currency(label: str, currency: str = "PYG") -> str:
        """
        Genera un label con el símbolo de moneda incorporado
        
        Args:
            label: Label base (ej: "Precio", "Total")
            currency: Código de moneda
            
        Returns:
            Label con moneda (ej: "Precio (Gs.)", "Total ($)")
            
        Examples:
            >>> CurrencyHelper.get_label_with_currency("Precio", "PYG")
            'Precio (Gs.)'
            >>> CurrencyHelper.get_label_with_currency("Total", "USD")
            'Total ($)'
        """
        symbol = CurrencyHelper.get_symbol(currency)
        return f"{label} ({symbol})"
    
    @staticmethod
    def get_validator_params(currency: str = "PYG") -> Dict[str, Any]:
        """
        Obtiene parámetros para QDoubleValidator según la moneda
        
        Args:
            currency: Código de moneda
            
        Returns:
            Dict con min, max y decimals para QDoubleValidator
            
        Example:
            >>> params = CurrencyHelper.get_validator_params("USD")
            >>> validator = QDoubleValidator(params["min"], params["max"], params["decimals"])
        """
        decimals = CurrencyHelper.get_decimals(currency)
        return {
            "min": 0.0,
            "max": 999999999.0,
            "decimals": decimals
        }
    
    @staticmethod
    def parse_input(text: str, currency: str = "PYG") -> float:
        """
        Parsea un input de texto a número según la moneda
        
        Args:
            text: Texto ingresado por el usuario
            currency: Código de moneda
            
        Returns:
            Valor numérico parseado
            
        Examples:
            >>> CurrencyHelper.parse_input("150.000", "PYG")
            150000.0
            >>> CurrencyHelper.parse_input("150.50", "USD")
            150.50
            >>> CurrencyHelper.parse_input("150,50", "EUR")
            150.50
        """
        config = CurrencyHelper._get_currency_config(currency)
        
        # Remover símbolo si está presente
        text = text.replace(config["symbol"], "").strip()
        
        # Remover separador de miles
        text = text.replace(config["thousands_sep"], "")
        
        # Reemplazar separador decimal por punto
        if config["decimal_sep"]:
            text = text.replace(config["decimal_sep"], ".")
        
        try:
            return float(text)
        except ValueError:
            return 0.0
    
    @classmethod
    def get_exchange_rate(cls, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Obtiene la tasa de cambio entre dos monedas usando sistema pivote USD.
        
        Sistema FinTech estándar:
        - Todas las tasas se guardan desde USD (moneda pivote)
        - Conversiones indirectas se calculan automáticamente
        - Ejemplo: EUR → PYG = (EUR → USD) * (USD → PYG)
        
        Args:
            from_currency: Código de moneda origen
            to_currency: Código de moneda destino
            
        Returns:
            Tasa de cambio o None si no existe
            
        Example:
            >>> rate = CurrencyHelper.get_exchange_rate("USD", "PYG")
            >>> print(rate)  # 7500.0 (directo desde BD)
            
            >>> rate = CurrencyHelper.get_exchange_rate("EUR", "PYG") 
            >>> print(rate)  # Calculado: (1/0.92) * 7500 = 8152.17
        """
        if from_currency == to_currency:
            return 1.0
        
        # Buscar en cache
        cache_key = (from_currency, to_currency)
        if cache_key in cls._exchange_rates_cache:
            return cls._exchange_rates_cache[cache_key]
        
        # Moneda pivote (siempre USD)
        PIVOT = "USD"
        
        try:
            conn = cls._get_db_connection()
            cursor = conn.cursor()
            
            # Caso 1: Conversión directa desde el pivote (USD → X)
            if from_currency == PIVOT:
                cursor.execute("""
                    SELECT rate FROM exchange_rates
                    WHERE base_currency = ? AND target_currency = ?
                """, (PIVOT, to_currency))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    rate = float(row[0])
                    cls._exchange_rates_cache[cache_key] = rate
                    return rate
                return None
            
            # Caso 2: Conversión directa hacia el pivote (X → USD)
            if to_currency == PIVOT:
                cursor.execute("""
                    SELECT rate FROM exchange_rates
                    WHERE base_currency = ? AND target_currency = ?
                """, (PIVOT, from_currency))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    # Invertir la tasa: si USD→EUR = 0.92, entonces EUR→USD = 1/0.92
                    usd_to_from = float(row[0])
                    if usd_to_from == 0:
                        return None
                    rate = 1.0 / usd_to_from
                    cls._exchange_rates_cache[cache_key] = rate
                    return rate
                return None
            
            # Caso 3: Conversión indirecta (X → Y) a través del pivote USD
            # Necesitamos: USD→X y USD→Y
            cursor.execute("""
                SELECT rate FROM exchange_rates
                WHERE base_currency = ? AND target_currency = ?
            """, (PIVOT, from_currency))
            row_from = cursor.fetchone()
            
            cursor.execute("""
                SELECT rate FROM exchange_rates
                WHERE base_currency = ? AND target_currency = ?
            """, (PIVOT, to_currency))
            row_to = cursor.fetchone()
            
            conn.close()
            
            if row_from and row_to:
                usd_to_from = float(row_from[0])  # USD → from
                usd_to_to = float(row_to[0])      # USD → to
                
                if usd_to_from == 0:
                    return None
                
                # from → USD → to
                # from → USD = 1 / (USD → from)
                # (from → USD) * (USD → to) = rate
                rate = (1.0 / usd_to_from) * usd_to_to
                cls._exchange_rates_cache[cache_key] = rate
                return rate
            
            return None
            
        except Exception as e:
            logger.error("CurrencyHelper", f"Error obteniendo tasa de cambio {from_currency} → {to_currency}: {e}")
            logger.log_exception("CurrencyHelper", e, "get_exchange_rate")
            return None
    
    @classmethod
    def convert(cls, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Convierte un monto de una moneda a otra
        
        Args:
            amount: Monto a convertir
            from_currency: Código de moneda origen
            to_currency: Código de moneda destino
            
        Returns:
            Monto convertido o None si no hay tasa de cambio
            
        Example:
            >>> converted = CurrencyHelper.convert(100, "USD", "PYG")
            >>> print(converted)  # 670936.0
        """
        if from_currency == to_currency:
            return amount
        
        rate = cls.get_exchange_rate(from_currency, to_currency)
        if rate is not None:
            return amount * rate
        
        return None
    
    @classmethod
    def update_exchange_rate(cls, base_currency: str, target_currency: str, rate: float) -> bool:
        """
        Actualiza o inserta una tasa de cambio
        
        Args:
            base_currency: Código de moneda base
            target_currency: Código de moneda objetivo
            rate: Nueva tasa de cambio
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            conn = cls._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO exchange_rates (base_currency, target_currency, rate, updated_at)
                VALUES (?, ?, ?, datetime('now', 'localtime'))
            """, (base_currency, target_currency, rate))
            conn.commit()
            conn.close()
            
            # Actualizar cache
            cls._exchange_rates_cache[(base_currency, target_currency)] = rate
            return True
        except Exception as e:
            logger.error("CurrencyHelper", f"Error actualizando tasa de cambio: {e}")
            logger.log_exception("CurrencyHelper", e, "set_exchange_rate")
            return False
    
    @classmethod
    def get_all_active_currencies(cls) -> List[Dict[str, Any]]:
        """
        Obtiene lista de todas las monedas activas
        
        Returns:
            Lista de diccionarios con información de monedas
        """
        try:
            conn = cls._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT code, symbol, name, decimals, is_active
                FROM currencies
                WHERE is_active = 1
                ORDER BY code
            """)
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "code": row[0],
                    "symbol": row[1],
                    "name": row[2],
                    "decimals": row[3],
                    "is_active": bool(row[4])
                }
                for row in rows
            ]
        except Exception as e:
            logger.error("CurrencyHelper", f"Error obteniendo monedas activas: {e}")
            logger.log_exception("CurrencyHelper", e, "get_all_active_currencies")
            return []
    
    @classmethod
    def get_currency_display_name(cls, currency: str = "PYG") -> str:
        """
        Obtiene nombre completo de la moneda para mostrar en UI
        
        Args:
            currency: Código de moneda
            
        Returns:
            Nombre completo (ej: "Guaraní Paraguayo (Gs.)")
        """
        config = cls._get_currency_config(currency)
        return f"{config['name']} ({config['symbol']})"
    
    @staticmethod
    def is_valid_currency(currency: str) -> bool:
        """
        Verifica si un código de moneda es válido y está activo
        
        Args:
            currency: Código de moneda a validar
            
        Returns:
            True si es válido, False en caso contrario
        """
        config = CurrencyHelper._get_currency_config(currency)
        return config.get("is_active", False)
    
    # ===== MÉTODOS PARA INTEGRACIÓN CON CURRENCYMANAGER =====
    
    @classmethod
    def get_current_currency(cls) -> str:
        """
        Obtiene el código de la moneda actual del sistema
        
        Returns:
            Código de moneda actual (ej: "PYG", "USD")
            
        Example:
            >>> current = CurrencyHelper.get_current_currency()
            >>> print(current)  # "PYG"
        """
        from core.managers.currency_manager import CurrencyManager
        return CurrencyManager().get_current_currency()
    
    @classmethod
    def format_with_current_currency(cls, amount: float, include_symbol: bool = True) -> str:
        """
        Formatea un monto usando la moneda actual del sistema
        
        Args:
            amount: Monto a formatear
            include_symbol: Si incluir el símbolo de moneda
            
        Returns:
            String formateado según la moneda actual
            
        Example:
            >>> # Si la moneda actual es PYG
            >>> CurrencyHelper.format_with_current_currency(150000)
            'Gs. 150.000'
        """
        current_currency = cls.get_current_currency()
        return cls.format(amount, current_currency, include_symbol)
    
    @classmethod
    def get_suffix_for_spinbox(cls, currency_code: str = None) -> str:
        """
        Obtiene el sufijo apropiado para un QDoubleSpinBox
        
        Args:
            currency_code: Código de moneda (None para usar actual)
            
        Returns:
            Sufijo con espacio si es necesario (ej: " Gs.", " $", " €")
            
        Example:
            >>> suffix = CurrencyHelper.get_suffix_for_spinbox("PYG")
            >>> spinbox.setSuffix(suffix)  # " Gs."
        """
        if currency_code is None:
            currency_code = cls.get_current_currency()
        
        config = cls._get_currency_config(currency_code)
        symbol = config["symbol"]
        
        # Solo agregar sufijo si el símbolo va después del número
        if config["symbol_position"] == "suffix":
            space = " " if config["space_between"] else ""
            return f"{space}{symbol}"
        
        # Si va como prefijo, retornar vacío (el prefijo se maneja en el label)
        return ""
    
    @classmethod
    def get_prefix_for_spinbox(cls, currency_code: str = None) -> str:
        """
        Obtiene el prefijo apropiado para un QDoubleSpinBox
        
        Args:
            currency_code: Código de moneda (None para usar actual)
            
        Returns:
            Prefijo con espacio si es necesario (ej: "Gs. ", "$ ", "")
            
        Example:
            >>> prefix = CurrencyHelper.get_prefix_for_spinbox("USD")
            >>> spinbox.setPrefix(prefix)  # "$ "
        """
        if currency_code is None:
            currency_code = cls.get_current_currency()
        
        config = cls._get_currency_config(currency_code)
        symbol = config["symbol"]
        
        # Solo agregar prefijo si el símbolo va antes del número
        if config["symbol_position"] == "prefix":
            space = " " if config["space_between"] else ""
            return f"{symbol}{space}"
        
        # Si va como sufijo, retornar vacío
        return ""
    
    @classmethod
    def configure_spinbox(cls, spinbox, currency_code: str = None):
        """
        Configura un QDoubleSpinBox con la moneda especificada
        
        Args:
            spinbox: QDoubleSpinBox a configurar
            currency_code: Código de moneda (None para usar actual)
            
        Example:
            >>> from PySide6.QtWidgets import QDoubleSpinBox
            >>> spinbox = QDoubleSpinBox()
            >>> CurrencyHelper.configure_spinbox(spinbox, "USD")
            # spinbox ahora tiene 2 decimales y prefijo "$ "
        """
        if currency_code is None:
            currency_code = cls.get_current_currency()
        
        config = cls._get_currency_config(currency_code)
        
        # Configurar decimales
        spinbox.setDecimals(config["decimals"])
        
        # Configurar prefijo/sufijo según posición del símbolo
        if config["symbol_position"] == "prefix":
            prefix = cls.get_prefix_for_spinbox(currency_code)
            spinbox.setPrefix(prefix)
            spinbox.setSuffix("")
        else:
            suffix = cls.get_suffix_for_spinbox(currency_code)
            spinbox.setPrefix("")
            spinbox.setSuffix(suffix)
