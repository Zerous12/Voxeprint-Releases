"""
Vista del selector de impresoras usando el UI existente
Implementa el patrón MVP con la interfaz generada
"""

from PySide6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtCore import QSize, QTimer, Signal, Qt, QEvent
from PySide6.QtGui import QIcon, QKeyEvent
from typing import List, Dict, Any, Optional

from core.utils.currency_helper import CurrencyHelper
from presentation.modules.printers.designs.select_printer_ui import Ui_Temp_Select_Printers
from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class PrinterSelectorDialogNew(QDialog):
    """
    Diálogo para selección de impresoras usando el UI generado
    Solo maneja la interfaz de usuario, la lógica está en el presenter
    """    
    # Señales emitidas hacia el presenter
    search_requested = Signal(str)
    refresh_requested = Signal()
    printer_selected = Signal(dict)
    add_printer_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_Temp_Select_Printers()
        self.ui.setupUi(self)

        # Vincula/recupera widgets por objectName para tolerar renombres en el UI
        self._bind_widgets()

        # Propiedades básicas de la ventana
        self.setWindowTitle(tr(I18N.Printer.DIALOG_SELECT_TITLE))
        self.setFixedSize(self.width(), self.height())

        # Configuración inicial
        self._setup_dialog()
        self._setup_table()
        self._setup_connections()
        self._setup_styles()

        # Estado interno de la vista
        self.current_selection = None

    def _bind_widgets(self):
        """Intenta asegurar que los atributos requeridos existan en self.ui.
        Si el UI generado cambia nombres, buscamos por objectName y reasignamos.
        """
        try:
            from PySide6.QtWidgets import QPushButton, QTableWidget, QLineEdit, QLabel, QTextEdit
            required: list[tuple[str, type]] = [
                ("btn_ok_select", QPushButton),
                ("btn_cancel_select", QPushButton),
                ("qtable_printers", QTableWidget),
                ("linedit_search", QLineEdit),
                ("btn_search", QPushButton),
                ("btn_refresh_panel", QPushButton),
                ("btn_add_printer", QPushButton),
                ("label_select", QLabel),
                ("label_printer_consumo", QLabel),
                ("label_printer_operation_price", QLabel),
                ("textEdit_details_printer", QTextEdit),
            ]
            missing: list[str] = []
            for name, cls in required:
                if not hasattr(self.ui, name) or getattr(self.ui, name) is None:
                    widget = self.findChild(cls, name)
                    if widget is not None:
                        setattr(self.ui, name, widget)
                    else:
                        missing.append(name)
            if missing:
                # Mensaje claro para desarrollador; no forzamos cierre violento
                logger.warning("PrinterSelectorDialogNew", f"Widgets faltantes en UI: {missing}")
        except Exception as e:
            logger.log_exception("PrinterSelectorDialogNew", e, "_bind_widgets")
    
    def _setup_dialog(self):
        """Configuración inicial del diálogo"""
        self.setWindowTitle(tr(I18N.Printer.DIALOG_SELECT_TITLE))
        self.setModal(True)
        self.setFixedSize(820, 547)

        # Textos del UI que vienen hardcodeados del .ui generado
        self.ui.label_headboard.setText(tr(I18N.Printer.SELECTOR_HEADING))
        self.ui.groupBox_action.setTitle(tr(I18N.Printer.SELECTOR_GROUP_ACTION))
        self.ui.groupbox_search.setTitle(tr(I18N.Printer.SELECTOR_GROUP_SEARCH))
        self.ui.btn_add_printer.setText(tr(I18N.Printer.SELECTOR_BTN_ADD))
        self.ui.btn_search.setText(tr(I18N.Printer.SELECTOR_BTN_SEARCH))
        self.ui.label_printer_details_title.setText(tr(I18N.Printer.SELECTOR_LABEL_DETAILS))
        self.ui.linedit_search.setToolTip(tr(I18N.Printer.SELECTOR_TOOLTIP_SEARCH_MIN))
        self.ui.btn_ok_select.setText(f"\u2714 {tr(I18N.Buttons.SELECT)}")
        self.ui.btn_cancel_select.setText(f"\u2715 {tr(I18N.Buttons.CANCEL)}")

        # Configurar iconos
        self._setup_icons()
    
    def _setup_icons(self):
        """Configura los iconos de los botones"""
        try:
            # Icono de refresh (ya está configurado en el UI)
            self.ui.btn_refresh_panel.setIconSize(QSize(18, 18))
            self.ui.btn_refresh_panel.setToolTip(tr(I18N.Printer.TOOLTIP_REFRESH))
            
            # Icono de agregar (ya está configurado en el UI)
            self.ui.btn_add_printer.setIconSize(QSize(20, 20))
            self.ui.btn_add_printer.setToolTip(tr(I18N.Printer.TOOLTIP_ADD_NEW))
            
        except Exception as e:
            logger.log_exception("PrinterSelectorDialogNew", e, "_setup_icons")
    
    def _setup_table(self):
        """Configuración de la tabla de impresoras"""
        table = self.ui.qtable_printers
        
        # Configurar encabezados
        headers = ["ID", tr(I18N.Printer.TABLE_HEADER_DESCRIPTION), tr(I18N.Printer.TABLE_HEADER_MODEL), tr(I18N.Printer.TABLE_HEADER_BRAND), tr(I18N.Printer.TABLE_HEADER_STATUS)]
        table.setHorizontalHeaderLabels(headers)
        
        # Ocultar la columna ID
        try:
            table.setColumnHidden(0, True)
        except Exception:
            pass

        # Configurar selección y deshabilitar edición (solo lectura)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Configurar columnas
        self._adjust_table_columns()
        
        # Configurar ordenamiento
        table.setSortingEnabled(True)
        
        # Ocultar numeración de filas
        table.verticalHeader().setVisible(False)
    
    def _adjust_table_columns(self):
        """Ajusta el tamaño de las columnas de la tabla"""
        header = self.ui.qtable_printers.horizontalHeader()
        
        # Configuración de columnas: (columna, modo, tamaño_fijo)
        column_configs = [
            (0, QHeaderView.ResizeMode.ResizeToContents, 0),     # ID (oculta)
            (1, QHeaderView.ResizeMode.Stretch, 200),            # Descripción
            (2, QHeaderView.ResizeMode.ResizeToContents, 120),   # Modelo
            (3, QHeaderView.ResizeMode.ResizeToContents, 120),   # Marca
            (4, QHeaderView.ResizeMode.ResizeToContents, 90)     # Status
        ]
        
        for column, mode, fixed_size in column_configs:
            header.setSectionResizeMode(column, mode)
            if fixed_size:
                header.resizeSection(column, fixed_size)
    
    def _setup_connections(self):
        """Configura las conexiones de señales"""
        # Conexiones de botones
        self.ui.btn_refresh_panel.clicked.connect(self._on_refresh_clicked)
        self.ui.btn_add_printer.clicked.connect(self._on_add_printer_clicked)
        self.ui.btn_search.clicked.connect(self._on_search_clicked)
        
        # Conexiones de la tabla
        self.ui.qtable_printers.itemSelectionChanged.connect(self._on_selection_changed)
        self.ui.qtable_printers.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Conexiones del campo de búsqueda - SOLO botón (no textChanged automático)
        # Instalar event filter personalizado para manejar Enter correctamente
        self.ui.linedit_search.installEventFilter(self)
        
        # Conexiones de botones de acción
        self.ui.btn_ok_select.clicked.connect(self._on_select_clicked)
        self.ui.btn_cancel_select.clicked.connect(self._on_cancel_clicked)

    def _setup_styles(self):
        """Configuración adicional de estilos y estado inicial"""
        # Placeholder del buscador
        try:
            self.ui.linedit_search.setPlaceholderText(
                tr(I18N.Printer.SEARCH_PLACEHOLDER)
            )
        except Exception:
            pass

        # Estado inicial de detalles y botones
        self._clear_printer_details()
    
    def eventFilter(self, obj, event):
        """
        Filtro de eventos personalizado para manejar Enter en el campo de búsqueda
        """
        if obj == self.ui.linedit_search and event.type() == QEvent.Type.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key.Key_Return or key_event.key() == Qt.Key.Key_Enter:
                # Interceptar Enter y ejecutar búsqueda
                self._on_search_clicked()
                return True  # Consumir el evento para evitar comportamiento por defecto
        
        # Llamar al filtro padre para otros eventos
        return super().eventFilter(obj, event)
    
    # === MÉTODOS DE INTERFAZ ===
    
    def populate_table(self, printers_data: List[Dict[str, Any]]):
        """Puebla la tabla con datos de impresoras"""
        table = self.ui.qtable_printers
        
        try:
            table.clearContents()
            table.setRowCount(len(printers_data))
            
            for row, printer in enumerate(printers_data):
                # ID
                id_item = QTableWidgetItem(str(printer.get('id', '')))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 0, id_item)
                
                # Descripción (nombre)
                name = printer.get('name', '') or tr(I18N.Printer.DEFAULT_NO_NAME)
                desc_item = QTableWidgetItem(name)
                desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 1, desc_item)
                
                # Modelo
                model = printer.get('model', '') or tr(I18N.Printer.DEFAULT_NOT_SPECIFIED)
                model_item = QTableWidgetItem(model)
                model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 2, model_item)
                
                # Marca
                brand = printer.get('brand', '') or tr(I18N.Printer.DEFAULT_NOT_SPECIFIED)
                brand_item = QTableWidgetItem(brand)
                brand_item.setFlags(brand_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 3, brand_item)
                
                # Status
                status = tr(I18N.Printer.STATUS_ACTIVE_TABLE) if printer.get('is_active', True) else tr(I18N.Printer.STATUS_INACTIVE_TABLE)
                status_item = QTableWidgetItem(status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 4, status_item)
                
                # Almacenar datos completos en la fila para recuperación
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item:
                        item.setData(Qt.ItemDataRole.UserRole, printer)
            
            # Limpiar selección
            self._clear_printer_details()
            
        except Exception as e:
            logger.log_exception("PrinterSelectorDialogNew", e, "populate_table")
            self.show_error_message(tr(I18N.Printer.MSG_ERROR_LOADING))
    
    def show_loading(self, message: str):
        """Muestra indicador de carga"""
        self.ui.label_select.setText(f"Cargando: {message}")
        self.ui.btn_ok_select.setEnabled(False)
        self.ui.qtable_printers.setEnabled(False)
    
    def hide_loading(self):
        """Oculta indicador de carga"""
        self.ui.qtable_printers.setEnabled(True)
        if not self.current_selection:
            self.ui.label_select.setText(tr(I18N.Printer.NO_SELECTION_MESSAGE))
            self.ui.btn_ok_select.setEnabled(False)
    
    def show_no_results(self, message: str):
        """Muestra mensaje cuando no hay resultados"""
        self.ui.qtable_printers.clearContents()
        self.ui.qtable_printers.setRowCount(0)
        # Limpiar detalles sin sobrescribir el mensaje
        self.current_selection = None
        self.ui.label_printer_consumo.setText(tr(I18N.Printer.LABEL_CONSUMPTION_NOT_SELECTED))
        self.ui.label_printer_operation_price.setText(tr(I18N.Printer.LABEL_OPERATION_PRICE_NOT_SELECTED))
        self.ui.textEdit_details_printer.setHtml(tr(I18N.Printer.MSG_SELECT_TO_VIEW))
        self.ui.btn_ok_select.setEnabled(False)
        # Establecer el mensaje personalizado AL FINAL
        self.ui.label_select.setText(f"{message}")
    
    def focus_search(self):
        """Establece el foco en el campo de búsqueda"""
        self.ui.linedit_search.setFocus()
    
    def get_search_text(self) -> str:
        """Obtiene el texto de búsqueda actual"""
        return self.ui.linedit_search.text().strip()
    
    def clear_search_text(self):
        """Limpia el campo de búsqueda"""
        self.ui.linedit_search.clear()
    
    def set_selected_printer_info(self, printer_data: Dict[str, Any]):
        """Actualiza la información de la impresora seleccionada"""
        try:
            self.current_selection = printer_data
            
            # Actualizar label de selección
            name = printer_data.get('name', tr(I18N.Printer.DEFAULT_NO_NAME))
            self.ui.label_select.setText(tr(I18N.Printer.SELECTOR_SELECTED_FMT).format(name=name))
            
            # Actualizar detalles en el TextEdit
            self._update_printer_details(printer_data)
            
            # Actualizar labels de consumo y precio
            self._update_consumption_and_cost_labels(printer_data)
            
            # Habilitar botón de selección
            self.ui.btn_ok_select.setEnabled(True)
            
        except Exception as e:
            logger.log_exception("PrinterSelectorDialogNew", e, "set_selected_printer_info")
    
    def _update_printer_details(self, printer_data: Dict[str, Any]):
        """Actualiza el TextEdit con detalles completos de la impresora - FORMATO IDÉNTICO AL TAB"""
        try:
            details = []
            
            # Obtener la moneda de la impresora
            printer_currency = printer_data.get('currency_code', 'PYG')
            
            # Información básica
            details.append(tr(I18N.Printer.GROUP_BASIC_INFO).upper())
            details.append("")
            details.append(f"**{tr(I18N.Printer.LABEL_NAME_DETAIL)}** {printer_data.get('name', 'N/A')}")
            details.append(f"**{tr(I18N.Printer.LABEL_BRAND)}** {printer_data.get('brand', 'N/A')}")
            details.append(f"**{tr(I18N.Printer.LABEL_MODEL_DETAIL)}** {printer_data.get('model', 'N/A')}")
            details.append("")
            
            # Especificaciones técnicas
            details.append(tr(I18N.Printer.GROUP_TECHNICAL_SPECS).upper())
            details.append("")
            power_consumption = printer_data.get('power_consumption_watts', 0)
            details.append(f"**{tr(I18N.Printer.LABEL_REAL_CONSUMPTION)}** {power_consumption:.0f} W")
            
            purchase_cost = printer_data.get('purchase_cost', 0)
            formatted_purchase = CurrencyHelper.format(purchase_cost or 0, printer_currency)
            details.append(f"**{tr(I18N.Printer.LABEL_PURCHASE_COST)}** {formatted_purchase}")
            
            useful_life = printer_data.get('useful_life_hours', 0)
            details.append(f"**{tr(I18N.Printer.LABEL_LIFESPAN_ESTIMATED)}** {useful_life:,.0f} {tr(I18N.Printer.UNIT_HOURS)}")
            details.append("")
            
            # Costos operativos
            details.append(tr(I18N.Printer.GROUP_COSTS).upper())
            details.append("")
            electricity_cost = printer_data.get('electricity_cost_per_hour', 0)
            formatted_elec = CurrencyHelper.format(electricity_cost or 0, printer_currency)
            details.append(f"**{tr(I18N.Printer.LABEL_ELECTRICAL_COST_HOUR)}** {formatted_elec}")
            
            machine_wear_cost = printer_data.get('machine_wear_cost_per_hour', 0)
            formatted_wear = CurrencyHelper.format(machine_wear_cost or 0, printer_currency)
            details.append(f"**{tr(I18N.Printer.LABEL_WEAR_HOUR)}** {formatted_wear}")
            
            maintenance_cost_per_hour = printer_data.get('maintenance_cost_per_hour', 0)
            formatted_maint = CurrencyHelper.format(maintenance_cost_per_hour or 0, printer_currency)
            details.append(f"**{tr(I18N.Printer.LABEL_MAINTENANCE_COST_HOUR)}** {formatted_maint}")
            
            service_cost = printer_data.get('service_cost_per_hour', 0)
            formatted_service = CurrencyHelper.format(service_cost or 0, printer_currency)
            details.append(f"**{tr(I18N.Printer.DETAIL_LABEL_SERVICE_COST_HOUR)}** {formatted_service}")
            
            # Calcular costo total/hora
            total_cost = (electricity_cost or 0) + (service_cost or 0)
            formatted_total = CurrencyHelper.format(total_cost, printer_currency)
            details.append(f"**{tr(I18N.Printer.LABEL_TOTAL_COST_HOUR_FULL)}** {formatted_total}")
            details.append("")
            
            # Mantenimiento
            details.append(tr(I18N.Printer.GROUP_MAINTENANCE).upper())
            details.append("")
            maintenance_cost = printer_data.get('maintenance_cost', 0)
            formatted_maint_cost = CurrencyHelper.format(maintenance_cost or 0, printer_currency)
            details.append(f"**{tr(I18N.Printer.LABEL_MAINTENANCE_COST)}** {formatted_maint_cost}")
            
            maintenance_interval = printer_data.get('maintenance_interval_hours', 0)
            details.append(f"**{tr(I18N.Printer.LABEL_MAINTENANCE_INTERVAL)}** {maintenance_interval:.0f} {tr(I18N.Printer.UNIT_HOURS)}")
            details.append("")
            
            # Cálculos estimados
            details.append(tr(I18N.Printer.GROUP_CALCULATIONS).upper())
            details.append("")
            cost_per_minute = total_cost / 60
            formatted_per_min = CurrencyHelper.format(cost_per_minute, printer_currency)
            details.append(f"**{tr(I18N.Printer.LABEL_COST_MINUTE)}** {formatted_per_min}")
            
            daily_cost = total_cost * 8  # 8 horas trabajo
            formatted_daily = CurrencyHelper.format(daily_cost, printer_currency)
            details.append(f"**{tr(I18N.Printer.LABEL_DAILY_COST)}** {formatted_daily}")
            
            monthly_cost = daily_cost * 22  # 22 días laborables
            formatted_monthly = CurrencyHelper.format(monthly_cost, printer_currency)
            details.append(f"**{tr(I18N.Printer.DETAIL_LABEL_MONTHLY_COST)}** {formatted_monthly}")
            details.append("")
            
            # Estado
            details.append(tr(I18N.Printer.GROUP_STATUS).upper())
            details.append("")
            is_active = printer_data.get('is_active', True)
            status = tr(I18N.Printer.STATUS_ACTIVE_TEXT) if is_active else tr(I18N.Printer.STATUS_INACTIVE_TEXT)
            details.append(f"**{tr(I18N.Printer.LABEL_ACTIVE_STATUS)}** {status}")
            
            # Establecer el texto en el TextEdit con formato HTML
            text = '\n'.join(details)
            
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
            logger.log_exception("PrinterSelectorDialogNew", e, "_update_printer_details")
            self.ui.textEdit_details_printer.setHtml(tr(I18N.Printer.MSG_ERROR_LOADING_DETAILS))
    
    def _update_consumption_and_cost_labels(self, printer_data: Dict[str, Any]):
        """Actualiza los labels de consumo y costo operativo"""
        try:
            # Label de consumo
            power_consumption = printer_data.get('power_consumption_watts', 0)
            
            if power_consumption > 0:
                consumption_text = f"{tr(I18N.Printer.LABEL_CONSUMPTION)} {power_consumption:.0f} W"
                # Clasificación por consumo
                if power_consumption < 200:
                    consumption_text += f" {tr(I18N.Printer.CONSUMPTION_LEVEL_LOW)}"
                elif power_consumption <= 400:
                    consumption_text += f" {tr(I18N.Printer.CONSUMPTION_LEVEL_MEDIUM)}"
                else:
                    consumption_text += f" {tr(I18N.Printer.CONSUMPTION_LEVEL_HIGH)}"
            else:
                consumption_text = tr(I18N.Printer.LABEL_CONSUMPTION_NOT_SELECTED)
            
            self.ui.label_printer_consumo.setText(consumption_text)
            
            # Label de precio de operación
            electricity_cost = printer_data.get('electricity_cost_per_hour', 0)
            service_cost = printer_data.get('service_cost_per_hour', 0)
            total_cost_per_hour = (electricity_cost or 0) + (service_cost or 0)
            
            if total_cost_per_hour > 0:
                symbol = CurrencyHelper.get_symbol(CurrencyHelper.get_current_currency())
                formatted_cost = CurrencyHelper.format_with_current_currency(total_cost_per_hour, include_symbol=False)
                cost_text = tr(I18N.Printer.LABEL_OPERATION_COST_FMT).format(symbol=symbol, cost=formatted_cost)
                # Clasificación por costo
                if total_cost_per_hour < 0.03:
                    cost_text += f" {tr(I18N.Printer.COST_LEVEL_ECONOMIC)}"
                elif total_cost_per_hour <= 0.05:
                    cost_text += f" {tr(I18N.Printer.COST_LEVEL_MODERATE)}"
                else:
                    cost_text += f" {tr(I18N.Printer.COST_LEVEL_EXPENSIVE)}"
            else:
                cost_text = tr(I18N.Printer.LABEL_OPERATION_PRICE_NOT_SELECTED)
            
            self.ui.label_printer_operation_price.setText(cost_text)
            
        except Exception as e:
            logger.log_exception("PrinterSelectorDialogNew", e, "_update_consumption_and_cost_labels")
    
    def _clear_printer_details(self):
        """Limpia los detalles de la impresora"""
        self.current_selection = None
        self.ui.label_select.setText(tr(I18N.Printer.NO_SELECTION_MESSAGE))
        self.ui.label_printer_consumo.setText(tr(I18N.Printer.LABEL_CONSUMPTION_NOT_SELECTED))
        self.ui.label_printer_operation_price.setText(tr(I18N.Printer.LABEL_OPERATION_PRICE_NOT_SELECTED))
        self.ui.textEdit_details_printer.setHtml(tr(I18N.Printer.MSG_SELECT_TO_VIEW))
        self.ui.btn_ok_select.setEnabled(False)
    
    # === MANEJADORES DE EVENTOS ===
    
    def _on_refresh_clicked(self):
        """Maneja clic en botón de actualizar"""
        self.refresh_requested.emit()
    
    def _on_add_printer_clicked(self):
        """Maneja clic en botón de agregar impresora"""
        self.add_printer_requested.emit()
    
    def _on_search_clicked(self):
        """Maneja clic en botón de búsqueda"""
        search_text = self.get_search_text()
        self.search_requested.emit(search_text)
    
    def _on_selection_changed(self):
        """Maneja cambio de selección en la tabla"""
        table = self.ui.qtable_printers
        selected_items = table.selectedItems()
        
        if selected_items:
            # Obtener datos del primer item seleccionado
            first_item = selected_items[0]
            printer_data = first_item.data(Qt.ItemDataRole.UserRole)
            
            if printer_data:
                self.set_selected_printer_info(printer_data)
        else:
            self._clear_printer_details()
    
    def _on_item_double_clicked(self, item):
        """Maneja doble clic en item de la tabla"""
        printer_data = item.data(Qt.ItemDataRole.UserRole)
        if printer_data:
            self.printer_selected.emit(printer_data)
            self.accept()
    
    def _on_select_clicked(self):
        """Maneja clic en botón de seleccionar"""
        if self.current_selection:
            self.printer_selected.emit(self.current_selection)
            self.accept()
        else:
            self.show_warning_message(tr(I18N.Printer.NO_SELECTION_REQUIRED_TITLE), 
                                    tr(I18N.Printer.SELECTOR_NO_SELECTION_MSG))
    
    def _on_cancel_clicked(self):
        """Maneja clic en botón de cancelar"""
        self.reject()
    
    # === MÉTODOS DE MENSAJES ===
    
    def show_success_message(self, message: str):
        """Muestra mensaje de éxito"""
        QMessageBox.information(self, tr(I18N.Dialogs.SUCCESS), message)
    
    def show_error_message(self, message: str):
        """Muestra mensaje de error"""
        QMessageBox.critical(self, tr(I18N.Dialogs.ERROR_TITLE), message)
    
    def show_warning_message(self, title: str, message: str):
        """Muestra mensaje de advertencia"""
        QMessageBox.warning(self, title, message)
    
    def show_info_message(self, title: str, message: str):
        """Muestra mensaje de información"""
        QMessageBox.information(self, title, message)
    
    # === MÉTODOS DE CIERRE ===
    
    def close_dialog_success(self):
        """Cierra el diálogo con éxito"""
        self.accept()
    
    def close_dialog_cancel(self):
        """Cierra el diálogo cancelando"""
        self.reject()
    
    def closeEvent(self, event):
        """Evento de cierre de la ventana"""
        super().closeEvent(event)
    
    def get_selected_printer(self) -> Optional[Dict[str, Any]]:
        """Retorna la impresora seleccionada"""
        return self.current_selection
