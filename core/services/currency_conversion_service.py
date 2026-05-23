"""
Servicio para conversión de moneda en tiempo real
Convierte valores monetarios entre diferentes monedas usando tasas de cambio
"""
from typing import Optional
from core.utils.currency_helper import CurrencyHelper
from infrastructure.database.repositories.currency_repository import CurrencyRepository
from infrastructure.database.repositories.exchange_rate_repository import ExchangeRateRepository
from infrastructure.database.connection import DatabaseConnection


class CurrencyConversionService:
    """Servicio para conversión de moneda entre entidades"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        Inicializa el servicio de conversión
        
        Args:
            db_connection: Conexión a la base de datos (opcional, no usado por los repos)
        """
        self.db_connection = db_connection  # Guardado por compatibilidad pero no usado
        self.currency_repo = CurrencyRepository()  # No recibe db_connection
        self.exchange_rate_repo = ExchangeRateRepository()  # No recibe db_connection
    
    def convert_amount(
        self, 
        amount: float, 
        from_currency: str, 
        to_currency: str,
        allow_inactive: bool = True
    ) -> Optional[float]:
        """
        Convierte un monto de una moneda a otra
        
        Args:
            amount: Monto a convertir
            from_currency: Código de moneda origen
            to_currency: Código de moneda destino
            allow_inactive: Si True, permite conversiones desde monedas inactivas (para datos históricos)
            
        Returns:
            Monto convertido o None si no hay tasa de cambio disponible
        """
        from core.utils.logger import logger
        
        # Si las monedas son iguales, no hay conversión
        if from_currency == to_currency:
            return amount
        
        # Verificar que ambas monedas existan
        source_currency = self.currency_repo.get_by_code(from_currency)
        target_currency = self.currency_repo.get_by_code(to_currency)
        
        if not source_currency or not target_currency:
            logger.warning("CurrencyConversion", 
                f"Moneda no encontrada: origen={from_currency}, destino={to_currency}")
            return None
        
        # Verificar estado de activación
        if not allow_inactive:
            # Modo estricto: ambas monedas deben estar activas
            if not source_currency.is_active or not target_currency.is_active:
                logger.warning("CurrencyConversion", 
                    f"Conversión bloqueada - moneda inactiva: {from_currency}={source_currency.is_active}, "
                    f"{to_currency}={target_currency.is_active}")
                return None
        else:
            # Modo permisivo: permitir conversión desde monedas inactivas (datos históricos)
            # pero advertir si la moneda origen está inactiva
            if not source_currency.is_active:
                logger.info("CurrencyConversion", 
                    f"Convirtiendo desde moneda inactiva {from_currency} -> {to_currency} "
                    f"(datos históricos: {amount:.2f} {from_currency})")
            
            # La moneda destino DEBE estar activa siempre
            if not target_currency.is_active:
                logger.error("CurrencyConversion", 
                    f"No se puede convertir a moneda inactiva: {to_currency}")
                return None
        
        # Obtener tasa de cambio usando sistema pivote USD
        exchange_rate = CurrencyHelper.get_exchange_rate(from_currency, to_currency)
        
        if not exchange_rate:
            logger.warning("CurrencyConversion", 
                f"No se encontró tasa de cambio para {from_currency} -> {to_currency}")
            return None
        
        # Convertir
        converted_amount = amount * exchange_rate
        
        # Redondear según decimales de la moneda destino
        if target_currency.decimals == 0:
            return round(converted_amount)
        else:
            return round(converted_amount, target_currency.decimals)
    
    def convert_printer_costs(self, printer, target_currency: str):
        """
        Convierte todos los costos de una impresora a la moneda destino
        NOTA: Modifica el objeto printer in-place
        
        Args:
            printer: Objeto Printer
            target_currency: Código de moneda destino
            
        Returns:
            True si se convirtió exitosamente, False si no
        """
        if printer.currency_code == target_currency:
            return True  # Ya está en la moneda correcta
        
        # Convertir costos
        converted_purchase = self.convert_amount(
            printer.purchase_cost, 
            printer.currency_code, 
            target_currency
        )
        converted_maintenance = self.convert_amount(
            printer.maintenance_cost, 
            printer.currency_code, 
            target_currency
        )
        
        if converted_purchase is None or converted_maintenance is None:
            return False  # No se pudo convertir
        
        # Actualizar valores (NO actualizamos currency_code para preservar el original)
        printer.purchase_cost = converted_purchase
        printer.maintenance_cost = converted_maintenance
        
        return True
    
    def convert_filament_prices(self, filament, target_currency: str):
        """
        Convierte todos los precios de un filamento a la moneda destino
        NOTA: Modifica el objeto filament in-place
        
        Args:
            filament: Objeto Filament
            target_currency: Código de moneda destino
            
        Returns:
            True si se convirtió exitosamente, False si no
        """
        if filament.currency_code == target_currency:
            return True  # Ya está en la moneda correcta
        
        # Convertir precios
        converted_price_unit = self.convert_amount(
            filament.price_per_unit, 
            filament.currency_code, 
            target_currency
        )
        converted_price_gram = self.convert_amount(
            filament.price_per_gram, 
            filament.currency_code, 
            target_currency
        )
        
        if converted_price_unit is None or converted_price_gram is None:
            return False  # No se pudo convertir
        
        # Actualizar valores (NO actualizamos currency_code para preservar el original)
        filament.price_per_unit = converted_price_unit
        filament.price_per_gram = converted_price_gram
        
        return True
    
    def get_conversion_info(self, from_currency: str, to_currency: str) -> dict:
        """
        Obtiene información detallada sobre la conversión entre dos monedas
        
        Args:
            from_currency: Moneda origen
            to_currency: Moneda destino
            
        Returns:
            Dict con información de conversión
        """
        if from_currency == to_currency:
            return {
                'needs_conversion': False,
                'rate': 1.0,
                'source': from_currency,
                'target': to_currency
            }
        
        exchange_rate = self.exchange_rate_repo.get_by_currencies(from_currency, to_currency)
        
        if not exchange_rate:
            return {
                'needs_conversion': True,
                'rate': None,
                'source': from_currency,
                'target': to_currency,
                'available': False
            }
        
        return {
            'needs_conversion': True,
            'rate': exchange_rate.rate,
            'source': from_currency,
            'target': to_currency,
            'available': True,
            'last_updated': exchange_rate.updated_at
        }
