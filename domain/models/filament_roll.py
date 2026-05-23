"""
Modelo de dominio para Rollo de Filamento individual
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class FilamentRoll:
    """Representa un rollo individual de filamento en el inventario"""
    id: Optional[int] = None
    filament_id: int = 0
    sku: str = ""
    initial_weight_grams: float = 0.0
    current_weight_grams: float = 0.0
    purchase_price: float = 0.0
    price_per_gram: float = 0.0
    purchase_date: Optional[str] = None
    is_active: bool = True
    notes: str = ""
    created_at: Optional[str] = None

    def calculate_price_per_gram(self) -> float:
        if self.initial_weight_grams > 0 and self.purchase_price > 0:
            return self.purchase_price / self.initial_weight_grams
        return 0.0

    def update_price_per_gram(self):
        self.price_per_gram = self.calculate_price_per_gram()

    @property
    def used_grams(self) -> float:
        return max(0.0, self.initial_weight_grams - self.current_weight_grams)

    @property
    def usage_percent(self) -> float:
        if self.initial_weight_grams > 0:
            return (self.used_grams / self.initial_weight_grams) * 100
        return 0.0
