"""
Inicialización de repositorios
"""
from .base_repository import BaseRepository
from .customer_repository import CustomerRepository
from .printer_repository import PrinterRepository
from .filament_repository import FilamentRepository
from .filament_roll_repository import FilamentRollRepository
from .quote_repository import QuoteRepository
from .system_config_repository import SystemConfigRepository

__all__ = [
    'BaseRepository',
    'CustomerRepository',
    'PrinterRepository',
    'FilamentRepository',
    'FilamentRollRepository',
    'QuoteRepository',
    'SystemConfigRepository'
]
