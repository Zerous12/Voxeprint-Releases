"""
Vista del selector de filamentos usando el UI existente
Implementa el patrón MVP con la interfaz generada
"""

from PySide6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtCore import QSize, QTimer, Signal, Qt, QEvent
from PySide6.QtGui import QIcon, QKeyEvent
from typing import List, Dict, Any, Optional

from core.utils.currency_helper import CurrencyHelper
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from presentation.modules.filaments.designs.select_filament_ui import Ui_Temp_Select_Filaments


class FilamentSelectorDialogNew(QDialog):
    """
    Diálogo para selección de filamentos usando el UI generado
    Solo maneja la interfaz de usuario, la lógica está en el presenter
    """    
    # Señales emitidas hacia el presenter
    search_requested = Signal(str)
    refresh_requested = Signal()
    filament_selected = Signal(dict)
    add_filament_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_Temp_Select_Filaments()
        self.ui.setupUi(self)

        # Vincula/recupera widgets por objectName para tolerar renombres en el UI
        self._bind_widgets()

        # Propiedades básicas de la ventana
        self.setWindowTitle(tr(I18N.Filament.SELECTOR_TITLE))
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
            from PySide6.QtWidgets import QPushButton, QTableWidget, QLineEdit, QLabel, QTextEdit, QGroupBox
            required: list[tuple[str, type]] = [
                ("btn_ok_select", QPushButton),
                ("btn_cancel_select", QPushButton),
                ("qtable_filament", QTableWidget),
                ("linedit_search", QLineEdit),
                ("btn_search", QPushButton),
                ("btn_refresh_panel", QPushButton),
                ("btn_add_filament", QPushButton),
                ("label_select", QLabel),
                ("label_filament_stock", QLabel),
                ("label_filament_price", QLabel),
                ("textEdit_details_filament", QTextEdit),
                ("label_headboard", QLabel),
                ("label_filament_details_title", QLabel),
                ("groupbox_search", QGroupBox),
                ("groupBox_action", QGroupBox),
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
                print(f"[FilamentSelectorDialogNew] Widgets faltantes en UI: {missing}")
        except Exception as e:
            print(f"[FilamentSelectorDialogNew] Error en _bind_widgets: {e}")
    
    def _setup_dialog(self):
        """Configuración inicial del diálogo"""
        self.setWindowTitle(tr(I18N.Filament.SELECTOR_TITLE))
        self.setModal(True)
        self.setFixedSize(820, 547)

        # Traducir textos definidos en el .ui
        try:
            self.ui.label_headboard.setText(tr(I18N.Filament.SELECTOR_LABEL_HEADBOARD))
        except Exception:
            pass
        try:
            self.ui.btn_add_filament.setText(tr(I18N.Filament.SELECTOR_BTN_ADD_LABEL))
        except Exception:
            pass
        try:
            self.ui.groupbox_search.setTitle(tr(I18N.CustomerSelector.GROUP_SEARCH))
        except Exception:
            pass
        try:
            self.ui.btn_search.setText(tr(I18N.CustomerSelector.BTN_QUERY))
            self.ui.linedit_search.setToolTip(tr(I18N.Filament.SELECTOR_TOOLTIP_SEARCH))
        except Exception:
            pass
        try:
            self.ui.groupBox_action.setTitle(tr(I18N.CustomerSelector.GROUP_ACTION))
        except Exception:
            pass
        try:
            self.ui.btn_ok_select.setText(tr(I18N.CustomerSelector.BTN_SELECT))
            self.ui.btn_ok_select.setToolTip(tr(I18N.Filament.SELECTOR_TOOLTIP_OK))
        except Exception:
            pass
        try:
            self.ui.btn_cancel_select.setText(tr(I18N.CustomerSelector.BTN_CANCEL))
            self.ui.btn_cancel_select.setToolTip(tr(I18N.Filament.SELECTOR_TOOLTIP_CANCEL))
        except Exception:
            pass
        try:
            self.ui.label_filament_details_title.setText(tr(I18N.Filament.SELECTOR_LABEL_DETAILS_TITLE))
        except Exception:
            pass

        # Configurar iconos
        self._setup_icons()
    
    def _setup_icons(self):
        """Configura los iconos de los botones"""
        try:
            # Icono de refresh (ya está configurado en el UI)
            self.ui.btn_refresh_panel.setIconSize(QSize(18, 18))
            self.ui.btn_refresh_panel.setToolTip(tr(I18N.Filament.SELECTOR_TOOLTIP_REFRESH))
            
            # Icono de agregar (ya está configurado en el UI)
            self.ui.btn_add_filament.setIconSize(QSize(20, 20))
            self.ui.btn_add_filament.setToolTip(tr(I18N.Filament.SELECTOR_TOOLTIP_ADD))
            
        except Exception as e:
            print(f"Error configurando iconos: {e}")
    
    def _setup_table(self):
        """Configuración de la tabla de filamentos"""
        table = self.ui.qtable_filament
        
        # Configurar encabezados
        headers = [
            tr(I18N.Filament.SELECTOR_TABLE_COL_ID),
            tr(I18N.Filament.SELECTOR_TABLE_COL_DESC),
            tr(I18N.Filament.SELECTOR_TABLE_COL_TYPE),
            tr(I18N.Filament.SELECTOR_TABLE_COL_BRAND),
            tr(I18N.Filament.SELECTOR_TABLE_COL_COLOR),
            tr(I18N.Filament.SELECTOR_TABLE_COL_STATUS),
        ]
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
        header = self.ui.qtable_filament.horizontalHeader()
        
        # Configuración de columnas: (columna, modo, tamaño_fijo)
        column_configs = [
            (0, QHeaderView.ResizeMode.ResizeToContents, 0),     # ID (oculta)
            (1, QHeaderView.ResizeMode.ResizeToContents, 200),   # Descripción
            (2, QHeaderView.ResizeMode.Stretch, 100),            # Tipo
            (3, QHeaderView.ResizeMode.Stretch, 120),            # Marca
            (4, QHeaderView.ResizeMode.Stretch, 100),            # Color
            (5, QHeaderView.ResizeMode.ResizeToContents, 90)     # Status
        ]
        
        for column, mode, fixed_size in column_configs:
            header.setSectionResizeMode(column, mode)
            if fixed_size:
                header.resizeSection(column, fixed_size)
    
    def _setup_connections(self):
        """Configura las conexiones de señales"""
        # Conexiones de botones
        self.ui.btn_refresh_panel.clicked.connect(self._on_refresh_clicked)
        self.ui.btn_add_filament.clicked.connect(self._on_add_filament_clicked)
        self.ui.btn_search.clicked.connect(self._on_search_clicked)
        
        # Conexiones de la tabla
        self.ui.qtable_filament.itemSelectionChanged.connect(self._on_selection_changed)
        self.ui.qtable_filament.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Conexiones del campo de búsqueda - SOLO botón (no textChanged automático)
        # Instalar event filter personalizado para manejar Enter correctamente
        self.ui.linedit_search.installEventFilter(self)
        
        # Conexiones de botones de acción (IDs actualizados en UI)
        self.ui.btn_ok_select.clicked.connect(self._on_select_clicked)
        self.ui.btn_cancel_select.clicked.connect(self._on_cancel_clicked)

    def _setup_styles(self):
        """Configuración adicional de estilos y estado inicial"""
        # Placeholder del buscador
        try:
            self.ui.linedit_search.setPlaceholderText(
                tr(I18N.Filament.SELECTOR_SEARCH_PLACEHOLDER)
            )
        except Exception:
            pass

        # Estado inicial de detalles y botones
        self._clear_filament_details()
    
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
    
    def populate_table(self, filaments_data: List[Dict[str, Any]]):
        """Puebla la tabla con datos de filamentos"""
        table = self.ui.qtable_filament
        
        try:
            table.clearContents()
            table.setRowCount(len(filaments_data))
            
            for row, filament in enumerate(filaments_data):
                # ID
                id_item = QTableWidgetItem(str(filament.get('id', '')))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 0, id_item)
                
                # Descripción
                description = filament.get('description', '') or tr(I18N.Filament.DEFAULT_NO_NAME)
                desc_item = QTableWidgetItem(description)
                desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 1, desc_item)
                
                # Tipo
                material_type = filament.get('material_type', '') or tr(I18N.Filament.DEFAULT_NOT_SPECIFIED)
                type_item = QTableWidgetItem(material_type)
                type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 2, type_item)
                
                # Marca
                brand = filament.get('brand', '') or tr(I18N.Filament.DEFAULT_NOT_SPECIFIED)
                brand_item = QTableWidgetItem(brand)
                brand_item.setFlags(brand_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 3, brand_item)
                
                # Color
                color = filament.get('color', '') or tr(I18N.Filament.DEFAULT_NOT_SPECIFIED)
                color_item = QTableWidgetItem(color)
                color_item.setFlags(color_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 4, color_item)
                
                # Status
                status = tr(I18N.Filament.DETAIL_ACTIVE) if filament.get('is_active', True) else tr(I18N.Filament.DETAIL_INACTIVE)
                status_item = QTableWidgetItem(status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 5, status_item)
                
                # Almacenar datos completos en la fila para recuperación
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item:
                        item.setData(Qt.ItemDataRole.UserRole, filament)
            
            # Limpiar selección
            self._clear_filament_details()
            
        except Exception as e:
            self.show_error_message(tr(I18N.Filament.SELECTOR_ERROR_LOADING_FMT).format(error=e))
    
    def show_loading(self, message: str):
        """Muestra indicador de carga"""
        self.ui.label_select.setText(tr(I18N.Filament.SELECTOR_LOADING_FMT).format(message=message))
        self.ui.btn_ok_select.setEnabled(False)
        self.ui.qtable_filament.setEnabled(False)
    
    def hide_loading(self):
        """Oculta indicador de carga"""
        self.ui.qtable_filament.setEnabled(True)
        if not self.current_selection:
            self.ui.label_select.setText(tr(I18N.Filament.MSG_NONE_SELECTED))
            self.ui.btn_ok_select.setEnabled(False)
    
    def show_no_results(self, message: str):
        """Muestra mensaje cuando no hay resultados"""
        self.ui.qtable_filament.clearContents()
        self.ui.qtable_filament.setRowCount(0)
        # Limpiar detalles sin sobrescribir el mensaje
        self.current_selection = None
        self.ui.label_filament_stock.setText(tr(I18N.Filament.LABEL_STOCK_NOT_SELECTED))
        self.ui.label_filament_price.setText(tr(I18N.Filament.LABEL_PRICE_NOT_SELECTED))
        self.ui.textEdit_details_filament.setHtml(tr(I18N.Filament.MSG_SELECT_TO_VIEW_SELECTOR))
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
    
    def set_selected_filament_info(self, filament_data: Dict[str, Any]):
        """Actualiza la información del filamento seleccionado"""
        try:
            self.current_selection = filament_data

            # Actualizar label de selección
            name = filament_data.get('description', 'Sin nombre')
            self.ui.label_select.setText(tr(I18N.Filament.LABEL_SELECTED_FMT).format(name=name))

            # Actualizar detalles en el TextEdit
            self._update_filament_details(filament_data)

            # Actualizar labels de stock y precio
            self._update_stock_and_price_labels(filament_data)

            # Habilitar botón de selección
            self.ui.btn_ok_select.setEnabled(True)

        except Exception as e:
            pass
    
    def _update_filament_details(self, filament_data: Dict[str, Any]):
        """Actualiza el TextEdit con detalles completos del filamento"""
        try:
            details = []

            # Obtener la moneda del filamento
            filament_currency = filament_data.get('currency_code', 'PYG')

            # Información básica
            details.append(tr(I18N.Filament.GROUP_BASIC_INFO).upper())
            details.append("")
            details.append(f"**{tr(I18N.Filament.LABEL_NAME_DETAIL)}** {filament_data.get('description', 'N/A')}")
            details.append(f"**{tr(I18N.Filament.LABEL_TYPE_MATERIAL)}** {filament_data.get('material_type', 'N/A')}")
            details.append(f"**{tr(I18N.Filament.LABEL_BRAND)}** {filament_data.get('brand', 'N/A')}")
            details.append(f"**{tr(I18N.Filament.LABEL_COLOR)}** {filament_data.get('color', 'N/A')}")
            details.append("")

            # Información de stock
            details.append(tr(I18N.Filament.GROUP_INVENTORY).upper())
            details.append("")
            stock_kg = filament_data.get('stock_kg', 0)
            details.append(f"**{tr(I18N.Filament.LABEL_STOCK_AVAILABLE)}** {stock_kg:.2f} kg")

            quantity_rolls = filament_data.get('quantity_rolls', 0)
            details.append(f"**{tr(I18N.Filament.LABEL_ROLL_COUNT)}** {quantity_rolls}")

            # Calcular promedio por rollo si hay datos
            if quantity_rolls > 0 and stock_kg > 0:
                avg_per_roll = stock_kg / quantity_rolls
                details.append(f"**{tr(I18N.Filament.LABEL_AVG_PER_ROLL)}** {avg_per_roll:.2f} kg")
            details.append("")

            # Información de precios
            details.append(tr(I18N.Filament.GROUP_PRICING).upper())
            details.append("")
            price_per_kg = filament_data.get('price_per_kg', 0)
            formatted_price_kg = CurrencyHelper.format(price_per_kg or 0, filament_currency)
            details.append(f"**{tr(I18N.Filament.LABEL_PRICE_PER_KG)}** {formatted_price_kg}")

            if stock_kg > 0:
                total_value = (price_per_kg or 0) * (stock_kg or 0)
                formatted_total = CurrencyHelper.format(total_value, filament_currency)
                details.append(f"**{tr(I18N.Filament.LABEL_TOTAL_VALUE)}** {formatted_total}")

            # Precio por gramo para cálculos detallados
            price_per_gram = (price_per_kg / 1000) if (price_per_kg and price_per_kg > 0) else 0
            formatted_price_gram = CurrencyHelper.format(price_per_gram, filament_currency)
            details.append(f"**{tr(I18N.Filament.LABEL_PRICE_PER_GRAM)}** {formatted_price_gram}")
            details.append("")

            # Estado y notas
            details.append(tr(I18N.Filament.DETAIL_SECTION_STATUS))
            details.append("")
            is_active = filament_data.get('is_active', True)
            status = tr(I18N.Filament.DETAIL_ACTIVE_AVAILABLE) if is_active else tr(I18N.Filament.DETAIL_INACTIVE)
            details.append(f"**{tr(I18N.Filament.LABEL_STATUS_DETAIL)}** {status}")

            notes = filament_data.get('notes', '')
            if notes:
                details.append("")
                details.append(tr(I18N.Filament.DETAIL_SECTION_NOTES))
                details.append("")
                details.append(notes)

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

            self.ui.textEdit_details_filament.setHtml(html_text)

        except Exception as e:
            self.ui.textEdit_details_filament.setHtml(f"{tr(I18N.Filament.MSG_ERROR_LOADING_DETAILS)}: {e}")
    
    def _update_stock_and_price_labels(self, filament_data: Dict[str, Any]):
        """Actualiza los labels de stock y precio"""
        try:
            # Label de stock
            stock_kg = filament_data.get('stock_kg', 0)
            quantity_rolls = filament_data.get('quantity_rolls', 0)

            if stock_kg > 0:
                stock_text = tr(I18N.Filament.SELECTOR_STOCK_FMT).format(
                    stock_kg=f"{stock_kg:.2f}", rolls=quantity_rolls
                )
                # Indicador de nivel
                if stock_kg < 1.0:
                    stock_text += f" {tr(I18N.Filament.DETAIL_STOCK_TAG_LOW)}"
                elif stock_kg < 3.0:
                    stock_text += f" {tr(I18N.Filament.DETAIL_STOCK_TAG_MEDIUM)}"
                else:
                    stock_text += f" {tr(I18N.Filament.DETAIL_STOCK_TAG_HIGH)}"
            else:
                stock_text = tr(I18N.Filament.SELECTOR_STOCK_NONE)

            self.ui.label_filament_stock.setText(stock_text)

            # Label de precio
            price_per_kg = filament_data.get('price_per_kg', 0)
            if price_per_kg > 0:
                filament_currency = filament_data.get('currency_code', 'PYG')
                symbol = CurrencyHelper.get_symbol(filament_currency)
                formatted_price = CurrencyHelper.format(price_per_kg, filament_currency, include_symbol=False)
                price_text = tr(I18N.Filament.SELECTOR_PRICE_FMT).format(
                    symbol=symbol, price=formatted_price
                )
                # Clasificación simple según rangos típicos en Gs.
                if price_per_kg < 160000:
                    price_text += f" {tr(I18N.Filament.DETAIL_PRICE_TAG_ECONOMIC)}"
                elif price_per_kg <= 200000:
                    price_text += f" {tr(I18N.Filament.DETAIL_PRICE_TAG_MODERATE)}"
                else:
                    price_text += f" {tr(I18N.Filament.DETAIL_PRICE_TAG_PREMIUM)}"
            else:
                price_text = tr(I18N.Filament.SELECTOR_PRICE_NONE)

            self.ui.label_filament_price.setText(price_text)

        except Exception as e:
            pass
    
    def _clear_filament_details(self):
        """Limpia los detalles del filamento"""
        self.current_selection = None
        self.ui.label_select.setText(tr(I18N.Filament.MSG_NONE_SELECTED))
        self.ui.label_filament_stock.setText(tr(I18N.Filament.LABEL_STOCK_NOT_SELECTED))
        self.ui.label_filament_price.setText(tr(I18N.Filament.LABEL_PRICE_NOT_SELECTED))
        self.ui.textEdit_details_filament.setHtml(tr(I18N.Filament.MSG_SELECT_TO_VIEW_SELECTOR))
        self.ui.btn_ok_select.setEnabled(False)
    
    # === MANEJADORES DE EVENTOS ===
    
    def _on_refresh_clicked(self):
        """Maneja clic en botón de actualizar"""
        self.refresh_requested.emit()
    
    def _on_add_filament_clicked(self):
        """Maneja clic en botón de agregar filamento"""
        self.add_filament_requested.emit()
    
    def _on_search_clicked(self):
        """Maneja clic en botón de búsqueda"""
        search_text = self.get_search_text()
        self.search_requested.emit(search_text)
    
    def _on_selection_changed(self):
        """Maneja cambio de selección en la tabla"""
        table = self.ui.qtable_filament
        selected_items = table.selectedItems()
        
        if selected_items:
            # Obtener datos del primer item seleccionado
            first_item = selected_items[0]
            filament_data = first_item.data(Qt.ItemDataRole.UserRole)
            
            if filament_data:
                self.set_selected_filament_info(filament_data)
        else:
            self._clear_filament_details()
    
    def _on_item_double_clicked(self, item):
        """Maneja doble clic en item de la tabla"""
        filament_data = item.data(Qt.ItemDataRole.UserRole)
        if filament_data:
            self.filament_selected.emit(filament_data)
            self.accept()
    
    def _on_select_clicked(self):
        """Maneja clic en botón de seleccionar"""
        if self.current_selection:
            self.filament_selected.emit(self.current_selection)
            self.accept()
        else:
            self.show_warning_message(
                tr(I18N.Filament.SELECTOR_WARN_SELECTION_TITLE),
                tr(I18N.Filament.SELECTOR_WARN_SELECTION_MSG)
            )
    
    def _on_cancel_clicked(self):
        """Maneja clic en botón de cancelar"""
        self.reject()
    
    # === MÉTODOS DE MENSAJES ===
    
    def show_success_message(self, message: str):
        """Muestra mensaje de éxito"""
        QMessageBox.information(self, tr(I18N.Filament.SELECTOR_MSG_SUCCESS_TITLE), message)
    
    def show_error_message(self, message: str):
        """Muestra mensaje de error"""
        QMessageBox.critical(self, tr(I18N.Filament.SELECTOR_MSG_ERROR_TITLE), message)
    
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
    
    def get_selected_filament(self) -> Optional[Dict[str, Any]]:
        """Retorna el filamento seleccionado"""
        return self.current_selection
