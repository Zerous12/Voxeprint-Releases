"""
Servicio para la gestión de filamentos
"""
from typing import Optional, Dict, Any, Union
from application.services.base_service import BaseService
from application.mappers.filament_mapper import FilamentMapper
from application.dtos.filament_dtos import FilamentListDTO, FilamentSearchDTO
from application.dtos.base_dtos import PaginationDTO
from infrastructure.database.repositories.filament_repository import FilamentRepository
from infrastructure.database.connection import DatabaseConnection


class FilamentService(BaseService):
    """Servicio para operaciones de filamento"""

    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el servicio
        
        Args:
            db_connection: Conexión a la base de datos
        """
        super().__init__(db_connection)
        self.repository = FilamentRepository(db_connection)
        self.mapper = FilamentMapper()

    def get_active_filaments(self, page: int = 1, page_size: int = 50) -> FilamentListDTO:
        """
        Obtiene todos los filamentos activos con paginación
        
        Args:
            page: Número de página (1-based)
            page_size: Tamaño de página
            
        Returns:
            FilamentListDTO con la lista de filamentos y paginación
        """
        try:
            # Obtener filamentos activos
            filaments = self.repository.find_active_filaments()
            
            # Convertir entidades a DTOs
            filament_dtos = [self.mapper.entity_to_response_dto(f) for f in filaments]
            
            # Calcular paginación
            total_items = len(filament_dtos)
            total_pages = max(1, (total_items + page_size - 1) // page_size)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            # Aplicar paginación
            paginated_data = filament_dtos[start_idx:end_idx]
            
            # Crear DTO de paginación
            pagination = PaginationDTO(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages
            )
            
            return FilamentListDTO(
                success=True,
                message=f"Se encontraron {total_items} filamentos activos",
                data=paginated_data,
                pagination=pagination
            )
            
        except Exception as e:
            # Crear paginación vacía para errores
            pagination = PaginationDTO(
                page=page,
                page_size=page_size,
                total_items=0,
                total_pages=1
            )
            
            return FilamentListDTO(
                success=False,
                message=f"Error obteniendo filamentos activos: {str(e)}",
                data=[],
                pagination=pagination
            )