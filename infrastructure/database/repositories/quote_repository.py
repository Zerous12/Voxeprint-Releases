"""
Repositorio para la entidad Quote
"""
from typing import List, Optional, Dict, Any, Tuple
from .base_repository import BaseRepository
from domain.models.quote import Quote
from domain.enums.enums import QuoteStatus


class QuoteRepository(BaseRepository):
    """Repositorio para gestionar presupuestos"""
    
    @property
    def table_name(self) -> str:
        return "quotes"
    
    def _row_to_entity(self, row: Dict[str, Any]) -> Quote:
        """Convierte una fila de BD a Quote"""
        # Convertir print_time_hours de DB a print_time_minutes para el modelo
        print_time_hours = float(row.get('print_time_hours', 0.0))
        print_time_minutes = print_time_hours * 60.0  # Convertir horas a minutos
        
        return Quote(
            id=row.get('id'),
            quote_number=row.get('quote_number', ''),
            customer_id=row.get('customer_id'),
            printer_id=row.get('printer_id'),
            filament_id=row.get('filament_id'),
            project_name=row.get('project_name', ''),
            print_time_minutes=print_time_minutes,  # Convertido de horas a minutos
            filament_weight_grams=float(row.get('filament_weight_grams', 0.0)),
            total_to_pay=float(row.get('final_price', 0.0)),  # final_price de DB -> total_to_pay del modelo
            currency_code=row.get('currency_code', 'PYG'),  # Mapear currency_code de BD
            file_path=row.get('file_path', ''),
            notes=row.get('notes', ''),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def _entity_to_dict(self, entity: Quote) -> Dict[str, Any]:
        """Convierte Quote a diccionario para la BD (solo campos que existen en la tabla)"""
        # Convertir print_time_minutes del modelo a print_time_hours para la DB
        print_time_hours = entity.print_time_minutes / 60.0 if hasattr(entity, 'print_time_minutes') else 0.0
        
        return {
            'id': entity.id,
            'quote_number': entity.quote_number,
            'customer_id': entity.customer_id,
            'printer_id': entity.printer_id,
            'filament_id': entity.filament_id,
            'project_name': entity.project_name,
            'print_time_hours': print_time_hours,  # Convertido de minutos a horas
            'filament_weight_grams': entity.filament_weight_grams,
            'final_price': getattr(entity, 'total_to_pay', 0.0),  # total_to_pay del modelo -> final_price de DB
            'file_path': getattr(entity, 'file_path', ''),
            'notes': getattr(entity, 'notes', ''),
            'created_at': getattr(entity, 'created_at', None),
            'updated_at': getattr(entity, 'updated_at', None)
        }
    
    def find_all(self) -> List[Quote]:
        """
        Obtiene todos los presupuestos ordenados del más nuevo al más antiguo
        
        Returns:
            Lista de presupuestos ordenados por fecha de creación descendente
        """
        query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC"
        rows = self.db_connection.execute_query(query)
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_by_customer(self, customer_id: int) -> List[Quote]:
        """
        Busca presupuestos por cliente
        
        Args:
            customer_id: ID del cliente
            
        Returns:
            Lista de presupuestos del cliente
        """
        query = f"SELECT * FROM {self.table_name} WHERE customer_id = ? ORDER BY created_at DESC"
        rows = self.db_connection.execute_query(query, (customer_id,))
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_by_status(self, status: QuoteStatus) -> List[Quote]:
        """
        Busca presupuestos por estado
        
        Args:
            status: Estado del presupuesto
            
        Returns:
            Lista de presupuestos con el estado especificado
        """
        query = f"SELECT * FROM {self.table_name} WHERE status = ? ORDER BY created_at DESC"
        rows = self.db_connection.execute_query(query, (status.value,))
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_by_quote_number(self, quote_number: str) -> Optional[Quote]:
        """
        Busca un presupuesto por su número
        
        Args:
            quote_number: Número del presupuesto
            
        Returns:
            Presupuesto encontrado o None
        """
        query = f"SELECT * FROM {self.table_name} WHERE quote_number = ? LIMIT 1"
        rows = self.db_connection.execute_query(query, (quote_number,))
        
        if rows:
            return self._row_to_entity(dict(rows[0]))
        return None
    
    def get_recent_quotes(self, limit: int = 10) -> List[Quote]:
        """
        Obtiene los presupuestos más recientes
        
        Args:
            limit: Número máximo de presupuestos a retornar
            
        Returns:
            Lista de presupuestos recientes
        """
        query = f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT ?"
        rows = self.db_connection.execute_query(query, (limit,))
        
        return [self._row_to_entity(dict(row)) for row in rows]

    # === MÉTODOS DE ESTADÍSTICAS ===

    def get_monthly_stats(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Obtiene estadísticas mensuales de cotización en un rango de fechas.
        
        Args:
            start_date: Fecha inicio formato 'YYYY-MM-DD'
            end_date: Fecha fin formato 'YYYY-MM-DD'
            
        Returns:
            Lista de dicts con: month, currency_code, total_amount, quote_count
        """
        query = """
            SELECT 
                strftime('%Y-%m', created_at) as month,
                currency_code,
                SUM(final_price) as total_amount,
                COUNT(*) as quote_count
            FROM quotes
            WHERE created_at >= ? AND created_at <= ?
            GROUP BY strftime('%Y-%m', created_at), currency_code
            ORDER BY month ASC
        """
        rows = self.db_connection.execute_query(query, (start_date, end_date))
        return [dict(row) for row in rows]

    def get_weekly_stats(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Obtiene estadísticas semanales de cotización en un rango de fechas.
        
        Returns:
            Lista de dicts con: week, week_start, currency_code, total_amount, quote_count
        """
        query = """
            SELECT 
                strftime('%Y-W%W', created_at) as week,
                MIN(date(created_at)) as week_start,
                currency_code,
                SUM(final_price) as total_amount,
                COUNT(*) as quote_count
            FROM quotes
            WHERE created_at >= ? AND created_at <= ?
            GROUP BY strftime('%Y-W%W', created_at), currency_code
            ORDER BY week ASC
        """
        rows = self.db_connection.execute_query(query, (start_date, end_date))
        return [dict(row) for row in rows]

    def get_daily_stats(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Obtiene estadísticas diarias de cotización en un rango de fechas.
        
        Returns:
            Lista de dicts con: day, currency_code, total_amount, quote_count
        """
        query = """
            SELECT 
                date(created_at) as day,
                currency_code,
                SUM(final_price) as total_amount,
                COUNT(*) as quote_count
            FROM quotes
            WHERE created_at >= ? AND created_at <= ?
            GROUP BY date(created_at), currency_code
            ORDER BY day ASC
        """
        rows = self.db_connection.execute_query(query, (start_date, end_date))
        return [dict(row) for row in rows]

    def get_top_customers(self, start_date: str, end_date: str, limit: int = 7) -> List[Dict[str, Any]]:
        """
        Obtiene ranking de clientes por monto cotizado en un rango de fechas.
        
        Returns:
            Lista de dicts con: customer_id, customer_name, currency_code, total_amount, quote_count
        """
        query = """
            SELECT 
                q.customer_id,
                COALESCE(c.full_name, 'Sin cliente') as customer_name,
                q.currency_code,
                SUM(q.final_price) as total_amount,
                COUNT(*) as quote_count
            FROM quotes q
            LEFT JOIN customers c ON q.customer_id = c.id
            WHERE q.created_at >= ? AND q.created_at <= ?
            GROUP BY q.customer_id, q.currency_code
            ORDER BY total_amount DESC
            LIMIT ?
        """
        rows = self.db_connection.execute_query(query, (start_date, end_date, limit))
        return [dict(row) for row in rows]

    def get_top_filaments(self, start_date: str, end_date: str, limit: int = 6) -> List[Dict[str, Any]]:
        """
        Obtiene ranking de filamentos por monto cotizado en un rango de fechas.
        
        Returns:
            Lista de dicts con: filament_id, filament_name, currency_code, total_amount, usage_count, total_weight
        """
        query = """
            SELECT 
                q.filament_id,
                COALESCE(f.name || ' - ' || f.brand || ' (' || f.color || ')', 'Sin filamento') as filament_name,
                q.currency_code,
                SUM(q.final_price) as total_amount,
                COUNT(*) as usage_count,
                SUM(q.filament_weight_grams) as total_weight
            FROM quotes q
            LEFT JOIN filaments f ON q.filament_id = f.id
            WHERE q.created_at >= ? AND q.created_at <= ?
            GROUP BY q.filament_id, q.currency_code
            ORDER BY total_amount DESC
            LIMIT ?
        """
        rows = self.db_connection.execute_query(query, (start_date, end_date, limit))
        return [dict(row) for row in rows]

    def get_all_amounts_in_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los montos individuales de quotes en un rango de fechas.
        Útil para calcular distribución/histograma.
        
        Returns:
            Lista de dicts con: final_price, currency_code
        """
        query = """
            SELECT final_price, currency_code
            FROM quotes
            WHERE created_at >= ? AND created_at <= ?
            ORDER BY final_price ASC
        """
        rows = self.db_connection.execute_query(query, (start_date, end_date))
        return [dict(row) for row in rows]

    def get_summary_stats(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Obtiene estadísticas resumidas (KPIs) en un rango de fechas, agrupadas por moneda.
        
        Returns:
            Lista de dicts con: currency_code, total_amount, quote_count, avg_ticket, max_amount, min_amount
        """
        query = """
            SELECT 
                currency_code,
                COALESCE(SUM(final_price), 0) as total_amount,
                COUNT(*) as quote_count,
                COALESCE(AVG(final_price), 0) as avg_ticket,
                COALESCE(MAX(final_price), 0) as max_amount,
                COALESCE(MIN(final_price), 0) as min_amount
            FROM quotes
            WHERE created_at >= ? AND created_at <= ?
            GROUP BY currency_code
        """
        rows = self.db_connection.execute_query(query, (start_date, end_date))
        return [dict(row) for row in rows] if rows else []
