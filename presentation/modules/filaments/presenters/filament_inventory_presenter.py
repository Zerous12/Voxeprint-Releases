"""
Presenter para el tab de inventario de filamentos en la ventana principal
Maneja la tabla de filamentos, búsqueda, selección y operaciones CRUD
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTableWidgetItem, QMessageBox, QHeaderView
from PySide6.QtCore import Qt
from typing import List, Optional, Dict, Any

from domain.models.filament import Filament
from domain.enums.enums import FilamentType, FilamentColor
from application.facades.voxeprint_facade import VoxeprintFacade
from core.utils.currency_helper import CurrencyHelper
from presentation.modules.filaments.views.edit_filament_dialog import EditFilamentDialog
from presentation.modules.filaments.views.add_filament_dialog import AddFilamentDialog
from presentation.modules.filaments.views.add_filament_more_dialog import MoreFilamentDialog
from presentation.modules.filaments.views.filament_details_dialog import FilamentDetailsDialog
from presentation.modules.filaments.views.roll_management_dialog import RollManagementDialog
from presentation.widgets.animation_mod.button_size_animator import ButtonSizeAnimator
from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class FilamentInventoryPresenter(QObject):
    """
    Presenter para el inventario de filamentos en la ventana principal
    """
    
    # Señales
    filament_selected = Signal(dict)  # Cuando se selecciona un filamento
    filament_modified = Signal(dict)  # Cuando se modifica un filamento
    filament_deleted = Signal(int)    # Cuando se elimina un filamento
    
    def __init__(self, main_view, parent=None):
        super().__init__(parent)
        self.main_view = main_view
        self.ui = main_view.ui
        
        # Facade para operaciones de negocio (inyección de dependencias)
        self.facade: Optional[VoxeprintFacade] = None
        
        # Estado interno
        self.all_filaments: List[Filament] = []
        self.filtered_filaments: List[Filament] = []
        self.selected_filament: Optional[Filament] = None
        
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
        self.load_filaments()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar tabla
        table = self.ui.qtable_filaments
        
        # Configurar cabeceras - ACTUALIZADO para incluir Descripcion
        headers = [
            "ID",
            tr(I18N.MainWindow.COL_DESCRIPTION),
            tr(I18N.MainWindow.COL_STOCK),
            tr(I18N.MainWindow.COL_TYPE),
            tr(I18N.MainWindow.COL_BRAND),
            tr(I18N.MainWindow.COL_COLOR),
            tr(I18N.MainWindow.COL_PRICE),
        ]
        table.setHorizontalHeaderLabels(headers)
        
        # Ocultar columna ID
        table.setColumnHidden(0, True)
        
        # Configurar anchos de columnas
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ID (oculta)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Descripcion (nueva!)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Stock
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Tipo
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Marca
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Color
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Precio
        
        # Configurar selección
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.SingleSelection)
        
        # Configurar ordenamiento
        table.setSortingEnabled(True)
        
        # Configurar textEdit inicial
        self.ui.textEdit_details_filament.setHtml(
            "Seleccione un filamento de la tabla para ver sus detalles aquí."
        )
        
        # Configurar estado inicial de botones
        self._update_button_states(False)
    
    def _connect_signals(self):
        """Conecta las señales de la UI"""
        # Señales de la tabla
        self.ui.qtable_filaments.itemSelectionChanged.connect(self._on_selection_changed)
        self.ui.qtable_filaments.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Señales del buscador
        self.ui.btn_search.clicked.connect(self._on_search_clicked)
        self.ui.linedit_search.returnPressed.connect(self._on_search_clicked)
        # NOTA: Búsqueda manual - NO conectamos textChanged para evitar búsqueda automática
        
        # Señales de botones de operaciones
        self.ui.btn_mod_filament.clicked.connect(self._on_modify_clicked)
        self.ui.btn_delete_filament.clicked.connect(self._on_delete_clicked)
        self.ui.btn_add_filament.clicked.connect(self._on_add_clicked)
        self.ui.btn_add_more_filament.clicked.connect(self._on_add_stock_clicked)
        
        # Señal del botón cleaner
        self.ui.btn_cleaner.clicked.connect(self._handle_clear_search)
    
    def _setup_button_animations(self):
        """Configura las animaciones de los botones de búsqueda"""
        try:
            # Crear animador para el par btn_search/btn_cleaner (filamentos)
            self.button_animator = ButtonSizeAnimator(
                primary_button=self.ui.btn_search,
                secondary_button=self.ui.btn_cleaner
            )
            
            logger.debug("FilamentInventory", "Animaciones de botones configuradas", 
                            botones="btn_search_2/btn_cleaner_2")
            
        except Exception as e:
            logger.error("FilamentInventory", "Error configurando animaciones de botones", error=str(e))
    
    def _handle_clear_search(self):
        """Maneja la limpieza de campos de búsqueda en filamentos"""
        try:
            # Limpiar campo de búsqueda
            self.ui.linedit_search.clear()
            
            # Restablecer filtros (mostrar todos los filamentos)
            self.filtered_filaments = self.all_filaments.copy()
            self._update_table()
            
            # Actualizar mensaje de estado
            self._update_status_message(f"Campos limpiados - Mostrando {len(self.all_filaments)} filamentos")
            
            logger.info("FilamentInventoryPresenter", f"Limpieza de campos completada - {len(self.all_filaments)} filamentos mostrados")
            
        except Exception as e:
            logger.error("FilamentInventoryPresenter", f"Error en limpieza de campos de filamentos: {e}")
            logger.log_exception("FilamentInventoryPresenter", e, "clear_fields")
            self._update_status_message("Error al limpiar campos")
    
    def load_filaments(self):
        """Carga los filamentos desde la base de datos"""
        try:
            if self.facade:
                self.all_filaments = self.facade.get_all_filaments_including_inactive()
                self.filtered_filaments = self.all_filaments.copy()
                
                logger.debug("FilamentInventory", "Filamentos cargados para inventario", 
                               cantidad=len(self.all_filaments))
                self._update_table()
                self._update_status_message(f"Cargados {len(self.all_filaments)} filamentos")
            else:
                self._update_status_message("Error: No hay conexión al facade")
                
        except Exception as e:
            logger.error("FilamentInventoryPresenter", f"Error cargando filamentos: {e}")
            logger.log_exception("FilamentInventoryPresenter", e, "load_filaments")
            self._update_status_message("Error cargando filamentos")
    
    def _update_table(self):
        """Actualiza la tabla con los filamentos filtrados"""
        table = self.ui.qtable_filaments
        
        # Limpiar tabla
        table.setRowCount(0)
        
        if not self.filtered_filaments:
            self._update_status_message("No hay filamentos para mostrar")
            return
        
        # Agregar filas
        table.setRowCount(len(self.filtered_filaments))
        
        for row, filament in enumerate(self.filtered_filaments):
            try:
                # Columna 0: ID (oculta)
                item_id = QTableWidgetItem(str(filament.id or ""))
                item_id.setData(Qt.ItemDataRole.UserRole, filament)  # Guardar objeto completo
                table.setItem(row, 0, item_id)
                
                # Columna 1: Descripción (NUEVA!)
                item_description = QTableWidgetItem(filament.name or "Sin descripción")
                table.setItem(row, 1, item_description)
                
                # Columna 2: Stock
                stock_kg = filament.current_stock_grams / 1000.0 if filament.current_stock_grams else 0.0
                stock_text = f"{stock_kg:.2f} kg"
                if filament.current_stock_grams and filament.minimum_stock_grams:
                    if filament.current_stock_grams < filament.minimum_stock_grams:
                        stock_text += " ⚠️"
                item_stock = QTableWidgetItem(stock_text)
                item_stock.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 2, item_stock)
                
                # Columna 3: Tipo
                filament_type = filament.type.value if hasattr(filament.type, 'value') else str(filament.type)
                item_type = QTableWidgetItem(filament_type)
                item_type.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 3, item_type)
                
                # Columna 4: Marca
                item_brand = QTableWidgetItem(filament.brand or "Sin marca")
                table.setItem(row, 4, item_brand)
                
                # Columna 5: Color
                filament_color = filament.color.value if hasattr(filament.color, 'value') else str(filament.color)
                item_color = QTableWidgetItem(filament_color)
                item_color.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 5, item_color)
                
                # Columna 6: Precio del stock actual (sin sufijos innecesarios)
                # Usar la moneda original del filamento
                filament_currency = getattr(filament, 'currency_code', 'PYG')
                
                if filament.price_per_gram and filament.current_stock_grams:
                    # Precio real del stock disponible
                    actual_stock_price = filament.price_per_gram * filament.current_stock_grams
                    stock_kg = filament.current_stock_grams / 1000.0
                    
                    if stock_kg >= 1.0:
                        # Si es 1kg o más, mostrar precio por kg
                        price_per_kg = filament.price_per_gram * 1000.0
                        price_text = CurrencyHelper.format(price_per_kg, filament_currency, include_symbol=True)
                    else:
                        # Si es menos de 1kg, mostrar precio del stock actual
                        price_text = CurrencyHelper.format(actual_stock_price, filament_currency, include_symbol=True)
                else:
                    price_text = CurrencyHelper.format(0, filament_currency, include_symbol=True)
                    
                item_price = QTableWidgetItem(price_text)
                item_price.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(row, 6, item_price)
                
            except Exception as e:
                logger.error("FilamentInventoryPresenter", f"Error agregando filamento a la tabla: {e}")
                logger.log_exception("FilamentInventoryPresenter", e, "_update_table")
        
        # Actualizar mensaje de estado
        count = len(self.filtered_filaments)
        total = len(self.all_filaments)
        if count == total:
            self._update_status_message(f"Mostrando {count} filamentos")
        else:
            self._update_status_message(f"Mostrando {count} de {total} filamentos")
    
    def _on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        selected_items = self.ui.qtable_filaments.selectedItems()
        
        if selected_items:
            # Obtener el filamento de la primera columna (ID)
            row = selected_items[0].row()
            id_item = self.ui.qtable_filaments.item(row, 0)
            
            if id_item:
                filament = id_item.data(Qt.ItemDataRole.UserRole)
                if isinstance(filament, Filament):
                    self.selected_filament = filament
                    self._update_filament_details(filament)
                    self._update_button_states(True)
                    
                    # Emitir señal de selección
                    filament_data = self._filament_to_dict(filament)
                    self.filament_selected.emit(filament_data)
                    
                    self._update_status_message("Filamento seleccionado")
        else:
            self.selected_filament = None
            self._clear_filament_details()
            self._update_button_states(False)
    
    def _update_filament_details(self, filament: Filament):
        """Actualiza el textEdit con los detalles del filamento"""
        try:
            # Información básica
            filament_type = filament.type.value if hasattr(filament.type, 'value') else str(filament.type)
            filament_color = (
                tr(f"FilamentColor.{filament.color.name}")
                if hasattr(filament.color, 'name')
                else str(filament.color)
            )

            # Cálculos
            stock_kg = filament.current_stock_grams / 1000.0 if filament.current_stock_grams else 0.0
            min_stock_kg = filament.minimum_stock_grams / 1000.0 if filament.minimum_stock_grams else 0.0
            price_per_kg = filament.price_per_gram * 1000.0 if filament.price_per_gram else 0.0

            # Estado del stock
            stock_status = tr(I18N.Filament.STOCK_STATUS_NORMAL)
            if filament.current_stock_grams and filament.minimum_stock_grams:
                if filament.current_stock_grams < filament.minimum_stock_grams:
                    stock_status = tr(I18N.Filament.STOCK_STATUS_LOW_PLAIN)
                elif filament.current_stock_grams < (filament.minimum_stock_grams * 1.5):
                    stock_status = tr(I18N.Filament.STOCK_STATUS_MEDIUM_PLAIN)

            # Usar la moneda original del filamento
            filament_currency = getattr(filament, 'currency_code', 'PYG')

            active_text = tr(I18N.Filament.DETAIL_ACTIVE) if filament.is_active else tr(I18N.Filament.DETAIL_INACTIVE)

            # Formatear información
            details = f"""{tr(I18N.Filament.DETAIL_TITLE)}

{tr(I18N.Filament.GROUP_BASIC_INFO).upper()}
**{tr(I18N.Filament.LABEL_NAME_DETAIL)}** {filament.name}
**{tr(I18N.Filament.LABEL_TYPE_MATERIAL)}** {filament_type}
**{tr(I18N.Filament.LABEL_BRAND)}** {filament.brand or tr(I18N.Filament.DEFAULT_NOT_SPECIFIED)}
**{tr(I18N.Filament.LABEL_COLOR)}** {filament_color}

{tr(I18N.Filament.GROUP_INVENTORY).upper()}
**{tr(I18N.Filament.LABEL_CURRENT_STOCK)}** {stock_kg:.2f} kg ({filament.current_stock_grams:.0f}g)
**{tr(I18N.Filament.LABEL_MIN_STOCK)}** {min_stock_kg:.2f} kg ({filament.minimum_stock_grams:.0f}g)
**{tr(I18N.Filament.LABEL_ROLL_COUNT)}** {filament.quantity_rolls}
**{tr(I18N.Filament.LABEL_STOCK_STATUS)}** {stock_status}

{tr(I18N.Filament.GROUP_PRICING).upper()}
**{tr(I18N.Filament.LABEL_PRICE_PER_UNIT)}** {CurrencyHelper.format(filament.price_per_unit if filament.price_per_unit else 0, filament_currency)}
**{tr(I18N.Filament.LABEL_PRICE_PER_GRAM)}** {CurrencyHelper.format(filament.price_per_gram or 0, filament_currency)}
**{tr(I18N.Filament.LABEL_PRICE_PER_KG)}** {CurrencyHelper.format(price_per_kg, filament_currency)}

{tr(I18N.Filament.GROUP_CHARACTERISTICS).upper()}
**{tr(I18N.Filament.LABEL_WEIGHT_PER_ROLL)}** {filament.weight_grams:.0f}g
**{tr(I18N.Filament.LABEL_STATUS_DETAIL)}** {active_text}

{tr(I18N.Filament.DETAIL_SECTION_NOTES)}
{filament.notes or tr(I18N.Filament.DETAIL_NO_NOTES)}

{tr(I18N.Filament.DETAIL_SECTION_RECORD)}
**{tr(I18N.Filament.LABEL_CREATED)}** {filament.created_at or tr(I18N.Filament.DEFAULT_NOT_AVAILABLE)}
**{tr(I18N.Filament.LABEL_UPDATED)}** {filament.updated_at or tr(I18N.Filament.DEFAULT_NOT_AVAILABLE)}"""

            # Convertir formato **negrita** a HTML
            html_details = details.replace("**", "<b>", 1)
            while "**" in html_details:
                html_details = html_details.replace("**", "</b>", 1)
                if "**" in html_details:
                    html_details = html_details.replace("**", "<b>", 1)

            # Reemplazar saltos de línea con <br>
            html_details = html_details.replace("\n", "<br>")

            self.ui.textEdit_details_filament.setHtml(html_details)

        except Exception as e:
            logger.error("FilamentInventoryPresenter", f"Error actualizando detalles del filamento: {e}")
            logger.log_exception("FilamentInventoryPresenter", e, "_update_filament_details")
            self.ui.textEdit_details_filament.setHtml(tr(I18N.Filament.MSG_ERROR_SHOWING_DETAILS))

    def _clear_filament_details(self):
        """Limpia los detalles del filamento"""
        self.ui.textEdit_details_filament.setHtml(tr(I18N.Filament.MSG_SELECT_TO_VIEW))
    
    def _update_button_states(self, has_selection: bool):
        """Actualiza el estado de los botones según la selección"""
        # Todos los botones permanecen habilitados para mostrar alertas (patrón consistente)
        # self.ui.btn_mod_filament.setEnabled(has_selection)
        # self.ui.btn_delete_filament.setEnabled(has_selection)
        # self.ui.btn_add_more_filament.setEnabled(has_selection)  # Ahora también siempre habilitado
    
    def _on_search_clicked(self):
        """Maneja el clic en el botón de búsqueda o presionar Enter"""
        search_text = self.ui.linedit_search.text().strip()
        self.search_filaments(search_text)
    
    def _on_search_text_changed(self, text: str):
        """Maneja el cambio en el texto de búsqueda (sin ejecutar búsqueda automática)"""
        # Este método ahora solo se usa para preparar la UI, NO ejecuta búsqueda automática
        # La búsqueda se ejecuta únicamente al presionar Enter o hacer clic en Consultar
        pass
    
    def search_filaments(self, search_text: str):
        """Realiza la búsqueda de filamentos"""
        if not search_text:
            self.filtered_filaments = self.all_filaments.copy()
        else:
            search_text = search_text.lower()
            self.filtered_filaments = []
            
            for filament in self.all_filaments:
                # Campos de búsqueda
                filament_type = filament.type.value if hasattr(filament.type, 'value') else str(filament.type)
                filament_color = filament.color.value if hasattr(filament.color, 'value') else str(filament.color)
                
                searchable_text = f"{filament.name} {filament_type} {filament.brand} {filament_color}".lower()
                
                if search_text in searchable_text:
                    self.filtered_filaments.append(filament)
        
        self._update_table()
        
        if search_text:
            self._update_status_message(f"Búsqueda: '{search_text}' - {len(self.filtered_filaments)} resultados")
        else:
            self._update_status_message(f"Mostrando todos los filamentos ({len(self.filtered_filaments)})")
    
    def _on_item_double_clicked(self, item):
        """Maneja el doble clic en un elemento de la tabla - muestra detalles"""
        if not self.selected_filament:
            return
        
        try:
            # Mostrar diálogo de detalles (con facade para mostrar rollos)
            dialog = FilamentDetailsDialog(self.main_view, self.selected_filament, facade=self.facade)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self.main_view,
                "Error",
                f"Error al mostrar detalles: {str(e)}"
            )
    
    def _on_modify_clicked(self):
        """Maneja el clic en el botón modificar filamento"""
        if not self.selected_filament:
            QMessageBox.warning(
                self.main_view,
                "Selección requerida",
                "Por favor, selecciona un filamento para modificar."
            )
            return
        
        # Validar que la moneda del filamento esté activa
        from infrastructure.database.repositories.currency_repository import CurrencyRepository
        currency_repo = CurrencyRepository()
        filament_currency = getattr(self.selected_filament, 'currency_code', 'USD')
        currency = currency_repo.get_by_code(filament_currency)
        
        if not currency or not currency.is_active:
            QMessageBox.warning(
                self.main_view,
                "Moneda Inactiva",
                f"No se puede modificar este filamento porque su moneda ({filament_currency}) está inactiva.\n\n"
                f"Para editarlo, primero debe activar la moneda en 'Ajustes > Sistema > Ajustes de moneda'."
            )
            return
        
        try:
            # Preguntar al usuario qué desea hacer
            msg_box = QMessageBox(self.main_view)
            msg_box.setWindowTitle(tr(I18N.Filament.DIALOG_EDIT_CHOOSE_TITLE))
            msg_box.setText(tr(I18N.Filament.DIALOG_EDIT_CHOOSE_TEXT, name=self.selected_filament.name))
            msg_box.setIcon(QMessageBox.Icon.Question)
            
            btn_metadata = msg_box.addButton(tr(I18N.Filament.BTN_GENERAL_DATA), QMessageBox.ButtonRole.ActionRole)
            btn_rolls = msg_box.addButton(tr(I18N.Filament.BTN_MANAGE_ROLLS), QMessageBox.ButtonRole.ActionRole)
            btn_cancel = msg_box.addButton(tr(I18N.Dialogs.CANCEL), QMessageBox.ButtonRole.RejectRole)
            
            for btn in (btn_metadata, btn_rolls, btn_cancel):
                btn.setFixedHeight(30)
                btn.setFixedWidth(105)
            
            msg_box.exec()
            clicked = msg_box.clickedButton()
            
            if clicked == btn_metadata:
                # Editar datos generales (nombre, marca, tipo, color, notas)
                result = EditFilamentDialog.edit_filament(self.main_view, self.selected_filament)
                if result:
                    self._process_filament_form_data(result)
            elif clicked == btn_rolls:
                # Gestionar rollos individuales
                self._open_roll_management()
                
        except Exception as e:
            logger.error("FilamentInventoryPresenter", f"Error abriendo formulario de edición: {e}")
            logger.log_exception("FilamentInventoryPresenter", e, "open_edit_form")
            QMessageBox.critical(
                self.main_view,
                tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.Filament.MSG_ERROR_OPEN_EDIT)
            )
    
    def _on_delete_clicked(self):
        """Maneja el clic en el botón eliminar"""
        if not self.selected_filament:
            QMessageBox.warning(
                self.main_view,
                tr(I18N.Filament.DELETE_NO_SELECTION_TITLE),
                tr(I18N.Filament.DELETE_NO_SELECTION_MSG)
            )
            return
        
        # Guardar información del filamento antes de eliminar
        filament_name = self.selected_filament.name
        filament_id = self.selected_filament.id
        filament_type = self.selected_filament.type.value if hasattr(self.selected_filament.type, 'value') else str(self.selected_filament.type)
        filament_brand = self.selected_filament.brand
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self.main_view,
            tr(I18N.Filament.DELETE_CONFIRM_TITLE),
            tr(I18N.Filament.DELETE_CONFIRM_MSG,
               name=filament_name,
               type=filament_type,
               brand=filament_brand),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.facade and filament_id:
                    # Eliminar usando el facade
                    deleted_successfully = self.facade.delete_filament(filament_id)
                    
                    if deleted_successfully:
                        # Emitir señal
                        self.filament_deleted.emit(filament_id)
                        
                        # Limpiar selección antes de recargar
                        self.selected_filament = None
                        
                        # Recargar datos
                        self.load_filaments()
                        
                        QMessageBox.information(
                            self.main_view,
                            tr(I18N.Filament.DELETE_SUCCESS_TITLE),
                            tr(I18N.Filament.DELETE_SUCCESS_MSG)
                        )
                        
                        self._update_status_message(tr(I18N.Filament.STATUS_DELETED))
                    else:
                        QMessageBox.warning(
                            self.main_view,
                            tr(I18N.Dialogs.ERROR_TITLE),
                            tr(I18N.Filament.DELETE_FAILED_MSG)
                        )
                        
                else:
                    QMessageBox.warning(
                        self.main_view,
                        tr(I18N.Dialogs.ERROR_TITLE),
                        tr(I18N.Filament.DELETE_NO_FACADE_MSG)
                    )
                    
            except Exception as e:
                logger.error("FilamentInventoryPresenter", f"Error eliminando filamento: {e}")
                logger.log_exception("FilamentInventoryPresenter", e, "_on_delete_clicked")
                QMessageBox.critical(
                    self.main_view,
                    tr(I18N.Filament.DELETE_ERROR_TITLE),
                    tr(I18N.Filament.DELETE_ERROR_MSG)
                )
    
    def _on_add_clicked(self):
        """Maneja el clic en el botón añadir filamento"""
        try:
            # Abrir diálogo especializado para agregar
            dialog = AddFilamentDialog(self.main_view)
            
            # Conectar señal para recargar cuando se añade exitosamente
            dialog.filament_added.connect(self._on_filament_added_successfully)
            
            # Mostrar diálogo
            dialog.exec()
            
        except Exception as e:
            logger.error("FilamentInventoryPresenter", f"Error abriendo formulario de nuevo filamento: {e}")
            logger.log_exception("FilamentInventoryPresenter", e, "_on_add_clicked")
            QMessageBox.critical(
                self.main_view,
                "Error al Agregar",
                "Ocurrió un error al abrir el formulario de nuevo filamento.\n\nRevise el archivo de log para más detalles."
            )
    
    def _on_filament_added_successfully(self, filament_data: Dict[str, Any]):
        """
        Maneja la señal cuando se añade un filamento exitosamente.
        El filamento YA FUE GUARDADO por el diálogo, solo necesitamos recargar.
        """
        try:
            logger.info("FilamentInventoryPresenter", f"Filamento añadido exitosamente: {filament_data['name']}")
            
            # Recargar datos del inventario
            self.load_filaments()
            self._update_status_message("Filamento agregado exitosamente")
            
            # Seleccionar el nuevo filamento
            if 'id' in filament_data:
                self._select_filament_by_id(filament_data['id'])
                
        except Exception as e:
            logger.error("FilamentInventoryPresenter", f"Error recargando después de añadir filamento: {e}")
            logger.log_exception("FilamentInventoryPresenter", e, "_on_filament_added_successfully")
    
    def _process_filament_form_data(self, form_data: Dict[str, Any]):
        """
        Procesa los datos del formulario de filamento
        NOTA: Ya no se usa para nuevos filamentos, solo para edición
        """
        try:
            if form_data.get('is_edit', False):
                # Modificar filamento existente
                self._update_filament_from_form(form_data)
            else:
                # NUEVO: Ya no guardamos aquí, el diálogo ya lo guardó
                logger.info("FilamentInventoryPresenter", "Nuevo filamento ya fue guardado por el diálogo, solo recargando")
                self.load_filaments()
                self._update_status_message("Filamento agregado exitosamente")
                
        except Exception as e:
            action = "modificar" if form_data.get('is_edit', False) else "crear"
            logger.error("FilamentInventoryPresenter", f"Error procesando datos del formulario: {e}")
            logger.log_exception("FilamentInventoryPresenter", e, "_process_filament_form_data")
            QMessageBox.critical(
                self.main_view,
                "Error",
                f"Error al {action} el filamento.\n\nRevise el archivo de log para más detalles."
            )    
    
    def _open_roll_management(self):
        """Abre el diálogo de gestión de rollos para el filamento seleccionado"""
        if not self.selected_filament or not self.facade:
            return
        
        try:
            changed = RollManagementDialog.manage_rolls(
                self.main_view, self.selected_filament, self.facade
            )
            if changed:
                self.load_filaments()
                self._select_filament_by_id(self.selected_filament.id)
                self._update_status_message("Rollos actualizados correctamente")
        except Exception as e:
            logger.error("FilamentInventoryPresenter", f"Error gestionando rollos: {e}")
            logger.log_exception("FilamentInventoryPresenter", e, "_open_roll_management")
    
    def _update_filament_from_form(self, form_data: Dict[str, Any]):
        """Actualiza un filamento existente desde los datos del formulario"""
        if not self.selected_filament:
            return
        
        try:
            # Convertir strings a enums
            filament_type = FilamentType[form_data['type']]
            filament_color = FilamentColor[form_data['color']]
            
            # Actualizar propiedades del filamento - solo metadatos
            self.selected_filament.name = form_data['name']
            self.selected_filament.type = filament_type
            self.selected_filament.brand = form_data['brand']
            self.selected_filament.color = filament_color
            self.selected_filament.is_active = form_data['is_active']
            
            # Campos opcionales de stock/precio (solo presentes en modo agregar)
            if 'weight_grams' in form_data:
                self.selected_filament.weight_grams = form_data['weight_grams']
            if 'price_per_unit' in form_data:
                self.selected_filament.price_per_unit = form_data['price_per_unit']
            if 'price_per_gram' in form_data:
                self.selected_filament.price_per_gram = form_data['price_per_gram']
            if 'current_stock_grams' in form_data:
                self.selected_filament.current_stock_grams = form_data['current_stock_grams']
            
            # Agregar notas si están presentes
            if 'notes' in form_data:
                self.selected_filament.notes = form_data['notes']
            
            # Guardar cambios en base de datos usando el facade
            updated_filament = self.facade.update_filament(self.selected_filament)
            
            if updated_filament:
                # Recargar datos
                self.load_filaments()
                self._update_status_message("Filamento modificado exitosamente")
                
                # Mostrar mensaje de éxito
                QMessageBox.information(
                    self.main_view,
                    "Operación Exitosa",
                    "El filamento ha sido modificado correctamente."
                )
                
                # Mantener selección
                self._select_filament_by_id(updated_filament.id)
            else:
                # Error al guardar
                QMessageBox.warning(
                    self.main_view,
                    "Error de Guardado",
                    "No se pudo guardar la modificación del filamento."
                )
                
        except Exception as e:
            # Error inesperado
            logger.error("FilamentInventoryPresenter", f"Error en _update_filament_from_form: {e}")
            logger.log_exception("FilamentInventoryPresenter", e, "_update_filament_from_form")
            QMessageBox.critical(
                self.main_view,
                "Error al Modificar",
                "Error al modificar el filamento.\n\nRevise el archivo de log para más detalles."
            )
            raise
    
    def _select_filament_by_id(self, filament_id: int):
        """Selecciona un filamento en la tabla por su ID"""
        table = self.ui.qtable_filaments
        
        for row in range(table.rowCount()):
            id_item = table.item(row, 0)  # Columna ID
            if id_item and int(id_item.text()) == filament_id:
                table.selectRow(row)
                break
    
    def _on_add_stock_clicked(self):
        """Maneja el clic en el botón añadir stock (agregar rollo)"""
        if not self.selected_filament:
            QMessageBox.information(
                self.main_view,
                "Sin Selección",
                "Por favor seleccione un filamento para agregar stock."
            )
            return
        
        # Validar que la moneda del filamento esté activa
        from infrastructure.database.repositories.currency_repository import CurrencyRepository
        currency_repo = CurrencyRepository()
        filament_currency = getattr(self.selected_filament, 'currency_code', 'USD')
        currency = currency_repo.get_by_code(filament_currency)
        
        if not currency or not currency.is_active:
            QMessageBox.warning(
                self.main_view,
                "Moneda Inactiva",
                f"No se puede agregar stock a este filamento porque su moneda ({filament_currency}) está inactiva.\n\n"
                f"Para agregar stock, primero debe activar la moneda en 'Ajustes > Sistema > Ajustes de moneda'."
            )
            return
        
        try:
            # Abrir diálogo especializado para añadir más filamento al existente
            result = MoreFilamentDialog.add_filament_roll(self.main_view, self.selected_filament)
            
            if result:
                # Procesar los datos del rollo
                self._process_filament_roll_data(result)
                
        except Exception as e:
            QMessageBox.critical(
                self.main_view,
                "Error al Agregar Rollo",
                f"Ocurrió un error al abrir el formulario de nuevo rollo:\n{str(e)}"
            )
    
    def _process_filament_roll_data(self, roll_data: Dict[str, Any]):
        """Procesa los datos del nuevo rollo usando precio promedio ponderado"""
        try:
            # Usar el método especializado del facade
            updated_filament = self.facade.add_filament_roll_with_weighted_price(roll_data)
            
            if updated_filament:
                # Recargar datos
                self.load_filaments()
                
                # Mostrar información del resultado
                if roll_data.get('is_new_filament', False):
                    self._update_status_message(tr(I18N.AddMoreFilament.MSG_ROLL_ADDED))
                else:
                    self._update_status_message(tr(I18N.AddMoreFilament.MSG_STOCK_ADDED))
                
                # Seleccionar el filamento actualizado
                self._select_filament_by_id(updated_filament.id)
                
                # Mostrar confirmación simple
                QMessageBox.information(
                    self.main_view,
                    tr(I18N.AddMoreFilament.MSG_SUCCESS_TITLE),
                    tr(I18N.AddMoreFilament.MSG_SUCCESS_TEXT)
                )
            else:
                raise Exception("No se pudo procesar el rollo en la base de datos")
                
        except Exception as e:
            QMessageBox.critical(
                self.main_view,
                tr(I18N.AddMoreFilament.MSG_ERROR_PROCESS_TITLE),
                tr(I18N.AddMoreFilament.MSG_ERROR_PROCESS_TEXT, error=str(e))
            )
    
    def _filament_to_dict(self, filament: Filament) -> Dict[str, Any]:
        """Convierte un filamento a diccionario para las señales"""
        return {
            'id': filament.id,
            'name': filament.name,
            'type': filament.type.value if hasattr(filament.type, 'value') else str(filament.type),
            'brand': filament.brand,
            'color': filament.color.value if hasattr(filament.color, 'value') else str(filament.color),
            'price_per_gram': filament.price_per_gram,
            'current_stock_grams': filament.current_stock_grams,
            'is_active': filament.is_active
        }
    
    def _update_status_message(self, message: str):
        """Actualiza el mensaje de estado - ahora usa logging centralizado"""
        try:
            # Log internal del inventario sin mostrar en UI
            logger.debug("FilamentInventory", message)
        except Exception as e:
            logger.error("FilamentInventory", "Error actualizando mensaje de estado", error=str(e))
    
    # === MÉTODOS PÚBLICOS ===
    
    def refresh_data(self):
        """Refresca los datos de la tabla"""
        self.load_filaments()
        self._update_status_message("Datos actualizados")
    
    def get_selected_filament(self) -> Optional[Filament]:
        """Retorna el filamento seleccionado"""
        return self.selected_filament
    
    def select_filament_by_id(self, filament_id: int):
        """Selecciona un filamento por su ID"""
        table = self.ui.qtable_filaments
        
        for row in range(table.rowCount()):
            id_item = table.item(row, 0)
            if id_item and id_item.text() == str(filament_id):
                table.selectRow(row)
                break
    
    def get_filament_count(self) -> int:
        """Retorna el número total de filamentos"""
        return len(self.all_filaments)
    
    def get_low_stock_count(self) -> int:
        """Retorna el número de filamentos con stock bajo"""
        count = 0
        for filament in self.all_filaments:
            if (filament.current_stock_grams and filament.minimum_stock_grams and 
                filament.current_stock_grams < filament.minimum_stock_grams):
                count += 1
        return count
    
    def cleanup(self):
        """Limpieza de recursos al cerrar el presenter"""
        try:
            if self.button_animator:
                self.button_animator.cleanup()
                self.button_animator = None
            logger.info("FilamentInventoryPresenter", "Cleanup completado en FilamentInventoryPresenter")
        except Exception as e:
            logger.error("FilamentInventoryPresenter", f"Error en cleanup de FilamentInventoryPresenter: {e}")
            logger.log_exception("FilamentInventoryPresenter", e, "cleanup")
