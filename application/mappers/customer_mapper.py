"""
Mapper para convertir entre entidades Customer y DTOs
"""
from typing import List, Optional
from datetime import datetime

from domain.models.customer import Customer
from application.dtos.customer_dtos import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerResponseDTO
)


class CustomerMapper:
    """Mapper para conversiones de Customer"""
    
    @staticmethod
    def create_dto_to_entity(dto: CustomerCreateDTO) -> Customer:
        """
        Convierte CustomerCreateDTO a Customer entity
        
        Args:
            dto: DTO de creación
            
        Returns:
            Entidad Customer
        """
        return Customer(
            full_name=dto.full_name.strip(),
            ruc_ci=dto.ruc_ci.strip(),
            email=dto.email.strip(),
            phone_number=dto.phone_number.strip(),
            is_default=dto.is_default,
            created_at=datetime.now().isoformat()
        )
    
    @staticmethod
    def entity_to_response_dto(entity: Customer) -> CustomerResponseDTO:
        """
        Convierte Customer entity a CustomerResponseDTO
        
        Args:
            entity: Entidad Customer
            
        Returns:
            DTO de respuesta
        """
        return CustomerResponseDTO(
            id=entity.id,
            full_name=entity.full_name,
            ruc_ci=entity.ruc_ci,
            email=entity.email,
            phone_number=entity.phone_number,
            is_default=entity.is_default,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def entities_to_response_dtos(entities: List[Customer]) -> List[CustomerResponseDTO]:
        """
        Convierte lista de Customer entities a lista de DTOs
        
        Args:
            entities: Lista de entidades Customer
            
        Returns:
            Lista de DTOs de respuesta
        """
        return [CustomerMapper.entity_to_response_dto(entity) for entity in entities]
    
    @staticmethod
    def apply_update_dto_to_entity(entity: Customer, dto: CustomerUpdateDTO) -> Customer:
        """
        Aplica los cambios de un UpdateDTO a una entidad existente
        
        Args:
            entity: Entidad Customer existente
            dto: DTO con cambios a aplicar
            
        Returns:
            Entidad Customer actualizada
        """
        if dto.full_name is not None:
            entity.full_name = dto.full_name.strip()
        if dto.ruc_ci is not None:
            entity.ruc_ci = dto.ruc_ci.strip()
        if dto.email is not None:
            entity.email = dto.email.strip()
        if dto.phone_number is not None:
            entity.phone_number = dto.phone_number.strip()
        if dto.is_default is not None:
            entity.is_default = dto.is_default
        
        entity.updated_at = datetime.now().isoformat()
        
        return entity
