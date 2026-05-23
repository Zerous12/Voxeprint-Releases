"""
Servicio para gestión de clientes
"""
from typing import List, Optional, Union
from datetime import datetime

from .base_service import BaseService
from application.dtos.customer_dtos import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerResponseDTO,
    CustomerListDTO,
    CustomerSearchDTO
)
from application.dtos.base_dtos import BaseResponseDTO, ErrorResponseDTO
from application.mappers.customer_mapper import CustomerMapper
from domain.models.customer import Customer
from infrastructure.database.repositories.customer_repository import CustomerRepository
from infrastructure.database.connection import DatabaseConnection


class CustomerService(BaseService):
    """Servicio para gestión de clientes"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el servicio de clientes
        
        Args:
            db_connection: Conexión a la base de datos
        """
        super().__init__(db_connection)
        self.repository = CustomerRepository(db_connection)
    
    def create_customer(self, dto: CustomerCreateDTO) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Crea un nuevo cliente
        
        Args:
            dto: Datos para crear el cliente
            
        Returns:
            Respuesta con el cliente creado o error
        """
        # Validar DTO
        validation_error = self.validate_dto(dto)
        if validation_error:
            return validation_error
        
        try:
            # Verificar si ya existe un cliente con el mismo RUC/CI (si no está vacío)
            if dto.ruc_ci.strip():
                existing = self.repository.find_by_ruc_ci(dto.ruc_ci)
                if existing:
                    return self.create_error_response(
                        message="Ya existe un cliente con ese RUC/CI",
                        error_code="DUPLICATE_RUC_CI"
                    )
            
            # Si se marca como predeterminado, quitar ese flag de otros clientes
            if dto.is_default:
                self.repository.clear_default_customers()
            
            # Crear entidad usando mapper
            customer = CustomerMapper.create_dto_to_entity(dto)
            
            # Guardar en repositorio
            saved_customer = self.repository.save(customer)
            
            # Convertir a DTO de respuesta usando mapper
            response_dto = CustomerMapper.entity_to_response_dto(saved_customer)
            
            return self.create_success_response(
                message="Cliente creado exitosamente",
                data=response_dto
            )
            
        except Exception as e:
            return self.handle_repository_error(e, "crear cliente")
    
    def update_customer(self, dto: CustomerUpdateDTO) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Actualiza un cliente existente
        
        Args:
            dto: Datos para actualizar el cliente
            
        Returns:
            Respuesta con el cliente actualizado o error
        """
        # Validar DTO
        validation_error = self.validate_dto(dto)
        if validation_error:
            return validation_error
        
        try:
            # Buscar cliente existente
            existing_customer = self.repository.find_by_id(dto.id)
            if not existing_customer:
                return self.create_error_response(
                    message="Cliente no encontrado",
                    error_code="CUSTOMER_NOT_FOUND"
                )
            
            # Verificar RUC/CI único si se está actualizando
            if dto.ruc_ci is not None and dto.ruc_ci.strip():
                existing_with_ruc = self.repository.find_by_ruc_ci(dto.ruc_ci)
                if existing_with_ruc and existing_with_ruc.id != dto.id:
                    return self.create_error_response(
                        message="Ya existe otro cliente con ese RUC/CI",
                        error_code="DUPLICATE_RUC_CI"
                    )
            
            # Si se marca como predeterminado, quitar ese flag de otros clientes
            if dto.is_default:
                self.repository.clear_default_customers()
            
            # Actualizar campos usando mapper
            CustomerMapper.apply_update_dto_to_entity(existing_customer, dto)
            
            # Guardar cambios
            updated_customer = self.repository.save(existing_customer)
            
            # Convertir a DTO de respuesta usando mapper
            response_dto = CustomerMapper.entity_to_response_dto(updated_customer)
            
            return self.create_success_response(
                message="Cliente actualizado exitosamente",
                data=response_dto
            )
            
        except Exception as e:
            return self.handle_repository_error(e, "actualizar cliente")
    
    def get_customer_by_id(self, customer_id: int) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Obtiene un cliente por su ID
        
        Args:
            customer_id: ID del cliente
            
        Returns:
            Respuesta con el cliente o error
        """
        if customer_id <= 0:
            return self.create_error_response(
                message="ID de cliente inválido",
                error_code="INVALID_ID"
            )
        
        try:
            customer = self.repository.find_by_id(customer_id)
            if not customer:
                return self.create_error_response(
                    message="Cliente no encontrado",
                    error_code="CUSTOMER_NOT_FOUND"
                )
            
            response_dto = CustomerMapper.entity_to_response_dto(customer)
            return self.create_success_response(data=response_dto)
            
        except Exception as e:
            return self.handle_repository_error(e, "obtener cliente")
    
    def search_customers(self, search_dto: CustomerSearchDTO) -> Union[CustomerListDTO, ErrorResponseDTO]:
        """
        Busca clientes según criterios
        
        Args:
            search_dto: Criterios de búsqueda
            
        Returns:
            Lista de clientes o error
        """
        try:
            customers = self.repository.search_customers(
                search_term=search_dto.search_term,
                is_default_only=search_dto.is_default_only
            )
            
            # Aplicar paginación si es necesario
            total_items = len(customers)
            start_idx = (search_dto.page - 1) * search_dto.page_size
            end_idx = start_idx + search_dto.page_size
            paginated_customers = customers[start_idx:end_idx]
            
            # Convertir a DTOs de respuesta usando mapper
            response_dtos = CustomerMapper.entities_to_response_dtos(paginated_customers)
            
            # Crear respuesta
            response = CustomerListDTO(
                success=True,
                message="Búsqueda completada",
                data=response_dtos
            )
            
            # Agregar información de paginación
            from application.dtos.base_dtos import PaginationDTO
            pagination = PaginationDTO(
                page=search_dto.page,
                page_size=search_dto.page_size
            )
            pagination.calculate_pagination(total_items)
            response.pagination = pagination
            
            return response
            
        except Exception as e:
            return self.handle_repository_error(e, "buscar clientes")
    
    def delete_customer(self, customer_id: int) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Elimina un cliente
        
        Args:
            customer_id: ID del cliente a eliminar
            
        Returns:
            Respuesta de éxito o error
        """
        if customer_id <= 0:
            return self.create_error_response(
                message="ID de cliente inválido",
                error_code="INVALID_ID"
            )
        
        try:
            # Verificar que el cliente existe
            customer = self.repository.find_by_id(customer_id)
            if not customer:
                return self.create_error_response(
                    message="Cliente no encontrado",
                    error_code="CUSTOMER_NOT_FOUND"
                )
            
            # Verificar que no es cliente predeterminado
            if customer.is_default:
                return self.create_error_response(
                    message="No se puede eliminar el cliente predeterminado",
                    error_code="CANNOT_DELETE_DEFAULT"
                )
            
            # TODO: Verificar que no tiene presupuestos asociados
            # quote_count = self.quote_repository.count_by_customer(customer_id)
            # if quote_count > 0:
            #     return self.create_error_response(
            #         message="No se puede eliminar un cliente con presupuestos asociados",
            #         error_code="CUSTOMER_HAS_QUOTES"
            #     )
            
            # Eliminar cliente
            deleted = self.repository.delete(customer_id)
            if not deleted:
                return self.create_error_response(
                    message="No se pudo eliminar el cliente",
                    error_code="DELETE_FAILED"
                )
            
            return self.create_success_response(message="Cliente eliminado exitosamente")
            
        except Exception as e:
            return self.handle_repository_error(e, "eliminar cliente")
    
    def get_default_customer(self) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Obtiene el cliente predeterminado
        
        Returns:
            Respuesta con el cliente predeterminado o error
        """
        try:
            customer = self.repository.find_default_customer()
            if not customer:
                return self.create_error_response(
                    message="No hay cliente predeterminado configurado",
                    error_code="NO_DEFAULT_CUSTOMER"
                )
            
            response_dto = CustomerMapper.entity_to_response_dto(customer)
            return self.create_success_response(data=response_dto)
            
        except Exception as e:
            return self.handle_repository_error(e, "obtener cliente predeterminado")
    
    def set_default_customer(self, customer_id: int) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Establece un cliente como predeterminado
        
        Args:
            customer_id: ID del cliente a establecer como predeterminado
            
        Returns:
            Respuesta de éxito o error
        """
        try:
            customer = self.repository.find_by_id(customer_id)
            if not customer:
                return self.create_error_response(
                    message="Cliente no encontrado",
                    error_code="CUSTOMER_NOT_FOUND"
                )
            
            if customer.is_default:
                return self.create_error_response(
                    message="Este cliente ya es el predeterminado",
                    error_code="ALREADY_DEFAULT"
                )
            
            # Quitar flag de otros clientes y asignar al nuevo
            self.repository.clear_default_customers()
            customer.is_default = True
            self.repository.save(customer)
            
            response_dto = CustomerMapper.entity_to_response_dto(customer)
            return self.create_success_response(
                message="Cliente establecido como predeterminado exitosamente",
                data=response_dto
            )
            
        except Exception as e:
            return self.handle_repository_error(e, "establecer cliente predeterminado")

    # Eliminamos el método _customer_to_response_dto ya que usamos el mapper
