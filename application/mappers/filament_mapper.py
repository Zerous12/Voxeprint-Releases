"""
Mapper para conversiones entre DTOs y entidades Filament
"""
from typing import Optional
from domain.models.filament import Filament
from domain.enums.enums import FilamentType, FilamentColor
from application.dtos.filament_dtos import (
    FilamentCreateDTO,
    FilamentUpdateDTO,
    FilamentResponseDTO
)
from core.utils.currency_helper import CurrencyHelper


class FilamentMapper:
    """Mapper para conversiones entre DTOs y entidades de filamento"""

    @staticmethod
    def create_dto_to_entity(dto: FilamentCreateDTO) -> Filament:
        """
        Convierte FilamentCreateDTO a Filament entity
        
        Args:
            dto: DTO con datos para crear filamento
            
        Returns:
            Filament: Entity domain model
        """
        # Convertir strings de enum a enum types
        filament_type = FilamentType.PLA  # Default
        try:
            filament_type = FilamentType(dto.type)
        except ValueError:
            pass  # Mantener default si no es válido
        
        filament_color = FilamentColor.WHITE  # Default
        try:
            filament_color = FilamentColor(dto.color)
        except ValueError:
            pass  # Mantener default si no es válido
        
        filament = Filament(
            name=dto.name,
            type=filament_type,
            brand=dto.brand,
            color=filament_color,
            weight_grams=dto.weight_grams,
            price_per_unit=dto.price_per_unit,
            quantity_rolls=dto.quantity_rolls,
            current_stock_grams=dto.current_stock_grams,
            minimum_stock_grams=dto.minimum_stock_grams,
            is_active=dto.is_active,
            notes=dto.notes,
            currency_code=CurrencyHelper.get_current_currency()  # Moneda del sistema
        )
        
        # Calcular precio por gramo automáticamente
        filament.update_price_per_gram()
        
        return filament
    
    @staticmethod
    def entity_to_response_dto(entity: Filament) -> FilamentResponseDTO:
        """
        Convierte Filament entity a FilamentResponseDTO
        
        Args:
            entity: Filament entity
            
        Returns:
            FilamentResponseDTO: DTO de respuesta
        """
        # Calcular propiedades derivadas
        is_low_stock = entity.current_stock_grams < entity.minimum_stock_grams
        total_value = entity.current_stock_grams * entity.price_per_gram
        
        return FilamentResponseDTO(
            id=entity.id,
            name=entity.name,
            type=entity.type.value,
            brand=entity.brand,
            color=entity.color.value,
            weight_grams=entity.weight_grams,
            price_per_unit=entity.price_per_unit,
            price_per_gram=entity.price_per_gram,
            quantity_rolls=entity.quantity_rolls,
            current_stock_grams=entity.current_stock_grams,
            minimum_stock_grams=entity.minimum_stock_grams,
            is_active=entity.is_active,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_low_stock=is_low_stock,
            total_value=total_value
        )
    
    @staticmethod
    def apply_update_dto_to_entity(entity: Filament, dto: FilamentUpdateDTO) -> Filament:
        """
        Aplica las actualizaciones del DTO a una entidad existente
        
        Args:
            entity: Entidad a actualizar
            dto: DTO con datos de actualización
            
        Returns:
            Filament: Entidad actualizada
        """
        # Actualizar solo campos no nulos
        if dto.name is not None:
            entity.name = dto.name
        
        if dto.type is not None:
            try:
                entity.type = FilamentType(dto.type)
            except ValueError:
                pass  # Mantener valor actual si no es válido
        
        if dto.brand is not None:
            entity.brand = dto.brand
        
        if dto.color is not None:
            try:
                entity.color = FilamentColor(dto.color)
            except ValueError:
                pass  # Mantener valor actual si no es válido
        
        if dto.weight_grams is not None:
            entity.weight_grams = dto.weight_grams
        
        if dto.price_per_unit is not None:
            entity.price_per_unit = dto.price_per_unit
            # Recalcular precio por gramo si cambia precio por unidad
            entity.update_price_per_gram()
        
        if dto.quantity_rolls is not None:
            entity.quantity_rolls = dto.quantity_rolls
        
        if dto.current_stock_grams is not None:
            entity.current_stock_grams = dto.current_stock_grams
        
        if dto.minimum_stock_grams is not None:
            entity.minimum_stock_grams = dto.minimum_stock_grams
        
        if dto.is_active is not None:
            entity.is_active = dto.is_active
        
        if dto.notes is not None:
            entity.notes = dto.notes
        
        return entity
    
    @staticmethod
    def update_dto_to_entity(dto: FilamentUpdateDTO) -> Filament:
        """
        Convierte FilamentUpdateDTO a Filament entity
        (Utilidad para casos donde necesitas una entidad completa)
        
        Args:
            dto: DTO con datos de actualización
            
        Returns:
            Filament: Entity con datos del DTO
        """
        # Convertir strings de enum a enum types (con defaults)
        filament_type = FilamentType.PLA
        if dto.type is not None:
            try:
                filament_type = FilamentType(dto.type)
            except ValueError:
                pass
        
        filament_color = FilamentColor.WHITE
        if dto.color is not None:
            try:
                filament_color = FilamentColor(dto.color)
            except ValueError:
                pass
        
        filament = Filament(
            id=dto.id,
            name=dto.name or "",
            type=filament_type,
            brand=dto.brand or "",
            color=filament_color,
            weight_grams=dto.weight_grams or 0.0,
            price_per_unit=dto.price_per_unit or 0.0,
            quantity_rolls=dto.quantity_rolls or 0,
            current_stock_grams=dto.current_stock_grams or 0.0,
            minimum_stock_grams=dto.minimum_stock_grams or 0.0,
            is_active=dto.is_active if dto.is_active is not None else True,
            notes=dto.notes or ""
        )
        
        # Calcular precio por gramo si hay datos suficientes
        if filament.price_per_unit > 0 and filament.weight_grams > 0:
            filament.update_price_per_gram()
        
        return filament
