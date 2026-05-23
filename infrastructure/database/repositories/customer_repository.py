"""
Repositorio para la entidad Customer
"""
from typing import List, Optional, Dict, Any
from .base_repository import BaseRepository
from domain.models.customer import Customer
from core.utils.logger import error


class CustomerRepository(BaseRepository):
    """Repositorio para gestionar clientes"""
    
    @property
    def table_name(self) -> str:
        return "customers"
    
    def _row_to_entity(self, row: Dict[str, Any]) -> Customer:
        """Convierte una fila de BD a Customer"""
        return Customer(
            id=row.get('id'),
            full_name=row.get('full_name', ''),
            ruc_ci=row.get('ruc_ci', ''),
            email=row.get('email', ''),
            phone_number=row.get('phone_number', ''),
            is_default=bool(row.get('is_default', False)),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def _entity_to_dict(self, entity: Customer) -> Dict[str, Any]:
        """Convierte Customer a diccionario"""
        return {
            'id': entity.id,
            'full_name': entity.full_name,
            'ruc_ci': entity.ruc_ci,
            'email': entity.email,
            'phone_number': entity.phone_number,
            'is_default': entity.is_default,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
    
    def find_default_customer(self) -> Optional[Customer]:
        """
        Busca el cliente marcado como predeterminado
        
        Returns:
            Cliente predeterminado o None si no existe
        """
        query = f"SELECT * FROM {self.table_name} WHERE is_default = 1 LIMIT 1"
        rows = self.db_connection.execute_query(query)
        
        if rows:
            return self._row_to_entity(dict(rows[0]))
        return None
    
    def find_by_ruc_ci(self, ruc_ci: str) -> Optional[Customer]:
        """
        Busca un cliente por RUC/CI
        
        Args:
            ruc_ci: RUC o CI a buscar
            
        Returns:
            Cliente encontrado o None
        """
        query = f"SELECT * FROM {self.table_name} WHERE ruc_ci = ? LIMIT 1"
        rows = self.db_connection.execute_query(query, (ruc_ci,))
        
        if rows:
            return self._row_to_entity(dict(rows[0]))
        return None
    
    def search_by_name(self, name_pattern: str) -> List[Customer]:
        """
        Busca clientes por patrón en el nombre
        
        Args:
            name_pattern: Patrón a buscar en el nombre
            
        Returns:
            Lista de clientes que coinciden
        """
        query = f"SELECT * FROM {self.table_name} WHERE full_name LIKE ? ORDER BY full_name"
        rows = self.db_connection.execute_query(query, (f'%{name_pattern}%',))
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def search_customers(self, search_term: Optional[str] = None, is_default_only: bool = False) -> List[Customer]:
        """
        Busca clientes con filtros opcionales
        
        Args:
            search_term: Término de búsqueda (nombre, email, teléfono, RUC/CI)
            is_default_only: Solo clientes predeterminados
            
        Returns:
            Lista de clientes que coinciden
        """
        conditions = []
        params = []
        
        if is_default_only:
            conditions.append("is_default = 1")
        
        if search_term:
            search_condition = "(full_name LIKE ? OR email LIKE ? OR phone_number LIKE ? OR ruc_ci LIKE ?)"
            conditions.append(search_condition)
            search_param = f'%{search_term}%'
            params.extend([search_param, search_param, search_param, search_param])
        
        where_clause = ""
        if conditions:
            where_clause = f" WHERE {' AND '.join(conditions)}"
        
        query = f"SELECT * FROM {self.table_name}{where_clause} ORDER BY full_name"
        rows = self.db_connection.execute_query(query, params)
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def clear_default_customers(self) -> int:
        """
        Remueve el flag is_default de todos los clientes
        
        Returns:
            Número de filas afectadas
        """
        command = f"UPDATE {self.table_name} SET is_default = 0 WHERE is_default = 1"
        return self.db_connection.execute_command(command)
    
    def create(self, customer_data: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo cliente
        
        Args:
            customer_data: Diccionario con los datos del cliente
            
        Returns:
            ID del cliente creado o None si falló
        """
        try:
            # Si se marca como predeterminado, limpiar otros primero
            if customer_data.get('is_default', False):
                self.clear_default_customers()
            
            # Crear objeto Customer
            customer = Customer(
                full_name=customer_data.get('full_name', ''),
                ruc_ci=customer_data.get('ruc_ci'),
                email=customer_data.get('email'),
                phone_number=customer_data.get('phone_number'),
                is_default=customer_data.get('is_default', False)
            )
            
            # Guardar usando el método base
            saved_customer = self.save(customer)
            return saved_customer.id if saved_customer else None
            
        except Exception as e:
            error("CustomerRepository", f"Error creando cliente: {e}")
            return None
    
    def update(self, customer_id: int, customer_data: Dict[str, Any]) -> bool:
        """
        Actualiza un cliente existente
        
        Args:
            customer_id: ID del cliente a actualizar
            customer_data: Diccionario con los datos actualizados
            
        Returns:
            True si se actualizó exitosamente, False en caso contrario
        """
        try:
            # Obtener el cliente actual
            current_customer = self.find_by_id(customer_id)
            if not current_customer:
                return False
            
            # Si se marca como predeterminado, limpiar otros primero
            if customer_data.get('is_default', False) and not current_customer.is_default:
                self.clear_default_customers()
            
            # Actualizar los campos
            current_customer.full_name = customer_data.get('full_name', current_customer.full_name)
            current_customer.ruc_ci = customer_data.get('ruc_ci', current_customer.ruc_ci)
            current_customer.email = customer_data.get('email', current_customer.email)
            current_customer.phone_number = customer_data.get('phone_number', current_customer.phone_number)
            current_customer.is_default = customer_data.get('is_default', current_customer.is_default)
            
            # Guardar usando el método base
            saved_customer = self.save(current_customer)
            return saved_customer is not None
            
        except Exception as e:
            error("CustomerRepository", f"Error actualizando cliente: {e}")
            return False