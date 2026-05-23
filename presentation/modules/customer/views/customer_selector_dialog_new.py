"""
Vista del selector de clientes usando el UI existente
Implementa el patrón MVP con la interfaz generada
"""

from PySide6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtCore import QSize, QTimer, Signal, Qt, QEvent
from PySide6.QtGui import QIcon, QKeyEvent
from typing import List, Dict, Any, Optional

from presentation.modules.customer.designs.select_customers_ui import Ui_Temp_Select_Customers
from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from core.managers.locale_manager import LocaleManager


class CustomerSelectorDialogNew(QDialog):
    """
    Diálogo para selección de clientes usando el UI generado
    Solo maneja la interfaz de usuario, la lógica está en el presenter
    """    
    # Señales emitidas hacia el presenter
    search_requested = Signal(str)
    refresh_requested = Signal()
    customer_selected = Signal(dict)
    add_customer_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_Temp_Select_Customers()
        self.ui.setupUi(self)

        # Vincula/recupera widgets por objectName para tolerar renombres en el UI
        self._bind_widgets()

        # Propiedades básicas de la ventana
        self.setWindowTitle("Seleccionar Cliente")
        self.setFixedSize(self.width(), self.height())

        # Configuración inicial
        self._setup_dialog()
        self._setup_table()
        self._setup_connections()
        self._setup_styles()

        # Estado interno de la vista
        self.current_selection = None

        # Aplicar etiquetas i18n (sobreescribe retranslateUi)
        self._apply_dynamic_labels()

    def _bind_widgets(self):
        """Intenta asegurar que los atributos requeridos existan en self.ui.
        Si el UI generado cambia nombres, buscamos por objectName y reasignamos.
        """
        try:
            from PySide6.QtWidgets import QPushButton, QTableWidget, QLineEdit, QLabel, QTextEdit
            required: list[tuple[str, type]] = [
                ("btn_ok_select", QPushButton),
                ("btn_cancel_select", QPushButton),
                ("qtable_customers", QTableWidget),  # Nombre correcto del UI
                ("linedit_search", QLineEdit),
                ("btn_search", QPushButton),
                ("btn_refresh_panel", QPushButton),
                ("btn_add_customer", QPushButton),
                ("label_select", QLabel),
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
                print(f"[CustomerSelectorDialogNew] Widgets faltantes en UI: {missing}")
        except Exception as e:
            print(f"[CustomerSelectorDialogNew] Error en _bind_widgets: {e}")
    
    def _setup_dialog(self):
        """Configuración inicial del diálogo"""
        self.setWindowTitle(tr(I18N.CustomerSelector.TITLE))
        self.setModal(True)
        self.setFixedSize(670, 534)
        
        # Configurar iconos
        self._setup_icons()

    def _apply_dynamic_labels(self):
        """Sobreescribe strings de retranslateUi con los del sistema i18n."""
        try:
            ui = self.ui
            self.setWindowTitle(tr(I18N.CustomerSelector.TITLE))
            ui.label_headboard.setText(tr(I18N.CustomerSelector.TITLE))
            ui.btn_add_customer.setText(tr(I18N.CustomerSelector.BTN_ADD))
            ui.groupbox_search.setTitle(tr(I18N.CustomerSelector.GROUP_SEARCH))
            ui.linedit_search.setToolTip(tr(I18N.CustomerSelector.TOOLTIP_SEARCH))
            ui.btn_search.setText(tr(I18N.CustomerSelector.BTN_QUERY))
            ui.groupBox_action.setTitle(tr(I18N.CustomerSelector.GROUP_ACTION))
            ui.label_select.setText(tr(I18N.CustomerSelector.LABEL_NO_SELECTION))
            ui.btn_ok_select.setText(tr(I18N.CustomerSelector.BTN_SELECT))
            ui.btn_ok_select.setToolTip(tr(I18N.CustomerSelector.TOOLTIP_OK))
            ui.btn_cancel_select.setText(tr(I18N.CustomerSelector.BTN_CANCEL))
            ui.btn_cancel_select.setToolTip(tr(I18N.CustomerSelector.TOOLTIP_CANCEL))
            # Headers tabla
            ui.qtable_customers.horizontalHeaderItem(0).setText(tr(I18N.CustomerSelector.COL_ID))
            ui.qtable_customers.horizontalHeaderItem(1).setText(tr(I18N.CustomerSelector.COL_NAME))
            ui.qtable_customers.horizontalHeaderItem(2).setText(LocaleManager().get_tax_id_label())
            ui.qtable_customers.horizontalHeaderItem(3).setText(tr(I18N.CustomerSelector.COL_PHONE))
            ui.qtable_customers.horizontalHeaderItem(4).setText(tr(I18N.CustomerSelector.COL_EMAIL))
        except Exception as e:
            logger.error("CustomerSelectorDialogNew", f"Error en _apply_dynamic_labels: {str(e)}")
    
    def _setup_icons(self):
        """Configura los iconos de los botones"""
        try:
            # Icono de refresh (ya está configurado en el UI)
            self.ui.btn_refresh_panel.setIconSize(QSize(18, 18))
            self.ui.btn_refresh_panel.setToolTip(tr(I18N.CustomerSelector.TOOLTIP_REFRESH))
            
            # Icono de agregar (ya está configurado en el UI)
            self.ui.btn_add_customer.setIconSize(QSize(20, 20))
            self.ui.btn_add_customer.setToolTip(tr(I18N.CustomerSelector.BTN_ADD))
            
        except Exception as e:
            print(f"Error configurando iconos: {e}")
    
    def _setup_table(self):
        """Configuración de la tabla de clientes"""
        table = self.ui.qtable_customers  # Nombre correcto del UI
        
        # Configurar encabezados
        headers = ["ID", "Nombre / Razón Social", LocaleManager().get_tax_id_label(), "Teléfono", "Email"]
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
        header = self.ui.qtable_customers.horizontalHeader()  # Nombre correcto del UI
        
        # Configuración de columnas: (columna, modo, tamaño_fijo)
        column_configs = [
            (0, QHeaderView.ResizeMode.ResizeToContents, 0),     # ID (oculta)
            (1, QHeaderView.ResizeMode.Stretch, 200),            # Nombre / Razón Social
            (2, QHeaderView.ResizeMode.ResizeToContents, 120),   # C.I / RUC
            (3, QHeaderView.ResizeMode.ResizeToContents, 120),   # Teléfono
            (4, QHeaderView.ResizeMode.Stretch, 150)             # Email
        ]
        
        for column, mode, fixed_size in column_configs:
            header.setSectionResizeMode(column, mode)
            if fixed_size:
                header.resizeSection(column, fixed_size)
    
    def _setup_connections(self):
        """Configura las conexiones de señales"""
        # Conexiones de botones
        self.ui.btn_refresh_panel.clicked.connect(self._on_refresh_clicked)
        self.ui.btn_add_customer.clicked.connect(self._on_add_customer_clicked)
        self.ui.btn_search.clicked.connect(self._on_search_clicked)
        
        # Conexiones de la tabla
        self.ui.qtable_customers.itemSelectionChanged.connect(self._on_selection_changed)  # Nombre correcto
        self.ui.qtable_customers.itemDoubleClicked.connect(self._on_item_double_clicked)  # Nombre correcto
        
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
                tr(I18N.CustomerSelector.PLACEHOLDER_SEARCH)
            )
        except Exception:
            pass

        # Estado inicial de detalles y botones
        self._clear_customer_details()
    
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
    
    def populate_table(self, customers_data: List[Dict[str, Any]]):
        """Puebla la tabla con datos de clientes"""
        table = self.ui.qtable_customers  # Nombre correcto del UI
        
        try:
            table.clearContents()
            table.setRowCount(len(customers_data))
            
            for row, customer in enumerate(customers_data):
                # ID
                id_item = QTableWidgetItem(str(customer.get('id', '')))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 0, id_item)
                
                # Nombre / Razón Social
                full_name = customer.get('full_name', '') or 'Sin nombre'
                name_item = QTableWidgetItem(full_name)
                # Marcar clientes predeterminados con un indicador visual
                if customer.get('is_default', False):
                    name_item.setText(f"⭐ {name_item.text()}")
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 1, name_item)
                
                # C.I / RUC
                ruc_ci = customer.get('ruc_ci', '') or 'No especificado'
                ruc_ci_item = QTableWidgetItem(ruc_ci)
                ruc_ci_item.setFlags(ruc_ci_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 2, ruc_ci_item)
                
                # Teléfono
                phone = customer.get('phone_number', '') or 'No disponible'
                phone_item = QTableWidgetItem(phone)
                phone_item.setFlags(phone_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 3, phone_item)
                
                # Email
                email = customer.get('email', '') or 'No disponible'
                email_item = QTableWidgetItem(email)
                email_item.setFlags(email_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 4, email_item)
                
                # Almacenar datos completos en la fila para recuperación
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item:
                        item.setData(Qt.ItemDataRole.UserRole, customer)
            
            # Limpiar selección
            self._clear_customer_details()
            
        except Exception as e:
            logger.error("CustomerSelectorDialog", f"Error poblando tabla: {e}")
            self.show_error_message(f"Error cargando clientes: {e}")
    
    def show_loading(self, message: str):
        """Muestra indicador de carga"""
        self.ui.label_select.setText(tr(I18N.CustomerSelector.LABEL_LOADING).format(message=message))
        self.ui.btn_ok_select.setEnabled(False)
        self.ui.qtable_customers.setEnabled(False)  # Nombre correcto
    
    def hide_loading(self):
        """Oculta indicador de carga"""
        self.ui.qtable_customers.setEnabled(True)  # Nombre correcto
        if not self.current_selection:
            self.ui.label_select.setText(tr(I18N.CustomerSelector.LABEL_NO_SELECTION))
            self.ui.btn_ok_select.setEnabled(False)
    
    def show_no_results(self, message: str):
        """Muestra mensaje cuando no hay resultados"""
        self.ui.qtable_customers.clearContents()  # Nombre correcto
        self.ui.qtable_customers.setRowCount(0)   # Nombre correcto
        self.ui.label_select.setText(f"{message}")
        self._clear_customer_details()
    
    def focus_search(self):
        """Establece el foco en el campo de búsqueda"""
        self.ui.linedit_search.setFocus()
    
    def get_search_text(self) -> str:
        """Obtiene el texto de búsqueda actual"""
        return self.ui.linedit_search.text().strip()
    
    def clear_search_text(self):
        """Limpia el campo de búsqueda"""
        self.ui.linedit_search.clear()
    
    def set_selected_customer_info(self, customer_data: Dict[str, Any]):
        """Actualiza la información del cliente seleccionado"""
        try:
            self.current_selection = customer_data
            
            # Actualizar label de selección
            name = customer_data.get('full_name', '') or 'Sin nombre'
            # Agregar indicador si es cliente predeterminado
            if customer_data.get('is_default', False):
                name = tr(I18N.CustomerSelector.LABEL_SELECTED_DEFAULT).format(name=name)
            
            self.ui.label_select.setText(tr(I18N.CustomerSelector.LABEL_SELECTED).format(name=name))
            
            # Habilitar botón de selección
            self.ui.btn_ok_select.setEnabled(True)
            
        except Exception as e:
            print(f"Error actualizando información de cliente: {e}")
    
    def _clear_customer_details(self):
        """Limpia los detalles del cliente"""
        self.current_selection = None
        self.ui.label_select.setText(tr(I18N.CustomerSelector.LABEL_NO_SELECTION))
        self.ui.btn_ok_select.setEnabled(False)
    
    # === MANEJADORES DE EVENTOS ===
    
    def _on_refresh_clicked(self):
        """Maneja clic en botón de actualizar"""
        self.refresh_requested.emit()
    
    def _on_add_customer_clicked(self):
        """Maneja clic en botón de agregar cliente"""
        self.add_customer_requested.emit()
    
    def _on_search_clicked(self):
        """Maneja clic en botón de búsqueda"""
        search_text = self.get_search_text()
        self.search_requested.emit(search_text)
    
    def _on_selection_changed(self):
        """Maneja cambio de selección en la tabla"""
        table = self.ui.qtable_customers  # Nombre correcto
        selected_items = table.selectedItems()
        
        if selected_items:
            # Obtener datos del primer item seleccionado
            first_item = selected_items[0]
            customer_data = first_item.data(Qt.ItemDataRole.UserRole)
            
            if customer_data:
                self.set_selected_customer_info(customer_data)
        else:
            self._clear_customer_details()
    
    def _on_item_double_clicked(self, item):
        """Maneja doble clic en item de la tabla"""
        customer_data = item.data(Qt.ItemDataRole.UserRole)
        if customer_data:
            self.customer_selected.emit(customer_data)
            self.accept()
    
    def _on_select_clicked(self):
        """Maneja clic en botón de seleccionar"""
        if self.current_selection:
            self.customer_selected.emit(self.current_selection)
            self.accept()
        else:
            self.show_warning_message("Selección requerida", 
                                    "Por favor selecciona un cliente de la tabla.")
    
    def _on_cancel_clicked(self):
        """Maneja clic en botón de cancelar"""
        self.reject()
    
    # === MÉTODOS DE MENSAJES ===
    
    def show_success_message(self, message: str):
        """Muestra mensaje de éxito"""
        QMessageBox.information(self, "Operación Exitosa", message)
    
    def show_error_message(self, message: str):
        """Muestra mensaje de error"""
        QMessageBox.critical(self, "Error", message)
    
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
    
    def get_selected_customer(self) -> Optional[Dict[str, Any]]:
        """Retorna el cliente seleccionado"""
        return self.current_selection
