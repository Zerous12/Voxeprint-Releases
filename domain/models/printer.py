"""
Modelo de dominio para Impresora 3D
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Printer:
    """Modelo de impresora 3D"""
    id: Optional[int] = None
    name: str = ""
    brand: str = ""
    model: str = ""
    power_consumption_watts: float = 0.0  # Consumo real en watts (ej: 230w)
    purchase_cost: float = 0.0
    maintenance_cost: float = 0.0  # Costo total de mantenimiento
    maintenance_interval_hours: float = 0.0  # Intervalo de mantenimiento en horas
    useful_life_hours: float = 10000.0  # Vida útil estimada en horas (7000-15000)
    is_active: bool = True
    currency_code: str = "PYG"  # Moneda en la que se guardaron los costos
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @property
    def electricity_cost_per_hour(self) -> float:
        """
        Calcula el costo de electricidad por hora basado en el consumo real
        Usa la tarifa eléctrica del sistema y la convierte a la moneda de la impresora
        Retorna valor en la moneda de la impresora, o 0 si hay error
        """
        if self.power_consumption_watts <= 0:
            return 0.0
            
        try:
            from infrastructure.database.connection import DatabaseConnection
            from core.utils.currency_helper import CurrencyHelper
            from core.utils.logger import VoxeprintLogger
            
            logger = VoxeprintLogger()
            
            # Leer tarifa eléctrica de la BD usando context manager
            db_conn = DatabaseConnection()
            with db_conn.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT config_value FROM system_configs WHERE config_key = ? LIMIT 1",
                    ('electricity_rate',)
                )
                result = cursor.fetchone()
                
                if not result or not result[0]:
                    logger.error(
                        "Printer.electricity_cost",
                        f"No se encontró tarifa eléctrica para impresora '{self.name}'. Configure la tarifa en Ajustes del Sistema."
                    )
                    return 0.0
                
                local_rate_per_kwh = float(result[0])
            
            system_currency = CurrencyHelper.get_current_currency()
            
            # Calcular costo en moneda del sistema
            kwh_per_hour = self.power_consumption_watts / 1000.0
            cost_in_system_currency = kwh_per_hour * local_rate_per_kwh
            
            # Si la impresora usa la misma moneda del sistema, retornar directo
            if system_currency == self.currency_code:
                return cost_in_system_currency
            
            # Convertir a la moneda de la impresora
            cost_converted = CurrencyHelper.convert(
                cost_in_system_currency,
                system_currency,
                self.currency_code
            )
            
            logger.debug(
                "Printer.electricity_cost",
                f"{self.name}: {self.power_consumption_watts}W × {local_rate_per_kwh} {system_currency}/kWh = {cost_converted:.4f} {self.currency_code}/h"
            )
            
            return cost_converted
            
        except ValueError as e:
            from core.utils.logger import VoxeprintLogger
            logger = VoxeprintLogger()
            logger.error(
                "Printer.electricity_cost",
                f"Valor inválido en tarifa eléctrica para '{self.name}': {e}"
            )
            return 0.0
        except Exception as e:
            from core.utils.logger import VoxeprintLogger
            logger = VoxeprintLogger()
            logger.log_exception(
                "Printer.electricity_cost",
                e,
                f"calcular costo eléctrico para '{self.name}'"
            )
            return 0.0
    
    @property
    def maintenance_cost_per_hour(self) -> float:
        """
        Calcula el costo de mantenimiento por hora basado en intervalo
        Retorna valor sin redondear (el formateo se hace en presentación)
        """
        if self.maintenance_interval_hours > 0 and self.maintenance_cost > 0:
            cost = self.maintenance_cost / self.maintenance_interval_hours
            return cost  # Retornar valor sin redondear
        return 0.0
    
    @property
    def machine_wear_cost_per_hour(self) -> float:
        """
        Calcula el desgaste de máquina por hora (solo costo de compra)
        Fórmula: Desgaste = Costo compra ÷ Vida útil (en horas)
        Retorna valor sin redondear (el formateo se hace en presentación)
        """
        if self.useful_life_hours > 0 and self.purchase_cost > 0:
            cost = self.purchase_cost / self.useful_life_hours
            return cost  # Retornar valor sin redondear
        return 0.0
    
    @property
    def service_cost_per_hour(self) -> float:
        """
        Costo de servicio interno por hora (desgaste + mantenimiento)
        Este es un cálculo interno, no se muestra directamente al cliente
        Retorna valor sin redondear (el formateo se hace en presentación)
        """
        cost = self.machine_wear_cost_per_hour + self.maintenance_cost_per_hour
        return cost  # Retornar valor sin redondear
    
    @property
    def operation_cost_per_hour(self) -> float:
        """
        Costo de operación por hora para mostrar al cliente
        Es la suma de desgaste de máquina + mantenimiento
        Este es el valor que se muestra en facturas/PDF como "Costo de Operación"
        Retorna valor redondeado a Guaraníes enteros
        """
        return self.service_cost_per_hour  # Es lo mismo, pero con nombre más claro para cliente
    
    @property
    def total_cost_per_hour(self) -> float:
        """
        Costo total de operación por hora (electricidad + servicio)
        Para uso interno y cálculos
        Retorna valor sin redondear (formato se aplica en presentación)
        """
        cost = self.electricity_cost_per_hour + self.service_cost_per_hour
        return cost  # Retornar sin redondear para preservar decimales
    
    def calculate_operation_cost(self, print_time_minutes: float) -> float:
        """
        Calcula el costo de operación para el cliente basado en tiempo de impresión
        
        Args:
            print_time_minutes: Tiempo de impresión en minutos
            
        Returns:
            float: Costo de operación (formato se aplica en presentación)
        """
        if print_time_minutes <= 0:
            return 0.0
        
        hours = print_time_minutes / 60.0
        cost = self.operation_cost_per_hour * hours
        return cost  # Retornar sin redondear para preservar decimales
    
    def calculate_operation_cost_breakdown(self, print_time_minutes: float) -> dict:
        """
        Calcula el desglose detallado del costo de operación
        
        Args:
            print_time_minutes: Tiempo de impresión en minutos
            
        Returns:
            dict: Desglose con wear_cost, maintenance_cost y total_operation_cost
        """
        if print_time_minutes <= 0:
            return {
                'wear_cost': 0.0,
                'maintenance_cost': 0.0,
                'total_operation_cost': 0.0,
                'hours': 0.0
            }
        
        hours = print_time_minutes / 60.0
        wear_cost = self.machine_wear_cost_per_hour * hours
        maintenance_cost = self.maintenance_cost_per_hour * hours
        total_operation_cost = wear_cost + maintenance_cost
        
        return {
            'wear_cost': wear_cost,
            'maintenance_cost': maintenance_cost,
            'total_operation_cost': total_operation_cost,
            'hours': hours
        }
