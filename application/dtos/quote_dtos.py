"""
DTOs para gestión de presupuestos
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from .base_dtos import BaseResponseDTO, ListResponseDTO


@dataclass
class FilamentSlotCalcDTO:
    """Datos de un slot de filamento multicolor para el cálculo de costos."""
    slot_index: int = 0
    filament_id: int = 0       # ID del filamento asignado del catálogo
    weight_grams: float = 0.0  # gramos de este slot (ya rebalanceados si aplica)
    # Campos calculados en runtime por el service (no son input)
    price_per_gram: float = 0.0
    slot_cost: float = 0.0


@dataclass
class QuoteCreateDTO:
    """DTO para crear un presupuesto"""
    customer_id: Optional[int] = None
    printer_id: int = 0
    filament_id: int = 0
    project_name: str = ""
    description: str = ""
    print_time_minutes: float = 0.0
    filament_weight_grams: float = 0.0
    filament_length_meters: float = 0.0
    failure_margin_percent: float = 5.0
    profit_margin_percent: float = 35.0
    tax_rate_percent: float = 10.0
    commission_rate_percent: float = 0.0
    file_path: str = ""
    notes: str = ""
    internal_notes: str = ""
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if not self.project_name.strip():
            errors.append("El nombre del proyecto es requerido")
        
        if len(self.project_name) > 100:
            errors.append("El nombre del proyecto no puede exceder 100 caracteres")
        
        if self.printer_id <= 0:
            errors.append("ID de impresora es requerido")
            
        if self.filament_id <= 0:
            errors.append("ID de filamento es requerido")
        
        if self.print_time_minutes <= 0:
            errors.append("El tiempo de impresión debe ser mayor a 0")
            
        if self.filament_weight_grams <= 0:
            errors.append("El peso del filamento debe ser mayor a 0")
        
        if self.failure_margin_percent < 0 or self.failure_margin_percent > 50:
            errors.append("El margen de error debe estar entre 0% y 50%")
            
        if self.profit_margin_percent < 0 or self.profit_margin_percent > 100:
            errors.append("El margen de ganancia debe estar entre 0% y 100%")
            
        if self.tax_rate_percent < 0 or self.tax_rate_percent > 50:
            errors.append("La tasa de impuesto debe estar entre 0% y 50%")
            
        if self.commission_rate_percent < 0 or self.commission_rate_percent > 50:
            errors.append("La tasa de comisión debe estar entre 0% y 50%")
        
        if len(self.description) > 500:
            errors.append("La descripción no puede exceder 500 caracteres")
            
        if len(self.notes) > 1000:
            errors.append("Las notas no pueden exceder 1000 caracteres")
            
        if len(self.internal_notes) > 1000:
            errors.append("Las notas internas no pueden exceder 1000 caracteres")
        
        return errors


@dataclass
class QuoteUpdateDTO:
    """DTO para actualizar un presupuesto"""
    id: int
    customer_id: Optional[int] = None
    printer_id: Optional[int] = None
    filament_id: Optional[int] = None
    project_name: Optional[str] = None
    description: Optional[str] = None
    print_time_minutes: Optional[float] = None
    filament_weight_grams: Optional[float] = None
    filament_length_meters: Optional[float] = None
    failure_margin_percent: Optional[float] = None
    profit_margin_percent: Optional[float] = None
    tax_rate_percent: Optional[float] = None
    commission_rate_percent: Optional[float] = None
    status: Optional[str] = None
    valid_until: Optional[str] = None
    file_path: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if self.id <= 0:
            errors.append("ID del presupuesto es requerido y debe ser mayor a 0")
        
        if self.project_name is not None:
            if not self.project_name.strip():
                errors.append("El nombre del proyecto no puede estar vacío")
            if len(self.project_name) > 100:
                errors.append("El nombre del proyecto no puede exceder 100 caracteres")
        
        if self.printer_id is not None and self.printer_id <= 0:
            errors.append("ID de impresora debe ser mayor a 0")
            
        if self.filament_id is not None and self.filament_id <= 0:
            errors.append("ID de filamento debe ser mayor a 0")
        
        if self.print_time_minutes is not None and self.print_time_minutes <= 0:
            errors.append("El tiempo de impresión debe ser mayor a 0")
            
        if self.filament_weight_grams is not None and self.filament_weight_grams <= 0:
            errors.append("El peso del filamento debe ser mayor a 0")
        
        if self.failure_margin_percent is not None and (self.failure_margin_percent < 0 or self.failure_margin_percent > 50):
            errors.append("El margen de error debe estar entre 0% y 50%")
            
        if self.profit_margin_percent is not None and (self.profit_margin_percent < 0 or self.profit_margin_percent > 100):
            errors.append("El margen de ganancia debe estar entre 0% y 100%")
            
        if self.tax_rate_percent is not None and (self.tax_rate_percent < 0 or self.tax_rate_percent > 50):
            errors.append("La tasa de impuesto debe estar entre 0% y 50%")
            
        if self.commission_rate_percent is not None and (self.commission_rate_percent < 0 or self.commission_rate_percent > 50):
            errors.append("La tasa de comisión debe estar entre 0% y 50%")
        
        return errors


@dataclass
class QuoteCalculationRequestDTO:
    """DTO para solicitar cálculo de presupuesto"""
    printer_id: int
    filament_id: int
    print_time_minutes: float
    filament_weight_grams: float
    failure_margin_percent: float = 5.0
    profit_margin_percent: float = 35.0
    tax_rate_percent: float = 10.0
    commission_rate_percent: float = 0.0
    electricity_rate_per_kwh: Optional[float] = None  # Si no se proporciona, se toma de config
    commission_tax_shield: bool = False  # Blindar comisión del IVA: comisión *= (1 + tax/100)
    # Slots multicolor opcionales. Si están presentes, el costo de material se calcula como
    # suma de (slot.weight_grams * filamento.price_per_gram) por slot en lugar del modo legacy.
    filament_slots: List[FilamentSlotCalcDTO] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if self.printer_id <= 0:
            errors.append("ID de impresora es requerido")
        
        # En modo multicolor, filament_id se usa como fallback; no es obligatorio
        is_multicolor = bool(self.filament_slots)
        if not is_multicolor and self.filament_id <= 0:
            errors.append("ID de filamento es requerido")
        
        if self.print_time_minutes <= 0:
            errors.append("El tiempo de impresión debe ser mayor a 0")
            
        if self.filament_weight_grams <= 0:
            errors.append("El peso del filamento debe ser mayor a 0")
        
        if self.failure_margin_percent < 0 or self.failure_margin_percent > 50:
            errors.append("El margen de error debe estar entre 0% y 50%")
            
        if self.profit_margin_percent < 0 or self.profit_margin_percent > 100:
            errors.append("El margen de ganancia debe estar entre 0% y 100%")
            
        if self.tax_rate_percent < 0 or self.tax_rate_percent > 50:
            errors.append("La tasa de impuesto debe estar entre 0% y 50%")
            
        if self.commission_rate_percent < 0 or self.commission_rate_percent > 50:
            errors.append("La tasa de comisión debe estar entre 0% y 50%")
        
        return errors


@dataclass
class QuoteCalculationResponseDTO:
    """DTO para respuesta de cálculo de presupuesto"""
    # Costos base
    material_cost: float = 0.0
    electricity_cost: float = 0.0
    operation_cost: float = 0.0
    
    # Subtotales
    subtotal_base_costs: float = 0.0
    failure_margin_cost: float = 0.0
    subtotal_with_margin: float = 0.0
    commission_cost: float = 0.0
    subtotal_before_profit: float = 0.0
    
    # Ganancia y totales
    profit_amount: float = 0.0
    subtotal_before_tax: float = 0.0
    tax_amount: float = 0.0
    total_to_pay: float = 0.0
    
    # Información adicional
    calculation_timestamp: Optional[str] = None
    printer_info: Optional[Dict[str, Any]] = None
    filament_info: Optional[Dict[str, Any]] = None
    calculation_details: Optional[Dict[str, Any]] = None


@dataclass
class QuoteResponseDTO:
    """DTO para respuesta de presupuesto"""
    id: int
    quote_number: str
    customer_id: Optional[int]
    customer_name: Optional[str]
    printer_id: int
    printer_name: str
    filament_id: int
    filament_name: str
    project_name: str
    description: str
    print_time_minutes: float
    filament_weight_grams: float
    filament_length_meters: float
    
    # Costos calculados
    material_cost: float
    electricity_cost: float
    operation_cost: float
    subtotal_costs: float
    failure_margin_cost: float
    commission_cost: float
    subtotal_before_tax: float
    tax_amount: float
    total_to_pay: float
    
    # Márgenes
    failure_margin_percent: float
    profit_margin_percent: float
    tax_rate_percent: float
    
    # Estado y fechas
    status: str
    valid_until: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    
    # Archivos y notas
    file_path: str
    notes: str
    internal_notes: str


@dataclass
class QuoteListDTO(ListResponseDTO):
    """DTO para lista de presupuestos"""
    data: List[QuoteResponseDTO] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.data is None:
            self.data = []


@dataclass
class QuoteSearchDTO:
    """DTO para búsqueda de presupuestos"""
    search_term: Optional[str] = None
    customer_id: Optional[int] = None
    printer_id: Optional[int] = None
    status_filter: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    page: int = 1
    page_size: int = 50


@dataclass
class QuoteStatusUpdateDTO:
    """DTO para actualizar estado de presupuesto"""
    id: int
    status: str
    notes: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if self.id <= 0:
            errors.append("ID del presupuesto es requerido")
        
        valid_statuses = ["DRAFT", "PENDING", "APPROVED", "REJECTED", "EXPIRED"]
        if self.status not in valid_statuses:
            errors.append(f"Estado debe ser uno de: {', '.join(valid_statuses)}")
        
        return errors
