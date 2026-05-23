"""
DTOs para gestión de filamentos
"""
from dataclasses import dataclass
from typing import Optional, List
from .base_dtos import BaseResponseDTO, ListResponseDTO


@dataclass
class FilamentCreateDTO:
    """DTO para crear un filamento"""
    name: str
    type: str  # Se convertirá a enum en el servicio
    brand: str = ""
    color: str = "WHITE"  # Se convertirá a enum en el servicio
    weight_grams: float = 0.0
    price_per_unit: float = 0.0
    quantity_rolls: int = 0
    current_stock_grams: float = 0.0
    minimum_stock_grams: float = 0.0
    is_active: bool = True
    notes: str = ""
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if not self.name.strip():
            errors.append("El nombre del filamento es requerido")
        
        if len(self.name) > 100:
            errors.append("El nombre no puede exceder 100 caracteres")
        
        if len(self.brand) > 50:
            errors.append("La marca no puede exceder 50 caracteres")
        
        if self.weight_grams < 0:
            errors.append("El peso no puede ser negativo")
            
        if self.price_per_unit < 0:
            errors.append("El precio por unidad no puede ser negativo")
            
        if self.quantity_rolls < 0:
            errors.append("La cantidad de rollos no puede ser negativa")
            
        if self.current_stock_grams < 0:
            errors.append("El stock actual no puede ser negativo")
            
        if self.minimum_stock_grams < 0:
            errors.append("El stock mínimo no puede ser negativo")
        
        if len(self.notes) > 500:
            errors.append("Las notas no pueden exceder 500 caracteres")
        
        return errors


@dataclass
class FilamentUpdateDTO:
    """DTO para actualizar un filamento"""
    id: int
    name: Optional[str] = None
    type: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    weight_grams: Optional[float] = None
    price_per_unit: Optional[float] = None
    quantity_rolls: Optional[int] = None
    current_stock_grams: Optional[float] = None
    minimum_stock_grams: Optional[float] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if self.id <= 0:
            errors.append("ID del filamento es requerido y debe ser mayor a 0")
        
        if self.name is not None:
            if not self.name.strip():
                errors.append("El nombre del filamento no puede estar vacío")
            if len(self.name) > 100:
                errors.append("El nombre no puede exceder 100 caracteres")
        
        if self.brand is not None and len(self.brand) > 50:
            errors.append("La marca no puede exceder 50 caracteres")
        
        if self.weight_grams is not None and self.weight_grams < 0:
            errors.append("El peso no puede ser negativo")
            
        if self.price_per_unit is not None and self.price_per_unit < 0:
            errors.append("El precio por unidad no puede ser negativo")
            
        if self.quantity_rolls is not None and self.quantity_rolls < 0:
            errors.append("La cantidad de rollos no puede ser negativa")
            
        if self.current_stock_grams is not None and self.current_stock_grams < 0:
            errors.append("El stock actual no puede ser negativo")
            
        if self.minimum_stock_grams is not None and self.minimum_stock_grams < 0:
            errors.append("El stock mínimo no puede ser negativo")
        
        if self.notes is not None and len(self.notes) > 500:
            errors.append("Las notas no pueden exceder 500 caracteres")
        
        return errors


@dataclass
class FilamentResponseDTO:
    """DTO para respuesta de filamento"""
    id: int
    name: str
    type: str
    brand: str
    color: str
    weight_grams: float
    price_per_unit: float
    price_per_gram: float
    quantity_rolls: int
    current_stock_grams: float
    minimum_stock_grams: float
    is_active: bool
    notes: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Propiedades calculadas
    is_low_stock: bool = False
    total_value: float = 0.0


@dataclass
class FilamentListDTO(ListResponseDTO):
    """DTO para lista de filamentos"""
    data: List[FilamentResponseDTO] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.data is None:
            self.data = []


@dataclass
class FilamentSearchDTO:
    """DTO para búsqueda de filamentos"""
    search_term: Optional[str] = None
    type_filter: Optional[str] = None
    brand_filter: Optional[str] = None
    color_filter: Optional[str] = None
    active_only: bool = True
    low_stock_only: bool = False
    page: int = 1
    page_size: int = 50


@dataclass
class FilamentStockUpdateDTO:
    """DTO para actualización de stock"""
    id: int
    quantity_change: float  # Positivo para agregar, negativo para restar
    operation_type: str  # "add", "remove", "set"
    notes: str = ""
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if self.id <= 0:
            errors.append("ID del filamento es requerido")
            
        if self.operation_type not in ["add", "remove", "set"]:
            errors.append("Tipo de operación debe ser 'add', 'remove' o 'set'")
            
        if self.operation_type == "set" and self.quantity_change < 0:
            errors.append("La cantidad no puede ser negativa al establecer stock")
        
        return errors


@dataclass
class FilamentCostCalculationDTO:
    """DTO para cálculo de costos de filamento"""
    filament_id: int
    weight_grams: float
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if self.filament_id <= 0:
            errors.append("ID de filamento es requerido")
            
        if self.weight_grams <= 0:
            errors.append("El peso debe ser mayor a 0")
        
        return errors
