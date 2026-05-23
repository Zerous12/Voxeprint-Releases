"""
Repositorio para las configuraciones del sistema
"""
from typing import List, Optional, Dict, Any
from .base_repository import BaseRepository
from domain.models.system_config import SystemConfig


class SystemConfigRepository(BaseRepository):
    """Repositorio para gestionar configuraciones del sistema"""
    
    @property
    def table_name(self) -> str:
        return "system_configs"
    
    def _row_to_entity(self, row: Dict[str, Any]) -> SystemConfig:
        """Convierte una fila de BD a SystemConfig"""
        return SystemConfig(
            id=row.get('id'),
            config_key=row.get('config_key', ''),
            config_value=row.get('config_value', ''),
            config_type=row.get('config_type', 'string'),
            description=row.get('description', ''),
            category=row.get('category', 'general'),
            is_editable=bool(row.get('is_editable', True)),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def _entity_to_dict(self, entity: SystemConfig) -> Dict[str, Any]:
        """Convierte SystemConfig a diccionario"""
        return {
            'id': entity.id,
            'config_key': entity.config_key,
            'config_value': entity.config_value,
            'config_type': entity.config_type,
            'description': entity.description,
            'category': entity.category,
            'is_editable': entity.is_editable,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
    
    def find_by_key(self, config_key: str) -> Optional[SystemConfig]:
        """
        Busca una configuración por su clave
        
        Args:
            config_key: Clave de la configuración
            
        Returns:
            Configuración encontrada o None
        """
        query = f"SELECT * FROM {self.table_name} WHERE config_key = ? LIMIT 1"
        rows = self.db_connection.execute_query(query, (config_key,))
        
        if rows:
            return self._row_to_entity(dict(rows[0]))
        return None
    
    def find_by_category(self, category: str) -> List[SystemConfig]:
        """
        Busca configuraciones por categoría
        
        Args:
            category: Categoría de las configuraciones
            
        Returns:
            Lista de configuraciones de la categoría
        """
        query = f"SELECT * FROM {self.table_name} WHERE category = ? ORDER BY config_key"
        rows = self.db_connection.execute_query(query, (category,))
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def get_value(self, config_key: str, default_value: str = "") -> str:
        """
        Obtiene el valor de una configuración
        
        Args:
            config_key: Clave de la configuración
            default_value: Valor por defecto si no se encuentra
            
        Returns:
            Valor de la configuración o valor por defecto
        """
        config = self.find_by_key(config_key)
        return config.config_value if config else default_value
    
    def get_float_value(self, config_key: str, default_value: float = 0.0) -> float:
        """
        Obtiene el valor float de una configuración
        
        Args:
            config_key: Clave de la configuración
            default_value: Valor por defecto si no se encuentra
            
        Returns:
            Valor float de la configuración
        """
        try:
            return float(self.get_value(config_key, str(default_value)))
        except ValueError:
            return default_value
    
    def get_int_value(self, config_key: str, default_value: int = 0) -> int:
        """
        Obtiene el valor int de una configuración
        
        Args:
            config_key: Clave de la configuración
            default_value: Valor por defecto si no se encuentra
            
        Returns:
            Valor int de la configuración
        """
        try:
            return int(self.get_value(config_key, str(default_value)))
        except ValueError:
            return default_value
    
    def get_bool_value(self, config_key: str, default_value: bool = False) -> bool:
        """
        Obtiene el valor bool de una configuración
        
        Args:
            config_key: Clave de la configuración
            default_value: Valor por defecto si no se encuentra
            
        Returns:
            Valor bool de la configuración
        """
        value = self.get_value(config_key, str(default_value)).lower()
        return value in ('1', 'true', 'yes', 'on')
    
    def update_value(self, config_key: str, new_value: str) -> bool:
        """
        Actualiza el valor de una configuración
        
        Args:
            config_key: Clave de la configuración
            new_value: Nuevo valor
            
        Returns:
            True si se actualizó correctamente
        """
        command = f"UPDATE {self.table_name} SET config_value = ? WHERE config_key = ? AND is_editable = 1"
        affected_rows = self.db_connection.execute_command(command, (new_value, config_key))
        return affected_rows > 0
    
    def set_config(self, config_key: str, config_value: str, category: str = "general") -> bool:
        """
        Establece o actualiza una configuración (insert or update)
        
        Args:
            config_key: Clave de la configuración
            config_value: Valor de la configuración
            category: Categoría de la configuración
            
        Returns:
            True si se estableció correctamente
        """
        existing_config = self.find_by_key(config_key)
        
        if existing_config:
            # Actualizar configuración existente
            return self.update_value(config_key, config_value)
        else:
            # Crear nueva configuración
            new_config = SystemConfig(
                config_key=config_key,
                config_value=config_value,
                category=category,
                is_editable=True
            )
            saved_config = self.save(new_config)
            return saved_config is not None
    
    def get_config(self, config_key: str, default_value: str = "") -> str:
        """
        Alias para get_value para mantener compatibilidad
        
        Args:
            config_key: Clave de la configuración
            default_value: Valor por defecto si no se encuentra
            
        Returns:
            Valor de la configuración o valor por defecto
        """
        return self.get_value(config_key, default_value)
