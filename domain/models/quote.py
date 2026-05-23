"""
Modelo de dominio para Presupuesto
"""
from dataclasses import dataclass
from typing import Optional
from domain.enums.enums import QuoteStatus


@dataclass
class Quote:
    """Modelo de presupuesto de impresión 3D basado en calculadora Excel"""
    id: Optional[int] = None
    quote_number: str = ""  # Número único de presupuesto
    customer_id: Optional[int] = None  # FK a Customer (opcional)
    printer_id: Optional[int] = None  # FK a Printer
    filament_id: Optional[int] = None  # FK a Filament
    
    # Datos del proyecto
    project_name: str = ""
    description: str = ""
    
    # Datos específicos de la pieza (como en tu Excel)
    print_time_minutes: float = 0.0  # Minutos de impresión
    filament_weight_grams: float = 0.0  # Gramos de filamento
    filament_length_meters: float = 0.0  # Metros de filamento (opcional)
    
    # Datos técnicos para el cálculo
    power_consumption_watts: float = 0.0  # Consumo watts (viene de printer)
    electricity_rate_per_kwh: float = 0.0  # Precio Kwh (viene de config general)
    
    # Costos calculados (como en tu Excel)
    material_cost: float = 0.0  # Precio Material
    electricity_cost: float = 0.0  # Precio Luz  
    machine_wear_cost: float = 0.0  # Desgaste de la máquina
    
    # Subtotales
    subtotal_costs: float = 0.0  # Suma de costos base (sin margen error)
    failure_margin_cost: float = 0.0  # Margen de Error calculado
    commission_cost: float = 0.0  # Comisión
    
    # Márgenes y ajustes (como en tu Excel)
    failure_margin_percent: float = 5.0  # % de Margen de error
    profit_margin_percent: float = 35.0  # Margen de Ganancia (0.35 = 35%)
    tax_rate_percent: float = 10.0  # IVA 10%
    
    # Totales finales
    subtotal_before_tax: float = 0.0  # Subtotal antes de IVA
    tax_amount: float = 0.0  # Monto del IVA
    total_to_pay: float = 0.0  # Total a PAGAR
    
    # Moneda del presupuesto
    currency_code: str = "PYG"  # Moneda en la que fue creado el presupuesto
    
    # Estado y fechas
    status: QuoteStatus = QuoteStatus.DRAFT
    valid_until: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Archivos y notas
    file_path: str = ""  # Ruta del archivo STL/3MF
    notes: str = ""
    internal_notes: str = ""
    
    def calculate_material_cost(self, filament_price_per_kg: float) -> float:
        """Calcula el costo del material: (precio_kg * gramos) / 1000"""
        return (filament_price_per_kg * self.filament_weight_grams) / 1000
    
    def calculate_electricity_cost(self) -> float:
        """Calcula el costo de electricidad: ((consumo_w * precio_kwh) / 1000) * minutos"""
        if self.power_consumption_watts > 0 and self.electricity_rate_per_kwh > 0:
            return ((self.power_consumption_watts * self.electricity_rate_per_kwh) / 1000) * self.print_time_minutes
        return 0.0
    
    def calculate_machine_wear_cost(self, spare_parts_cost: float, machine_life_hours: float) -> float:
        """Calcula desgaste: (repuestos / horas_vida) * minutos"""
        if machine_life_hours > 0:
            return (spare_parts_cost / machine_life_hours) * self.print_time_minutes
        return 0.0
    
    def calculate_failure_margin_cost(self) -> float:
        """Calcula margen de error: suma_costos_base * (% error / 100)"""
        base_costs = self.material_cost + self.electricity_cost + self.machine_wear_cost
        self.failure_margin_cost = base_costs * (self.failure_margin_percent / 100)
        return self.failure_margin_cost
    
    def calculate_subtotal_costs(self) -> float:
        """Calcula subtotal incluyendo margen de error"""
        base_costs = self.material_cost + self.electricity_cost + self.machine_wear_cost
        self.calculate_failure_margin_cost()  # Calcula el margen de error
        self.subtotal_costs = base_costs + self.failure_margin_cost
        return self.subtotal_costs
    
    def calculate_commission(self, commission_rate: float = 0.0) -> float:
        """Calcula comisión si aplica"""
        return self.subtotal_costs * commission_rate
    
    def calculate_total_with_tax(self) -> float:
        """Calcula el total final con IVA"""
        self.subtotal_before_tax = self.subtotal_costs + self.commission_cost
        profit_amount = self.subtotal_before_tax * self.profit_margin_percent
        before_tax = self.subtotal_before_tax + profit_amount
        self.tax_amount = before_tax * (self.tax_rate_percent / 100)
        self.total_to_pay = before_tax + self.tax_amount
        return self.total_to_pay
