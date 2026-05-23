"""
Servicio base para todos los servicios de aplicación
"""
from abc import ABC
from typing import List, Optional, Any
from infrastructure.database.connection import DatabaseConnection
from application.dtos.base_dtos import BaseResponseDTO, ErrorResponseDTO


class BaseService(ABC):
    """Servicio base con funcionalidades comunes"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el servicio base
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
    
    def create_success_response(self, message: str = "Operación exitosa", data: Any = None) -> BaseResponseDTO:
        """
        Crea una respuesta exitosa
        
        Args:
            message: Mensaje de éxito
            data: Datos de respuesta
            
        Returns:
            Respuesta exitosa
        """
        response = BaseResponseDTO(success=True, message=message)
        if data is not None:
            response.data = data
        return response
    
    def create_error_response(self, message: str, error_code: str = None, error_details: dict = None) -> ErrorResponseDTO:
        """
        Crea una respuesta de error
        
        Args:
            message: Mensaje de error
            error_code: Código de error
            error_details: Detalles del error
            
        Returns:
            Respuesta de error
        """
        return ErrorResponseDTO(
            message=message,
            error_code=error_code,
            error_details=error_details
        )
    
    def validate_dto(self, dto: Any) -> Optional[ErrorResponseDTO]:
        """
        Valida un DTO y retorna error si hay problemas
        
        Args:
            dto: DTO a validar
            
        Returns:
            ErrorResponseDTO si hay errores, None si es válido
        """
        if hasattr(dto, 'validate'):
            errors = dto.validate()
            if errors:
                return self.create_error_response(
                    message="Datos de entrada inválidos",
                    error_code="VALIDATION_ERROR",
                    error_details={"validation_errors": errors}
                )
        return None
    
    def handle_repository_error(self, error: Exception, operation: str) -> ErrorResponseDTO:
        """
        Maneja errores del repositorio
        
        Args:
            error: Excepción capturada
            operation: Nombre de la operación que falló
            
        Returns:
            Respuesta de error
        """
        error_message = f"Error en {operation}: {str(error)}"
        return self.create_error_response(
            message=error_message,
            error_code="REPOSITORY_ERROR",
            error_details={"operation": operation, "original_error": str(error)}
        )
