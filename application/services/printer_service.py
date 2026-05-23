"""
Servicio para gestión de impresoras 3D
"""
from typing import List, Union
from application.dtos.printer_dtos import (
    PrinterCreateDTO,
    PrinterUpdateDTO,
    PrinterResponseDTO,
    PrinterListDTO,
    PrinterSearchDTO,
    PrinterCostCalculationDTO
)
from application.dtos.base_dtos import BaseResponseDTO, ErrorResponseDTO
from application.mappers.printer_mapper import PrinterMapper
from application.services.base_service import BaseService
from infrastructure.database.repositories.printer_repository import PrinterRepository


class PrinterService(BaseService):
    """
    Servicio para operaciones CRUD y lógica de negocio de impresoras
    """
    
    def __init__(self, db_connection):
        """
        Inicializa el servicio de impresoras
        
        Args:
            db_connection: Conexión a la base de datos
        """
        super().__init__(db_connection)
        self.printer_repository = PrinterRepository(db_connection)
        self.mapper = PrinterMapper()
    
    def create_printer(self, dto: PrinterCreateDTO) -> Union[PrinterResponseDTO, ErrorResponseDTO]:
        """
        Crea una nueva impresora
        
        Args:
            dto: Datos de la impresora a crear
            
        Returns:
            Respuesta con la impresora creada o error
        """
        try:
            # Validar datos
            validation_errors = dto.validate()
            if validation_errors:
                return ErrorResponseDTO(
                    message="Datos inválidos para crear impresora",
                    error_code="VALIDATION_ERROR",
                    error_details={"validation_errors": validation_errors}
                )
            
            # Verificar si ya existe una impresora con el mismo nombre
            existing = self.printer_repository.find_by_name(dto.name.strip())
            if existing:
                return ErrorResponseDTO(
                    message=f"Ya existe una impresora con el nombre '{dto.name.strip()}'",
                    error_code="DUPLICATE_PRINTER_NAME"
                )
            
            # Convertir DTO a entidad
            entity = self.mapper.create_dto_to_entity(dto)
            
            # Guardar en base de datos
            saved_entity = self.printer_repository.save(entity)
            
            # Convertir a DTO de respuesta
            response_dto = self.mapper.entity_to_response_dto(saved_entity)
            
            return response_dto
            
        except Exception as e:
            return ErrorResponseDTO(
                message=f"Error al crear impresora: {str(e)}",
                error_code="CREATE_PRINTER_FAILED"
            )
    
    def get_printer_by_id(self, printer_id: int) -> Union[PrinterResponseDTO, ErrorResponseDTO]:
        """
        Obtiene una impresora por su ID
        
        Args:
            printer_id: ID de la impresora
            
        Returns:
            Respuesta con la impresora o error
        """
        try:
            if printer_id <= 0:
                return ErrorResponseDTO(
                    message="ID de impresora debe ser mayor a 0",
                    error_code="INVALID_PRINTER_ID"
                )
            
            entity = self.printer_repository.find_by_id(printer_id)
            if not entity:
                return ErrorResponseDTO(
                    message=f"No se encontró impresora con ID {printer_id}",
                    error_code="PRINTER_NOT_FOUND"
                )
            
            response_dto = self.mapper.entity_to_response_dto(entity)
            return response_dto
            
        except Exception as e:
            return ErrorResponseDTO(
                message=f"Error al obtener impresora: {str(e)}",
                error_code="GET_PRINTER_FAILED"
            )
    
    def update_printer(self, dto: PrinterUpdateDTO) -> Union[PrinterResponseDTO, ErrorResponseDTO]:
        """
        Actualiza una impresora existente
        
        Args:
            dto: Datos de actualización
            
        Returns:
            Respuesta con la impresora actualizada o error
        """
        try:
            # Validar datos
            validation_errors = dto.validate()
            if validation_errors:
                return ErrorResponseDTO(
                    message="Datos inválidos para actualizar impresora",
                    error_code="VALIDATION_ERROR",
                    error_details={"validation_errors": validation_errors}
                )
            
            # Buscar impresora existente
            existing_entity = self.printer_repository.find_by_id(dto.id)
            if not existing_entity:
                return ErrorResponseDTO(
                    message=f"No se encontró impresora con ID {dto.id}",
                    error_code="PRINTER_NOT_FOUND"
                )
            
            # Verificar nombre duplicado (si se está cambiando)
            if dto.name and dto.name.strip() != existing_entity.name:
                duplicate = self.printer_repository.find_by_name(dto.name.strip())
                if duplicate and duplicate.id != dto.id:
                    return ErrorResponseDTO(
                        message=f"Ya existe otra impresora con el nombre '{dto.name.strip()}'",
                        error_code="DUPLICATE_PRINTER_NAME"
                    )
            
            # Aplicar cambios
            updated_entity = self.mapper.apply_update_dto_to_entity(existing_entity, dto)
            
            # Guardar cambios
            saved_entity = self.printer_repository.update(updated_entity)
            
            # Convertir a DTO de respuesta
            response_dto = self.mapper.entity_to_response_dto(saved_entity)
            
            return response_dto
            
        except Exception as e:
            return ErrorResponseDTO(
                message=f"Error al actualizar impresora: {str(e)}",
                error_code="UPDATE_PRINTER_FAILED"
            )
    
    def delete_printer(self, printer_id: int) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Elimina una impresora (soft delete - marca como inactiva)
        
        Args:
            printer_id: ID de la impresora a eliminar
            
        Returns:
            Respuesta de éxito o error
        """
        try:
            if printer_id <= 0:
                return ErrorResponseDTO(
                    message="ID de impresora debe ser mayor a 0",
                    error_code="INVALID_PRINTER_ID"
                )
            
            # Verificar que existe
            existing = self.printer_repository.find_by_id(printer_id)
            if not existing:
                return ErrorResponseDTO(
                    message=f"No se encontró impresora con ID {printer_id}",
                    error_code="PRINTER_NOT_FOUND"
                )
            
            # TODO: Verificar que no esté siendo usada en cotizaciones activas
            
            # Marcar como inactiva
            existing.is_active = False
            self.printer_repository.update(existing)
            
            return BaseResponseDTO(
                success=True,
                message=f"Impresora '{existing.name}' eliminada correctamente"
            )
            
        except Exception as e:
            return ErrorResponseDTO(
                message=f"Error al eliminar impresora: {str(e)}",
                error_code="DELETE_PRINTER_FAILED"
            )
    
    def search_printers(self, search_dto: PrinterSearchDTO) -> Union[PrinterListDTO, ErrorResponseDTO]:
        """
        Busca impresoras según criterios
        
        Args:
            search_dto: Criterios de búsqueda
            
        Returns:
            Lista de impresoras o error
        """
        try:
            # Obtener entidades del repositorio
            entities = self.printer_repository.search(
                search_term=search_dto.search_term,
                brand_filter=search_dto.brand_filter,
                active_only=search_dto.active_only
            )
            
            # Convertir a DTOs
            printer_dtos = self.mapper.entities_to_response_dtos(entities)
            
            # Aplicar paginación
            total_items = len(printer_dtos)
            start_index = (search_dto.page - 1) * search_dto.page_size
            end_index = start_index + search_dto.page_size
            paginated_items = printer_dtos[start_index:end_index]
            
            # Crear respuesta
            response = PrinterListDTO(
                data=paginated_items,
                success=True,
                message=f"Se encontraron {len(paginated_items)} impresoras"
            )
            
            # Inicializar paginación si no existe
            if response.pagination is None:
                from application.dtos.base_dtos import PaginationDTO
                response.pagination = PaginationDTO()
            
            # Configurar paginación
            response.pagination.page = search_dto.page
            response.pagination.page_size = search_dto.page_size
            response.pagination.total_items = total_items
            response.pagination.calculate_pagination(total_items)
            
            return response
            
        except Exception as e:
            return ErrorResponseDTO(
                message=f"Error al buscar impresoras: {str(e)}",
                error_code="SEARCH_PRINTERS_FAILED"
            )
    
    def get_active_printers(self) -> Union[PrinterListDTO, ErrorResponseDTO]:
        """
        Obtiene todas las impresoras activas
        
        Returns:
            Lista de impresoras activas o error
        """
        search_dto = PrinterSearchDTO(active_only=True, page_size=100)
        return self.search_printers(search_dto)
    
    def calculate_printer_cost(self, dto: PrinterCostCalculationDTO) -> Union[dict, ErrorResponseDTO]:
        """
        Calcula el costo de uso de una impresora
        
        Args:
            dto: Datos para el cálculo
            
        Returns:
            Diccionario con costos calculados o error
        """
        try:
            # Validar datos
            validation_errors = dto.validate()
            if validation_errors:
                return ErrorResponseDTO(
                    message="Datos inválidos para calcular costo",
                    error_code="VALIDATION_ERROR",
                    error_details={"validation_errors": validation_errors}
                )
            
            # Obtener impresora
            printer_response = self.get_printer_by_id(dto.printer_id)
            if isinstance(printer_response, ErrorResponseDTO):
                return printer_response
            
            printer = printer_response
            
            # Convertir minutos a horas
            print_hours = dto.print_time_minutes / 60.0
            
            # Calcular costos
            wear_cost = printer.wear_rate_per_hour * print_hours
            power_cost_kwh = (printer.power_consumption_watts / 1000.0) * print_hours
            
            # TODO: Obtener tarifa eléctrica de configuración
            electricity_rate = 265.0  # Gs por kWh (valor por defecto)
            electricity_cost = power_cost_kwh * electricity_rate
            
            depreciation_cost = (printer.purchase_cost * printer.depreciation_rate / 100) / 8760 * print_hours  # Por hora de vida útil
            
            total_printer_cost = wear_cost + electricity_cost + depreciation_cost
            
            return {
                'printer_info': {
                    'id': printer.id,
                    'name': printer.name,
                    'brand': printer.brand,
                    'model': printer.model
                },
                'calculation_details': {
                    'print_hours': print_hours,
                    'wear_cost': wear_cost,
                    'electricity_cost': electricity_cost,
                    'depreciation_cost': depreciation_cost,
                    'total_cost': total_printer_cost
                }
            }
            
        except Exception as e:
            return ErrorResponseDTO(
                message=f"Error al calcular costo de impresora: {str(e)}",
                error_code="CALCULATE_PRINTER_COST_FAILED"
            )
