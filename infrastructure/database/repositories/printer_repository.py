"""
Repositorio para la entidad Printer
"""
from typing import List, Optional, Dict, Any
from .base_repository import BaseRepository
from domain.models.printer import Printer
from core.utils.logger import error


class PrinterRepository(BaseRepository):
    """Repositorio para gestionar impresoras"""
    
    @property
    def table_name(self) -> str:
        return "printers"
    
    def _row_to_entity(self, row: Dict[str, Any]) -> Printer:
        """Convierte una fila de BD a Printer"""
        return Printer(
            id=row.get('id'),
            name=row.get('name', ''),
            brand=row.get('brand', ''),
            model=row.get('model', ''),
            power_consumption_watts=float(row.get('power_consumption_watts', 0.0)),
            purchase_cost=float(row.get('purchase_cost', 0.0)),
            maintenance_cost=float(row.get('maintenance_cost', 0.0)),
            maintenance_interval_hours=float(row.get('maintenance_interval_hours', 0.0)),
            useful_life_hours=float(row.get('useful_life_hours', 10000.0)),
            is_active=bool(row.get('is_active', True)),
            currency_code=row.get('currency_code', 'PYG'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def _entity_to_dict(self, entity: Printer) -> Dict[str, Any]:
        """Convierte Printer a diccionario"""
        return {
            'id': entity.id,
            'name': entity.name,
            'brand': entity.brand,
            'model': entity.model,
            'power_consumption_watts': entity.power_consumption_watts,
            'purchase_cost': entity.purchase_cost,
            'maintenance_cost': entity.maintenance_cost,
            'maintenance_interval_hours': entity.maintenance_interval_hours,
            'useful_life_hours': entity.useful_life_hours,
            'is_active': entity.is_active,
            'currency_code': entity.currency_code,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
    
    def find_active_printers(self) -> List[Printer]:
        """
        Encuentra todas las impresoras activas
        
        Returns:
            Lista de impresoras activas
        """
        query = f"SELECT * FROM {self.table_name} WHERE is_active = 1 ORDER BY name"
        rows = self.db_connection.execute_query(query)
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_by_brand(self, brand: str) -> List[Printer]:
        """
        Busca impresoras por marca
        
        Args:
            brand: Marca de la impresora
            
        Returns:
            Lista de impresoras de la marca especificada
        """
        query = f"SELECT * FROM {self.table_name} WHERE brand = ? ORDER BY name"
        rows = self.db_connection.execute_query(query, (brand,))
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_printers_needing_maintenance(self, total_hours_used: float) -> List[Printer]:
        """
        Encuentra impresoras que necesitan mantenimiento basado en horas de uso
        
        Args:
            total_hours_used: Total de horas de uso de la impresora
            
        Returns:
            Lista de impresoras que necesitan mantenimiento
        """
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE is_active = 1 
            AND maintenance_interval_hours > 0 
            AND maintenance_interval_hours <= ?
            ORDER BY name
        """
        rows = self.db_connection.execute_query(query, (total_hours_used,))
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def get_maintenance_cost_per_hour(self, printer_id: int) -> float:
        """
        Calcula el costo de mantenimiento por hora para una impresora
        
        Args:
            printer_id: ID de la impresora
            
        Returns:
            float: Costo de mantenimiento por hora
        """
        printer = self.find_by_id(printer_id)
        if printer and printer.maintenance_interval_hours > 0:
            return printer.maintenance_cost / printer.maintenance_interval_hours
        return 0.0
    
    def get_total_operating_cost_per_hour(self, printer_id: int) -> Dict[str, float]:
        """
        Calcula el costo total de operación por hora incluyendo todos los factores
        
        Args:
            printer_id: ID de la impresora
            
        Returns:
            dict: Desglose de costos por hora
        """
        printer = self.find_by_id(printer_id)
        if not printer:
            return {}
        
        return {
            'electricity_cost_per_hour': printer.electricity_cost_per_hour,
            'machine_wear_cost_per_hour': printer.machine_wear_cost_per_hour,
            'maintenance_cost_per_hour': printer.maintenance_cost_per_hour,
            'service_cost_per_hour': printer.service_cost_per_hour,
            'total_cost_per_hour': printer.total_cost_per_hour,
            'useful_life_hours': printer.useful_life_hours,
            'power_consumption_watts': printer.power_consumption_watts
        }
    
    def calculate_operation_cost_for_time(self, printer_id: int, print_time_minutes: float) -> Dict[str, float]:
        """
        Calcula el costo de operación para un tiempo específico de impresión
        
        Args:
            printer_id: ID de la impresora
            print_time_minutes: Tiempo de impresión en minutos
            
        Returns:
            dict: Desglose de costos para el tiempo especificado
        """
        printer = self.find_by_id(printer_id)
        if not printer:
            return {}
        
        operation_cost = printer.calculate_operation_cost(print_time_minutes)
        electricity_cost = printer.electricity_cost_per_hour * (print_time_minutes / 60.0)
        
        return {
            'operation_cost': operation_cost,  # Para el cliente: "Costo de Operación"
            'electricity_cost': electricity_cost,  # Para el cliente: "Electricidad"
            'total_equipment_cost': operation_cost + electricity_cost,
            'print_time_minutes': print_time_minutes,
            'print_time_hours': print_time_minutes / 60.0,
            'service_cost_per_hour': printer.service_cost_per_hour,
            'electricity_cost_per_hour': printer.electricity_cost_per_hour
        }
    
    def find_by_name(self, name: str) -> Optional[Printer]:
        """
        Busca una impresora por nombre exacto
        
        Args:
            name: Nombre de la impresora
            
        Returns:
            Impresora si existe, None en caso contrario
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE LOWER(name) = LOWER(?)"
            rows = self.db_connection.execute_query(query, (name.strip(),))
            
            if rows:
                return self._row_to_entity(dict(rows[0]))
            return None
            
        except Exception as e:
            error("PrinterRepository", f"Error buscando impresora por nombre '{name}': {e}")
            return None
    
    def search(self, search_term: Optional[str] = None, brand_filter: Optional[str] = None, 
               active_only: bool = True) -> List[Printer]:
        """
        Busca impresoras según criterios flexibles
        
        Args:
            search_term: Término a buscar en nombre, marca o modelo
            brand_filter: Filtrar por marca específica
            active_only: Solo impresoras activas
            
        Returns:
            Lista de impresoras que coinciden
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
            params = []
            
            # Filtro de activas
            if active_only:
                query += " AND is_active = ?"
                params.append(True)
            
            # Búsqueda por término
            if search_term and search_term.strip():
                search_term = search_term.strip()
                query += " AND (LOWER(name) LIKE ? OR LOWER(brand) LIKE ? OR LOWER(model) LIKE ?)"
                like_term = f"%{search_term.lower()}%"
                params.extend([like_term, like_term, like_term])
            
            # Filtro por marca
            if brand_filter and brand_filter.strip():
                query += " AND LOWER(brand) = LOWER(?)"
                params.append(brand_filter.strip())
            
            # Ordenar por nombre
            query += " ORDER BY name ASC"
            
            rows = self.db_connection.execute_query(query, params)
            return [self._row_to_entity(dict(row)) for row in rows]
            
        except Exception as e:
            error("PrinterRepository", f"Error buscando impresoras: {e}")
            return []
