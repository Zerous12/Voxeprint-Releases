"""
Inicialización de modelos de dominio
"""
from .customer import Customer
from .printer import Printer
from .filament import Filament
from .filament_roll import FilamentRoll
from .quote import Quote
from .system_config import SystemConfig
from .currency import Currency, ExchangeRate

__all__ = [
    'Customer',
    'Printer', 
    'Filament',
    'FilamentRoll',
    'Quote',
    'SystemConfig',
    'Currency',
    'ExchangeRate'
]
