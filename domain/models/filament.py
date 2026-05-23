"""
Modelo de dominio para Filamento
"""
from dataclasses import dataclass
from typing import Optional
from domain.enums.enums import FilamentType, FilamentColor


@dataclass
class Filament:
    """Modelo de filamento"""
    id: Optional[int] = None
    name: str = ""
    type: FilamentType = FilamentType.PLA
    brand: str = ""
    color: FilamentColor = FilamentColor.WHITE
    weight_grams: float = 0.0  # Peso en gramos por unidad
    price_per_unit: float = 0.0  # Precio por unidad (rollo)
    price_per_gram: float = 0.0  # Precio por gramo (calculado automáticamente)
    quantity_rolls: int = 0  # Cantidad de rollos en stock
    current_stock_grams: float = 0.0  # Stock actual en gramos
    minimum_stock_grams: float = 0.0  # Stock mínimo en gramos
    is_active: bool = True
    notes: str = ""
    currency_code: str = "PYG"  # Moneda en la que se guardó el precio
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def calculate_price_per_gram(self) -> float:
        """
        Calcula el precio por gramo basado en precio por unidad y peso
        
        Returns:
            float: Precio por gramo
        """
        if self.weight_grams > 0 and self.price_per_unit > 0:
            return self.price_per_unit / self.weight_grams
        return 0.0
    
    def update_price_per_gram(self):
        """Actualiza automáticamente el precio por gramo"""
        self.price_per_gram = self.calculate_price_per_gram()
