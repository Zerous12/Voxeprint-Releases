from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt, QObject, Signal
from typing import List, Optional, Dict, Any

from application.facades.voxeprint_facade import VoxeprintFacade
from domain.models.printer import Printer
from core.utils.currency_helper import CurrencyHelper
# Import dinámico para evitar dependencias circulares
# from presentation.modules.printers.add_printer_dialog import AddPrinterDialog
from presentation.modules.printers.views.edit_printer_dialog import EditPrinterDialog
from presentation.modules.printers.views.printer_details_dialog import PrinterDetailsDialog

# Importar el animador de botones
from presentation.widgets.animation_mod import ButtonSizeAnimator
from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class PrinterInventoryPresenter(QObject):
    """Presenter para gestionar el inventario de impresoras"""
    
    # Señales
    printer_selected = Signal(dict)  # Cuando se selecciona una impresora
    printer_modified = Signal(dict)  # Cuando se modifica una impresora
    printer_deleted = Signal(int)    # Cuando se elimina una impresora
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui = main_window.ui  # Acceder a la UI a través del ui del main_window
        
        # Facade para operaciones de negocio (inyección de dependencias)
        self.facade: Optional[VoxeprintFacade] = None
        
        # Estado interno
        self.all_printers: List[Printer] = []
        self.filtered_printers: List[Printer] = []
        self.selected_printer: Optional[Printer] = None
        
        # Animador de botones
        self.button_animator: Optional[ButtonSizeAnimator] = None
        
        # Configurar UI
        self._setup_ui()
        self._connect_signals()
        self._setup_button_animations()
    
    def set_facade(self, facade: VoxeprintFacade):
        """Establece el facade para acceso a datos"""
        self.facade = facade
        # Cargar datos iniciales cuando el facade esté disponible
        self.load_printers()

    def _setup_ui(self):
        """Configurar elementos de la interfaz"""
        table = self.ui.qtable_printers  # Ahora usar self.ui

        # Configurar cabeceras
        headers = [
            "ID",
            tr(I18N.MainWindow.COL_DESCRIPTION),
            tr(I18N.MainWindow.COL_MODEL),
            tr(I18N.MainWindow.COL_BRAND),
            tr(I18N.MainWindow.COL_CONSUMPTION),
            tr(I18N.MainWindow.COL_COST),
            tr(I18N.MainWindow.COL_STATUS_HDR),
        ]
        table.setHorizontalHeaderLabels(headers)

        # Configurar el header de la tabla para que se ajuste al contenido
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Configurar altura de las filas
        table.verticalHeader().setDefaultSectionSize(35)
        table.verticalHeader().setVisible(False)

    def _connect_signals(self):
        """Conectar señales de la interfaz"""
        # Botón agregar impresora
        self.ui.btn_add_printer.clicked.connect(self._handle_add_printer)
        
        # Botón modificar impresora
        self.ui.btn_mod_printer.clicked.connect(self._handle_modify_printer)
        
        # Botón eliminar impresora
        self.ui.btn_delete_printer.clicked.connect(self._handle_delete_printer)
        
        # Botón buscar
        self.ui.btn_search_2.clicked.connect(self._handle_search)
        
        # Enter en campo de búsqueda
        self.ui.linedit_search_2.returnPressed.connect(self._handle_search)
        
        # Selección simple para mostrar resumen en textEdit
        self.ui.qtable_printers.itemSelectionChanged.connect(self._handle_selection_changed)
        
        # Doble clic en tabla para ver detalles
        self.ui.qtable_printers.itemDoubleClicked.connect(self._handle_show_details)

    def _setup_button_animations(self):
        """Configura las animaciones de intercambio de tamaños entre botones"""
        try:
            # Verificar que los botones existen
            if not hasattr(self.ui, 'btn_search_2') or not hasattr(self.ui, 'btn_cleaner_2'):
                logger.warning("PrinterInventoryPresenter", "Uno o ambos botones no encontrados para animación")
                return
            
            # Crear el animador con los parámetros especificados
            self.button_animator = ButtonSizeAnimator(
                primary_button=self.ui.btn_search_2,      # Botón de búsqueda (principal)
                secondary_button=self.ui.btn_cleaner_2,   # Botón de limpieza (secundario)
                primary_normal_width=90,                  # Búsqueda normal: 90px
                primary_hover_width=25,                   # Búsqueda en hover: 25px
                secondary_normal_width=25,                # Limpieza normal: 25px
                secondary_hover_width=90,                 # Limpieza en hover: 90px
                animation_duration=200                    # Duración: 200ms
            )
            
            # Conectar el click del botón cleaner
            self.ui.btn_cleaner_2.clicked.connect(self._handle_clear_search)
            
        except Exception as e:
            logger.error("PrinterInventory", f"Error configurando animación de botones: {e}")

    def load_printers(self, search_term=None):
        """Cargar TODAS las impresoras en la tabla (activas e inactivas)"""
        try:
            if not self.facade:
                self._update_status_message("❌ Error: No hay conexión al facade")
                return
                
            if search_term and len(search_term.strip()) >= 2:
                # ✅ CAMBIADO: Buscar en todas las impresoras, no solo activas
                printers = self.facade.search_all_printers(search_term.strip())
            else:
                # ✅ CAMBIADO: Obtener todas las impresoras, no solo activas
                printers = self.facade.get_all_printers_including_inactive()
            
            self.all_printers = printers
            self.filtered_printers = printers.copy()
            
            self._populate_table(printers)
            
            # Log de carga de impresoras
            logger.debug("PrinterInventory", "Impresoras cargadas para inventario", 
                           cantidad=len(printers), incluye="activas e inactivas")
            self._update_status_message(f"Cargados {len(printers)} impresoras")
            
        except Exception as e:
            logger.error("PrinterInventoryPresenter", f"Error cargando impresoras: {e}")
            logger.log_exception("PrinterInventoryPresenter", e, "load_printers")
            self._update_status_message("Error cargando impresoras")
            QMessageBox.critical(
                self.main_window,
                tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.Printer.MSG_ERROR_LOADING)
            )

    def _populate_table(self, printers):
        """Poblar la tabla con los datos de las impresoras incluyendo Status"""
        table = self.ui.qtable_printers
        table.setRowCount(len(printers))
        
        # ✅ OCULTAR la columna ID (columna 0) y Costo (columna 5)
        table.setColumnHidden(0, True)  # ID
        table.setColumnHidden(5, True)  # Costo
        
        for row, printer in enumerate(printers):
            # ID (oculta pero necesaria para funcionalidad interna)
            item_id = QTableWidgetItem(str(printer.id))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, item_id)
            
            # Descripción (usando name del modelo)
            item_description = QTableWidgetItem(printer.name or "")
            table.setItem(row, 1, item_description)
            
            # Modelo
            item_model = QTableWidgetItem(printer.model or "")
            table.setItem(row, 2, item_model)
            
            # Marca
            item_brand = QTableWidgetItem(printer.brand or "")
            table.setItem(row, 3, item_brand)
            
            # Consumo real en watts
            consumption_text = f"{printer.power_consumption_watts:.0f}W"
            item_consumption = QTableWidgetItem(consumption_text)
            item_consumption.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 4, item_consumption)
            
            # Costo de compra de la impresora - usar la moneda original del printer
            printer_currency = getattr(printer, 'currency_code', 'PYG')
            purchase_cost = printer.purchase_cost or 0
            cost_text = CurrencyHelper.format(purchase_cost, printer_currency)
            item_cost = QTableWidgetItem(cost_text)
            item_cost.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 5, item_cost)
            
            # ✅ NUEVO: Status (columna 6)
            status_text = tr(I18N.Printer.STATUS_ACTIVE_TABLE) if printer.is_active else tr(I18N.Printer.STATUS_INACTIVE_TABLE)
            item_status = QTableWidgetItem(status_text)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 6, item_status)
        
        # Limpiar selección anterior
        table.clearSelection()  # Limpiar selección visual
        self.selected_printer = None
        self._clear_printer_summary()
    
    def _update_status_message(self, message: str):
        """Actualiza el mensaje de estado - ahora usa logging centralizado"""
        try:
            # Log internal del inventario sin mostrar en UI
            logger.debug("PrinterInventory", message)
        except Exception as e:
            logger.error("PrinterInventory", "Error actualizando mensaje de estado", error=str(e))

    def _handle_add_printer(self):
        """Manejar clic en botón agregar impresora"""
        # Import dinámico para evitar dependencias circulares
        from presentation.modules.printers.views.add_printer_dialog import AddPrinterDialog
        
        dialog = AddPrinterDialog(self.main_window)
        if dialog.exec():
            self.load_printers()
            self._show_success_message(tr(I18N.Printer.MSG_ADDED_SUCCESSFULLY))

    def _handle_modify_printer(self):
        """Manejar clic en botón modificar impresora"""
        current_row = self.ui.qtable_printers.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self.main_window,
                tr(I18N.Printer.NO_SELECTION_REQUIRED_TITLE),
                tr(I18N.Printer.NO_SELECTION_MODIFY_MSG)
            )
            return
        
        # Obtener ID de la impresora seleccionada
        printer_id_item = self.ui.qtable_printers.item(current_row, 0)
        if not printer_id_item:
            return
        
        printer_id = int(printer_id_item.text())
        
        try:
            # Obtener impresora desde la base de datos
            if not self.facade:
                QMessageBox.warning(
                    self.main_window,
                    tr(I18N.Dialogs.ERROR_TITLE),
                    tr(I18N.Printer.NO_FACADE_MSG)
                )
                return
                
            printer = self.facade.get_printer_by_id(printer_id)
            if not printer:
                QMessageBox.warning(
                    self.main_window,
                    tr(I18N.Dialogs.ERROR_TITLE),
                    tr(I18N.Printer.NOT_FOUND_MSG)
                )
                return
            
            # Validar que la moneda de la impresora esté activa
            from infrastructure.database.repositories.currency_repository import CurrencyRepository
            currency_repo = CurrencyRepository()
            printer_currency = getattr(printer, 'currency_code', 'USD')
            currency = currency_repo.get_by_code(printer_currency)
            
            if not currency or not currency.is_active:
                QMessageBox.warning(
                    self.main_window,
                    tr(I18N.Printer.CURRENCY_INACTIVE_TITLE),
                    tr(I18N.Printer.CURRENCY_INACTIVE_MSG).format(currency=printer_currency)
                )
                return
            
            # Abrir diálogo de modificación
            dialog = EditPrinterDialog(self.main_window, printer)
            if dialog.exec():
                # Emitir señal de modificación
                printer_data = self._printer_to_dict(printer)
                self.printer_modified.emit(printer_data)
                
                self.load_printers()
                self._show_success_message(tr(I18N.Printer.MSG_MODIFIED_SUCCESSFULLY))
                self._update_status_message(tr(I18N.Printer.MSG_MODIFIED_SUCCESSFULLY))
                
        except Exception as e:
            logger.error("PrinterInventoryPresenter", f"Error al modificar impresora: {e}")
            logger.log_exception("PrinterInventoryPresenter", e, "_handle_modify_printer")
            QMessageBox.critical(
                self.main_window,
                tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.Printer.MSG_ERROR_MODIFYING)
            )

    def _handle_delete_printer(self):
        """Manejar clic en botón eliminar impresora"""
        current_row = self.ui.qtable_printers.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self.main_window,
                tr(I18N.Printer.NO_SELECTION_REQUIRED_TITLE),
                tr(I18N.Printer.NO_SELECTION_DELETE_MSG)
            )
            return
        
        # Obtener información de la impresora seleccionada
        printer_id_item = self.ui.qtable_printers.item(current_row, 0)
        description_item = self.ui.qtable_printers.item(current_row, 1)
        
        if not printer_id_item or not description_item:
            return
        
        printer_id = int(printer_id_item.text())
        description = description_item.text()
        
        # ✅ SIMPLIFICADO: Confirmar eliminación (SQLite maneja las referencias automáticamente)
        reply = QMessageBox.question(
            self.main_window,
            tr(I18N.Printer.DELETE_CONFIRM_TITLE),
            tr(I18N.Printer.DELETE_CONFIRM_MSG).format(name=description),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if not self.facade:
                    QMessageBox.warning(
                        self.main_window,
                        tr(I18N.Dialogs.ERROR_TITLE),
                        tr(I18N.Printer.NO_FACADE_MSG)
                    )
                    return
                    
                self.facade.delete_printer(printer_id)
                
                # Emitir señal
                self.printer_deleted.emit(printer_id)
                
                self.load_printers()
                self._show_success_message(tr(I18N.Printer.MSG_DELETED_FMT).format(name=description))
                self._update_status_message(tr(I18N.Printer.STATUS_DELETED))
                
            except Exception as e:
                logger.error("PrinterInventoryPresenter", f"Error al eliminar impresora: {e}")
                logger.log_exception("PrinterInventoryPresenter", e, "_handle_delete_printer")
                QMessageBox.critical(
                    self.main_window,
                    tr(I18N.Dialogs.ERROR_TITLE),
                    tr(I18N.Printer.MSG_ERROR_DELETING)
                )

    def _handle_search(self):
        """Manejar búsqueda de impresoras"""
        search_term = self.ui.linedit_search_2.text().strip()
        
        if search_term and len(search_term) < 2:
            QMessageBox.information(
                self.main_window,
                tr(I18N.Printer.SEARCH_TITLE),
                tr(I18N.Printer.SEARCH_MIN_CHARS_MSG)
            )
            return
        
        if not search_term:
            # Sin filtro, mostrar todas
            self.filtered_printers = self.all_printers.copy()
            self._populate_table(self.filtered_printers)
            self._update_status_message(f"Mostrando todas las impresoras ({len(self.filtered_printers)})")
        else:
            # Buscar localmente primero para mejor rendimiento
            search_lower = search_term.lower()
            self.filtered_printers = [
                printer for printer in self.all_printers
                if (search_lower in (printer.name or "").lower() or
                    search_lower in (printer.brand or "").lower() or
                    search_lower in (printer.model or "").lower())
            ]
            
            self._populate_table(self.filtered_printers)
            self._update_status_message(f"Búsqueda: '{search_term}' - {len(self.filtered_printers)} resultados")

    def _handle_clear_search(self):
        """Limpiar el campo de búsqueda y mostrar todas las impresoras"""
        try:
            # Limpiar el campo de texto
            self.ui.linedit_search_2.clear()
            
            # Recargar todas las impresoras
            self.filtered_printers = self.all_printers.copy()
            self._populate_table(self.filtered_printers)
            self._update_status_message(f"Búsqueda limpiada - Mostrando todas las impresoras ({len(self.filtered_printers)})")
            
            logger.debug("PrinterInventoryPresenter", "Campo de búsqueda limpiado")
            
        except Exception as e:
            logger.error("PrinterInventoryPresenter", f"Error limpiando búsqueda: {e}")
            logger.log_exception("PrinterInventoryPresenter", e, "_handle_clear_search")

    def _handle_selection_changed(self):
        """Manejar cambio de selección para mostrar resumen en textEdit"""
        table = self.ui.qtable_printers
        current_row = table.currentRow()
        
        if current_row < 0:
            # No hay selección, limpiar el textEdit
            self.selected_printer = None
            self._clear_printer_summary()
            return
        
        # Obtener ID de la impresora seleccionada
        printer_id_item = table.item(current_row, 0)
        if not printer_id_item:
            self.selected_printer = None
            self._clear_printer_summary()
            return
        
        try:
            printer_id = int(printer_id_item.text())
            
            # Obtener impresora desde la base de datos
            if self.facade:
                printer = self.facade.get_printer_by_id(printer_id)
                if printer:
                    self.selected_printer = printer
                    self._update_printer_summary(printer)
                    
                    # Emitir señal de selección
                    printer_data = self._printer_to_dict(printer)
                    self.printer_selected.emit(printer_data)
                    
                    self._update_status_message("Impresora seleccionada")
                else:
                    self.selected_printer = None
                    self._clear_printer_summary()
            else:
                self.selected_printer = None
                self._clear_printer_summary()
                
        except (ValueError, Exception):
            self.selected_printer = None
            self._clear_printer_summary()
    
    def _printer_to_dict(self, printer: Printer) -> Dict[str, Any]:
        """Convierte una impresora a diccionario para las señales"""
        return {
            'id': printer.id,
            'name': printer.name,
            'brand': printer.brand,
            'model': printer.model,
            'power_consumption_watts': printer.power_consumption_watts,
            'is_active': printer.is_active
        }

    def _update_printer_summary(self, printer):
        """Actualizar el resumen de la impresora en el textEdit"""
        try:
            summary = []
            
            # Usar la moneda original de la impresora
            printer_currency = getattr(printer, 'currency_code', 'PYG')
            
            # Información básica
            summary.append(tr(I18N.Printer.GROUP_BASIC_INFO).upper())
            summary.append("")
            summary.append(f"**{tr(I18N.Printer.LABEL_NAME_DETAIL)}** {printer.name}")
            summary.append(f"**{tr(I18N.Printer.LABEL_BRAND)}** {printer.brand or tr(I18N.Printer.DEFAULT_NO_BRAND)}")
            summary.append(f"**{tr(I18N.Printer.LABEL_MODEL_DETAIL)}** {printer.model or tr(I18N.Printer.DEFAULT_NO_MODEL)}")
            summary.append("")
            
            # Especificaciones técnicas
            summary.append(tr(I18N.Printer.GROUP_TECHNICAL_SPECS).upper())
            summary.append("")
            summary.append(f"**{tr(I18N.Printer.LABEL_REAL_CONSUMPTION)}** {printer.power_consumption_watts:.0f} W")
            summary.append(f"**{tr(I18N.Printer.LABEL_PURCHASE_COST)}** {CurrencyHelper.format(printer.purchase_cost, printer_currency)}")
            summary.append(f"**{tr(I18N.Printer.LABEL_LIFESPAN_ESTIMATED)}** {printer.useful_life_hours:,.0f} {tr(I18N.Printer.UNIT_HOURS)}")
            summary.append("")
            
            # Costos operativos
            summary.append(tr(I18N.Printer.GROUP_COSTS).upper())
            summary.append("")
            summary.append(f"**{tr(I18N.Printer.LABEL_ELECTRICAL_COST_HOUR)}** {CurrencyHelper.format(printer.electricity_cost_per_hour, printer_currency)}")
            summary.append(f"**{tr(I18N.Printer.LABEL_WEAR_HOUR)}** {CurrencyHelper.format(printer.machine_wear_cost_per_hour, printer_currency)}")
            summary.append(f"**{tr(I18N.Printer.LABEL_MAINTENANCE_COST_HOUR)}** {CurrencyHelper.format(printer.maintenance_cost_per_hour, printer_currency)}")
            summary.append(f"**{tr(I18N.Printer.DETAIL_LABEL_SERVICE_COST_HOUR)}** {CurrencyHelper.format(printer.service_cost_per_hour, printer_currency)}")
            
            total_cost = printer.electricity_cost_per_hour + printer.service_cost_per_hour
            summary.append(f"**{tr(I18N.Printer.LABEL_TOTAL_COST_HOUR_FULL)}** {CurrencyHelper.format(total_cost, printer_currency)}")
            summary.append("")
            
            # Mantenimiento
            summary.append(tr(I18N.Printer.GROUP_MAINTENANCE).upper())
            summary.append("")
            summary.append(f"**{tr(I18N.Printer.LABEL_MAINTENANCE_COST)}** {CurrencyHelper.format(printer.maintenance_cost, printer_currency)}")
            summary.append(f"**{tr(I18N.Printer.LABEL_MAINTENANCE_INTERVAL)}** {printer.maintenance_interval_hours:.0f} {tr(I18N.Printer.UNIT_HOURS)}")
            summary.append("")
            
            # Cálculos adicionales
            summary.append(tr(I18N.Printer.GROUP_CALCULATIONS).upper())
            summary.append("")
            cost_per_minute = total_cost / 60
            summary.append(f"**{tr(I18N.Printer.LABEL_COST_MINUTE)}** {CurrencyHelper.format(cost_per_minute, printer_currency)}")
            
            daily_cost = total_cost * 8  # 8 horas trabajo
            summary.append(f"**{tr(I18N.Printer.LABEL_DAILY_COST)}** {CurrencyHelper.format(daily_cost, printer_currency)}")
            
            monthly_cost = daily_cost * 22  # 22 días laborables
            summary.append(f"**{tr(I18N.Printer.DETAIL_LABEL_MONTHLY_COST)}** {CurrencyHelper.format(monthly_cost, printer_currency)}")
            
            # Estado
            summary.append("")
            summary.append(tr(I18N.Labels.STATUS).upper())
            summary.append("")
            status = tr(I18N.Printer.STATUS_ACTIVE_TABLE).upper() if printer.is_active else tr(I18N.Printer.STATUS_INACTIVE_TABLE).upper()
            summary.append(f"**{tr(I18N.Printer.LABEL_ACTIVE_STATUS)}** {status}")
            
            # Mostrar en el textEdit
            text = "\n".join(summary)
            if hasattr(self.ui, 'textEdit_details_printer'):
                # Convertir formato **negrita** a HTML
                html_text = text.replace("**", "<b>", 1)
                while "**" in html_text:
                    html_text = html_text.replace("**", "</b>", 1)
                    if "**" in html_text:
                        html_text = html_text.replace("**", "<b>", 1)
                
                # Reemplazar saltos de línea con <br>
                html_text = html_text.replace("\n", "<br>")
                
                self.ui.textEdit_details_printer.setHtml(html_text)
            
        except Exception as e:
            logger.error("PrinterInventoryPresenter", f"Error actualizando resumen de impresora: {e}")
            logger.log_exception("PrinterInventoryPresenter", e, "_update_printer_summary")
            self._clear_printer_summary()

    def _clear_printer_summary(self):
        """Limpiar el resumen del textEdit"""
        try:
            if hasattr(self.ui, 'textEdit_details_printer'):
                self.ui.textEdit_details_printer.setHtml(
                    tr(I18N.Printer.MSG_SELECT_TO_VIEW)
                )
        except Exception:
            pass

    def _handle_show_details(self, item):
        """Manejar doble clic para mostrar detalles de la impresora"""
        current_row = item.row()
        
        # Obtener ID de la impresora seleccionada
        printer_id_item = self.ui.qtable_printers.item(current_row, 0)
        if not printer_id_item:
            return
        
        printer_id = int(printer_id_item.text())
        
        try:
            # Obtener impresora desde la base de datos
            printer = self.facade.get_printer_by_id(printer_id)
            if not printer:
                QMessageBox.warning(
                    self.main_window,
                    tr(I18N.Dialogs.ERROR_TITLE),
                    "No se pudo encontrar la impresora seleccionada."
                )
                return
            
            # Mostrar detalles
            dialog = PrinterDetailsDialog(self.main_window, printer)
            dialog.exec()
            
        except Exception as e:
            logger.error("PrinterInventoryPresenter", f"Error al mostrar detalles: {e}")
            logger.log_exception("PrinterInventoryPresenter", e, "_handle_show_details")
            QMessageBox.critical(
                self.main_window,
                tr(I18N.Dialogs.ERROR_TITLE),
                "Error al mostrar detalles.\n\nRevise el archivo de log para más detalles."
            )

    def _show_success_message(self, message):
        """Mostrar mensaje de éxito"""
        QMessageBox.information(
            self.main_window,
            tr(I18N.Dialogs.SUCCESS),
            message
        )

    def cleanup(self):
        """Limpiar recursos al destruir el presenter"""
        try:
            if self.button_animator:
                self.button_animator.cleanup()
                self.button_animator = None
            logger.info("PrinterInventoryPresenter", "Recursos del presenter limpiados")
        except Exception as e:
            logger.error("PrinterInventoryPresenter", f"Error limpiando recursos: {e}")
            logger.log_exception("PrinterInventoryPresenter", e, "cleanup")
