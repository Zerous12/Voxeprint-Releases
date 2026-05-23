"""
Modelo de dominio para Configuraciones del Sistema
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SystemConfig:
    """Configuraciones generales del sistema"""
    id: Optional[int] = None
    config_key: str = ""
    config_value: str = ""
    config_type: str = "string"  # string, float, int, bool
    description: str = ""
    category: str = "general"  # general, printing, costs, system
    is_editable: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
