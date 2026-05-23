"""
Repositorio para la entidad FilamentRoll
"""
from typing import List, Optional, Dict, Any
from .base_repository import BaseRepository
from domain.models.filament_roll import FilamentRoll
from core.utils.logger import error


class FilamentRollRepository(BaseRepository):
    """Repositorio para gestionar rollos individuales de filamento"""

    @property
    def table_name(self) -> str:
        return "filament_rolls"

    def _row_to_entity(self, row: Dict[str, Any]) -> FilamentRoll:
        return FilamentRoll(
            id=row.get('id'),
            filament_id=int(row.get('filament_id', 0)),
            sku=row.get('sku', ''),
            initial_weight_grams=float(row.get('initial_weight_grams', 0.0)),
            current_weight_grams=float(row.get('current_weight_grams', 0.0)),
            purchase_price=float(row.get('purchase_price', 0.0)),
            price_per_gram=float(row.get('price_per_gram', 0.0)),
            purchase_date=row.get('purchase_date'),
            is_active=bool(row.get('is_active', True)),
            notes=row.get('notes', ''),
            created_at=row.get('created_at')
        )

    def _entity_to_dict(self, entity: FilamentRoll) -> Dict[str, Any]:
        from datetime import datetime
        data = {
            'id': entity.id,
            'filament_id': entity.filament_id,
            'sku': entity.sku,
            'initial_weight_grams': entity.initial_weight_grams,
            'current_weight_grams': entity.current_weight_grams,
            'purchase_price': entity.purchase_price,
            'price_per_gram': entity.price_per_gram,
            'purchase_date': entity.purchase_date or datetime.now().strftime('%Y-%m-%d'),
            'is_active': entity.is_active,
            'notes': entity.notes,
            'created_at': entity.created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return data

    # ── Queries ────────────────────────────────────────────

    def find_by_filament_id(self, filament_id: int, active_only: bool = True) -> List[FilamentRoll]:
        """Obtiene todos los rollos de un filamento"""
        condition = "AND is_active = 1" if active_only else ""
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE filament_id = ? {condition}
            ORDER BY created_at DESC
        """
        rows = self.db_connection.execute_query(query, (filament_id,))
        return [self._row_to_entity(dict(row)) for row in rows]

    def count_active_rolls(self, filament_id: int) -> int:
        query = f"SELECT COUNT(*) as cnt FROM {self.table_name} WHERE filament_id = ? AND is_active = 1"
        rows = self.db_connection.execute_query(query, (filament_id,))
        return rows[0]['cnt'] if rows else 0

    def get_stock_summary(self, filament_id: int) -> Dict[str, Any]:
        """Retorna resumen de stock agregado desde los rollos activos"""
        query = f"""
            SELECT
                COUNT(*)                    AS roll_count,
                COALESCE(SUM(current_weight_grams), 0)  AS total_stock_grams,
                COALESCE(SUM(purchase_price), 0)         AS total_value
            FROM {self.table_name}
            WHERE filament_id = ? AND is_active = 1
        """
        rows = self.db_connection.execute_query(query, (filament_id,))
        if rows:
            r = rows[0]
            total_stock = float(r['total_stock_grams'])
            total_value = float(r['total_value'])
            return {
                'roll_count': int(r['roll_count']),
                'total_stock_grams': total_stock,
                'total_value': total_value,
                'weighted_price_per_gram': total_value / total_stock if total_stock > 0 else 0.0
            }
        return {'roll_count': 0, 'total_stock_grams': 0.0, 'total_value': 0.0, 'weighted_price_per_gram': 0.0}

    def soft_delete(self, roll_id: int) -> bool:
        """Desactiva un rollo (soft delete)"""
        command = f"UPDATE {self.table_name} SET is_active = 0 WHERE id = ?"
        affected = self.db_connection.execute_command(command, (roll_id,))
        return affected > 0

    def adjust_weight(self, roll_id: int, new_weight: float) -> bool:
        """Ajusta el peso actual de un rollo"""
        command = f"UPDATE {self.table_name} SET current_weight_grams = ? WHERE id = ?"
        affected = self.db_connection.execute_command(command, (new_weight, roll_id))
        return affected > 0

    def delete_by_filament_id(self, filament_id: int) -> int:
        """Elimina físicamente todos los rollos de un filamento"""
        command = f"DELETE FROM {self.table_name} WHERE filament_id = ?"
        return self.db_connection.execute_command(command, (filament_id,))

    def generate_next_sku(self, filament_id: int) -> str:
        """Genera el siguiente SKU para un rollo del filamento dado.
        Formato: VX-XXXXX-YY (filament_id con 5 dígitos, secuencial con 2 dígitos)"""
        query = f"""
            SELECT COUNT(*) as total FROM {self.table_name}
            WHERE filament_id = ?
        """
        rows = self.db_connection.execute_query(query, (filament_id,))
        next_seq = (rows[0]['total'] if rows else 0) + 1
        return f"VX-{filament_id:05d}-{next_seq:02d}"
