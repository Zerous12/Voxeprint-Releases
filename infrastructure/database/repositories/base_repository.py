"""
Repositorio base con operaciones CRUD comunes
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..connection import DatabaseConnection


class BaseRepository(ABC):
    """Repositorio base con operaciones CRUD comunes"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el repositorio base
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Nombre de la tabla en la base de datos"""
        pass
    
    @abstractmethod
    def _row_to_entity(self, row: Dict[str, Any]) -> Any:
        """
        Convierte una fila de la base de datos a una entidad
        
        Args:
            row: Fila de la base de datos
            
        Returns:
            Entidad correspondiente
        """
        pass
    
    @abstractmethod
    def _entity_to_dict(self, entity: Any) -> Dict[str, Any]:
        """
        Convierte una entidad a un diccionario para la base de datos
        
        Args:
            entity: Entidad a convertir
            
        Returns:
            Diccionario con los datos de la entidad
        """
        pass
    
    def find_by_id(self, entity_id: int) -> Optional[Any]:
        """
        Busca una entidad por su ID
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            Entidad encontrada o None
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        rows = self.db_connection.execute_query(query, (entity_id,))
        
        if rows:
            return self._row_to_entity(dict(rows[0]))
        return None
    
    def find_all(self) -> List[Any]:
        """
        Obtiene todas las entidades
        
        Returns:
            Lista de entidades
        """
        query = f"SELECT * FROM {self.table_name} ORDER BY id"
        rows = self.db_connection.execute_query(query)
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def save(self, entity: Any) -> Any:
        """
        Guarda una entidad (insertar o actualizar)
        
        Args:
            entity: Entidad a guardar
            
        Returns:
            Entidad guardada con ID actualizado
        """
        if hasattr(entity, 'id') and entity.id:
            return self._update(entity)
        else:
            return self._insert(entity)
    
    def delete(self, entity_id: int) -> bool:
        """
        Elimina una entidad por su ID
        
        Args:
            entity_id: ID de la entidad a eliminar
            
        Returns:
            True si se eliminó, False si no se encontró
        """
        command = f"DELETE FROM {self.table_name} WHERE id = ?"
        affected_rows = self.db_connection.execute_command(command, (entity_id,))
        return affected_rows > 0
    
    def _insert(self, entity: Any) -> Any:
        """
        Inserta una nueva entidad
        
        Args:
            entity: Entidad a insertar
            
        Returns:
            Entidad insertada con ID asignado
        """
        data = self._entity_to_dict(entity)
        data.pop('id', None)  # Remover ID para auto-increment
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        command = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        new_id = self.db_connection.execute_command(command, values)
        
        entity.id = new_id
        
        # Actualizar fechas en el objeto si las tiene
        if hasattr(entity, 'created_at') and 'created_at' in data:
            entity.created_at = data['created_at']
        if hasattr(entity, 'updated_at') and 'updated_at' in data:
            entity.updated_at = data['updated_at']
            
        return entity
    
    def _update(self, entity: Any) -> Any:
        """
        Actualiza una entidad existente
        
        Args:
            entity: Entidad a actualizar
            
        Returns:
            Entidad actualizada
        """
        data = self._entity_to_dict(entity)
        entity_id = data.pop('id')
        
        set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
        values = tuple(data.values()) + (entity_id,)
        
        command = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        self.db_connection.execute_command(command, values)
        
        # Actualizar fechas en el objeto si las tiene
        if hasattr(entity, 'updated_at') and 'updated_at' in data:
            entity.updated_at = data['updated_at']
        
        return entity
