"""
DTOs base para la aplicación
"""
from dataclasses import dataclass
from typing import Optional, Any, Dict, List
from datetime import datetime


@dataclass
class BaseResponseDTO:
    """DTO base para respuestas"""
    success: bool = True
    message: str = ""
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ErrorResponseDTO(BaseResponseDTO):
    """DTO para respuestas de error"""
    success: bool = False
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class PaginationDTO:
    """DTO para paginación"""
    page: int = 1
    page_size: int = 50
    total_items: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_previous: bool = False
    
    def calculate_pagination(self, total_items: int):
        """Calcula los valores de paginación"""
        self.total_items = total_items
        self.total_pages = (total_items + self.page_size - 1) // self.page_size
        self.has_next = self.page < self.total_pages
        self.has_previous = self.page > 1


@dataclass
class ListResponseDTO(BaseResponseDTO):
    """DTO base para respuestas de listas"""
    data: List[Any] = None
    pagination: Optional[PaginationDTO] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.data is None:
            self.data = []
