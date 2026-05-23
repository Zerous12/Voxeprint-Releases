"""
DTOs para gestión de impresoras
"""
from dataclasses import dataclass
from typing import Optional, List
from .base_dtos import BaseResponseDTO, ListResponseDTO


@dataclass
class PrinterCreateDTO:
    """DTO para crear una impresora"""
    name: str
    brand: str = ""
    model: str = ""
    purchase_cost: float = 0.0
    wear_rate_per_hour: float = 0.0
    power_consumption_watts: float = 0.0
    maintenance_cost: float = 0.0
    maintenance_interval_hours: float = 0.0
    depreciation_rate: float = 0.0
    is_active: bool = True
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if not self.name.strip():
            errors.append("El nombre de la impresora es requerido")
        
        if len(self.name) > 100:
            errors.append("El nombre no puede exceder 100 caracteres")
        
        if len(self.brand) > 50:
            errors.append("La marca no puede exceder 50 caracteres")
            
        if len(self.model) > 50:
            errors.append("El modelo no puede exceder 50 caracteres")
        
        if self.purchase_cost < 0:
            errors.append("El costo de compra no puede ser negativo")
            
        if self.wear_rate_per_hour < 0:
            errors.append("La tasa de desgaste no puede ser negativa")
            
        if self.power_consumption_watts < 0:
            errors.append("El consumo de energía no puede ser negativo")
            
        if self.maintenance_cost < 0:
            errors.append("El costo de mantenimiento no puede ser negativo")
            
        if self.maintenance_interval_hours < 0:
            errors.append("El intervalo de mantenimiento no puede ser negativo")
            
        if self.depreciation_rate < 0 or self.depreciation_rate > 100:
            errors.append("La tasa de depreciación debe estar entre 0 y 100")
        
        return errors


@dataclass
class PrinterUpdateDTO:
    """DTO para actualizar una impresora"""
    id: int
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    purchase_cost: Optional[float] = None
    wear_rate_per_hour: Optional[float] = None
    power_consumption_watts: Optional[float] = None
    maintenance_cost: Optional[float] = None
    maintenance_interval_hours: Optional[float] = None
    depreciation_rate: Optional[float] = None
    is_active: Optional[bool] = None
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if self.id <= 0:
            errors.append("ID de la impresora es requerido y debe ser mayor a 0")
        
        if self.name is not None:
            if not self.name.strip():
                errors.append("El nombre de la impresora no puede estar vacío")
            if len(self.name) > 100:
                errors.append("El nombre no puede exceder 100 caracteres")
        
        if self.brand is not None and len(self.brand) > 50:
            errors.append("La marca no puede exceder 50 caracteres")
            
        if self.model is not None and len(self.model) > 50:
            errors.append("El modelo no puede exceder 50 caracteres")
        
        if self.purchase_cost is not None and self.purchase_cost < 0:
            errors.append("El costo de compra no puede ser negativo")
            
        if self.wear_rate_per_hour is not None and self.wear_rate_per_hour < 0:
            errors.append("La tasa de desgaste no puede ser negativa")
            
        if self.power_consumption_watts is not None and self.power_consumption_watts < 0:
            errors.append("El consumo de energía no puede ser negativo")
            
        if self.maintenance_cost is not None and self.maintenance_cost < 0:
            errors.append("El costo de mantenimiento no puede ser negativo")
            
        if self.maintenance_interval_hours is not None and self.maintenance_interval_hours < 0:
            errors.append("El intervalo de mantenimiento no puede ser negativo")
            
        if self.depreciation_rate is not None and (self.depreciation_rate < 0 or self.depreciation_rate > 100):
            errors.append("La tasa de depreciación debe estar entre 0 y 100")
        
        return errors


@dataclass
class PrinterResponseDTO:
    """DTO para respuesta de impresora"""
    id: int
    name: str
    brand: str
    model: str
    purchase_cost: float
    wear_rate_per_hour: float
    power_consumption_watts: float
    maintenance_cost: float
    maintenance_interval_hours: float
    depreciation_rate: float
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class PrinterListDTO(ListResponseDTO):
    """DTO para lista de impresoras"""
    data: List[PrinterResponseDTO] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.data is None:
            self.data = []


@dataclass
class PrinterSearchDTO:
    """DTO para búsqueda de impresoras"""
    search_term: Optional[str] = None
    brand_filter: Optional[str] = None
    active_only: bool = True
    page: int = 1
    page_size: int = 50


@dataclass
class PrinterCostCalculationDTO:
    """DTO para cálculo de costos de impresora"""
    printer_id: int
    print_time_minutes: float
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if self.printer_id <= 0:
            errors.append("ID de impresora es requerido")
            
        if self.print_time_minutes <= 0:
            errors.append("El tiempo de impresión debe ser mayor a 0")
        
        return errors
