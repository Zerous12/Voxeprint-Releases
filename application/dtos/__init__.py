"""
DTOs (Data Transfer Objects) para la aplicación Voxeprint
"""
from .customer_dtos import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerResponseDTO,
    CustomerListDTO
)
from .printer_dtos import (
    PrinterCreateDTO,
    PrinterUpdateDTO,
    PrinterResponseDTO,
    PrinterListDTO
)
from .filament_dtos import (
    FilamentCreateDTO,
    FilamentUpdateDTO,
    FilamentResponseDTO,
    FilamentListDTO
)
from .quote_dtos import (
    QuoteCreateDTO,
    QuoteUpdateDTO,
    QuoteResponseDTO,
    QuoteListDTO,
    QuoteCalculationRequestDTO,
    QuoteCalculationResponseDTO
)
from .system_config_dtos import (
    SystemConfigCreateDTO,
    SystemConfigUpdateDTO,
    SystemConfigResponseDTO
)
from .base_dtos import (
    BaseResponseDTO,
    PaginationDTO,
    ErrorResponseDTO
)
from .quote_breakdown_dto import (
    QuoteBreakdownLine,
    QuoteBreakdownResult
)

__all__ = [
    # Customer DTOs
    "CustomerCreateDTO",
    "CustomerUpdateDTO", 
    "CustomerResponseDTO",
    "CustomerListDTO",
    
    # Printer DTOs
    "PrinterCreateDTO",
    "PrinterUpdateDTO",
    "PrinterResponseDTO", 
    "PrinterListDTO",
    
    # Filament DTOs
    "FilamentCreateDTO",
    "FilamentUpdateDTO",
    "FilamentResponseDTO",
    "FilamentListDTO",
    
    # Quote DTOs
    "QuoteCreateDTO",
    "QuoteUpdateDTO",
    "QuoteResponseDTO",
    "QuoteListDTO",
    "QuoteCalculationRequestDTO",
    "QuoteCalculationResponseDTO",
    
    # System Config DTOs
    "SystemConfigCreateDTO",
    "SystemConfigUpdateDTO",
    "SystemConfigResponseDTO",
    
    # Base DTOs
    "BaseResponseDTO",
    "PaginationDTO", 
    "ErrorResponseDTO",
    
    # Quote Breakdown DTOs
    "QuoteBreakdownLine",
    "QuoteBreakdownResult"
]
