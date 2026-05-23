"""
Modelo de dominio para Currency (Moneda)
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Currency:
    """Modelo de dominio para Moneda"""
    code: str                          # USD, PYG, EUR, etc.
    symbol: str                        # $, Gs., €
    name: str                          # Dólar Estadounidense
    decimals: int = 2                  # 0 para PYG, 2 para USD/EUR
    thousands_sep: str = ","           # Separador de miles
    decimal_sep: str = "."             # Separador decimal
    symbol_position: str = "prefix"    # prefix o suffix
    space_between: bool = False        # Espacio entre símbolo y número
    is_active: bool = True             # Activa/Desactivada
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones post-inicialización"""
        if self.symbol_position not in ["prefix", "suffix"]:
            self.symbol_position = "prefix"
        if self.decimals < 0:
            self.decimals = 0


@dataclass
class ExchangeRate:
    """Modelo de dominio para Tasa de Cambio"""
    base_currency: str                 # Moneda base (ej: USD)
    target_currency: str               # Moneda objetivo (ej: PYG)
    rate: float                        # Tasa: 1 USD = 6709.36 PYG
    id: Optional[int] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones post-inicialización"""
        if self.rate <= 0:
            raise ValueError(f"La tasa de cambio debe ser positiva, recibido: {self.rate}")
        if self.base_currency == self.target_currency:
            raise ValueError("La moneda base y objetivo no pueden ser iguales")

    def get_inverse_rate(self) -> float:
        """Retorna la tasa inversa (para conversión inversa)"""
        return 1.0 / self.rate
