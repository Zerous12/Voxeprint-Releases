"""
Repositorio para gestión de Tasas de Cambio (ExchangeRate)
"""
import sqlite3
from typing import List, Optional, Dict
from datetime import datetime

from domain.models.currency import ExchangeRate
from infrastructure.database.connection import DatabaseConnection
from core.utils.logger import logger


class ExchangeRateRepository:
    """Repositorio para operaciones CRUD de tasas de cambio"""
    
    def __init__(self):
        self.db_conn = DatabaseConnection()
    
    def get_all(self) -> List[ExchangeRate]:
        """Obtiene todas las tasas de cambio"""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, base_currency, target_currency, rate, updated_at
                FROM exchange_rates
                ORDER BY base_currency, target_currency
            """)
            rows = cursor.fetchall()
            
            return [self._row_to_exchange_rate(row) for row in rows]
    
    def get_by_currencies(self, base_currency: str, target_currency: str) -> Optional[ExchangeRate]:
        """Obtiene tasa de cambio entre dos monedas"""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, base_currency, target_currency, rate, updated_at
                FROM exchange_rates
                WHERE base_currency = ? AND target_currency = ?
            """, (base_currency, target_currency))
            row = cursor.fetchone()
            
            return self._row_to_exchange_rate(row) if row else None
    
    def get_by_base_currency(self, base_currency: str) -> List[ExchangeRate]:
        """Obtiene todas las tasas de cambio para una moneda base"""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, base_currency, target_currency, rate, updated_at
                FROM exchange_rates
                WHERE base_currency = ?
                ORDER BY target_currency
            """, (base_currency,))
            rows = cursor.fetchall()
            
            return [self._row_to_exchange_rate(row) for row in rows]
    
    def upsert(self, exchange_rate: ExchangeRate) -> bool:
        """Inserta o actualiza una tasa de cambio"""
        try:
            with self.db_conn.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO exchange_rates (
                        base_currency, target_currency, rate
                    ) VALUES (?, ?, ?)
                """, (
                    exchange_rate.base_currency,
                    exchange_rate.target_currency,
                    exchange_rate.rate
                ))
            return True
        except Exception as e:
            logger.error("ExchangeRateRepository", f"Error guardando tasa de cambio: {e}")
            return False
    
    def update_rate(self, base_currency: str, target_currency: str, new_rate: float) -> bool:
        """Actualiza o crea una tasa de cambio"""
        try:
            with self.db_conn.get_connection() as conn:
                cursor = conn.cursor()
                # Usar INSERT OR REPLACE para crear si no existe
                cursor.execute("""
                    INSERT OR REPLACE INTO exchange_rates (
                        base_currency, target_currency, rate, updated_at
                    ) VALUES (?, ?, ?, datetime('now', 'localtime'))
                """, (base_currency, target_currency, new_rate))
                return True
        except Exception as e:
            logger.error("ExchangeRateRepository", f"Error actualizando/creando tasa: {e}")
            return False
    
    def delete(self, base_currency: str, target_currency: str) -> bool:
        """Elimina una tasa de cambio"""
        try:
            with self.db_conn.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM exchange_rates
                    WHERE base_currency = ? AND target_currency = ?
                """, (base_currency, target_currency))
            return True
        except Exception as e:
            logger.error("ExchangeRateRepository", f"Error eliminando tasa: {e}")
            return False
    
    def recalculate_rates(self, old_base: str, new_base: str) -> bool:
        """
        Recalcula todas las tasas de cambio cuando cambia la moneda base del sistema
        
        Args:
            old_base: Moneda base anterior
            new_base: Nueva moneda base
            
        Returns:
            True si se recalculó correctamente
        """
        try:
            # Obtener todas las tasas actuales con la base antigua
            old_rates = self.get_by_base_currency(old_base)
            
            # Obtener tasa de conversión de old_base a new_base
            conversion_rate = self.get_by_currencies(old_base, new_base)
            if not conversion_rate:
                logger.error("ExchangeRateRepository", f"No existe tasa de cambio de {old_base} a {new_base}")
                return False
            
            # Recalcular tasas para la nueva base
            cursor = self.db_conn.connection.cursor()
            
            for rate in old_rates:
                if rate.target_currency == new_base:
                    continue  # Skip la conversión a sí misma
                
                # Nueva tasa: (tasa_antigua / tasa_conversión)
                new_rate = rate.rate / conversion_rate.rate
                
                cursor.execute("""
                    INSERT OR REPLACE INTO exchange_rates (base_currency, target_currency, rate)
                    VALUES (?, ?, ?)
                """, (new_base, rate.target_currency, new_rate))
            
            # Agregar tasa inversa (new_base -> old_base)
            cursor.execute("""
                INSERT OR REPLACE INTO exchange_rates (base_currency, target_currency, rate)
                VALUES (?, ?, ?)
            """, (new_base, old_base, 1.0 / conversion_rate.rate))
            
            self.db_conn.connection.commit()
            return True
            
        except Exception as e:
            logger.error("ExchangeRateRepository", f"Error recalculando tasas: {e}")
            self.db_conn.connection.rollback()
            return False
    
    def get_rates_as_dict(self, base_currency: str) -> Dict[str, float]:
        """
        Obtiene tasas de cambio como diccionario para consulta rápida
        
        Args:
            base_currency: Moneda base
            
        Returns:
            Dict con código de moneda como key y tasa como value
        """
        rates = self.get_by_base_currency(base_currency)
        return {rate.target_currency: rate.rate for rate in rates}
    
    def _row_to_exchange_rate(self, row) -> ExchangeRate:
        """Convierte una fila de la DB a objeto ExchangeRate"""
        return ExchangeRate(
            id=row[0],
            base_currency=row[1],
            target_currency=row[2],
            rate=row[3],
            updated_at=row[4]
        )
