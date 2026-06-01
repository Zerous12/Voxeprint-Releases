"""
Presenter para el tab de inventario de presupuestos en la ventana principal
Maneja la tabla de quotes, búsqueda, selección y operaciones CRUD
"""

import os
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTableWidgetItem, QMessageBox, QHeaderView
from PySide6.QtCore import Qt, QDate
from typing import List, Optional, Dict, Any

from application.facades.voxeprint_facade import VoxeprintFacade
from domain.models.quote import Quote
from datetime import datetime
from core.utils.logger import logger
from core.utils.currency_helper import CurrencyHelper
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from core.managers.locale_manager import LocaleManager
from presentation.widgets.animation_mod.button_size_animator import ButtonSizeAnimator


class QuoteInventoryPresenter(QObject):
    """Presenter para gestionar el inventario de presupuestos"""
    
    # Señales para comunicarse con el exterior
    quote_selected = Signal(dict)  # Emite datos del quote seleccionado
    quote_deleted = Signal(int)    # Emite ID del quote eliminado
    quote_modified = Signal(dict)  # Emite datos del quote modificado
    
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        self.ui = main_view.ui
        
        # Facade para acceso a datos
        self.voxeprint_facade: Optional[VoxeprintFacade] = None
        
        # Estado
        self.all_quotes: List[Quote] = []
        self.displayed_quotes: List[Quote] = []
        self.selected_quote: Optional[Quote] = None
        self._updating_filters = False  # Flag para evitar bucles infinitos
        
        # Animador de botones
        self.button_animator: Optional[ButtonSizeAnimator] = None
        
        # Configurar UI
        self._setup_ui()
        self._connect_signals()
        self._setup_button_animations()
    
    def set_facade(self, facade: VoxeprintFacade):
        """Establece el facade para acceso a datos"""
        self.voxeprint_facade = facade
        # Cargar datos iniciales cuando el facade esté disponible
        self.load_quotes()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar tabla
        table = self.ui.qtable_quote
        
        # Configurar cabeceras
        headers = [
            tr(I18N.Quote.COL_ID),
            tr(I18N.Quote.COL_NUM),
            tr(I18N.Quote.COL_CLIENT),
            tr(I18N.Quote.COL_AMOUNT),
            tr(I18N.Quote.COL_DATE),
            tr(I18N.Quote.COL_FILE),
        ]
        table.setHorizontalHeaderLabels(headers)
        
        # Ocultar columna ID
        table.setColumnHidden(0, True)
        
        # Configurar anchos de columnas
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Número
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Cliente
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Monto
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Fecha
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Archivo
              
        # Configurar selección
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.SingleSelection)
        
        # Configurar ordenamiento
        table.setSortingEnabled(True)
        
        # Configurar textEdit inicial
        self.ui.textEdit_details_quotes.setHtml(
            tr(I18N.Quote.STATUS_SELECT_QUOTE)
        )
        
        # Configurar estado inicial de botones
        self._update_button_states(False)
        
        # Configurar filtros de fecha
        self._setup_date_filters()
    
    def _setup_date_filters(self):
        """Configura los filtros de fecha"""
        try:
            if self._updating_filters:
                return  # Evitar bucle infinito
                
            self._updating_filters = True
            
            # Configurar fechas por defecto (últimos 3 meses)
            end_date = QDate.currentDate()
            start_date = end_date.addMonths(-3)
            
            # Desconectar temporalmente las señales para evitar bucles
            self.ui.datedit_desde.dateChanged.disconnect()
            self.ui.datedit_hasta.dateChanged.disconnect()
            
            # Establecer las fechas
            self.ui.datedit_desde.setDate(start_date)
            self.ui.datedit_hasta.setDate(end_date)
            
            # Reconectar las señales
            self.ui.datedit_desde.dateChanged.connect(self._on_date_filter_changed)
            self.ui.datedit_hasta.dateChanged.connect(self._on_date_filter_changed)
            
        except Exception as e:
            logger.error("QuoteInventory", f"Error configurando filtros de fecha: {e}")
        finally:
            self._updating_filters = False
    
    def _connect_signals(self):
        """Conecta las señales de la UI"""
        # Señales de la tabla
        self.ui.qtable_quote.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Señales del buscador
        self.ui.btn_search_4.clicked.connect(self._on_search_clicked)
        self.ui.linedit_search_4.returnPressed.connect(self._on_search_clicked)
        
        # Señales de filtros de fecha
        self.ui.datedit_desde.dateChanged.connect(self._on_date_filter_changed)
        self.ui.datedit_hasta.dateChanged.connect(self._on_date_filter_changed)
        
        # Doble clic en tabla para abrir PDF
        self.ui.qtable_quote.itemDoubleClicked.connect(self._on_open_clicked)
        
        # Señales de botones de operaciones
        self.ui.btn_open_quote.clicked.connect(self._on_open_clicked)
        self.ui.btn_report_quotes.clicked.connect(self._on_export_clicked)
        self.ui.btn_delete_quote.clicked.connect(self._on_delete_clicked)
        
        # Señal del botón cleaner
        self.ui.btn_cleaner_4.clicked.connect(self._handle_clear_search)
    
    def _setup_button_animations(self):
        """Configura las animaciones de los botones de búsqueda"""
        try:
            # Crear animador para el par btn_search_4/btn_cleaner_4 (quotes)
            self.button_animator = ButtonSizeAnimator(
                primary_button=self.ui.btn_search_4,
                secondary_button=self.ui.btn_cleaner_4
            )
            
            logger.debug("QuoteInventory", "Animaciones de botones configuradas", 
                            botones="btn_search_4/btn_cleaner_4")
            
        except Exception as e:
            logger.error("QuoteInventory", "Error configurando animaciones de botones", error=str(e))
    
    def _handle_clear_search(self):
        """Maneja la limpieza de campos de búsqueda y filtros en quotes"""
        try:
            # Limpiar campo de búsqueda
            self.ui.linedit_search_4.clear()
            
            # Restablecer filtros de fecha
            self._setup_date_filters()
            
            # Aplicar filtros (que ahora serán los por defecto)
            self._filter_quotes()
            
            # 🔇 Cambiado a mensaje menos visible para reducir ruido
            self._update_status_message(tr(I18N.Quote.INV_STATUS_SHOWING, count=len(self.displayed_quotes)))
            
            logger.info("QuoteInventoryPresenter", f"Limpieza de campos y filtros completada - {len(self.displayed_quotes)} presupuestos mostrados")
            
        except Exception as e:
            logger.log_exception("QuoteInventoryPresenter", e, "clear_fields")
            self._update_status_message(tr(I18N.Quote.INV_STATUS_CLEAR_ERROR))
    
    def _update_status_message(self, message: str):
        """Actualiza el mensaje de estado en la vista principal"""
        try:
            if hasattr(self.main_view, 'add_status_message'):
                self.main_view.add_status_message(f"HISTORIAL: {message}")
            else:
                logger.debug("QuoteInventoryPresenter", f"Historial: {message}")
        except Exception as e:
            logger.log_exception("QuoteInventoryPresenter", e, "_update_status_message")
    
    def load_quotes(self):
        """Carga los presupuestos desde la base de datos"""
        try:
            if self.voxeprint_facade:
                response = self.voxeprint_facade.get_all_quotes()
                if hasattr(response, 'success') and response.success:
                    self.all_quotes = response.data
                    self.displayed_quotes = self.all_quotes.copy()
                    
                    logger.debug("QuoteInventory", "Presupuestos cargados para inventario", 
                                   cantidad=len(self.all_quotes))
                    self._update_table()
                    self._update_status_label()
                else:
                    logger.error("QuoteInventory", "Error cargando presupuestos desde el facade")
                    self.all_quotes = []
                    self.displayed_quotes = []
            else:
                logger.error("QuoteInventory", "Facade no disponible para cargar presupuestos")
                
        except Exception as e:
            logger.error("QuoteInventory", f"Error cargando presupuestos: {e}")
            QMessageBox.critical(
                self.main_view,
                tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.Quote.MSG_ERROR_LOADING, error=str(e))
            )
    
    def _update_table(self):
        """Actualiza la tabla con los presupuestos filtrados"""
        table = self.ui.qtable_quote
        table.setRowCount(len(self.displayed_quotes))
        
        for row, quote in enumerate(self.displayed_quotes):
            # ID (oculto)
            table.setItem(row, 0, QTableWidgetItem(str(quote.id or "")))
            
            # Número
            number_item = QTableWidgetItem(quote.quote_number or "")
            number_item.setFlags(number_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 1, number_item)
            
            # Cliente (obtener nombre del cliente)
            customer_name = self._get_customer_name(quote.customer_id)
            customer_item = QTableWidgetItem(customer_name)
            customer_item.setFlags(customer_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 2, customer_item)
            
            # Monto - usar la moneda del quote
            quote_currency = getattr(quote, 'currency_code', 'PYG')
            amount_text = CurrencyHelper.format(quote.total_to_pay, quote_currency) if quote.total_to_pay else CurrencyHelper.format(0, quote_currency)
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setFlags(amount_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 3, amount_item)
            
            # Fecha
            try:
                if quote.created_at:
                    date_fmt = LocaleManager().get_date_format_strftime()
                    if isinstance(quote.created_at, str):
                        # Si es string, intentar parsearlo
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(quote.created_at.replace('Z', '+00:00'))
                        date_text = date_obj.strftime(date_fmt)
                    else:
                        # Si ya es datetime
                        date_text = quote.created_at.strftime(date_fmt)
                else:
                    date_text = tr(I18N.Quote.DATE_NOT_AVAILABLE)
            except Exception as e:
                logger.log_exception("QuoteInventoryPresenter", e, "_update_table")
                date_text = tr(I18N.Quote.DATE_INVALID)
                
            date_item = QTableWidgetItem(date_text)
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 4, date_item)
            
            # Archivo
            # 🎯 Verificar no solo si tiene file_path, sino si el archivo existe realmente
            if quote.file_path and os.path.exists(quote.file_path):
                file_text = tr(I18N.Quote.FILE_AVAILABLE)
            else:
                file_text = tr(I18N.Quote.FILE_NOT_AVAILABLE)
            file_item = QTableWidgetItem(file_text)
            file_item.setFlags(file_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 5, file_item)
        
        # Limpiar selección anterior
        table.clearSelection()  # Limpiar selección visual
        self.selected_quote = None
        self._update_button_states(False)
        self._update_details_text("")
        
        # NO reiniciar filtros de fecha aquí - causa bucle infinito
    
    def _get_customer_name(self, customer_id):
        """Obtiene el nombre del cliente por ID"""
        try:
            if not customer_id or not self.voxeprint_facade:
                return tr(I18N.Quote.NAME_NOT_AVAILABLE)
                
            # Usar el facade para obtener el cliente
            customer_response = self.voxeprint_facade.get_customer(customer_id)
            
            if hasattr(customer_response, 'success') and customer_response.success:
                customer = customer_response.data
                return customer.full_name if hasattr(customer, 'full_name') else tr(I18N.Quote.NAME_NOT_AVAILABLE)
            else:
                return tr(I18N.Quote.NAME_NOT_AVAILABLE)
                
        except Exception as e:
            logger.log_exception("QuoteInventoryPresenter", e, "_get_customer_name")
            return tr(I18N.Quote.NAME_NOT_AVAILABLE)

    def _get_printer_name(self, printer_id):
        """Obtiene el nombre de la impresora por ID"""
        try:
            if not printer_id or not self.voxeprint_facade:
                return tr(I18N.Quote.NAME_NOT_AVAILABLE)
                
            printer = self.voxeprint_facade.get_printer_by_id(printer_id)
            if printer and hasattr(printer, 'name'):
                return f"{printer.name} ({printer.brand} {printer.model})" if printer.brand and printer.model else printer.name
            else:
                return tr(I18N.Quote.NAME_NOT_AVAILABLE)
                
        except Exception as e:
            logger.log_exception("QuoteInventoryPresenter", e, "_get_printer_name")
            return tr(I18N.Quote.NAME_NOT_AVAILABLE)

    def _get_filament_name(self, filament_id):
        """Obtiene el nombre del filamento por ID"""
        try:
            if not filament_id or not self.voxeprint_facade:
                return tr(I18N.Quote.NAME_NOT_AVAILABLE)
                
            filament = self.voxeprint_facade.get_filament_by_id(filament_id)
            if filament and hasattr(filament, 'name'):
                color_str = (
                    tr(f"FilamentColor.{filament.color.name}")
                    if hasattr(filament, 'color') and hasattr(filament.color, 'name')
                    else str(getattr(filament, 'color', ''))
                )
                return f"{filament.name} - {filament.brand} ({color_str})" if filament.brand and color_str else filament.name
            else:
                return tr(I18N.Quote.NAME_NOT_AVAILABLE)
                
        except Exception as e:
            logger.log_exception("QuoteInventoryPresenter", e, "_get_filament_name")
            return tr(I18N.Quote.NAME_NOT_AVAILABLE)
    
    def _update_status_label(self):
        """Actualiza la etiqueta de estado"""
        total = len(self.all_quotes)
        filtered = len(self.displayed_quotes)
        
        if total == filtered:
            status_text = tr(I18N.Quote.INV_STATUS_COUNT, total=total)
        else:
            status_text = tr(I18N.Quote.INV_STATUS_FILTERED, filtered=filtered, total=total)
        
        # Actualizar label si existe en la UI
        if hasattr(self.ui, 'label_quote_count'):
            self.ui.label_quote_count.setText(status_text)
    
    def _on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        table = self.ui.qtable_quote
        current_row = table.currentRow()
        
        if 0 <= current_row < len(self.displayed_quotes):
            self.selected_quote = self.displayed_quotes[current_row]
            self._update_button_states(True)
            self._update_details_text(self._get_quote_details())
            
            # Emitir señal para notificar la selección (si es necesario)
            quote_data = {
                'id': self.selected_quote.id,
                'quote_number': self.selected_quote.quote_number,
                'customer_id': self.selected_quote.customer_id,
                'total_to_pay': self.selected_quote.total_to_pay
            }
            self.quote_selected.emit(quote_data)
        else:
            self.selected_quote = None
            self._update_button_states(False)
            self._update_details_text("")
    
    def _update_button_states(self, has_selection: bool):
        """Actualiza el estado de los botones según la selección"""
        # Habilitar botón de abrir solo si hay selección Y hay archivo PDF disponible
        if has_selection and self.selected_quote and self.selected_quote.file_path:
            # Verificar que el archivo existe realmente
            pdf_available = os.path.exists(self.selected_quote.file_path)
            self.ui.btn_open_quote.setEnabled(pdf_available)
            
            if pdf_available:
                self.ui.btn_open_quote.setToolTip(tr(I18N.Quote.TOOLTIP_OPEN_PDF))
            else:
                self.ui.btn_open_quote.setToolTip(tr(I18N.Quote.MSG_PDF_NOT_FOUND))
        else:
            self.ui.btn_open_quote.setEnabled(False)
            if has_selection:
                self.ui.btn_open_quote.setToolTip(tr(I18N.Quote.MSG_PDF_NOT_AVAILABLE))
            else:
                self.ui.btn_open_quote.setToolTip(tr(I18N.Quote.STATUS_SELECT_QUOTE_PDF))
    
    def _update_details_text(self, details: str):
        """Actualiza el texto de detalles"""
        if not details:
            details = tr(I18N.Quote.STATUS_SELECT_QUOTE)
        
        # Convertir formato **negrita** a HTML
        html_details = details.replace("**", "<b>", 1)
        while "**" in html_details:
            html_details = html_details.replace("**", "</b>", 1)
            if "**" in html_details:
                html_details = html_details.replace("**", "<b>", 1)
        
        # Reemplazar saltos de línea con <br>
        html_details = html_details.replace("\n", "<br>")
        
        self.ui.textEdit_details_quotes.setHtml(html_details)
    
    def _get_quote_details(self) -> str:
        """Genera el texto de detalles del presupuesto seleccionado"""
        if not self.selected_quote:
            return ""
        
        quote = self.selected_quote
        customer_name = self._get_customer_name(quote.customer_id)
        
        # Usar la moneda original del presupuesto
        quote_currency = getattr(quote, 'currency_code', 'PYG')
        
        details = [
            tr(I18N.Quote.INV_DETAIL_HEADER, number=quote.quote_number),
            "",
            tr(I18N.Quote.INV_FIELD_CUSTOMER, value=customer_name),
            tr(I18N.Quote.INV_FIELD_PROJECT, value=quote.project_name or tr(I18N.Quote.INV_NOT_SPECIFIED)),
            "",
            tr(I18N.Quote.INV_SECTION_FINANCIAL),
            tr(I18N.Quote.INV_FIELD_FINAL_PRICE, value=CurrencyHelper.format(quote.total_to_pay, quote_currency)) if quote.total_to_pay else tr(I18N.Quote.INV_FIELD_FINAL_PRICE_NONE),
            "",
            tr(I18N.Quote.INV_SECTION_PRODUCTION),
        ]
        
        # Tiempo de impresión
        if quote.print_time_minutes:
            hours = quote.print_time_minutes / 60
            details.append(tr(I18N.Quote.INV_FIELD_PRINT_TIME, value=f"{hours:.2f}"))
        else:
            details.append(tr(I18N.Quote.INV_FIELD_PRINT_TIME_NONE))
        
        # Peso del filamento
        if quote.filament_weight_grams:
            details.append(tr(I18N.Quote.INV_FIELD_FILAMENT_WEIGHT, value=quote.filament_weight_grams))
        else:
            details.append(tr(I18N.Quote.INV_FIELD_FILAMENT_WEIGHT_NONE))
        
        # Información adicional
        details.extend([
            "",
            tr(I18N.Quote.INV_SECTION_ADDITIONAL),
            tr(I18N.Quote.INV_FIELD_FILE, value=quote.file_path if quote.file_path else tr(I18N.Quote.INV_NOT_SPECIFIED)),
            tr(I18N.Quote.INV_FIELD_NOTES, value=quote.notes if quote.notes else tr(I18N.Quote.INV_NO_NOTES)),
            "",
            tr(I18N.Quote.INV_SECTION_DATES),
        ])
        
        # Fechas con formato regional
        date_fmt = LocaleManager().get_date_format_strftime() + " %H:%M"
        try:
            if quote.created_at:
                if isinstance(quote.created_at, str):
                    created_date = datetime.fromisoformat(quote.created_at.replace('Z', '+00:00'))
                else:
                    created_date = quote.created_at
                details.append(tr(I18N.Quote.INV_FIELD_CREATED, value=created_date.strftime(date_fmt)))
            else:
                details.append(tr(I18N.Quote.INV_FIELD_CREATED, value=tr(I18N.Quote.INV_FIELD_DATE_NONE)))
                
            if quote.updated_at:
                if isinstance(quote.updated_at, str):
                    updated_date = datetime.fromisoformat(quote.updated_at.replace('Z', '+00:00'))
                else:
                    updated_date = quote.updated_at
                details.append(tr(I18N.Quote.INV_FIELD_UPDATED, value=updated_date.strftime(date_fmt)))
            else:
                details.append(tr(I18N.Quote.INV_FIELD_UPDATED, value=tr(I18N.Quote.INV_FIELD_DATE_NONE)))
        except Exception as e:
            logger.log_exception("QuoteInventoryPresenter", e, "_format_quote_details")
            details.append(tr(I18N.Quote.INV_FIELD_DATES_ERROR))
        
        return "\n".join(details)
    
    def _on_search_clicked(self):
        """Maneja la búsqueda de presupuestos"""
        search_text = self.ui.linedit_search_4.text().strip()
        
        # Si all_quotes está vacío, cargar primero desde BD
        if not self.all_quotes:
            logger.warning("QuoteInventoryPresenter", "all_quotes vacío, cargando desde BD primero")
            self.load_quotes()
        
        if len(search_text) >= 3 or search_text == "":
            self._filter_quotes()
        else:
            logger.debug("QuoteInventoryPresenter", "Mínimo 3 caracteres para buscar")
    
    def _on_date_filter_changed(self):
        """Maneja cambios en los filtros de fecha"""
        try:
            if self._updating_filters:
                return  # Evitar bucle infinito
                
            logger.debug("QuoteInventoryPresenter", "Cambio en filtro de fecha detectado")
            self._filter_quotes()
        except Exception as e:
            logger.log_exception("QuoteInventoryPresenter", e, "_on_date_filter_changed")
    
    def _filter_quotes(self):
        """Filtra los presupuestos por fecha y búsqueda"""
        try:
            search_text = self.ui.linedit_search_4.text().strip().lower()
            start_date = self.ui.datedit_desde.date().toPython()
            end_date = self.ui.datedit_hasta.date().toPython()
            
            # Convertir end_date al final del día
            end_date = datetime.combine(end_date, datetime.max.time())
            start_date = datetime.combine(start_date, datetime.min.time())
            
            filtered_quotes = []
            for quote in self.all_quotes:
                # Filtro por fecha
                if quote.created_at:
                    try:
                        if isinstance(quote.created_at, str):
                            # Si es string, parsearlo
                            quote_date = datetime.fromisoformat(quote.created_at.replace('Z', '+00:00'))
                        else:
                            # Si ya es datetime
                            quote_date = quote.created_at
                            
                        if not (start_date <= quote_date <= end_date):
                            continue
                    except Exception as e:
                        logger.error("QuoteInventory", f"Error procesando fecha de quote {quote.id}: {e}")
                        continue
                
                # Filtro por búsqueda
                if search_text:
                    customer_name = self._get_customer_name(quote.customer_id).lower()
                    project_name = (quote.project_name or "").lower()
                    quote_number = (quote.quote_number or "").lower()
                    
                    if not (search_text in customer_name or 
                           search_text in project_name or 
                           search_text in quote_number):
                        continue
                
                filtered_quotes.append(quote)
            
            self.displayed_quotes = filtered_quotes
            self._update_table()
            self._update_status_label()
            
        except Exception as e:
            logger.error("QuoteInventory", f"Error aplicando filtros: {e}")
    
    def _on_open_clicked(self):
        """Maneja el evento de abrir presupuesto guardado"""
        if not self.selected_quote:
            QMessageBox.warning(
                self.main_view,
                tr(I18N.Quote.INV_NO_SELECTION_TITLE),
                tr(I18N.Quote.INV_NO_SELECTION_OPEN)
            )
            return
        
        # Verificar que el presupuesto tenga PDF disponible
        if not self.selected_quote.file_path:
            QMessageBox.warning(
                self.main_view,
                tr(I18N.Quote.INV_PDF_NO_PDF_TITLE),
                tr(I18N.Quote.INV_PDF_NO_PDF)
            )
            return
        
        # Verificar que el archivo existe
        if not os.path.exists(self.selected_quote.file_path):
            QMessageBox.warning(
                self.main_view,
                tr(I18N.Quote.INV_FILE_NOT_FOUND_TITLE),
                tr(I18N.Quote.INV_FILE_NOT_FOUND, path=self.selected_quote.file_path)
            )
            return
        
        try:
            # Abrir el visor de PDF para presupuesto guardado
            from presentation.modules.visualizer.views.saved_quote_pdf_viewer import SavedQuotePDFViewer
            
            viewer = SavedQuotePDFViewer(
                pdf_path=self.selected_quote.file_path,
                quote_number=self.selected_quote.quote_number,
                parent=self.main_view
            )
            
            logger.info("QuoteInventory", "PDF abierto para visualización", 
                           quote=self.selected_quote.quote_number,
                           path=self.selected_quote.file_path)
            
            # Mostrar el visor
            viewer.exec()
            
        except ImportError:
            # Si no existe el visor específico, usar el visor estándar sin funcionalidad de guardado
            try:
                from presentation.modules.visualizer.views.pdf_viewer_dialog import PDFViewer
                
                viewer = PDFViewer(
                    pdf_path=self.selected_quote.file_path,
                    quote_number=self.selected_quote.quote_number,
                    save_callback=None,  # Sin callback porque ya está guardado
                    parent=self.main_view
                )
                
                logger.info("QuoteInventory", "PDF abierto con visor estándar", 
                               quote=self.selected_quote.quote_number)
                
                viewer.exec()
                
            except Exception as e:
                logger.error("QuoteInventory", "Error abriendo visor PDF", 
                                quote=self.selected_quote.quote_number,
                                error=str(e))
                QMessageBox.critical(
                    self.main_view,
                    tr(I18N.Dialogs.ERROR_TITLE),
                    tr(I18N.Quote.INV_ERROR_OPEN_VIEWER, error=str(e))
                )
        
        except Exception as e:
            logger.error("QuoteInventory", "Error abriendo PDF", 
                             quote=self.selected_quote.quote_number,
                             error=str(e))
            QMessageBox.critical(
                self.main_view,
                tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.Quote.INV_ERROR_OPEN, error=str(e))
            )
    
    def _on_export_clicked(self):
        """Genera el reporte PDF de estadísticas usando el rango de fechas del filtro"""
        if not self.voxeprint_facade:
            QMessageBox.warning(self.main_view, tr(I18N.Dialogs.ERROR_TITLE), tr(I18N.Quote.INV_ERROR_NOT_INIT))
            return

        # Obtener rango de fechas de los filtros
        start_date = self.ui.datedit_desde.date().toPython().strftime('%Y-%m-%d')
        end_date = self.ui.datedit_hasta.date().toPython().strftime('%Y-%m-%d')

        logger.info("QuoteInventoryPresenter",
                     f"Generando reporte de estadísticas: {start_date} a {end_date}")

        # Deshabilitar botón para evitar doble clic
        self.ui.btn_report_quotes.setEnabled(False)

        # Mostrar animación y ejecutar generación en hilo secundario
        from presentation.widgets.animation_mod.rotating_circle import WaitingCircle

        self._loading = WaitingCircle(parent=self.ui.frame_content)
        self._loading.superposition(True)
        self._loading.run_async(
            self._generate_stats_pdf, 
            lambda result, error: self._on_stats_ready(result, error, start_date, end_date),
            start_date, end_date
        )

    def _generate_stats_pdf(self, start_date: str, end_date: str):
        """Trabajo pesado: consulta DB + genera PDF. Se ejecuta en hilo secundario."""
        response = self.voxeprint_facade.get_quote_stats(start_date, end_date)
        if not (hasattr(response, 'success') and response.success):
            raise RuntimeError(getattr(response, 'message', tr(I18N.Quote.INV_ERROR_UNKNOWN)))

        stats_data = response.data
        if stats_data.get('quote_count', 0) == 0:
            return None  # Sin datos

        import tempfile
        from core.managers.stats_pdf_manager import StatsPDFManager

        pdf_manager = StatsPDFManager()
        temp_file = tempfile.NamedTemporaryFile(
            suffix='.pdf', prefix='Statistics_tmp_', delete=False
        )
        temp_path = temp_file.name
        temp_file.close()
        pdf_manager.generate(temp_path, stats_data)
        return {'path': temp_path, 'stats': stats_data}

    def _on_stats_ready(self, result, error, start_date, end_date):
        """Callback en hilo principal cuando el PDF está listo."""
        self.ui.btn_report_quotes.setEnabled(True)
        if hasattr(self, '_loading') and self._loading:
            self._loading.stop()
        self._loading = None

        if error:
            logger.log_exception("QuoteInventoryPresenter", error, "_on_stats_ready")
            QMessageBox.critical(
                self.main_view, tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.Quote.INV_ERROR_STATS))
            return

        if result is None:
            QMessageBox.information(
                self.main_view,
                tr(I18N.Quote.INV_NO_DATA_TITLE),
                tr(I18N.Quote.INV_NO_DATA, start=start_date, end=end_date))
            return


        temp_path = result['path']
        stats_data = result['stats']

        self._update_status_message(
            tr(I18N.Quote.INV_STATUS_REPORT, count=stats_data['quote_count']))

        from presentation.modules.visualizer.views.saved_quote_pdf_viewer import SavedQuotePDFViewer

        # Compactar fechas a formato 'YYYY-MM a YYYY-MM'
        try:
            start_label = start_date[:7]  # 'YYYY-MM'
            end_label = end_date[:7]      # 'YYYY-MM'
            report_label = f"{start_label} - {end_label}"
        except Exception:
            report_label = f"{start_date} - {end_date}"

        viewer = SavedQuotePDFViewer(
            pdf_path=temp_path,
            quote_number=report_label,
            parent=self.main_view,
            is_report=True
        )
        viewer.exec()

        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except OSError:
            pass

        logger.info("QuoteInventoryPresenter", f"Reporte PDF visualizado: {report_label}")
    
    def _on_delete_clicked(self):
        """Maneja el evento de eliminar presupuesto"""
        if not self.selected_quote:
            QMessageBox.warning(
                self.main_view,
                tr(I18N.Quote.INV_NO_SELECTION_TITLE),
                tr(I18N.Quote.INV_NO_SELECTION_DELETE)
            )
            return
        
        quote = self.selected_quote
        
        # Usar la moneda del quote
        quote_currency = getattr(quote, 'currency_code', 'PYG')
        
        # Confirmar eliminación
        amount_text = CurrencyHelper.format(quote.total_to_pay, quote_currency) if quote.total_to_pay else "—"
        reply = QMessageBox.question(
            self.main_view,
            tr(I18N.Quote.INV_CONFIRM_DELETE_TITLE),
            tr(I18N.Quote.INV_CONFIRM_DELETE,
               number=quote.quote_number,
               customer=self._get_customer_name(quote.customer_id),
               amount=amount_text),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Eliminar el presupuesto usando el facade
                logger.info("QuoteInventoryPresenter", f"Eliminando presupuesto: {quote.quote_number}")
                
                response = self.voxeprint_facade.delete_quote(quote.id)
                
                if response.success:
                    # Emitir señal de eliminación
                    self.quote_deleted.emit(quote.id)
                    
                    # Recargar la lista
                    self.load_quotes()
                    
                    # Limpiar selección
                    self.selected_quote = None
                    
                    QMessageBox.information(
                        self.main_view,
                        tr(I18N.Quote.INV_DELETED_TITLE),
                        response.message
                    )
                else:
                    QMessageBox.warning(
                        self.main_view,
                        tr(I18N.Dialogs.ERROR_TITLE),
                        response.message
                    )
                    
            except Exception as e:
                logger.log_exception("QuoteInventoryPresenter", e, "_on_delete_clicked")
                QMessageBox.critical(
                    self.main_view,
                    tr(I18N.Dialogs.ERROR_TITLE),
                    tr(I18N.Quote.INV_ERROR_DELETE)
                )
    
    def refresh(self):
        """Refresca los datos del inventario y reaplica los filtros actuales"""
        self.load_quotes()
        # Reaplicar filtros después de cargar para mantener la vista consistente
        search_text = self.ui.linedit_search_4.text().strip()
        if search_text or True:  # Siempre aplicar filtro de fecha
            self._filter_quotes()
    
    def cleanup(self):
        """Limpieza de recursos al cerrar el presenter"""
        try:
            if self.button_animator:
                self.button_animator.cleanup()
                self.button_animator = None
            logger.info("QuoteInventoryPresenter", "Cleanup completado en QuoteInventoryPresenter")
        except Exception as e:
            logger.log_exception("QuoteInventoryPresenter", e, "cleanup")
