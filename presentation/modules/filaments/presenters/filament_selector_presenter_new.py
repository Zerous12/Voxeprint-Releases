"""
Presenter mejorado para la selección de filamentos
Contiene toda la lógica de negocio siguiendo el patrón MVP con Facade
"""

from PySide6.QtCore import  QTimer
from PySide6.QtWidgets import QDialog
from typing import List, Dict, Any, Optional
from domain.models.filament import Filament
from application.facades.voxeprint_facade import VoxeprintFacade
from presentation.modules.filaments.views.filament_selector_dialog_new import FilamentSelectorDialogNew
from core.utils.logger import logger
from core.utils.currency_helper import CurrencyHelper
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N

class FilamentSelectorPresenterNew:
    """
    Presenter para la ventana de selección de filamentos
    Contiene toda la lógica de negocio, la vista solo maneja UI
    Sigue patrón MVP con inyección de dependencias (Facade)
    """

    def __init__(self, parent=None):  
        self.parent = parent     
        self.view = None        
        
        # Facade para operaciones de negocio (inyección de dependencias)
        self.facade: Optional[VoxeprintFacade] = None
        
        # Estado interno
        self.all_filaments: List[Filament] = []
        self.filtered_filaments: List[Filament] = []
        self.selected_filament: Optional[Filament] = None
        
        # Timer para búsqueda con delay
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
    
    def set_facade(self, facade: VoxeprintFacade):
        """Establece el facade para acceso a datos"""
        self.facade = facade
        
        
    
    def run(self, initial_filter: str = ""):
        # Crear vista con un QWidget válido como parent
        self.view = FilamentSelectorDialogNew(self.parent)
        # Variable para el último texto de búsqueda
        self.current_search_text = ""
        # Conectar señales de la vista
        self._connect_view_signals()
        # Pre-establecer filtro si se proporcionó
        if initial_filter:
            self.view.ui.linedit_search.setText(initial_filter)
            self.current_search_text = initial_filter
        # Cargar datos inicial
        self._load_initial_data()
        # Ejecutar diálogo y devolver el filamento seleccionado
        result = self.view.exec()
        if result == QDialog.Accepted:
            return self.get_selected_filament()
        return None


    def _connect_view_signals(self):
        """Conecta las señales de la vista al presenter"""
        self.view.search_requested.connect(self._on_search_requested)
        self.view.refresh_requested.connect(self._on_refresh_requested)
        self.view.filament_selected.connect(self._on_filament_selected)
        self.view.add_filament_requested.connect(self._on_add_filament_requested)
    
    def _load_initial_data(self):
        """Carga los datos iniciales"""
        self.view.show_loading(
            "Cargando filamentos disponibles...")
        
        # Usar timer para no bloquear la UI
        QTimer.singleShot(100, self._load_filaments_from_db)
    
    def _load_filaments_from_db(self):
        """Carga filamentos activos desde la base de datos usando facade"""
        try:
            if self.facade:
                # Usar facade para obtener todos los filamentos activos
                all_filaments_raw = self.facade.get_all_filaments()
                logger.info("FilamentSelector", f"Filamentos cargados desde DB: {len(all_filaments_raw)}")
                
                # Obtener monedas activas
                from infrastructure.database.repositories.currency_repository import CurrencyRepository
                currency_repo = CurrencyRepository()
                active_currencies = currency_repo.get_active()
                active_currency_codes = {currency.code for currency in active_currencies}
                logger.info("FilamentSelector", f"Monedas activas: {active_currency_codes}")
                
                # Filtrar solo filamentos con monedas activas (o sin currency_code = USD por defecto)
                self.all_filaments = []
                for filament in all_filaments_raw:
                    currency_code = getattr(filament, 'currency_code', None)
                    # Si no tiene currency_code, asumimos USD (moneda pivote siempre activa)
                    if currency_code is None:
                        currency_code = 'USD'
                    
                    if currency_code in active_currency_codes:
                        self.all_filaments.append(filament)
                    else:
                        logger.debug("FilamentSelector", f"Filamento {filament.id} filtrado: moneda {currency_code} inactiva")
                
                logger.info("FilamentSelector", f"Filamentos con monedas activas: {len(self.all_filaments)}")
                
                # Ordenar por ID de menor a mayor (consistencia con inventario)
                self.all_filaments.sort(key=lambda filament: filament.id if filament.id is not None else 0)
                self.filtered_filaments = self.all_filaments.copy()
                
                if self.all_filaments:
                    # Si hay filtro inicial, aplicarlo; si no, mostrar todos
                    if self.current_search_text:
                        self._perform_search()
                    else:
                        self._update_view_with_filaments(self.all_filaments)
                else:
                    # Verificar si hay filamentos pero todos fueron filtrados por moneda inactiva
                    if len(all_filaments_raw) > 0:
                        from PySide6.QtWidgets import QMessageBox
                        mensaje = (
                            f"Hay {len(all_filaments_raw)} filamento(s) registrado(s), pero todos tienen monedas inactivas.\n\n"
                            f"Monedas activas: {', '.join(sorted(active_currency_codes))}\n\n"
                            f"Para usar estos filamentos, active sus monedas en:\n"
                            f"'Ajustes > Sistema > Ajustes de moneda'"
                        )
                        self.view.show_no_results("No hay filamentos con monedas activas.")
                        QMessageBox.information(self.view, "Monedas Inactivas", mensaje)
                    else:
                        self.view.show_no_results("No hay filamentos activos registrados.")
            else:
                # Error de sistema - solo loggear, no mostrar al usuario
                logger.error("FilamentSelector", "No hay conexión al facade")
                self.view.show_no_results("No hay filamentos disponibles")
                
        except Exception as e:
            # Loggear error técnico completo
            logger.error("FilamentSelector", "Error cargando filamentos", error=str(e))
            # Mostrar mensaje amigable al usuario
            self.view.show_no_results("No se pudieron cargar los filamentos.")
        
        finally:
            self.view.hide_loading()
        
    def _tr_color(self, filament_color) -> str:
        """Devuelve el nombre del color traducido al idioma activo."""
        if hasattr(filament_color, 'name'):
            return tr(f"FilamentColor.{filament_color.name}")
        return str(filament_color)

    def _update_view_with_filaments(self, filaments: List[Filament]):
        """Actualiza la vista con la lista de filamentos"""
        # Convertir a diccionarios para la vista
        filaments_data = []
        for filament in filaments:
            # Usar campos directos de la base de datos
            filament_type = filament.type.value if hasattr(filament.type, 'value') else str(filament.type)
            filament_color = self._tr_color(filament.color)

            # Calcular stock en kg
            stock_kg = filament.current_stock_grams / 1000.0 if filament.current_stock_grams else 0.0

            # Precio por kg (basado en price_per_gram * 1000)
            price_per_kg = filament.price_per_gram * 1000.0 if filament.price_per_gram else 0.0

            filaments_data.append({
                'id': filament.id,
                'description': filament.name,  # Mapear name -> description para compatibilidad con vista
                'material_type': filament_type,
                'brand': filament.brand or "",
                'color': filament_color,
                'price_per_kg': price_per_kg,
                'stock_kg': stock_kg,
                'quantity_rolls': filament.quantity_rolls or 0,
                'is_active': getattr(filament, 'is_active', True),
                'notes': filament.notes or "",
                'currency_code': getattr(filament, 'currency_code', 'PYG')
            })

        self.view.populate_table(filaments_data)
        logger.debug("FilamentSelector", "Tabla actualizada", filamentos=len(filaments_data))
    
    def _on_search_requested(self, search_text: str):
        """Maneja la solicitud de búsqueda"""
        # Usar timer para evitar búsquedas excesivas
        self.search_timer.stop()
        self.current_search_text = search_text
        self.search_timer.start(300)  # 300ms de delay
    
    def _perform_search(self):
        """Realiza la búsqueda con el texto actual"""
        search_text = self.current_search_text.lower().strip()
        
        if not search_text:
            # Si no hay texto, mostrar todos (ya ordenados por ID)
            self.filtered_filaments = self.all_filaments.copy()
        else:
            # Filtrar filamentos
            self.filtered_filaments = []
            
            for filament in self.all_filaments:
                # Buscar en múltiples campos
                filament_type = filament.type.value if hasattr(filament.type, 'value') else str(filament.type)
                # Buscar tanto en valor original (español) como en traducción activa
                filament_color_raw = filament.color.value if hasattr(filament.color, 'value') else str(filament.color)
                filament_color_tr = self._tr_color(filament.color)

                search_fields = [
                    filament.name.lower(),
                    filament_type.lower(),
                    (filament.brand or "").lower(),
                    filament_color_raw.lower(),
                    filament_color_tr.lower(),
                    (filament.notes or "").lower()
                ]
                
                # Si algún campo contiene el texto de búsqueda
                if any(search_text in field for field in search_fields):
                    self.filtered_filaments.append(filament)
            
            # Mantener orden por ID en los resultados filtrados
            self.filtered_filaments.sort(key=lambda filament: filament.id if filament.id is not None else 0)
        
        # Actualizar vista
        if self.filtered_filaments:
            self._update_view_with_filaments(self.filtered_filaments)
        else:
            if search_text:
                self.view.show_no_results(f"No se encontraron filamentos que contengan '{search_text}'")
            else:
                self.view.show_no_results("No hay filamentos disponibles")
    
    def _on_refresh_requested(self):
        """Maneja la solicitud de actualización"""
        self.view.show_loading("Actualizando lista de filamentos...")
        
        # Limpiar filtros
        self.view.clear_search_text()
        self.current_search_text = ""
        
        # Recargar desde base de datos
        QTimer.singleShot(500, self._load_filaments_from_db)
    
    def _on_filament_selected(self, filament_data: Dict[str, Any]):
        """Maneja la selección de un filamento"""
        # Buscar el filamento completo por ID
        filament_id = filament_data.get('id')
        selected_filament = None
        
        for filament in self.all_filaments:
            if filament.id == filament_id:
                selected_filament = filament
                break
        
        if selected_filament:
            self.selected_filament = selected_filament            
        else:
            logger.error("FilamentSelectorPresenter", f"No se encontró el filamento con ID {filament_id}")
    
    def _on_add_filament_requested(self):
        """Maneja la solicitud de agregar nuevo filamento"""
        from presentation.modules.filaments.views.add_filament_dialog import AddFilamentDialog
        dialog = AddFilamentDialog(self.view)
        new_filament_data = None
        def on_filament_added(data):
            nonlocal new_filament_data
            new_filament_data = data
        dialog.filament_added.connect(on_filament_added)
        if dialog.exec() == QDialog.DialogCode.Accepted and new_filament_data:
            # Recargar la lista de filamentos desde la base de datos
            self._load_filaments_from_db()
            
            # Buscar el nuevo filamento en la lista y seleccionarlo
            filament_id = new_filament_data.get('id')
            for idx, filament in enumerate(self.all_filaments):
                if filament.id == filament_id:
                    # Actualizar la tabla con el nuevo filamento
                    self.filtered_filaments = [filament]
                    self._update_view_with_filaments(self.filtered_filaments)
                    # Establecer la información del filamento recién agregado como seleccionado
                    self.view.set_selected_filament_info({
                        'id': filament.id,
                        'description': filament.name,  # Mapear name -> description
                        'material_type': filament.type.value if hasattr(filament.type, 'value') else str(filament.type),
                        'brand': filament.brand,
                        'color': self._tr_color(filament.color),
                        'stock_kg': filament.current_stock_grams / 1000.0 if filament.current_stock_grams else 0.0,
                        'price_per_kg': filament.price_per_gram * 1000.0 if filament.price_per_gram else 0.0
                    })
                    break
    
    def get_selected_filament(self) -> Optional[Filament]:
        """Retorna el filamento seleccionado"""
        return self.selected_filament
    
    def search_filaments(self, search_text: str) -> List[Filament]:
        """Busca filamentos que coincidan con el texto"""
        if not search_text:
            return self.all_filaments.copy()
        
        search_text = search_text.lower()
        results = []
        
        for filament in self.all_filaments:
            # Campos de búsqueda (raw + traducido para que funcione en cualquier idioma)
            filament_type = filament.type.value if hasattr(filament.type, 'value') else str(filament.type)
            filament_color_raw = filament.color.value if hasattr(filament.color, 'value') else str(filament.color)
            filament_color_tr = self._tr_color(filament.color)
            searchable_text = f"{filament.name} {filament_type} {filament.brand} {filament_color_raw} {filament_color_tr}".lower()
            
            if search_text in searchable_text:
                results.append(filament)
        
        return results
    
    def get_filaments_by_material(self, material_type: str) -> List[Filament]:
        """Obtiene filamentos filtrados por tipo de material"""
        results = []
        for filament in self.all_filaments:
            filament_type = filament.type.value if hasattr(filament.type, 'value') else str(filament.type)
            if filament_type.lower() == material_type.lower():
                results.append(filament)
        return results
    
    def get_available_materials(self) -> List[str]:
        """Obtiene lista de materiales disponibles"""
        materials = set()
        for filament in self.all_filaments:
            material_value = filament.type.value if hasattr(filament.type, 'value') else str(filament.type)
            materials.add(material_value)
        return sorted(list(materials))
    
    def get_available_brands(self) -> List[str]:
        """Obtiene lista de marcas disponibles"""
        brands = set()
        for filament in self.all_filaments:
            if filament.brand:
                brands.add(filament.brand)
        return sorted(list(brands))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de los filamentos"""
        if not self.all_filaments:
            return {}
        
        total_count = len(self.all_filaments)
        total_stock = sum(f.current_stock_grams / 1000.0 for f in self.all_filaments)  # Convertir a kg
        avg_price = sum(f.price_per_unit for f in self.all_filaments) / total_count
        
        materials = {}
        brands = {}
        colors = {}
        
        for filament in self.all_filaments:
            # Materiales
            material = filament.type.value if hasattr(filament.type, 'value') else str(filament.type)
            materials[material] = materials.get(material, 0) + 1
            
            # Marcas
            if filament.brand:
                brands[filament.brand] = brands.get(filament.brand, 0) + 1
            
            # Colores
            color = filament.color.value if hasattr(filament.color, 'value') else str(filament.color)
            colors[color] = colors.get(color, 0) + 1
        
        return {
            'total_filaments': total_count,
            'total_stock_kg': total_stock,
            'average_price': avg_price,
            'materials_count': materials,
            'brands_count': brands,
            'colors_count': colors,
            'unique_materials': len(materials),
            'unique_brands': len(brands),
            'unique_colors': len(colors)
        }
    
    def validate_filament_selection(self, filament: Filament) -> tuple[bool, str]:
        """Valida si un filamento puede ser seleccionado"""
        if not filament:
            return False, "No hay filamento seleccionado"
        
        # Verificar si está activo
        if hasattr(filament, 'is_active') and not filament.is_active:
            return False, "El filamento seleccionado está inactivo"
        
        # Verificar stock
        if not filament.current_stock_grams or filament.current_stock_grams <= 0:
            return False, "El filamento seleccionado no tiene stock disponible"
        
        # Verificar precio
        if not filament.price_per_gram or filament.price_per_gram <= 0:
            return False, "El filamento seleccionado no tiene precio configurado"
        
        return True, "Filamento válido para selección"
    
    def format_filament_summary(self, filament: Filament) -> str:
        """Retorna un resumen formateado del filamento"""
        if not filament:
            return "Ningún filamento seleccionado"
        material = filament.type.value if hasattr(filament.type, 'value') else str(filament.type)
        color = filament.color.value if hasattr(filament.color, 'value') else str(filament.color)
        stock_kg = filament.current_stock_grams / 1000.0 if filament.current_stock_grams else 0.0
        price_kg = filament.price_per_gram * 1000.0 if filament.price_per_gram else 0.0

        return f"{filament.name} ({material} {color}) - {stock_kg:.2f}kg @ {CurrencyHelper.format_with_current_currency(price_kg)}/kg"
