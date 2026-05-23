"""
Mapper para convertir entre entidades Printer y DTOs
"""
from typing import List, Optional
from datetime import datetime

from domain.models.printer import Printer
from application.dtos.printer_dtos import (
    PrinterCreateDTO,
    PrinterUpdateDTO,
    PrinterResponseDTO
)
from core.utils.currency_helper import CurrencyHelper


class PrinterMapper:
    """Mapper para conversiones de Printer"""
    
    @staticmethod
    def create_dto_to_entity(dto: PrinterCreateDTO) -> Printer:
        """
        Convierte PrinterCreateDTO a Printer entity
        
        Args:
            dto: DTO de creación
            
        Returns:
            Entidad Printer
        """
        return Printer(
            name=dto.name.strip(),
            brand=dto.brand.strip(),
            model=dto.model.strip(),
            purchase_cost=dto.purchase_cost,
            power_consumption_watts=dto.power_consumption_watts,
            maintenance_cost=dto.maintenance_cost,
            maintenance_interval_hours=dto.maintenance_interval_hours,
            useful_life_hours=10000.0,  # Valor por defecto
            is_active=dto.is_active,
            currency_code=CurrencyHelper.get_current_currency(),  # Moneda del sistema
            created_at=datetime.now().isoformat()
        )
    
    @staticmethod
    def entity_to_response_dto(entity: Printer) -> PrinterResponseDTO:
        """
        Convierte Printer entity a PrinterResponseDTO
        
        Args:
            entity: Entidad Printer
            
        Returns:
            DTO de respuesta
        """
        return PrinterResponseDTO(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            model=entity.model,
            purchase_cost=entity.purchase_cost,
            wear_rate_per_hour=0.0,  # Campo que existe en DTO pero no en entidad
            power_consumption_watts=entity.power_consumption_watts,
            maintenance_cost=entity.maintenance_cost,
            maintenance_interval_hours=entity.maintenance_interval_hours,
            depreciation_rate=0.0,  # Campo que existe en DTO pero no en entidad
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def entities_to_response_dtos(entities: List[Printer]) -> List[PrinterResponseDTO]:
        """
        Convierte lista de Printer entities a lista de DTOs
        
        Args:
            entities: Lista de entidades Printer
            
        Returns:
            Lista de DTOs de respuesta
        """
        return [PrinterMapper.entity_to_response_dto(entity) for entity in entities]
    
    @staticmethod
    def apply_update_dto_to_entity(entity: Printer, dto: PrinterUpdateDTO) -> Printer:
        """
        Aplica los cambios de un UpdateDTO a una entidad existente
        
        Args:
            entity: Entidad Printer existente
            dto: DTO con cambios a aplicar
            
        Returns:
            Entidad Printer actualizada
        """
        if dto.name is not None:
            entity.name = dto.name.strip()
        if dto.brand is not None:
            entity.brand = dto.brand.strip()
        if dto.model is not None:
            entity.model = dto.model.strip()
        if dto.purchase_cost is not None:
            entity.purchase_cost = dto.purchase_cost
        if dto.power_consumption_watts is not None:
            entity.power_consumption_watts = dto.power_consumption_watts
        if dto.maintenance_cost is not None:
            entity.maintenance_cost = dto.maintenance_cost
        if dto.maintenance_interval_hours is not None:
            entity.maintenance_interval_hours = dto.maintenance_interval_hours
        if dto.is_active is not None:
            entity.is_active = dto.is_active
        
        # Nota: wear_rate_per_hour y depreciation_rate no existen en el modelo actual
        
        entity.updated_at = datetime.now().isoformat()
        
        return entity
