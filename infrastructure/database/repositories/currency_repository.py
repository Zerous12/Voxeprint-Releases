"""
Repositorio para gestión de Monedas (Currency)
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from domain.models.currency import Currency
from infrastructure.database.connection import DatabaseConnection
from core.utils.logger import logger


class CurrencyRepository:
    """Repositorio para operaciones CRUD de monedas"""
    
    def __init__(self):
        self.db_conn = DatabaseConnection()
    
    def get_all(self) -> List[Currency]:
        """Obtiene todas las monedas"""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT code, symbol, name, decimals, thousands_sep, decimal_sep,
                       symbol_position, space_between, is_active, created_at, updated_at
                FROM currencies
                ORDER BY code
            """)
            rows = cursor.fetchall()
            
            return [self._row_to_currency(row) for row in rows]
    
    def get_active(self) -> List[Currency]:
        """Obtiene solo las monedas activas"""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT code, symbol, name, decimals, thousands_sep, decimal_sep,
                       symbol_position, space_between, is_active, created_at, updated_at
                FROM currencies
                WHERE is_active = 1
                ORDER BY code
            """)
            rows = cursor.fetchall()
            
            return [self._row_to_currency(row) for row in rows]
    
    def get_by_code(self, code: str) -> Optional[Currency]:
        """Obtiene una moneda por su código"""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT code, symbol, name, decimals, thousands_sep, decimal_sep,
                       symbol_position, space_between, is_active, created_at, updated_at
                FROM currencies
                WHERE code = ?
            """, (code,))
            row = cursor.fetchone()
            
            return self._row_to_currency(row) if row else None
    
    def create(self, currency: Currency) -> bool:
        """Crea una nueva moneda"""
        try:
            with self.db_conn.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO currencies (
                        code, symbol, name, decimals, thousands_sep, decimal_sep,
                        symbol_position, space_between, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    currency.code,
                    currency.symbol,
                    currency.name,
                    currency.decimals,
                    currency.thousands_sep,
                    currency.decimal_sep,
                    currency.symbol_position,
                    1 if currency.space_between else 0,
                    1 if currency.is_active else 0
                ))
            return True
        except sqlite3.IntegrityError:
            logger.warning("CurrencyRepository", f"La moneda {currency.code} ya existe")
            return False
        except Exception as e:
            logger.error("CurrencyRepository", f"Error creando moneda: {e}")
            return False
    
    def update(self, currency: Currency) -> bool:
        """Actualiza una moneda existente"""
        try:
            with self.db_conn.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE currencies
                    SET symbol = ?, name = ?, decimals = ?, thousands_sep = ?,
                        decimal_sep = ?, symbol_position = ?, space_between = ?,
                        is_active = ?
                    WHERE code = ?
                """, (
                    currency.symbol,
                    currency.name,
                    currency.decimals,
                    currency.thousands_sep,
                    currency.decimal_sep,
                    currency.symbol_position,
                    1 if currency.space_between else 0,
                    1 if currency.is_active else 0,
                    currency.code
                ))
            return True
        except Exception as e:
            logger.error("CurrencyRepository", f"Error actualizando moneda: {e}")
            return False
    
    def delete(self, code: str) -> bool:
        """Elimina una moneda (solo si no está en uso)"""
        try:
            with self.db_conn.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM currencies WHERE code = ?", (code,))
            return True
        except sqlite3.IntegrityError:
            logger.warning("CurrencyRepository", f"No se puede eliminar la moneda {code} porque está en uso")
            return False
        except Exception as e:
            logger.error("CurrencyRepository", f"Error eliminando moneda: {e}")
            return False
    
    def toggle_active(self, code: str) -> bool:
        """Activa/desactiva una moneda"""
        try:
            with self.db_conn.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE currencies
                    SET is_active = NOT is_active
                    WHERE code = ?
                """, (code,))
            return True
        except Exception as e:
            logger.error("CurrencyRepository", f"Error cambiando estado de moneda: {e}")
            return False
    
    def update_active_status(self, code: str, is_active: bool) -> bool:
        """Establece el estado activo/inactivo de una moneda"""
        try:
            with self.db_conn.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE currencies
                    SET is_active = ?
                    WHERE code = ?
                """, (1 if is_active else 0, code))
            return True
        except Exception as e:
            logger.error("CurrencyRepository", f"Error actualizando estado de moneda {code}: {e}")
            return False
    
    def _row_to_currency(self, row) -> Currency:
        """Convierte una fila de la DB a objeto Currency"""
        return Currency(
            code=row[0],
            symbol=row[1],
            name=row[2],
            decimals=row[3],
            thousands_sep=row[4],
            decimal_sep=row[5],
            symbol_position=row[6],
            space_between=bool(row[7]),
            is_active=bool(row[8]),
            created_at=row[9],
            updated_at=row[10]
        )
