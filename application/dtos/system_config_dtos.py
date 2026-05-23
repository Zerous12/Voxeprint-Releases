"""
DTOs para gestión de configuraciones del sistema
"""
from dataclasses import dataclass
from typing import Optional, List, Any, Union
from .base_dtos import BaseResponseDTO, ListResponseDTO


@dataclass
class SystemConfigCreateDTO:
    """DTO para crear una configuración del sistema"""
    config_key: str
    config_value: str
    config_type: str = "string"
    description: str = ""
    category: str = "general"
    is_editable: bool = True
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if not self.config_key.strip():
            errors.append("La clave de configuración es requerida")
        
        if len(self.config_key) > 100:
            errors.append("La clave no puede exceder 100 caracteres")
        
        if not self.config_value.strip():
            errors.append("El valor de configuración es requerido")
        
        if len(self.config_value) > 500:
            errors.append("El valor no puede exceder 500 caracteres")
        
        valid_types = ["string", "int", "float", "bool", "json"]
        if self.config_type not in valid_types:
            errors.append(f"Tipo debe ser uno de: {', '.join(valid_types)}")
        
        valid_categories = ["general", "printing", "costs", "system", "ui", "database"]
        if self.category not in valid_categories:
            errors.append(f"Categoría debe ser una de: {', '.join(valid_categories)}")
        
        if len(self.description) > 300:
            errors.append("La descripción no puede exceder 300 caracteres")
        
        # Validar formato del valor según el tipo
        if self.config_type == "int":
            try:
                int(self.config_value)
            except ValueError:
                errors.append("El valor debe ser un número entero válido")
        
        elif self.config_type == "float":
            try:
                float(self.config_value)
            except ValueError:
                errors.append("El valor debe ser un número decimal válido")
        
        elif self.config_type == "bool":
            if self.config_value.lower() not in ["true", "false", "1", "0"]:
                errors.append("El valor booleano debe ser 'true', 'false', '1' o '0'")
        
        return errors


@dataclass
class SystemConfigUpdateDTO:
    """DTO para actualizar una configuración del sistema"""
    id: int
    config_value: Optional[str] = None
    description: Optional[str] = None
    is_editable: Optional[bool] = None
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if self.id <= 0:
            errors.append("ID de configuración es requerido y debe ser mayor a 0")
        
        if self.config_value is not None:
            if not self.config_value.strip():
                errors.append("El valor de configuración no puede estar vacío")
            if len(self.config_value) > 500:
                errors.append("El valor no puede exceder 500 caracteres")
        
        if self.description is not None and len(self.description) > 300:
            errors.append("La descripción no puede exceder 300 caracteres")
        
        return errors


@dataclass
class SystemConfigResponseDTO:
    """DTO para respuesta de configuración del sistema"""
    id: int
    config_key: str
    config_value: str
    config_type: str
    description: str
    category: str
    is_editable: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Valor tipado
    typed_value: Optional[Any] = None
    
    def get_typed_value(self) -> Any:
        """Devuelve el valor convertido al tipo apropiado"""
        if self.typed_value is not None:
            return self.typed_value
        
        try:
            if self.config_type == "int":
                return int(self.config_value)
            elif self.config_type == "float":
                return float(self.config_value)
            elif self.config_type == "bool":
                return self.config_value.lower() in ["true", "1"]
            elif self.config_type == "json":
                import json
                return json.loads(self.config_value)
            else:
                return self.config_value
        except (ValueError, TypeError):
            return self.config_value


@dataclass
class SystemConfigListDTO(ListResponseDTO):
    """DTO para lista de configuraciones del sistema"""
    data: List[SystemConfigResponseDTO] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.data is None:
            self.data = []


@dataclass
class SystemConfigSearchDTO:
    """DTO para búsqueda de configuraciones"""
    search_term: Optional[str] = None
    category_filter: Optional[str] = None
    config_type_filter: Optional[str] = None
    editable_only: bool = False
    page: int = 1
    page_size: int = 50


@dataclass
class SystemConfigBatchUpdateDTO:
    """DTO para actualización en lote de configuraciones"""
    configs: List[dict]  # Lista de {id, config_value}
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if not self.configs:
            errors.append("Debe proporcionar al menos una configuración para actualizar")
        
        for i, config in enumerate(self.configs):
            if not isinstance(config, dict):
                errors.append(f"Configuración {i+1}: debe ser un diccionario")
                continue
            
            if "id" not in config:
                errors.append(f"Configuración {i+1}: ID es requerido")
            elif not isinstance(config["id"], int) or config["id"] <= 0:
                errors.append(f"Configuración {i+1}: ID debe ser un entero mayor a 0")
            
            if "config_value" not in config:
                errors.append(f"Configuración {i+1}: config_value es requerido")
            elif not isinstance(config["config_value"], str):
                errors.append(f"Configuración {i+1}: config_value debe ser una cadena")
        
        return errors


@dataclass
class SystemConfigDefaultsDTO:
    """DTO para configuraciones predeterminadas del sistema"""
    electricity_rate_per_kwh: float = 265.0
    default_failure_margin_percent: float = 5.0
    default_profit_margin_percent: float = 35.0
    default_tax_rate_percent: float = 10.0
    currency_symbol: str = "Gs."
    date_format: str = "DD/MM/YYYY"
    time_format: str = "HH:mm"
    decimal_places: int = 0
    backup_frequency_days: int = 7
    quote_validity_days: int = 30
