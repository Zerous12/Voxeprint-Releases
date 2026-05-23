"""
Repositorio para la entidad Filament
"""
from typing import List, Optional, Dict, Any
from .base_repository import BaseRepository
from domain.models.filament import Filament
from domain.enums.enums import FilamentType, FilamentColor
from core.utils.logger import error


class FilamentRepository(BaseRepository):
    """Repositorio para gestionar filamentos"""
    
    @property
    def table_name(self) -> str:
        return "filaments"
    
    def _row_to_entity(self, row: Dict[str, Any]) -> Filament:
        """Convierte una fila de BD a Filament"""
        return Filament(
            id=row.get('id'),
            name=row.get('name', ''),
            type=FilamentType(row.get('type', 'PLA')),
            brand=row.get('brand', ''),
            color=FilamentColor(row.get('color', 'Blanco')),
            weight_grams=float(row.get('weight_grams', 0.0)),
            price_per_unit=float(row.get('price_per_unit', 0.0)),
            price_per_gram=float(row.get('price_per_gram', 0.0)),
            quantity_rolls=int(row.get('quantity_rolls', 0)),
            current_stock_grams=float(row.get('current_stock_grams', 0.0)),
            minimum_stock_grams=float(row.get('minimum_stock_grams', 0.0)),
            is_active=bool(row.get('is_active', True)),
            notes=row.get('notes', ''),
            currency_code=row.get('currency_code', 'PYG'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def _entity_to_dict(self, entity: Filament) -> Dict[str, Any]:
        """Convierte Filament a diccionario"""
        # NOTA: NO actualizamos automáticamente el precio por gramo aquí
        # porque en el sistema de rollos con precio promedio ponderado,
        # el precio por gramo se calcula manualmente
        # entity.update_price_per_gram()
        
        # Manejar fechas manualmente para asegurar funcionamiento correcto
        from datetime import datetime, timezone
        
        data = {
            'id': entity.id,
            'name': entity.name,
            'type': entity.type.value,
            'brand': entity.brand,
            'color': entity.color.value,
            'weight_grams': entity.weight_grams,
            'price_per_unit': entity.price_per_unit,
            'price_per_gram': entity.price_per_gram,
            'quantity_rolls': entity.quantity_rolls,
            'current_stock_grams': entity.current_stock_grams,
            'minimum_stock_grams': entity.minimum_stock_grams,
            'is_active': entity.is_active,
            'notes': entity.notes,
            'currency_code': entity.currency_code
        }
        
        # Usar hora local consistente para evitar diferencias de zona horaria
        # Formato: YYYY-MM-DD HH:MM:SS (mismo que SQLite)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Manejar fechas según si es inserción o actualización
        if entity.id is None:
            # Nuevo filamento - ambas fechas deben ser idénticas
            data['created_at'] = current_time
            data['updated_at'] = current_time
        else:
            # Actualización - mantener created_at original, actualizar updated_at
            data['created_at'] = entity.created_at  # Preservar fecha original de creación
            data['updated_at'] = current_time
        
        return data
    
    def find_active_filaments(self) -> List[Filament]:
        """
        Encuentra todos los filamentos activos
        
        Returns:
            Lista de filamentos activos
        """
        query = f"SELECT * FROM {self.table_name} WHERE is_active = 1 ORDER BY type, brand, name"
        rows = self.db_connection.execute_query(query)
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_by_type(self, filament_type: FilamentType) -> List[Filament]:
        """
        Busca filamentos por tipo
        
        Args:
            filament_type: Tipo de filamento
            
        Returns:
            Lista de filamentos del tipo especificado
        """
        query = f"SELECT * FROM {self.table_name} WHERE type = ? AND is_active = 1 ORDER BY brand, name"
        rows = self.db_connection.execute_query(query, (filament_type.value,))
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_low_stock(self) -> List[Filament]:
        """
        Encuentra filamentos con stock bajo
        
        Returns:
            Lista de filamentos con stock menor al mínimo
        """
        query = f"SELECT * FROM {self.table_name} WHERE current_stock_grams < minimum_stock_grams AND is_active = 1 ORDER BY current_stock_grams"
        rows = self.db_connection.execute_query(query)
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_by_brand(self, brand: str) -> List[Filament]:
        """
        Busca filamentos por marca
        
        Args:
            brand: Marca del filamento
            
        Returns:
            Lista de filamentos de la marca especificada
        """
        query = f"SELECT * FROM {self.table_name} WHERE brand = ? AND is_active = 1 ORDER BY type, name"
        rows = self.db_connection.execute_query(query, (brand,))
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def calculate_average_price_per_gram_by_type(self, filament_type: FilamentType) -> float:
        """
        Calcula el precio promedio por gramo para un tipo de filamento específico
        
        Args:
            filament_type: Tipo de filamento
            
        Returns:
            float: Precio promedio por gramo
        """
        query = f"""
            SELECT 
                SUM(price_per_unit) as total_price,
                SUM(weight_grams) as total_weight
            FROM {self.table_name} 
            WHERE type = ? AND is_active = 1 AND weight_grams > 0
        """
        rows = self.db_connection.execute_query(query, (filament_type.value,))
        
        if rows and rows[0]['total_weight'] and rows[0]['total_weight'] > 0:
            return rows[0]['total_price'] / rows[0]['total_weight']
        return 0.0
    
    def save(self, entity: Filament) -> Filament:
        """
        Guarda un filamento y actualiza las fechas en el objeto
        
        Args:
            entity: Filamento a guardar
            
        Returns:
            Filamento guardado con fechas actualizadas
        """
        is_new = entity.id is None
        
        # Llamar al método save del padre
        saved_entity = super().save(entity)
        
        # Solo recargar para actualizaciones, no para nuevas inserciones
        # Esto preserva las fechas idénticas en creación
        if not is_new and saved_entity.id:
            return self.find_by_id(saved_entity.id)
        
        return saved_entity
    
    def update(self, entity: Filament) -> Filament:
        """
        Método público para actualizar un filamento
        
        Args:
            entity: Filamento a actualizar
            
        Returns:
            Filamento actualizado con fechas actualizadas
        """
        # Simplemente usar el método padre que ya actualiza las fechas
        return self._update(entity)
    
    def get_price_statistics_by_type(self, filament_type: FilamentType) -> Dict[str, float]:
        """
        Obtiene estadísticas de precios para un tipo de filamento
        
        Args:
            filament_type: Tipo de filamento
            
        Returns:
            dict: Estadísticas (promedio, mínimo, máximo, total_weight, total_units)
        """
        query = f"""
            SELECT 
                AVG(price_per_gram) as avg_price_per_gram,
                MIN(price_per_gram) as min_price_per_gram,
                MAX(price_per_gram) as max_price_per_gram,
                SUM(weight_grams) as total_weight,
                COUNT(*) as total_units,
                SUM(current_stock_grams) as total_stock
            FROM {self.table_name} 
            WHERE type = ? AND is_active = 1 AND price_per_gram > 0
        """
        rows = self.db_connection.execute_query(query, (filament_type.value,))
        
        if rows and rows[0]['avg_price_per_gram']:
            row = rows[0]
            return {
                'average_price_per_gram': float(row['avg_price_per_gram'] or 0.0),
                'min_price_per_gram': float(row['min_price_per_gram'] or 0.0),
                'max_price_per_gram': float(row['max_price_per_gram'] or 0.0),
                'total_weight_grams': float(row['total_weight'] or 0.0),
                'total_units': int(row['total_units'] or 0),
                'total_stock_grams': float(row['total_stock'] or 0.0),
                'weighted_average': self.calculate_average_price_per_gram_by_type(filament_type)
            }
        
        return {
            'average_price_per_gram': 0.0,
            'min_price_per_gram': 0.0,
            'max_price_per_gram': 0.0,
            'total_weight_grams': 0.0,
            'total_units': 0,
            'total_stock_grams': 0.0,
            'weighted_average': 0.0
        }
    
    def get_all(self) -> List[Filament]:
        """
        Obtiene todos los filamentos
        
        Returns:
            Lista de todos los filamentos
        """
        query = f"SELECT * FROM {self.table_name} ORDER BY type, brand, name"
        rows = self.db_connection.execute_query(query)
        
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def find_by_name(self, name: str) -> Optional[Filament]:
        """
        Busca un filamento por nombre exacto
        
        Args:
            name: Nombre del filamento
            
        Returns:
            Filament o None si no se encuentra
        """
        query = f"SELECT * FROM {self.table_name} WHERE name = ? LIMIT 1"
        rows = self.db_connection.execute_query(query, (name,))
        
        if rows:
            return self._row_to_entity(dict(rows[0]))
        return None
    
    def search(self, search_term: Optional[str] = None, 
               type_filter: Optional[str] = None,
               brand_filter: Optional[str] = None, 
               color_filter: Optional[str] = None,
               active_only: bool = True,
               low_stock_only: bool = False,
               limit: Optional[int] = None, 
               offset: Optional[int] = None) -> List[Filament]:
        """
        Busca filamentos con criterios flexibles
        
        Args:
            search_term: Término de búsqueda en nombre, marca o tipo
            type_filter: Filtrar por tipo específico
            brand_filter: Filtrar por marca específica
            color_filter: Filtrar por color específico
            active_only: Solo filamentos activos
            low_stock_only: Solo filamentos con stock bajo
            limit: Límite de resultados
            offset: Desplazamiento para paginación
            
        Returns:
            Lista de filamentos que cumplen los criterios
        """
        conditions = []
        params = []
        
        # Búsqueda por término general
        if search_term:
            conditions.append("(LOWER(name) LIKE ? OR LOWER(brand) LIKE ? OR LOWER(type) LIKE ?)")
            search_pattern = f"%{search_term.lower()}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        # Filtros específicos
        if type_filter:
            conditions.append("type = ?")
            params.append(type_filter)
        
        if brand_filter:
            conditions.append("brand = ?")
            params.append(brand_filter)
            
        if color_filter:
            conditions.append("color = ?")
            params.append(color_filter)
        
        if active_only:
            conditions.append("is_active = 1")
        
        if low_stock_only:
            conditions.append("current_stock_grams < minimum_stock_grams")
        
        # Construir query
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause} ORDER BY type, brand, name"
        
        # Agregar paginación si se especifica
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
            
            if offset is not None:
                query += " OFFSET ?"
                params.append(offset)
        
        rows = self.db_connection.execute_query(query, tuple(params))
        return [self._row_to_entity(dict(row)) for row in rows]
    
    def add_roll_with_weighted_price(self, roll_data: Dict[str, Any]) -> Optional[Filament]:
        """
        Agrega un rollo de filamento calculando el precio promedio ponderado.
        Implementa la lógica similar al procedimiento MySQL 'Actualizar_precio_producto'.
        
        Args:
            roll_data: Datos del rollo (descripción, marca, tipo, color, peso, precio, etc.)
            
        Returns:
            Filament actualizado o None si hay error
        """
        try:
            # Buscar si ya existe un filamento con las mismas características
            existing_filament = self._find_existing_filament(roll_data)
            
            if existing_filament:
                # Actualizar filamento existente con precio promedio ponderado
                return self._update_with_weighted_average(existing_filament, roll_data)
            else:
                # Crear nuevo filamento
                return self._create_new_filament_from_roll(roll_data)
                
        except Exception as e:
            error("FilamentRepository", f"Error agregando rollo con precio ponderado: {e}")
            return None
    
    def _find_existing_filament(self, roll_data: Dict[str, Any]) -> Optional[Filament]:
        """Busca un filamento existente con las mismas características"""
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE LOWER(name) = LOWER(?) 
            AND LOWER(brand) = LOWER(?) 
            AND type = ? 
            AND color = ?
            LIMIT 1
        """
        
        params = [
            roll_data['description'],
            roll_data['brand'],
            roll_data['type'],
            roll_data['color']
        ]
        
        rows = self.db_connection.execute_query(query, params)
        
        if rows:
            return self._row_to_entity(dict(rows[0]))
        return None
    
    def _update_with_weighted_average(self, existing: Filament, roll_data: Dict[str, Any]) -> Filament:
        """
        Actualiza un filamento existente calculando el precio promedio ponderado.
        Implementa la lógica del procedimiento MySQL.
        """
        # Variables del estado actual (como en el procedimiento MySQL)
        actual_stock = existing.current_stock_grams
        actual_price_per_gram = existing.price_per_gram
        
        # Variables del nuevo rollo
        new_weight = roll_data['weight_grams']
        new_price_per_gram = roll_data['price_per_gram']
        
        # Cálculos (siguiendo la lógica del procedimiento)
        nuevo_stock = actual_stock + new_weight
        nuevo_total = (actual_stock * actual_price_per_gram) + (new_weight * new_price_per_gram)
        
        # Calcular nuevo precio promedio
        if nuevo_stock > 0:
            nuevo_precio_promedio = nuevo_total / nuevo_stock
        else:
            nuevo_precio_promedio = 0
        
        # Actualizar el filamento existente
        existing.current_stock_grams = nuevo_stock
        existing.price_per_gram = nuevo_precio_promedio
        existing.quantity_rolls += 1  # Incrementar número de rollos
        existing.is_active = roll_data.get('is_active', True)
        
        # Si hay notas del rollo, agregarlas
        roll_notes = roll_data.get('notes', '').strip()
        if roll_notes:
            if existing.notes:
                existing.notes += f"\\n--- Rollo {existing.quantity_rolls}: {roll_notes}"
            else:
                existing.notes = f"Rollo {existing.quantity_rolls}: {roll_notes}"
        
        # Guardar en base de datos
        updated = self.update(existing)
        
        # Log solo si es importante (para debugging)
        from core.utils.logger import VoxeprintLogger
        logger = VoxeprintLogger()
        logger.info(
            "FilamentRepository",
            f"Rollo añadido a '{existing.name}': {new_weight}g. Nuevo stock: {nuevo_stock}g a {nuevo_precio_promedio:.6f}/g"
        )
        
        return updated
    
    def _create_new_filament_from_roll(self, roll_data: Dict[str, Any]) -> Filament:
        """Crea un nuevo filamento a partir de los datos del rollo"""
        new_filament = Filament(
            name=roll_data['description'],
            type=FilamentType(roll_data['type']),
            brand=roll_data['brand'],
            color=FilamentColor(roll_data['color']),
            weight_grams=roll_data['weight_grams'],  # Peso del rollo estándar
            price_per_unit=roll_data['price_roll'],  # Precio por rollo
            price_per_gram=roll_data['price_per_gram'],  # Precio por gramo
            quantity_rolls=1,  # Primer rollo
            current_stock_grams=roll_data['weight_grams'],  # Stock inicial
            minimum_stock_grams=100,  # Stock mínimo por defecto
            is_active=roll_data.get('is_active', True),
            notes=roll_data.get('notes', '')
        )
        
        # Guardar en base de datos
        saved = self.save(new_filament)
        
        # Log importante
        from core.utils.logger import VoxeprintLogger
        logger = VoxeprintLogger()
        logger.info(
            "FilamentRepository",
            f"Filamento creado: '{saved.name}' ({saved.brand}), {saved.weight_grams}g a {saved.price_per_gram:.6f}/g"
        )
        
        return saved
