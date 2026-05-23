"""
Presenter para el nuevo selector de impresoras 3D
Maneja la lógica de búsqueda y selección siguiendo patrón MVP con Facade
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog
from typing import List, Dict, Any, Optional
from domain.models.printer import Printer
from application.facades.voxeprint_facade import VoxeprintFacade
from presentation.modules.printers.views.printer_selector_dialog_new import PrinterSelectorDialogNew
from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class PrinterSelectorPresenterNew:
    """
    Presenter para el nuevo diálogo de selección de impresoras 3D
    Contiene toda la lógica de negocio, la vista solo maneja UI
    Sigue patrón MVP con inyección de dependencias (Facade)
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        self.view = None
        
        # Facade para operaciones de negocio (inyección de dependencias)
        self.facade: Optional[VoxeprintFacade] = None
        
        # Estado interno
        self.all_printers: List[Printer] = []
        self.filtered_printers: List[Printer] = []
        self.selected_printer: Optional[Printer] = None
        
        # Timer para búsqueda con delay
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
    
    def set_facade(self, facade: VoxeprintFacade):
        """Establece el facade para acceso a datos"""
        self.facade = facade
        
    def run(self):
        # Crear vista con un QWidget válido como parent
        self.view = PrinterSelectorDialogNew(self.parent)
        # Variable para el último texto de búsqueda
        self.current_search_text = ""
        # Conectar señales de la vista
        self._connect_view_signals()
        # Cargar datos inicial
        self._load_initial_data()
        # Ejecutar diálogo y devolver la impresora seleccionada
        result = self.view.exec()
        if result == QDialog.Accepted:
            return self.get_selected_printer()
        return None

    def _connect_view_signals(self):
        """Conecta las señales de la vista al presenter"""
        self.view.search_requested.connect(self._on_search_requested)
        self.view.refresh_requested.connect(self._on_refresh_requested)
        self.view.printer_selected.connect(self._on_printer_selected)
        self.view.add_printer_requested.connect(self._on_add_printer_requested)
    
    def _load_initial_data(self):
        """Carga los datos iniciales"""
        self.view.show_loading(tr(I18N.Printer.MSG_LOADING_INITIAL))
        
        # Usar timer para no bloquear la UI
        QTimer.singleShot(100, self._load_printers_from_db)
    
    def _load_printers_from_db(self):
        """Carga impresoras activas desde la base de datos usando facade"""
        try:
            if self.facade:
                # Usar facade para obtener todas las impresoras activas
                all_printers_raw = self.facade.get_all_printers()
                logger.info("PrinterSelector", f"Impresoras cargadas desde DB: {len(all_printers_raw)}")
                
                # Obtener monedas activas
                from infrastructure.database.repositories.currency_repository import CurrencyRepository
                currency_repo = CurrencyRepository()
                active_currencies = currency_repo.get_active()
                active_currency_codes = {currency.code for currency in active_currencies}
                logger.info("PrinterSelector", f"Monedas activas: {active_currency_codes}")
                
                # Filtrar solo impresoras con monedas activas (o sin currency_code = USD por defecto)
                self.all_printers = []
                for printer in all_printers_raw:
                    currency_code = getattr(printer, 'currency_code', None)
                    # Si no tiene currency_code, asumimos USD (moneda pivote siempre activa)
                    if currency_code is None:
                        currency_code = 'USD'
                    
                    if currency_code in active_currency_codes:
                        self.all_printers.append(printer)
                    else:
                        logger.debug("PrinterSelector", f"Impresora {printer.id} filtrada: moneda {currency_code} inactiva")
                
                logger.info("PrinterSelector", f"Impresoras con monedas activas: {len(self.all_printers)}")
                
                # Ordenar por ID de menor a mayor (consistencia con inventario)
                self.all_printers.sort(key=lambda printer: printer.id if printer.id is not None else 0)
                self.filtered_printers = self.all_printers.copy()
                
                if self.all_printers:
                    self._update_view_with_printers(self.all_printers)
                else:
                    # Verificar si hay impresoras pero todas fueron filtradas por moneda inactiva
                    if len(all_printers_raw) > 0:
                        from PySide6.QtWidgets import QMessageBox
                        mensaje = tr(I18N.Printer.MSG_INACTIVE_CURRENCIES_FMT).format(
                            count=len(all_printers_raw),
                            currencies=', '.join(sorted(active_currency_codes))
                        )
                        self.view.show_no_results(tr(I18N.Printer.MSG_NO_PRINTERS_ACTIVE_CURRENCY))
                        QMessageBox.information(self.view, tr(I18N.Printer.MSG_INACTIVE_CURRENCIES_TITLE), mensaje)
                    else:
                        self.view.show_no_results(tr(I18N.Printer.MSG_NO_ACTIVE_PRINTERS))
            else:
                # Error de sistema - solo loggear, no mostrar al usuario
                logger.error("PrinterSelector", "No hay conexión al facade")
                self.view.show_no_results(tr(I18N.Printer.MSG_NO_ACTIVE_PRINTERS))
                
        except Exception as e:
            # Loggear error técnico completo
            logger.error("PrinterSelector", "Error cargando impresoras", error=str(e))
            # Mostrar mensaje amigable al usuario
            self.view.show_no_results(tr(I18N.Printer.MSG_LOAD_FAILED))
        
        finally:
            self.view.hide_loading()
        
    def _update_view_with_printers(self, printers: List[Printer]):
        """Actualiza la vista con la lista de impresoras"""
        # Convertir a diccionarios para la vista con TODOS los campos necesarios
        printers_data = []
        for printer in printers:
            printers_data.append({
                'id': printer.id,
                'name': printer.name or '',
                'brand': printer.brand or '',
                'model': printer.model or '',
                'power_consumption_watts': printer.power_consumption_watts or 0,
                'is_active': printer.is_active,
                'created_at': getattr(printer, 'created_at', None),
                'updated_at': getattr(printer, 'updated_at', None),
                # Costos
                'purchase_cost': printer.purchase_cost or 0,
                'electricity_cost_per_hour': printer.electricity_cost_per_hour or 0,
                'service_cost_per_hour': printer.service_cost_per_hour or 0,
                'machine_wear_cost_per_hour': printer.machine_wear_cost_per_hour or 0,
                'maintenance_cost_per_hour': printer.maintenance_cost_per_hour or 0,
                # Mantenimiento
                'maintenance_cost': printer.maintenance_cost or 0,
                'maintenance_interval_hours': printer.maintenance_interval_hours or 0,
                # Vida útil
                'useful_life_hours': printer.useful_life_hours or 0,
                # Moneda
                'currency_code': getattr(printer, 'currency_code', 'PYG')
            })
        
        self.view.populate_table(printers_data)
        # print(f"📋 Tabla actualizada con {len(printers_data)} impresoras")
    
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
            self.filtered_printers = self.all_printers.copy()
        else:
            # Filtrar impresoras
            self.filtered_printers = []
            
            for printer in self.all_printers:
                # Buscar en múltiples campos
                search_fields = [
                    printer.name.lower(),
                    (printer.brand or "").lower(),
                    (printer.model or "").lower()
                ]
                
                # Si algún campo contiene el texto de búsqueda
                if any(search_text in field for field in search_fields):
                    self.filtered_printers.append(printer)
            
            # Mantener orden por ID en los resultados filtrados
            self.filtered_printers.sort(key=lambda printer: printer.id if printer.id is not None else 0)
        
        # Actualizar vista
        if self.filtered_printers:
            self._update_view_with_printers(self.filtered_printers)
            logger.debug("PrinterSelector", f"Búsqueda '{search_text}': {len(self.filtered_printers)} resultados")
        else:
            if search_text:
                self.view.show_no_results(tr(I18N.Printer.MSG_SEARCH_NO_RESULTS_FMT).format(text=search_text))
            else:
                self.view.show_no_results(tr(I18N.Printer.MSG_NO_ACTIVE_PRINTERS))
    
    def _on_refresh_requested(self):
        """Maneja la solicitud de actualización"""
        self.view.show_loading(tr(I18N.Printer.MSG_LOADING_REFRESHING))
        
        # Limpiar filtros
        self.view.clear_search_text()
        self.current_search_text = ""
        
        # Recargar desde base de datos
        QTimer.singleShot(500, self._load_printers_from_db)
    
    def _on_printer_selected(self, printer_data: Dict[str, Any]):
        """Maneja la selección de una impresora"""
        # Buscar la impresora completa por ID
        printer_id = printer_data.get('id')
        selected_printer = None
        
        for printer in self.all_printers:
            if printer.id == printer_id:
                selected_printer = printer
                break
        
        if selected_printer:
            self.selected_printer = selected_printer
        else:
            logger.error("PrinterSelectorPresenter", f"No se encontró la impresora con ID {printer_id}")
    
    def _on_add_printer_requested(self):
        """Maneja la solicitud de agregar nueva impresora"""
        from presentation.modules.printers.views.add_printer_dialog import AddPrinterDialog
        dialog = AddPrinterDialog(self.view)
        new_printer_data = None
        def on_printer_added(data):
            nonlocal new_printer_data
            new_printer_data = data
        dialog.printer_added.connect(on_printer_added)
        if dialog.exec() == QDialog.DialogCode.Accepted and new_printer_data:
            # Recargar la lista de impresoras desde la base de datos
            self._load_printers_from_db()
            # Buscar la nueva impresora en la lista y seleccionarla
            printer_id = new_printer_data.get('id')
            for idx, printer in enumerate(self.all_printers):
                if printer.id == printer_id:
                    self.filtered_printers = [printer]
                    self._update_view_with_printers(self.filtered_printers)
                    self.view.set_selected_printer_info({
                        'id': printer.id,
                        'name': printer.name,
                        'brand': printer.brand,
                        'model': printer.model,
                        'power_consumption_watts': printer.power_consumption_watts,
                        'is_active': printer.is_active,
                        'created_at': getattr(printer, 'created_at', None),
                        'updated_at': getattr(printer, 'updated_at', None)
                    })
                    break
            self.view.show_success_message(tr(I18N.Printer.MSG_PRINTER_ADDED_SELECTED_FMT).format(name=new_printer_data.get('name', '')))
    
    def get_selected_printer(self) -> Optional[Printer]:
        """Retorna la impresora seleccionada"""
        return self.selected_printer
    
    def search_printers(self, search_text: str) -> List[Printer]:
        """Busca impresoras activas que coincidan con el texto"""
        if not search_text:
            return self.all_printers.copy()
        
        search_text = search_text.lower()
        results = []
        
        # ✅ Solo buscar entre impresoras activas (self.all_printers ya filtradas)
        for printer in self.all_printers:
            # Campos de búsqueda
            searchable_text = f"{printer.name} {printer.brand} {printer.model}".lower()
            
            if search_text in searchable_text:
                results.append(printer)
        
        return results
    
    def get_printer_by_id(self, printer_id: int) -> Optional[Printer]:
        """
        Busca una impresora por ID usando facade
        
        Args:
            printer_id: ID de la impresora
            
        Returns:
            Objeto Printer o None si no se encuentra
        """
        try:
            if self.facade:
                response = self.facade.get_printer_by_id(printer_id)
                if response.success:
                    return response.data
                else:
                    logger.error("PrinterSelectorPresenter", f"Error desde facade buscando impresora {printer_id}: {response.message}")
                    return None
            else:
                logger.error("PrinterSelectorPresenter", f"No hay facade disponible para buscar impresora {printer_id}")
                return None
        except Exception as e:
            logger.error("PrinterSelectorPresenter", f"Error buscando impresora por ID {printer_id}: {e}")
            logger.log_exception("PrinterSelectorPresenter", e, "get_printer_by_id")
            return None
    
    def validate_printer_selection(self, printer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida si una impresora puede ser seleccionada
        
        Args:
            printer_data: Datos de la impresora
            
        Returns:
            Diccionario con resultado de validación
        """
        issues = []
        warnings = []
        
        # Verificaciones críticas
        if not printer_data.get('is_active', True):
            issues.append("La impresora está inactiva")
        
        electricity_cost = printer_data.get('electricity_cost_per_hour', 0)
        if electricity_cost <= 0:
            power_consumption = printer_data.get('power_consumption_watts', 0)
            if power_consumption <= 0:
                issues.append("Consumo eléctrico no configurado")
        
        # Verificaciones de advertencia
        power_consumption = printer_data.get('power_consumption_watts', 0)
        if power_consumption <= 0:
            warnings.append("Consumo eléctrico no especificado")
        
        purchase_cost = printer_data.get('purchase_cost', 0)
        if purchase_cost <= 0:
            warnings.append("Costo de compra no configurado")
        
        useful_life = printer_data.get('useful_life_hours', 0)
        if useful_life <= 0:
            warnings.append("Vida útil no configurada")
        
        maintenance_interval = printer_data.get('maintenance_interval_hours', 0)
        if maintenance_interval <= 0:
            warnings.append("Intervalo de mantenimiento no configurado")
        
        if not printer_data.get('brand'):
            warnings.append("Marca no especificada")
        
        if not printer_data.get('model'):
            warnings.append("Modelo no especificado")
        
        is_valid = len(issues) == 0
        
        return {
            'is_valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'can_select': is_valid
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de las impresoras cargadas (solo activas)
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.all_printers:
            return {
                'total_printers': 0,
                'active_printers': 0,
                'inactive_printers': 0
            }
        
        # ✅ NOTA: self.all_printers ya contiene solo impresoras activas
        return {
            'total_printers': len(self.all_printers),  # Total de activas
            'active_printers': len(self.all_printers),  # Todas son activas
            'inactive_printers': 0,  # No mostramos inactivas
            'filtered_count': len(self.filtered_printers)
        }
