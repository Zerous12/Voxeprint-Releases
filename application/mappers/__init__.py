"""
Mappers para convertir entre entidades y DTOs
"""
from .customer_mapper import CustomerMapper
from .printer_mapper import PrinterMapper
from .filament_mapper import FilamentMapper
# TODO: Implementar otros mappers
# from .quote_mapper import QuoteMapper
# from .system_config_mapper import SystemConfigMapper

__all__ = [
    "CustomerMapper",
    "PrinterMapper", 
    "FilamentMapper",
    # "QuoteMapper",
    # "SystemConfigMapper"
]
