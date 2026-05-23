"""
Modelo de dominio para Cliente
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    """Modelo de cliente"""
    id: Optional[int] = None
    full_name: str = ""
    ruc_ci: str = ""
    email: str = ""
    phone_number: str = ""
    is_default: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if not self.full_name and not self.is_default:
            raise ValueError("El nombre completo es requerido para clientes no predeterminados")
