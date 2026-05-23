"""
Presenter para el tab de inventario de clientes en la ventana principal
Maneja la tabla de clientes, búsqueda, selección y operaciones CRUD
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTableWidgetItem, QMessageBox, QHeaderView
from PySide6.QtCore import Qt
from typing import List, Optional, Dict, Any

from domain.models.customer import Customer
from application.facades.voxeprint_facade import VoxeprintFacade
from presentation.modules.customer.views.add_customer_dialog import AddCustomerDialog
from presentation.modules.customer.views.edit_customer_dialog import EditCustomerDialog
from presentation.modules.customer.views.customer_details_dialog import CustomerDetailsDialog
from presentation.widgets.animation_mod.button_size_animator import ButtonSizeAnimator
from core.utils.logger import logger
from core.utils.translation_keys import I18N
from core.utils.translation_helper import tr
from core.managers.locale_manager import LocaleManager


class CustomerInventoryPresenter(QObject):
    """Presenter para gestionar el inventario de clientes"""
    
    # Señales
    customer_selected = Signal(dict)  # Cuando se selecciona un cliente
    customer_modified = Signal(dict)  # Cuando se modifica un cliente  
    customer_deleted = Signal(int)    # Cuando se elimina un cliente
    
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        self.ui = main_view.ui
        
        # Facade para operaciones de negocio (inyección de dependencias)
        self.facade: Optional[VoxeprintFacade] = None
        
        # Estado
        self.all_customers: List[Customer] = []
        self.filtered_customers: List[Customer] = []
        self.selected_customer: Optional[Customer] = None
        
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
        self.load_customers()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar tabla
        table = self.ui.qtable_customers

        # Configurar cabeceras
        locale_mgr = LocaleManager()
        headers = [
            "ID",
            tr(I18N.MainWindow.COL_SOCIAL_REASON),
            locale_mgr.get_tax_id_label(),
            tr(I18N.MainWindow.COL_EMAIL),
            tr(I18N.MainWindow.COL_PHONE),
            tr(I18N.MainWindow.COL_PREFERENCE),
        ]
        table.setHorizontalHeaderLabels(headers)

        # Ocultar columna ID
        table.setColumnHidden(0, True)
        
        # Configurar anchos de columnas
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Razón Social
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # RUC/CI
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Teléfono
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        
        # Configurar selección
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.SingleSelection)
        
        # Configurar ordenamiento
        table.setSortingEnabled(True)
        
        # Configurar textEdit inicial
        self.ui.textEdit_details_customer.setHtml(
            tr(I18N.Customer.DETAILS_NO_SELECTION)
        )
        
        # Configurar estado inicial de botones
        self._update_button_states(False)
    
    def _connect_signals(self):
        """Conecta las señales de la UI"""
        # Señales de la tabla
        self.ui.qtable_customers.itemSelectionChanged.connect(self._on_selection_changed)
        self.ui.qtable_customers.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Señales del buscador
        self.ui.btn_search_3.clicked.connect(self._on_search_clicked)
        self.ui.linedit_search_3.returnPressed.connect(self._on_search_clicked)
        
        # Señales de botones de operaciones
        self.ui.btn_mod_customer.clicked.connect(self._on_modify_clicked)
        self.ui.btn_delete_customer.clicked.connect(self._on_delete_clicked)
        self.ui.btn_add_customer.clicked.connect(self._on_add_clicked)
        self.ui.btn_default_customer.clicked.connect(self._on_default_clicked)
        
        # Señal del botón cleaner
        self.ui.btn_cleaner_3.clicked.connect(self._handle_clear_search)
    
    def _setup_button_animations(self):
        """Configura las animaciones de los botones de búsqueda"""
        try:
            # Crear animador para el par btn_search_3/btn_cleaner_3 (clientes)
            self.button_animator = ButtonSizeAnimator(
                primary_button=self.ui.btn_search_3,
                secondary_button=self.ui.btn_cleaner_3
            )
            
            logger.debug("CustomerInventory", "Animaciones de botones configuradas", 
                            botones="btn_search_3/btn_cleaner_3")
            
        except Exception as e:
            logger.error("CustomerInventory", "Error configurando animaciones de botones", error=str(e))
    
    def _handle_clear_search(self):
        """Maneja la limpieza de campos de búsqueda en clientes"""
        try:
            # Limpiar campo de búsqueda
            self.ui.linedit_search_3.clear()
            
            # Restablecer filtros (mostrar todos los clientes)
            self.filtered_customers = self.all_customers.copy()
            self._update_table()
            self._update_status_label()
            
            # Actualizar mensaje de estado
            self._update_status_message(f"Campos limpiados - Mostrando {len(self.all_customers)} clientes")
            
            logger.info("CustomerInventoryPresenter", f"Limpieza de campos completada - {len(self.all_customers)} clientes mostrados")
            
        except Exception as e:
            print(f"❌ Error en limpieza de campos de clientes: {e}")
            self._update_status_message("❌ Error al limpiar campos")
    
    def load_customers(self):
        """Carga los clientes desde la base de datos ordenados por ID"""
        try:
            if self.facade:
                # Usar facade en lugar de repositorio directo
                response = self.facade.search_customers()
                if response.success:
                    self.all_customers = response.data or []
                    # Ordenar por ID de menor a mayor
                    self.all_customers.sort(key=lambda customer: customer.id if customer.id is not None else 0)
                    self.filtered_customers = self.all_customers.copy()
                    
                    logger.debug("CustomerInventory", "Clientes cargados para inventario", 
                                   cantidad=len(self.all_customers))
                    self._update_table()
                    self._update_status_label()
                    self._update_status_message(f"Cargados {len(self.all_customers)} clientes")
                else:
                    logger.error("CustomerInventory", "Error desde facade", mensaje=response.message)
                    self._update_status_message(f"❌ Error: {response.message}")
            else:
                self._update_status_message("❌ Error: No hay conexión al facade")
                
        except Exception as e:
            print(f"❌ Error cargando clientes: {e}")
            self._update_status_message(f"❌ Error cargando clientes: {str(e)}")
            QMessageBox.critical(
                self.main_view,
                "Error",
                f"Error al cargar clientes desde la base de datos:\n{str(e)}"
            )
    
    def _update_table(self):
        """Actualiza la tabla con los clientes filtrados"""
        table = self.ui.qtable_customers
        table.setRowCount(len(self.filtered_customers))
        
        for row, customer in enumerate(self.filtered_customers):
            # ID (oculto)
            table.setItem(row, 0, QTableWidgetItem(str(customer.id or "")))
            
            # Razón Social
            name_item = QTableWidgetItem(customer.full_name or "")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 1, name_item)
            
            # RUC/CI
            ruc_item = QTableWidgetItem(customer.ruc_ci or "")
            ruc_item.setFlags(ruc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 2, ruc_item)
            
            # Email
            email_item = QTableWidgetItem(customer.email or "")
            email_item.setFlags(email_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 3, email_item)
            
            # Teléfono
            phone_item = QTableWidgetItem(customer.phone_number or "")
            phone_item.setFlags(phone_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 4, phone_item)
            
            # Estado
            status = tr(I18N.Customer.TABLE_STATUS_DEFAULT) if customer.is_default else tr(I18N.Customer.TABLE_STATUS_NORMAL)
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if customer.is_default:
                status_item.setBackground(Qt.GlobalColor.lightGray)
            table.setItem(row, 5, status_item)
        
        # Limpiar selección anterior
        table.clearSelection()  # Limpiar selección visual
        self.selected_customer = None
        self._update_button_states(False)
        self._update_details_text("")
    
    def _update_status_message(self, message: str):
        """Actualiza el mensaje de estado - ahora usa logging centralizado"""
        try:
            # Log internal del inventario sin mostrar en UI
            logger.debug("CustomerInventory", message)
        except Exception as e:
            logger.error("CustomerInventory", "Error actualizando mensaje de estado", error=str(e))
    
    def _update_status_label(self):
        """Actualiza la etiqueta de estado"""
        total = len(self.all_customers)
        filtered = len(self.filtered_customers)
        
        if total == filtered:
            status_text = tr(I18N.Customer.COUNT_ALL, total=total)
        else:
            status_text = tr(I18N.Customer.COUNT_FILTERED, filtered=filtered, total=total)
        
        # Actualizar label si existe en la UI
        if hasattr(self.ui, 'label_customer_count'):
            self.ui.label_customer_count.setText(status_text)
    
    def _on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        table = self.ui.qtable_customers
        current_row = table.currentRow()
        
        if 0 <= current_row < len(self.filtered_customers):
            self.selected_customer = self.filtered_customers[current_row]
            self._update_button_states(True)
            self._update_details_text(self._get_customer_details())
            
            # Emitir señal de selección
            customer_data = self._customer_to_dict(self.selected_customer)
            self.customer_selected.emit(customer_data)
            
            self._update_status_message("Cliente seleccionado")
        else:
            self.selected_customer = None
            self._update_button_states(False)
            self._update_details_text("")
    
    def _update_button_states(self, has_selection: bool):
        """Actualiza el estado de los botones según la selección"""
        self.ui.btn_default_customer.setEnabled(has_selection)
    
    def _update_details_text(self, details: str):
        """Actualiza el texto de detalles"""
        if not details:
            details = tr(I18N.Customer.DETAILS_NO_SELECTION)
        
        # Convertir formato **negrita** a HTML
        html_details = details.replace("**", "<b>", 1)
        while "**" in html_details:
            html_details = html_details.replace("**", "</b>", 1)
            if "**" in html_details:
                html_details = html_details.replace("**", "<b>", 1)
        
        # Reemplazar saltos de línea con <br>
        html_details = html_details.replace("\n", "<br>")
        
        self.ui.textEdit_details_customer.setHtml(html_details)
    
    def _get_customer_details(self) -> str:
        """Genera el texto de detalles del cliente seleccionado"""
        if not self.selected_customer:
            return ""
        
        customer = self.selected_customer
        locale_mgr = LocaleManager()
        not_spec = tr(I18N.Customer.DEFAULT_NOT_SPECIFIED)
        
        details = [
            tr(I18N.Customer.DETAILS_TITLE),
            "",
            f"**{tr(I18N.Customer.LABEL_FULL_NAME).rstrip(':')}:** {customer.full_name}",
            f"**{locale_mgr.get_tax_id_label().rstrip(':')}:** {customer.ruc_ci or not_spec}",
            f"**{tr(I18N.Customer.LABEL_EMAIL).rstrip(':')}:** {customer.email or not_spec}",
            f"**{tr(I18N.Customer.LABEL_PHONE).rstrip(':')}:** {customer.phone_number or not_spec}",
            "",
            f"**{tr(I18N.Customer.LABEL_STATUS).rstrip(':')}:** {tr(I18N.Customer.DETAILS_STATUS_DEFAULT) if customer.is_default else tr(I18N.Customer.DETAILS_STATUS_NORMAL)}",
        ]
        
        # Agregar contacto principal solo si existe
        contact_info = []
        if customer.phone_number:
            contact_info.append(f"{tr(I18N.Customer.LABEL_PHONE)} {customer.phone_number}")
        if customer.email:
            contact_info.append(f"{tr(I18N.Customer.LABEL_EMAIL)} {customer.email}")
        
        if contact_info:
            details.extend([
                "",
                tr(I18N.Customer.DETAILS_CONTACT_SECTION),
                *[f"  {info}" for info in contact_info]
            ])
        
        if customer.created_at:
            details.extend([
                "",
                f"{tr(I18N.Customer.LABEL_REGISTRATION_DATE)} {customer.created_at}"
            ])
        
        return "\n".join(details)
    
    def _customer_to_dict(self, customer: Customer) -> Dict[str, Any]:
        """Convierte un cliente a diccionario para las señales"""
        return {
            'id': customer.id,
            'full_name': customer.full_name,
            'ruc_ci': customer.ruc_ci,
            'email': customer.email,
            'phone_number': customer.phone_number,
            'is_default': customer.is_default
        }
    
    def _on_search_clicked(self):
        """Maneja la búsqueda de clientes"""
        search_text = self.ui.linedit_search_3.text().strip()
        
        if not search_text:
            # Sin filtro, mostrar todos (ya ordenados por ID)
            self.filtered_customers = self.all_customers.copy()
        else:
            # Buscar en nombre, RUC/CI, email y teléfono
            search_lower = search_text.lower()
            self.filtered_customers = [
                customer for customer in self.all_customers
                if (search_lower in (customer.full_name or "").lower() or
                    search_lower in (customer.ruc_ci or "").lower() or
                    search_lower in (customer.email or "").lower() or
                    search_lower in (customer.phone_number or "").lower())
            ]
            # Mantener orden por ID en los resultados filtrados
            self.filtered_customers.sort(key=lambda customer: customer.id if customer.id is not None else 0)
        
        self._update_table()
        self._update_status_label()
        
        logger.debug("CustomerInventory", f"Búsqueda '{search_text}': {len(self.filtered_customers)} resultados")
    
    def _on_item_double_clicked(self):
        """Maneja el doble clic en un item - muestra detalles"""
        if not self.selected_customer:
            return
        
        try:
            # Mostrar diálogo de detalles
            dialog = CustomerDetailsDialog(self.main_view, self.selected_customer)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self.main_view,
                "Error",
                f"Error al mostrar detalles: {str(e)}"
            )
    
    def _on_add_clicked(self):
        """Maneja el evento de agregar cliente"""
        try:
            # Crear el diálogo
            dialog = AddCustomerDialog(self.main_view)
            
            # Conectar la señal para manejar cuando se agrega un cliente
            def on_customer_added(customer_data):
                logger.info("CustomerInventoryPresenter", f"Cliente agregado: {customer_data['full_name']}")
                # Recargar la lista
                self.load_customers()
            
            dialog.customer_added.connect(on_customer_added)
            
            # Mostrar el diálogo
            dialog.exec()
            
        except Exception as e:
            print(f"❌ Error agregando cliente: {e}")
            QMessageBox.critical(
                self.main_view,
                "Error",
                f"Error al agregar cliente:\n{str(e)}"
            )
    
    def _on_modify_clicked(self):
        """Maneja el evento de modificar cliente"""
        if not self.selected_customer:
            QMessageBox.warning(
                self.main_view,
                tr(I18N.Customer.MSG_SELECTION_REQUIRED),
                tr(I18N.Customer.MSG_SELECT_TO_MODIFY)
            )
            return
        
        try:
            # Crear el diálogo
            dialog = EditCustomerDialog(self.main_view, self.selected_customer)
            
            # Conectar la señal para manejar cuando se guarda un cliente
            def on_customer_saved(customer_data):
                logger.info("CustomerInventoryPresenter", f"Cliente modificado: {customer_data['full_name']}")
                
                # Emitir señal de modificación
                self.customer_modified.emit(customer_data)
                
                # Recargar la lista
                self.load_customers()
                
                self._update_status_message("Cliente modificado exitosamente")
            
            dialog.customer_saved.connect(on_customer_saved)
            
            # Mostrar el diálogo
            dialog.exec()
            
        except Exception as e:
            print(f"❌ Error modificando cliente: {e}")
            QMessageBox.critical(
                self.main_view,
                "Error", 
                f"Error al modificar cliente:\n{str(e)}"
            )
    
    def _on_delete_clicked(self):
        """Maneja el evento de eliminar cliente"""
        if not self.selected_customer:
            QMessageBox.warning(
                self.main_view,
                tr(I18N.Customer.MSG_SELECTION_REQUIRED),
                tr(I18N.Customer.MSG_SELECT_TO_DELETE)
            )
            return
        
        customer = self.selected_customer
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self.main_view,
            tr(I18N.Customer.MSG_CONFIRM_DELETE_TITLE),
            tr(
                I18N.Customer.MSG_CONFIRM_DELETE_TEXT,
                name=customer.full_name,
                tax_id_label=LocaleManager().get_tax_id_label().rstrip(':'),
                tax_id=customer.ruc_ci or tr(I18N.Customer.DEFAULT_NOT_SPECIFIED)
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Verificar si es cliente predeterminado
                if customer.is_default:
                    QMessageBox.warning(
                        self.main_view,
                        tr(I18N.Customer.MSG_CANNOT_DELETE_DEFAULT_TITLE),
                        tr(I18N.Customer.MSG_CANNOT_DELETE_DEFAULT)
                    )
                    return
                
                # Eliminar cliente usando el facade
                if self.facade:
                    response = self.facade.delete_customer(customer.id)
                    if response.success:
                        logger.info("CustomerInventoryPresenter", f"Cliente eliminado: {customer.full_name}")
                        
                        # Emitir señal
                        self.customer_deleted.emit(customer.id)
                        
                        # Recargar la lista
                        self.load_customers()
                        
                        QMessageBox.information(
                            self.main_view,
                            tr(I18N.Customer.MSG_DELETED_TITLE),
                            tr(I18N.Customer.MSG_DELETED_DETAIL, name=customer.full_name)
                        )
                        
                        self._update_status_message(tr(I18N.Customer.STATUS_DELETED))
                    else:
                        QMessageBox.warning(
                            self.main_view,
                            "Error",
                            f"No se pudo eliminar el cliente: {response.message}"
                        )
                else:
                    QMessageBox.warning(
                        self.main_view,
                        tr(I18N.Dialogs.ERROR_TITLE),
                        "No se pudo eliminar el cliente. Verifique la conexión al facade."
                    )
                    
            except Exception as e:
                logger.error("CustomerInventory", "Error eliminando cliente", error=str(e))
                QMessageBox.critical(
                    self.main_view,
                    "Error",
                    f"Error al eliminar cliente:\n{str(e)}"
                )
    
    def _on_default_clicked(self):
        """Maneja el evento de establecer cliente como predeterminado"""
        if not self.selected_customer:
            QMessageBox.warning(
                self.main_view,
                tr(I18N.Customer.MSG_SELECTION_REQUIRED),
                tr(I18N.Customer.MSG_SELECT_TO_DEFAULT)
            )
            return
        
        customer = self.selected_customer
        
        # Si ya es predeterminado, informar al usuario
        if customer.is_default:
            QMessageBox.information(
                self.main_view,
                tr(I18N.Customer.MSG_ALREADY_DEFAULT_TITLE),
                tr(I18N.Customer.MSG_ALREADY_DEFAULT, name=customer.full_name)
            )
            return
        
        try:
            if self.facade:
                response = self.facade.set_default_customer(customer.id)
                if response.success:
                    logger.info("CustomerInventoryPresenter", 
                               f"Cliente establecido como predeterminado: {customer.full_name}")
                    
                    # Recargar la lista para reflejar el cambio
                    self.load_customers()
                    
                    QMessageBox.information(
                        self.main_view,
                        tr(I18N.Customer.MSG_DEFAULT_UPDATED_TITLE),
                        tr(I18N.Customer.MSG_DEFAULT_UPDATED, name=customer.full_name)
                    )
                else:
                    QMessageBox.warning(
                        self.main_view,
                        "Error",
                        f"No se pudo establecer como predeterminado: {response.message}"
                    )
            else:
                QMessageBox.warning(
                    self.main_view,
                    tr(I18N.Dialogs.ERROR_TITLE),
                    "No se pudo establecer como predeterminado. Verifique la conexión."
                )
                
        except Exception as e:
            logger.error("CustomerInventory", "Error estableciendo predeterminado", error=str(e))
            QMessageBox.critical(
                self.main_view,
                "Error",
                f"Error al establecer cliente predeterminado:\n{str(e)}"
            )

    def cleanup(self):
        """Limpieza de recursos al cerrar el presenter"""
        try:
            if self.button_animator:
                self.button_animator.cleanup()
                self.button_animator = None
            logger.debug("CustomerInventory", "Cleanup completado en CustomerInventoryPresenter")
        except Exception as e:
            logger.error("CustomerInventory", "Error en cleanup", error=str(e))
