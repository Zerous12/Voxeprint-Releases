"""
DTOs para gestión de clientes
"""
from dataclasses import dataclass
from typing import Optional, List
from .base_dtos import BaseResponseDTO, ListResponseDTO


@dataclass
class CustomerCreateDTO:
    """DTO para crear un cliente"""
    full_name: str
    ruc_ci: str = ""
    email: str = ""
    phone_number: str = ""
    is_default: bool = False
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if not self.full_name.strip():
            errors.append("El nombre completo es requerido")
        
        if len(self.full_name) > 200:
            errors.append("El nombre completo no puede exceder 200 caracteres")
            
        if self.email and not self._is_valid_email(self.email):
            errors.append("El formato del email no es válido")
            
        if len(self.ruc_ci) > 50:
            errors.append("RUC/CI no puede exceder 50 caracteres")
            
        if len(self.phone_number) > 20:
            errors.append("El teléfono no puede exceder 20 caracteres")
        
        return errors
    
    def _is_valid_email(self, email: str) -> bool:
        """Valida formato básico de email"""
        return "@" in email and "." in email.split("@")[-1]


@dataclass
class CustomerUpdateDTO:
    """DTO para actualizar un cliente"""
    id: int
    full_name: Optional[str] = None
    ruc_ci: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    is_default: Optional[bool] = None
    
    def validate(self) -> List[str]:
        """Valida los datos del DTO"""
        errors = []
        
        if self.id <= 0:
            errors.append("ID del cliente es requerido y debe ser mayor a 0")
        
        if self.full_name is not None:
            if not self.full_name.strip():
                errors.append("El nombre completo no puede estar vacío")
            if len(self.full_name) > 200:
                errors.append("El nombre completo no puede exceder 200 caracteres")
        
        if self.email is not None and self.email:
            if not self._is_valid_email(self.email):
                errors.append("El formato del email no es válido")
        
        if self.ruc_ci is not None and len(self.ruc_ci) > 50:
            errors.append("RUC/CI no puede exceder 50 caracteres")
            
        if self.phone_number is not None and len(self.phone_number) > 20:
            errors.append("El teléfono no puede exceder 20 caracteres")
        
        return errors
    
    def _is_valid_email(self, email: str) -> bool:
        """Valida formato básico de email"""
        return "@" in email and "." in email.split("@")[-1]


@dataclass
class CustomerResponseDTO:
    """DTO para respuesta de cliente"""
    id: int
    full_name: str
    ruc_ci: str
    email: str
    phone_number: str
    is_default: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class CustomerListDTO(ListResponseDTO):
    """DTO para lista de clientes"""
    data: List[CustomerResponseDTO] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.data is None:
            self.data = []


@dataclass
class CustomerSearchDTO:
    """DTO para búsqueda de clientes"""
    search_term: Optional[str] = None
    include_inactive: bool = False
    is_default_only: bool = False
    page: int = 1
    page_size: int = 50
