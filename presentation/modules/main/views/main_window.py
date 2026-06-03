from PySide6.QtWidgets import (QMainWindow, QMessageBox, QVBoxLayout, QWidget, 
                              QDateEdit, QLineEdit, QPushButton, QTableWidget, QTextEdit, QTableWidgetItem, QHeaderView)
from PySide6.QtGui import QKeySequence, QShortcut, QCursor
from PySide6.QtCore import Signal, QDate, QTimer, Qt, QEvent

from config.build_config import BUILD_CONFIG
from presentation.modules.main.designs.main_window_ui import Ui_MainPanel
from presentation.modules.main.views.system_settings_widget import SystemSettingsWidget
from presentation.modules.main.presenters.system_settings_presenter import SystemSettingsPresenter
from presentation.widgets.animation_mod.donation_event_label import DonationEventLabel
from presentation.widgets.animation_mod.panel_size_animator import PanelSizeAnimator
from core.managers.app_preferences_manager import AppPreferencesManager
from core.managers.locale_manager import LocaleManager
from domain.enums.enums import AdvanceMode
from core.utils.logger import logger
from core.utils.currency_helper import CurrencyHelper
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from typing import Optional


class MainPanel(QMainWindow):
    # (PanelSizeAnimator ahora es importado desde animation_mod)
    """
    Vista principal de la aplicación (View en patrón MVP)
    Solo contiene lógica de UI, toda la lógica de negocio está en el Presenter
    """
    
    # Etiquetas de campos — se actualizan en _apply_dynamic_labels() con tr(I18N.*)
    LABELS = {
        'filament_type': 'Tipo',
        'filament_color': 'Color',
        'filament_price': 'Precio',
        'filament_stock': 'Stock',
        'printer_brand': 'Marca',
        'printer_model': 'Modelo',
        'printer_consumption': 'Consumo',
        'client_name': 'Razón Social',
        'client_ruc': 'RUC/CI',
    }
    
    # Señales para comunicarse con el Presenter
    client_search_requested = Signal()
    filament_search_requested = Signal()
    printer_search_requested = Signal()
    load_gcode_requested = Signal()
    printer_combox_changed = Signal(int)  # índice seleccionado en combobox de impresora
    filament_combox_changed = Signal(int)  # índice seleccionado en combobox de filamento
    calculate_quote_requested = Signal()
    clear_form_requested = Signal()
    preview_requested = Signal()
    save_quote_requested = Signal()
    generate_note_requested = Signal()
    settings_requested = Signal()  # Nueva señal para el diálogo de configuraciones
    close_application_requested = Signal()  # Nueva señal para cerrar la aplicación
    # Señal multicolor: (slot_index, filament_id)
    multicolor_slot_changed = Signal(int, int)
    multicolor_slot_selected = Signal(int)
    multicolor_search_requested = Signal(int)  # slot_index
    
    # Señales para elementos clickeables
    build_info_requested = Signal()      # Señal para mostrar info de build (version)
    donation_requested = Signal()  # Señal para abrir página de donaciones
    
    # Señales para cambios en spinboxes CON DELAY (para auto-cálculo)
    time_changed = Signal(int, int)  # horas, minutos
    weight_changed = Signal(int)     # gramos
    quantity_changed = Signal(int)   # cantidad
    customer_optional_changed = Signal(bool)  # estado del checkbox opcional
    
    # Señales para sistema de anticipo CON DELAY
    advance_enabled_changed = Signal(bool)    # estado del checkbox de anticipo
    advance_percentage_changed = Signal(int)  # porcentaje de anticipo
    
    # Señales para sistema de post-procesado CON DELAY
    post_enabled_changed = Signal(bool)    # estado del checkbox de post-procesado
    post_amount_changed = Signal(int)      # monto de post-procesado
    post_type_changed = Signal(str)        # tipo de post-procesado (Lote/Trabajo)
    
    # ⚡ SEÑALES INMEDIATAS (para invalidación del botón - 0ms delay)
    time_changed_immediate = Signal()      # Cambio inmediato en tiempo
    weight_changed_immediate = Signal()    # Cambio inmediato en peso  
    quantity_changed_immediate = Signal()  # Cambio inmediato en cantidad
    advance_enabled_changed_immediate = Signal()  # Cambio inmediato en anticipo
    advance_percentage_changed_immediate = Signal()  # Cambio inmediato en % anticipo
    post_enabled_changed_immediate = Signal()  # Cambio inmediato en post-procesado
    post_amount_changed_immediate = Signal()  # Cambio inmediato en monto post
    post_type_changed_immediate = Signal()  # Cambio inmediato en tipo post
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Inicializar manager de preferencias
        self.app_preferences = AppPreferencesManager()
        
        self.ui = Ui_MainPanel()
        self.ui.setupUi(self)
        self.setWindowTitle(tr(I18N.App.TITLE))
        
        # Altura fija, ancho controlado por toggle del panel de procesos
        self.setFixedHeight(self.height())
        
        # Estado inicial: panel de procesos oculto (ventana colapsada)
        self._process_view_visible = False
        self._icon_panel_collapsed = None
        self._icon_panel_expanded = None
        self._icon_panel_collapsed_hover = None
        self._icon_panel_expanded_hover = None
        self._collapsed_width = 652
        self._expanded_width = 975
        self._collapsed_height = 0
        self._expanded_height = 710 
        self.ui.content_process_view.setMaximumHeight(self._collapsed_height)
        self.ui.content_process_view.setVisible(False)
        self.setMinimumWidth(self._collapsed_width)
        self.setMaximumWidth(self._collapsed_width)
        self.resize(self._collapsed_width, self.height())
        self.panel_animator: Optional[PanelSizeAnimator] = None   
        self._setup_animation_panel()  # Configurar el animador para el panel de procesos
        # Timer para el autocompletado de tiempo (evitar intervenciones mientras escribe)
        self.time_conversion_timer = QTimer()
        self.time_conversion_timer.setSingleShot(True)  # Solo ejecutar una vez
        self.time_conversion_timer.timeout.connect(self._process_time_conversion)
        
        # Timer para emisión de señal de tiempo con delay
        self.time_timer = QTimer()
        self.time_timer.setSingleShot(True)
        self.time_timer.timeout.connect(self._emit_time_changed)
        
        # Timers para evitar spam en peso y cantidad
        self.weight_timer = QTimer()
        self.weight_timer.setSingleShot(True)
        self.weight_timer.timeout.connect(self._emit_weight_changed)
        
        self.quantity_timer = QTimer()
        self.quantity_timer.setSingleShot(True)
        self.quantity_timer.timeout.connect(self._emit_quantity_changed)
        
        self.advance_timer = QTimer()
        self.advance_timer.setSingleShot(True)
        self.advance_timer.timeout.connect(self._emit_advance_changed)
        
        # Flags para control de bucles de recálculo
        self._programmatic_change = False  # Flag para evitar bucles de recálculo
        self._user_manual_override = False  # Flag para indicar que el usuario cambió manualmente el anticipo
        
        self.post_timer = QTimer()
        self.post_timer.setSingleShot(True)
        self.post_timer.timeout.connect(self._emit_post_changed)
        
        # Inicializar el módulo de ajustes
        self._setup_settings_tab()
        
        # Configurar widgets de desarrollo futuro
        self._setup_development_widgets()
        
        # Configurar widgets personalizados
        self._setup_custom_widgets()
        
        # Configurar widget de post-procesado con decimales
        self._setup_post_system()
        
        # Configurar información dinámica de la aplicación
        self._setup_dynamic_app_info()
        
        # Conectar señales internas
        self._connect_ui_signals()
        
        # Configurar estado inicial
        self._setup_initial_state()

        # Aplicar etiquetas dinámicas del sistema i18n (sobreescribe retranslateUi)
        self._apply_dynamic_labels()
    
    def _apply_dynamic_labels(self):
        """
        Sobreescribe los strings de retranslateUi() de main_window_ui.py
        con los valores del sistema i18n (tr/LanguageManager).
        Debe llamarse al final del __init__ para que prevalezca sobre setupUi().
        Al agregar nuevos widgets a main_window_ui.py, también añadir aquí.
        """
        try:
            ui = self.ui
            currency_symbol = CurrencyHelper.get_current_currency()

            # --- Tabs ---
            ui.tabWidget.setTabText(ui.tabWidget.indexOf(ui.tab_one), tr(I18N.Mainwindow.TAB_QUOTES))
            ui.tabWidget.setTabText(ui.tabWidget.indexOf(ui.tab_five), tr(I18N.MainWindow.TAB_HISTORY))
            ui.tabWidget.setTabText(ui.tabWidget.indexOf(ui.tab_two), tr(I18N.MainWindow.TAB_INVENTORY))
            ui.tabWidget.setTabText(ui.tabWidget.indexOf(ui.tab_three), tr(I18N.Mainwindow.TAB_PRINTERS))
            ui.tabWidget.setTabText(ui.tabWidget.indexOf(ui.tab_six), tr(I18N.Mainwindow.TAB_CUSTOMERS))
            ui.tabWidget.setTabText(ui.tabWidget.indexOf(ui.tab_four), tr(I18N.Mainwindow.TAB_SETTINGS))

            # --- GroupBoxes: tab Presupuesto ---
            ui.groupbox_autofill.setTitle(tr(I18N.MainWindow.GROUP_AUTOFILL))
            ui.groupbox_multi_filament.setTitle(tr(I18N.MainWindow.GROUP_MULTI_FILAMENT))
            ui.groupbox_filament.setTitle(tr(I18N.MainWindow.GROUP_FILAMENT))
            ui.groupBox_post.setTitle(tr(I18N.MainWindow.GROUP_POST))
            ui.groupbox_client.setTitle(tr(I18N.MainWindow.GROUP_CLIENT))
            ui.groupbox_printer_info.setTitle(tr(I18N.MainWindow.GROUP_PRINTER))
            ui.groupbox_piece_info.setTitle(tr(I18N.MainWindow.GROUP_PIECE))
            ui.groupBox_operations.setTitle(tr(I18N.MainWindow.GROUP_OPERATIONS))
            ui.groupBox_advance.setTitle(tr(I18N.MainWindow.GROUP_ADVANCE))
            ui.groupBox_action.setTitle(tr(I18N.MainWindow.GROUP_ACTION))
            ui.groupbox_details.setTitle(tr(I18N.MainWindow.GROUP_SUMMARY))

            # --- GroupBoxes: tab Historial ---
            ui.groupBox_operations_4.setTitle(tr(I18N.MainWindow.GROUP_OPERATIONS))
            ui.groupbox_search_4.setTitle(tr(I18N.MainWindow.GROUP_QUICK_SEARCH))

            # --- GroupBoxes: tab Inventario (filamentos) ---
            ui.groupBox_operations_2.setTitle(tr(I18N.MainWindow.GROUP_OPERATIONS))
            ui.groupbox_search.setTitle(tr(I18N.MainWindow.GROUP_QUICK_SEARCH))

            # --- GroupBoxes: tab Impresoras ---
            ui.groupBox_operations_3.setTitle(tr(I18N.MainWindow.GROUP_OPERATIONS))
            ui.groupbox_search_2.setTitle(tr(I18N.MainWindow.GROUP_QUICK_SEARCH))

            # --- GroupBoxes: tab Clientes ---
            ui.groupBox_operations_5.setTitle(tr(I18N.MainWindow.GROUP_OPERATIONS))
            ui.groupbox_search_3.setTitle(tr(I18N.MainWindow.GROUP_QUICK_SEARCH))

            # --- Labels: sección Autocompletar ---
            ui.label_desc_proyect_mf.setText(tr(I18N.MainWindow.LABEL_DESCRIPTION))
            ui.linedit_desc_gcode.setPlaceholderText(tr(I18N.MainWindow.PLACEHOLDER_PROJECT))
            ui.btn_load_gcode.setText(tr(I18N.MainWindow.BTN_PROJECT))
            ui.btn_load_gcode.setToolTip(tr(I18N.MainWindow.TOOLTIP_LOAD_GCODE))

            # --- Labels/combos: Multi-Filamento ---
            ui.label_desc_multi_filament.setText(tr(I18N.MainWindow.LABEL_DESCRIPTION))
            ui.combox_desc_multi_filament.setToolTip(tr(I18N.MainWindow.TOOLTIP_SELECT_FILAMENT_COMBO))
            ui.combox_desc_multi_filament.setPlaceholderText(tr(I18N.MainWindow.PLACEHOLDER_SELECT_FILAMENT))
            ui.btn_multicolor_search.setToolTip(tr(I18N.MainWindow.TOOLTIP_MULTICOLOR_SEARCH))

            # --- Labels/combos: Filamento ---
            ui.label_desc.setText(tr(I18N.MainWindow.LABEL_DESCRIPTION))
            ui.btn_select_filament.setText(tr(I18N.MainWindow.BTN_FILAMENT_SELECT))
            ui.btn_select_filament.setToolTip(tr(I18N.MainWindow.TOOLTIP_SELECT_FILAMENT_BTN))
            ui.combox_desc_filament.setToolTip(tr(I18N.MainWindow.TOOLTIP_SELECT_FILAMENT_COMBO))
            ui.combox_desc_filament.setPlaceholderText(tr(I18N.MainWindow.PLACEHOLDER_SELECT_FILAMENT))

            # --- Post-procesado ---
            ui.label_type_post.setText(tr(I18N.MainWindow.LABEL_QUOTE_CONFIG))
            ui.combox_type_post.setToolTip(tr(I18N.MainWindow.TOOLTIP_POST_TYPE))
            ui.label_post_on.setText(tr(I18N.MainWindow.LABEL_POST_ON))
            ui.label_post.setText(tr(I18N.MainWindow.LABEL_POST_AMOUNT).format(symbol=currency_symbol))
            ui.label_post.setToolTip(tr(I18N.MainWindow.TOOLTIP_POST_AMOUNT))
            ui.doublespinbox_post_price.setToolTip(tr(I18N.MainWindow.TOOLTIP_GRAMS_INPUT))
            ui.label_post_range.setText(tr(I18N.MainWindow.LABEL_POST_RANGE))
            ui.label_post_range.setToolTip(tr(I18N.MainWindow.TOOLTIP_POST_TYPE))

            # --- Cliente ---
            ui.label_client_razon_social.setText(tr(I18N.MainWindow.LABEL_SOCIAL_REASON))
            ui.checkbox_client_optional.setText(tr(I18N.MainWindow.LABEL_OPTIONAL))
            ui.checkbox_client_optional.setToolTip(tr(I18N.MainWindow.TOOLTIP_OPTIONAL_CLIENT))
            ui.btn_select_client.setText(tr(I18N.MainWindow.BTN_CLIENT_SELECT))
            ui.btn_select_client.setToolTip(tr(I18N.MainWindow.TOOLTIP_SELECT_CLIENT))
            ui.btn_cleaner_client.setToolTip(tr(I18N.MainWindow.TOOLTIP_CLEAN_FIELDS))

            # --- Impresora ---
            ui.label_desc_printer.setText(tr(I18N.MainWindow.LABEL_DESCRIPTION))
            ui.combox_desc_printer.setToolTip(tr(I18N.MainWindow.TOOLTIP_SELECT_PRINTER_COMBO))
            ui.combox_desc_printer.setPlaceholderText(tr(I18N.MainWindow.PLACEHOLDER_SELECT_PRINTER))
            ui.btn_select_printer_3d.setText(tr(I18N.MainWindow.BTN_PRINTER_SELECT))
            ui.btn_select_printer_3d.setToolTip(tr(I18N.MainWindow.TOOLTIP_SELECT_PRINTER_BTN))
            ui.btn_cleaner_printer_3d.setToolTip(tr(I18N.MainWindow.TOOLTIP_CLEAN_FIELDS))

            # --- Pieza ---
            ui.label_time_print.setText(tr(I18N.MainWindow.LABEL_PRINT_TIME))
            ui.label_time_print.setToolTip(tr(I18N.MainWindow.TOOLTIP_PRINT_TIME_BATCH))
            ui.label_gram_filament.setText(tr(I18N.MainWindow.LABEL_FILAMENT_GRAMS))
            ui.label_gram_filament.setToolTip(tr(I18N.MainWindow.TOOLTIP_GRAMS_BATCH))
            ui.spinbox_gram_piece.setToolTip(tr(I18N.MainWindow.TOOLTIP_GRAMS_INPUT))
            ui.label.setText(tr(I18N.MainWindow.LABEL_QUANTITY_GR))
            ui.label.setToolTip(tr(I18N.MainWindow.TOOLTIP_QUANTITY_GR))
            ui.label_hour.setText(tr(I18N.MainWindow.LABEL_HOURS))
            ui.label_hour.setToolTip(tr(I18N.MainWindow.TOOLTIP_UNITS_LABEL))
            ui.spinbox_cant_piece.setToolTip(tr(I18N.MainWindow.TOOLTIP_BATCHES_INPUT))
            ui.label_price_product_2.setText(tr(I18N.MainWindow.LABEL_BATCHES))
            ui.label_price_product_2.setToolTip(tr(I18N.MainWindow.TOOLTIP_BATCHES_LABEL))
            ui.label_3.setText(tr(I18N.MainWindow.LABEL_QUANTITY_UD))
            ui.label_3.setToolTip(tr(I18N.MainWindow.TOOLTIP_QUANTITY_UD))
            ui.label_minute.setText(tr(I18N.MainWindow.LABEL_MINUTES))
            ui.label_minute.setToolTip(tr(I18N.MainWindow.TOOLTIP_UNITS_LABEL))
            ui.spinbox_time_minute_piece.setToolTip(tr(I18N.MainWindow.TOOLTIP_MINUTES_INPUT))
            ui.spinbox_time_hour_piece.setToolTip(tr(I18N.MainWindow.TOOLTIP_HOURS_INPUT))

            # --- Operaciones (tab Presupuesto) ---
            ui.btn_clear_all_selected.setText(tr(I18N.Buttons.CLEAR))
            ui.btn_clear_all_selected.setToolTip(tr(I18N.MainWindow.TOOLTIP_CLEAR_ALL))
            ui.btn_calculator.setText(tr(I18N.Buttons.CALCULATE))
            ui.btn_calculator.setToolTip(tr(I18N.MainWindow.TOOLTIP_CALCULATE))
            ui.btn_tuning.setText(tr(I18N.MainWindow.BTN_TUNING))
            ui.btn_tuning.setToolTip(tr(I18N.MainWindow.TOOLTIP_TUNING))

            # --- Anticipo ---
            ui.label_advance_on.setText(tr(I18N.MainWindow.LABEL_ADVANCE))
            ui.spinbox_advance.setToolTip(tr(I18N.MainWindow.TOOLTIP_ADVANCE_PCT_INPUT))
            ui.label_advance.setText(tr(I18N.MainWindow.LABEL_ADVANCE_PCT))
            ui.label_advance.setToolTip(tr(I18N.MainWindow.TOOLTIP_ADVANCE_PCT_LABEL))

            # --- Acción ---
            ui.btn_generate.setToolTip(tr(I18N.MainWindow.TOOLTIP_GENERATE))
            ui.btn_select_type_doc.setToolTip(tr(I18N.MainWindow.TOOLTIP_SELECT_DOC_TYPE))
            ui.btn_preview.setText(tr(I18N.MainWindow.BTN_PREVIEW_MAIN))
            ui.btn_preview.setToolTip(tr(I18N.MainWindow.TOOLTIP_PREVIEW))
            ui.btn_close.setText(tr(I18N.MainWindow.BTN_CLOSE_MAIN))
            ui.btn_close.setToolTip(tr(I18N.MainWindow.TOOLTIP_CLOSE_BTN))

            # --- Tab Historial ---
            ui.btn_open_quote.setText(tr(I18N.MainWindow.BTN_FILE))
            ui.btn_delete_quote.setText(tr(I18N.Buttons.DELETE))
            ui.btn_delete_quote.setToolTip(tr(I18N.MainWindow.TOOLTIP_DELETE_QUOTE))
            ui.btn_report_quotes.setText(tr(I18N.MainWindow.BTN_REPORTS))
            ui.btn_report_quotes.setToolTip(tr(I18N.MainWindow.TOOLTIP_BTN_REPORTS))
            ui.label_desde.setText(tr(I18N.MainWindow.LABEL_FROM))
            ui.label_hasta.setText(tr(I18N.MainWindow.LABEL_TO))
            ui.btn_search_4.setText(tr(I18N.MainWindow.BTN_QUERY))
            ui.linedit_search_4.setToolTip(tr(I18N.MainWindow.TOOLTIP_SEARCH_MIN_DIGITS))
            ui.btn_cleaner_4.setToolTip(tr(I18N.MainWindow.TOOLTIP_CLEAN_FIELDS))
            # Headers tabla quotes
            ui.qtable_quote.horizontalHeaderItem(1).setText(tr(I18N.MainWindow.COL_NUM))
            ui.qtable_quote.horizontalHeaderItem(2).setText(tr(I18N.MainWindow.COL_CLIENT))
            ui.qtable_quote.horizontalHeaderItem(3).setText(tr(I18N.MainWindow.COL_AMOUNT))
            ui.qtable_quote.horizontalHeaderItem(4).setText(tr(I18N.MainWindow.COL_CREATED))
            ui.qtable_quote.horizontalHeaderItem(5).setText(tr(I18N.MainWindow.COL_FILE))

            # --- Tab Inventario (filamentos) ---
            ui.btn_add_more_filament.setText(tr(I18N.MainWindow.BTN_ADD_LABEL))
            ui.btn_add_more_filament.setToolTip(tr(I18N.MainWindow.TOOLTIP_ADD_FILAMENT_BTN))
            ui.btn_mod_filament.setText(tr(I18N.MainWindow.BTN_MODIFY))
            ui.btn_mod_filament.setToolTip(tr(I18N.MainWindow.TOOLTIP_EDIT_FILAMENT))
            ui.btn_delete_filament.setText(tr(I18N.Buttons.DELETE))
            ui.btn_delete_filament.setToolTip(tr(I18N.MainWindow.TOOLTIP_DELETE_FILAMENT))
            ui.btn_add_filament.setText(tr(I18N.MainWindow.BTN_FILAMENT_SELECT))
            ui.btn_add_filament.setToolTip(tr(I18N.MainWindow.TOOLTIP_ADD_NEW_FILAMENT))
            ui.btn_search.setText(tr(I18N.MainWindow.BTN_QUERY))
            ui.linedit_search.setToolTip(tr(I18N.MainWindow.TOOLTIP_SEARCH_MIN_DIGITS))
            ui.btn_cleaner.setToolTip(tr(I18N.MainWindow.TOOLTIP_CLEAN_FIELDS))
            # Headers tabla filamentos
            ui.qtable_filaments.horizontalHeaderItem(1).setText(tr(I18N.MainWindow.COL_DESCRIPTION))
            ui.qtable_filaments.horizontalHeaderItem(2).setText(tr(I18N.MainWindow.COL_STOCK))
            ui.qtable_filaments.horizontalHeaderItem(3).setText(tr(I18N.MainWindow.COL_TYPE))
            ui.qtable_filaments.horizontalHeaderItem(4).setText(tr(I18N.MainWindow.COL_BRAND))
            ui.qtable_filaments.horizontalHeaderItem(5).setText(tr(I18N.MainWindow.COL_COLOR))
            ui.qtable_filaments.horizontalHeaderItem(6).setText(tr(I18N.MainWindow.COL_PRICE))

            # --- Tab Impresoras ---
            ui.btn_mod_printer.setText(tr(I18N.MainWindow.BTN_MODIFY))
            ui.btn_mod_printer.setToolTip(tr(I18N.MainWindow.TOOLTIP_EDIT_PRINTER))
            ui.btn_delete_printer.setText(tr(I18N.Buttons.DELETE))
            ui.btn_delete_printer.setToolTip(tr(I18N.MainWindow.TOOLTIP_DELETE_PRINTER))
            ui.btn_add_printer.setText(tr(I18N.MainWindow.BTN_ADD_PRINTER))
            ui.btn_add_printer.setToolTip(tr(I18N.MainWindow.TOOLTIP_ADD_NEW_PRINTER))
            ui.btn_search_2.setText(tr(I18N.MainWindow.BTN_QUERY))
            ui.linedit_search_2.setToolTip(tr(I18N.MainWindow.TOOLTIP_SEARCH_MIN_DIGITS))
            ui.btn_cleaner_2.setToolTip(tr(I18N.MainWindow.TOOLTIP_CLEAN_FIELDS))
            # Headers tabla impresoras
            ui.qtable_printers.horizontalHeaderItem(1).setText(tr(I18N.MainWindow.COL_DESCRIPTION))
            ui.qtable_printers.horizontalHeaderItem(2).setText(tr(I18N.MainWindow.COL_MODEL))
            ui.qtable_printers.horizontalHeaderItem(3).setText(tr(I18N.MainWindow.COL_BRAND))
            ui.qtable_printers.horizontalHeaderItem(4).setText(tr(I18N.MainWindow.COL_CONSUMPTION))
            ui.qtable_printers.horizontalHeaderItem(5).setText(tr(I18N.MainWindow.COL_COST))
            ui.qtable_printers.horizontalHeaderItem(6).setText(tr(I18N.MainWindow.COL_STATUS_HDR))

            # --- Tab Clientes ---
            ui.btn_default_customer.setText(tr(I18N.MainWindow.BTN_SET_DEFAULT))
            ui.btn_mod_customer.setText(tr(I18N.MainWindow.BTN_MODIFY))
            ui.btn_mod_customer.setToolTip(tr(I18N.MainWindow.TOOLTIP_EDIT_CUSTOMER))
            ui.btn_delete_customer.setText(tr(I18N.Buttons.DELETE))
            ui.btn_delete_customer.setToolTip(tr(I18N.MainWindow.TOOLTIP_DELETE_CUSTOMER))
            ui.btn_add_customer.setText(tr(I18N.MainWindow.BTN_ADD_CUSTOMER))
            ui.btn_add_customer.setToolTip(tr(I18N.MainWindow.TOOLTIP_ADD_NEW_CUSTOMER))
            ui.btn_search_3.setText(tr(I18N.MainWindow.BTN_QUERY))
            ui.linedit_search_3.setToolTip(tr(I18N.MainWindow.TOOLTIP_SEARCH_MIN_DIGITS))
            ui.btn_cleaner_3.setToolTip(tr(I18N.MainWindow.TOOLTIP_CLEAN_FIELDS))
            # Headers tabla clientes
            ui.qtable_customers.horizontalHeaderItem(1).setText(tr(I18N.MainWindow.COL_SOCIAL_REASON))
            ui.qtable_customers.horizontalHeaderItem(2).setText(LocaleManager().get_tax_id_label())
            ui.qtable_customers.horizontalHeaderItem(3).setText(tr(I18N.MainWindow.COL_PHONE))
            ui.qtable_customers.horizontalHeaderItem(4).setText(tr(I18N.MainWindow.COL_EMAIL))
            ui.qtable_customers.horizontalHeaderItem(5).setText(tr(I18N.MainWindow.COL_PREFERENCE))

            # --- Bottom bar ---
            ui.plaintextedit_status.setPlaceholderText(tr(I18N.MainWindow.PLACEHOLDER_PROCESSES))
            if hasattr(ui, 'version') and ui.version:
                ui.version.setToolTip(tr(I18N.MainWindow.TOOLTIP_VERSION))

            # --- Actualizar LABELS para que los métodos de detalle usen el idioma activo ---
            self.LABELS['filament_type'] = tr(I18N.MainWindow.DETAIL_FILAMENT_TYPE)
            self.LABELS['filament_color'] = tr(I18N.MainWindow.DETAIL_FILAMENT_COLOR)
            self.LABELS['filament_price'] = tr(I18N.MainWindow.DETAIL_FILAMENT_PRICE)
            self.LABELS['filament_stock'] = tr(I18N.MainWindow.DETAIL_FILAMENT_STOCK)
            self.LABELS['printer_brand'] = tr(I18N.MainWindow.DETAIL_PRINTER_BRAND)
            self.LABELS['printer_model'] = tr(I18N.MainWindow.DETAIL_PRINTER_MODEL)
            self.LABELS['printer_consumption'] = tr(I18N.MainWindow.DETAIL_PRINTER_CONSUMPTION)
            self.LABELS['client_name'] = tr(I18N.MainWindow.LABEL_SOCIAL_REASON)
            locale_mgr = LocaleManager()
            self.LABELS['client_ruc'] = locale_mgr.get_tax_id_label()

            # --- Actualizar opciones del combobox de tipo de post-procesado ---
            combo = self.ui.combox_type_post
            if combo.count() >= 2:
                combo.setItemText(0, tr(I18N.MainWindow.POST_TYPE_BATCH))
                combo.setItemText(1, tr(I18N.MainWindow.POST_TYPE_JOB))

        except Exception as e:
            logger.error("MainWindow", f"Error en _apply_dynamic_labels: {str(e)}")
            logger.log_exception("MainWindow", e, "_apply_dynamic_labels")

    def _setup_settings_tab(self):
        """Configura el tab de ajustes del sistema"""
        try:
            # Crear el widget de ajustes
            self.settings_widget = SystemSettingsWidget()
            
            # Crear el presenter para los ajustes
            self.settings_presenter = SystemSettingsPresenter(self.settings_widget)
            
            # Verificar si el frame_ajust ya tiene un layout
            existing_layout = self.ui.frame_ajust.layout()
            if existing_layout is not None:
                # Limpiar el layout existente
                while existing_layout.count():
                    child = existing_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            else:
                # Crear un nuevo layout
                existing_layout = QVBoxLayout(self.ui.frame_ajust)
                existing_layout.setContentsMargins(0, 0, 0, 0)
            
            # Agregar el widget de ajustes
            existing_layout.addWidget(self.settings_widget)
            
            # Cargar las configuraciones iniciales
            self.settings_presenter.load_all_settings()
            
        except Exception as e:
            logger.error("MainWindow", f"Error al configurar el tab de ajustes: {str(e)}")
            logger.log_exception("MainWindow", e, "_setup_settings_tab")
    
    def _setup_development_widgets(self):
        """Configura widgets para funcionalidades en desarrollo"""
        try:
            # Configurar tooltip del botón de configuraciones
            self.ui.btn_settings_app.setToolTip(
                tr(I18N.MainWindow.TOOLTIP_SETTINGS_APP)
            )
            
        except Exception as e:
            logger.error("MainWindow", f"Error al configurar widgets de desarrollo: {str(e)}")
            logger.log_exception("MainWindow", e, "_setup_development_widgets")
    
    def _setup_custom_widgets(self):
        """Configura widgets personalizados para reemplazar elementos estándar"""
        try:
            # Importar el toggle personalizado
            from presentation.widgets.toggle_mod.custom_toggle import PyToggle
            
            # Desactivar scroll de mouse en TextEdits de solo lectura
            self._disable_wheel_on_readonly_textedits()
            
            # Configurar el sistema de anticipo
            self._setup_advance_system()
            
            # Configurar el sistema de post-procesado
            self._setup_post_system()
            
            # Recolorear ícono del botón toggle panel al gris del bottomBar
            self._recolor_toggle_panel_icon()
            
        except Exception as e:
            logger.error("MainWindow", f"Error al configurar widgets personalizados: {str(e)}")            
    
    def _recolor_toggle_panel_icon(self):
        """Precarga los íconos del toggle panel: normal (gris) y hover (blanco/negro según tema).
        Nota: Los nombres de los SVGs están invertidos respecto a su visual:
        - collapse_v1 muestra flecha '>' (visual: expandir)
        - expand_v1 muestra flecha '<' (visual: colapsar)
        """
        try:
            from presentation.common.icon_utils import IconUtils
            from core.utils.path_helper import build_resource_path
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QIcon

            color_normal = "#717E95"
            app = QApplication.instance()
            is_dark = hasattr(app, 'palette_manager') and app.palette_manager.is_dark_mode
            color_hover = "#FFFFFF" if is_dark else "#000000"

            svg_collapsed = build_resource_path("resources/icons/sys_layout_sidebar_right_collapse_v1.svg")
            svg_expanded = build_resource_path("resources/icons/sys_layout_sidebar_right_expand_v1.svg")

            # Íconos normales (gris)
            self._icon_panel_collapsed = IconUtils.recolor_icon_svg(svg_collapsed, color_normal)
            self._icon_panel_expanded = IconUtils.recolor_icon_svg(svg_expanded, color_normal)
            # Íconos hover (blanco en oscuro, negro en claro)
            self._icon_panel_collapsed_hover = IconUtils.recolor_icon_svg(svg_collapsed, color_hover)
            self._icon_panel_expanded_hover = IconUtils.recolor_icon_svg(svg_expanded, color_hover)

            # Estado inicial: panel cerrado
            self.ui.btn_toggle_panel.setIcon(self._icon_panel_collapsed)

            # Instalar event filter para hover
            self.ui.btn_toggle_panel.installEventFilter(self)
            self.ui.btn_toggle_panel.setProperty("_toggle_panel_hover", True)
        except Exception as e:
            self._icon_panel_collapsed = None
            self._icon_panel_expanded = None
            self._icon_panel_collapsed_hover = None
            self._icon_panel_expanded_hover = None
            logger.error("MainWindow", f"Error recoloreando íconos toggle panel: {str(e)}")

    def _disable_wheel_on_readonly_textedits(self):
        """Desactiva el scroll de mouse en QTextEdits de solo visualización."""
        targets = [
            self.ui.textEdit_details_filament_select,
            self.ui.textEdit_details_printer_select,
            self.ui.textEdit_name_client_select,
            self.ui.textEdit_ruc_ci_client_select,
            self.ui.textEdit_details_gcode,
            self.ui.textEdit_details_multi_filament_select,
        ]
        for widget in targets:
            widget.installEventFilter(self)
            widget.setProperty("_block_wheel", True)

    def eventFilter(self, obj, event):
        """Filtro de eventos:
        - Selecciona todo el texto en spinboxes con valor 0 al hacer click izquierdo.
        - Bloquea la rueda en widgets con propiedad '_block_wheel'.
        - Cambia icono en hover si el widget tiene '_toggle_panel_hover'.
        """
        # --- SelectAll en spinbox con valor 0 al recibir foco ---
        if event.type() == QEvent.FocusIn and obj.property("_select_all_if_zero"):
            if obj.value() == 0:
                QTimer.singleShot(0, obj.selectAll)

        # --- Bloqueo de rueda ---
        if event.type() == QEvent.Wheel and obj.property("_block_wheel"):
            return True  # bloquea el evento de rueda

        # --- Hover en panel toggle ---
        if obj.property("_toggle_panel_hover"):
            if event.type() == QEvent.HoverEnter:
                self._update_toggle_panel_icon(hover=True)
                return False
            elif event.type() == QEvent.HoverLeave:
                self._update_toggle_panel_icon(hover=False)
                return False

        # --- Tooltip custom para botones de slot multicolor ---
        if hasattr(self, '_mc_buttons') and obj in self._mc_buttons:
            if event.type() == QEvent.Type.Enter:
                idx = self._mc_buttons.index(obj)
                text = self._mc_slot_tooltips.get(idx, "")
                if text:
                    self._slot_tooltip_mgr.show_delayed(obj, text)
                return False
            elif event.type() == QEvent.Type.Leave:
                self._slot_tooltip_mgr.hide()
                return False

        # Si no se manejó nada, delegar al padre
        return super().eventFilter(obj, event)

    def _setup_dynamic_app_info(self):
        """Configura la información dinámica de la aplicación usando build_config.py"""
        try:
            # 1. titleRightInfo - Descripción de la aplicación
            self.ui.titleRightInfo.setText(tr(I18N.App.DESCRIPTION))
            
            # 2. version - Versión de la aplicación (CLICKEABLE)
            from config.build_config import get_main_window_version
            version_text = get_main_window_version()
            if hasattr(self.ui, 'version') and self.ui.version:
                self.ui.version.setText(version_text)
                # Hacer clickeable
                self._make_label_clickeable(self.ui.version, "Clic para ver información detallada del build")
                self.ui.version.mousePressEvent = self._on_version_clicked
            
            # 3. donationLabel - Botón para donaciones (CLICKEABLE)
            if hasattr(self.ui, 'donationLabel') and self.ui.donationLabel:
                self.update_donation_label()  # Actualizar con mensaje de donaciones
                # Hacer clickeable
                self._make_label_clickeable(self.ui.donationLabel, "Clic para apoyar el proyecto con una donación")
                self.ui.donationLabel.mousePressEvent = self._on_donation_clicked
            
            # 4. eventLabel_pb - Cartelera de eventos de donaciones (ANIMADO)
            if hasattr(self.ui, 'eventLabel_pb') and self.ui.eventLabel_pb:
                self._setup_donation_event_label()
            
            # 5. topLogoInfo - Abre diálogo About al hacer click
            if hasattr(self.ui, 'topLogoInfo') and self.ui.topLogoInfo:
                self.ui.topLogoInfo.mousePressEvent = self._on_version_clicked
            
        except Exception as e:
            pass
    
    def _make_label_clickeable(self, label, tooltip_text: str):
        """Hace que un QLabel sea clickeable con estilo visual"""
        try:
            # Establecer cursor de mano
            label.setCursor(QCursor(Qt.PointingHandCursor))
            
            # Actualizar tooltip
            label.setToolTip(tooltip_text)
            
            # Aplicar estilo para indicar que es clickeable
            original_style = label.styleSheet()
            clickable_style = """
                QLabel {
                    font-weight: bold;
                }
                QLabel:hover {
                    color: #ffaaff;
                }
            """
            label.setStyleSheet(f"{original_style}\n{clickable_style}")
            
        except Exception as e:
            logger.error("MainWindow", f"Error haciendo label clickeable: {str(e)}")
            logger.log_exception("MainWindow", e, "_make_label_clickeable")
    
    def _on_version_clicked(self, event):
        """Maneja el click en el label de versión"""
        try:
            self.build_info_requested.emit()
        except Exception as e:
            logger.error("MainWindow", f"Error manejando click en version: {str(e)}")
            logger.log_exception("MainWindow", e, "_on_version_clicked")
    
    def _on_donation_clicked(self, event):
        """Maneja el click en el label de donaciones"""
        try:
            self.donation_requested.emit()
        except Exception as e:
            logger.error("MainWindow", f"Error manejando click en donaciones: {str(e)}")
            logger.log_exception("MainWindow", e, "_on_donation_clicked")
    
    def update_donation_label(self):
        """
        Actualiza el label de donaciones con un mensaje motivador
        """
        try:
            # Configuración del mensaje de donaciones
            text = tr(I18N.MainWindow.DONATION_LABEL)
            color = "#4CAF50"  # Verde amigable
            tooltip = tr(I18N.MainWindow.DONATION_TOOLTIP)
            
            # Aplicar al label
            if hasattr(self.ui, 'donationLabel') and self.ui.donationLabel:
                self.ui.donationLabel.setText(text)
                self.ui.donationLabel.setToolTip(tooltip)
                
                # Aplicar color y font weight
                self.ui.donationLabel.setStyleSheet(f"""
                    QLabel {{
                        color: {color};
                        font-weight: bold;
                    }}
                    QLabel:hover {{
                        color: #66BB6A;
                    }}
                """)
            
            # Actualizar también la cartelera de eventos
            self.update_donation_event_label()
                
        except Exception as e:
            logger.error("MainWindow", f"Error actualizando label de donaciones: {str(e)}")
            logger.log_exception("MainWindow", e, "update_donation_label")
            # Fallback silencioso
            if hasattr(self.ui, 'donationLabel') and self.ui.donationLabel:
                self.ui.donationLabel.setText(tr(I18N.MainWindow.DONATION_FALLBACK))
                self.ui.donationLabel.setStyleSheet("color: #4CAF50;")
    
    def _setup_donation_event_label(self):
        """
        Configura el widget de cartelera animada para eventos de donaciones
        Reemplaza el QLabel estático por un widget animado personalizado
        """
        try:
            # Obtener el layout que contiene el eventLabel_pb original
            parent_layout = self.ui.eventLabel_pb.parent().layout()
            
            if parent_layout:
                # Encontrar el índice del widget original
                index = parent_layout.indexOf(self.ui.eventLabel_pb)
                
                # Eliminar el widget original
                parent_layout.removeWidget(self.ui.eventLabel_pb)
                self.ui.eventLabel_pb.deleteLater()
                
                # Crear el nuevo widget animado
                self.ui.eventLabel_pb = DonationEventLabel(self.ui.bottomBar)
                
                # Insertar en la misma posición
                parent_layout.insertWidget(index, self.ui.eventLabel_pb)
                
                # Actualizar con el estado actual
                self.update_donation_event_label()
            
        except Exception as e:
            pass
    
    def update_donation_event_label(self):
        """
        Actualiza los mensajes de la cartelera animada con mensajes de donaciones
        """
        try:
            if not hasattr(self.ui, 'eventLabel_pb') or not isinstance(self.ui.eventLabel_pb, DonationEventLabel):
                return
            
            # Actualizar el widget con mensajes de donaciones
            self.ui.eventLabel_pb.set_donation_messages()
            
        except Exception as e:
            logger.error("MainWindow", f"Error actualizando cartelera de donaciones: {str(e)}")
            
        except Exception as e:
            logger.error("MainWindow", f"Error actualizando cartelera de licencias: {str(e)}")
    
    def _setup_advance_system(self):
        """Configura el sistema de anticipo"""
        try:
            # ✅ REEMPLAZAR checkbox_advance con PyToggle personalizado
            from presentation.widgets.toggle_mod.custom_toggle import PyToggle
            
            # Obtener la posición y el padre del checkbox original
            original_checkbox = self.ui.checkbox_advance
            parent_widget = original_checkbox.parent()
            original_geometry = original_checkbox.geometry()
            original_checked = original_checkbox.isChecked()
            
            # Crear el nuevo toggle personalizado para anticipo
            self.custom_advance_toggle = PyToggle(width=50, height=25, parent=parent_widget)
            
            # Configurar posición (manteniendo la posición original)
            self.custom_advance_toggle.move(
                original_geometry.x(), 
                original_geometry.y()
            )
            
            # Configurar estado inicial (desactivado por defecto)
            self.custom_advance_toggle.setChecked(False)
            
            # Ocultar el checkbox original
            original_checkbox.hide()
            
            # Mostrar el toggle personalizado
            self.custom_advance_toggle.show()
            
            # Configurar tooltip
            self.custom_advance_toggle.setToolTip(tr(I18N.MainWindow.TOOLTIP_ADVANCE_TOGGLE))
            
            # SpinBox configurado pero deshabilitado inicialmente
            self.ui.spinbox_advance.setMinimum(0)  # ✅ Permitir 0% para validación
            self.ui.spinbox_advance.setMaximum(100)
            # El valor inicial se establecerá en _apply_default_advance()
            self.ui.spinbox_advance.setValue(0)  # ✅ Iniciar en 0% por defecto
            self.ui.spinbox_advance.setSuffix("%")
            self.ui.spinbox_advance.setEnabled(False)  # Deshabilitado por defecto
            
            # ✅ Conectar señal del toggle personalizado (no del checkbox original)
            self.custom_advance_toggle.stateChanged.connect(self._on_advance_checkbox_changed)
            
            # Conectar señal del spinbox para recalcular cuando cambie el porcentaje
            self.ui.spinbox_advance.valueChanged.connect(self._on_advance_percentage_changed_with_delay)
            
        except Exception as e:
            logger.error("MainWindow", f"Error al configurar sistema de anticipo: {str(e)}")
            logger.log_exception("MainWindow", e, "_setup_advance_system")
    
    def _setup_post_system(self):
        """Configura el sistema de post-procesado"""
        try:
            # ✅ REEMPLAZAR checkbox_post con PyToggle personalizado
            from presentation.widgets.toggle_mod.custom_toggle import PyToggle
            
            # Obtener la posición y el padre del checkbox original
            original_checkbox = self.ui.checkbox_post
            parent_widget = original_checkbox.parent()
            
            # ✅ Crear PyToggle personalizado en la posición del checkbox original
            self.custom_post_toggle = PyToggle(width=50, height=25, parent=parent_widget)
            
            # Posicionar el toggle en el lugar del checkbox original
            self.custom_post_toggle.move(
                original_checkbox.x(), 
                original_checkbox.y()
            )
            
            # Configuración inicial del toggle (desactivado por defecto)
            self.custom_post_toggle.setChecked(False)
            
            # ✅ Ocultar el checkbox original (no eliminarlo para evitar errores de UI)
            original_checkbox.hide()
            
            # Mostrar el toggle personalizado
            self.custom_post_toggle.show()
            
            # Configurar tooltip
            self.custom_post_toggle.setToolTip(tr(I18N.MainWindow.TOOLTIP_POST_TOGGLE))
            
            # Configurar el doublespinbox nativo con decimales dinámicos
            from core.utils.currency_helper import CurrencyHelper
            CurrencyHelper.configure_spinbox(self.ui.doublespinbox_post_price)
            self.ui.doublespinbox_post_price.setMinimum(0)
            self.ui.doublespinbox_post_price.setMaximum(999999999)
            self.ui.doublespinbox_post_price.setValue(0)
            self.ui.doublespinbox_post_price.setEnabled(False)
            self.ui.doublespinbox_post_price.installEventFilter(self)
            self.ui.doublespinbox_post_price.setProperty("_select_all_if_zero", True)
            
            # ✅ Configurar ComboBox de tipo de post-procesado
            self.ui.combox_type_post.clear()
            self.ui.combox_type_post.addItem(tr(I18N.MainWindow.POST_TYPE_BATCH), "lote")
            self.ui.combox_type_post.addItem(tr(I18N.MainWindow.POST_TYPE_JOB), "trabajo")
            self.ui.combox_type_post.setCurrentIndex(0)  # Por defecto "Cobrar por Lote"
            self.ui.combox_type_post.setEnabled(False)  # Deshabilitado por defecto
            
            # ✅ Conectar señal del toggle personalizado (no del checkbox original)
            self.custom_post_toggle.stateChanged.connect(self._on_post_checkbox_changed)
            
            # Conectar señal del spinbox para recalcular cuando cambie el monto
            self.ui.doublespinbox_post_price.valueChanged.connect(self._on_post_amount_changed_with_delay)
            
            # Conectar señal del combobox para recalcular cuando cambie el tipo
            self.ui.combox_type_post.currentTextChanged.connect(self._on_post_type_changed)
            
        except Exception as e:
            logger.error("MainWindow", f"Error al configurar sistema de post-procesado: {str(e)}")
            logger.log_exception("MainWindow", e, "_setup_post_system")
    
    def _connect_ui_signals(self):
        """Conecta las señales de la UI con los métodos locales"""
        # Botones de búsqueda/selección
        self.ui.btn_select_client.clicked.connect(self.client_search_requested.emit)
        self.ui.btn_select_filament.clicked.connect(self.filament_search_requested.emit)
        self.ui.btn_select_printer_3d.clicked.connect(self.printer_search_requested.emit)
        self.ui.btn_load_gcode.clicked.connect(self.load_gcode_requested.emit)
        self.ui.combox_desc_printer.currentIndexChanged.connect(self._on_printer_combox_changed)
        self.ui.combox_desc_filament.currentIndexChanged.connect(self._on_filament_combox_changed)
        
        # Botones de operaciones
        self.ui.btn_calculator.clicked.connect(self.calculate_quote_requested.emit)  # Calcular
        self.ui.btn_clear_all_selected.clicked.connect(self.clear_form_requested.emit)
        self.ui.btn_preview.clicked.connect(self.preview_requested.emit)        # Vista Previa
        self._setup_generate_menu()                                             # Menú Generar
        
        # Configurar shortcuts de teclado
        self._setup_keyboard_shortcuts()
        
        # Botón de configuraciones - emitir señal al presenter
        self.ui.btn_settings_app.clicked.connect(self.settings_requested.emit)
        
        # Botón de cerrar aplicación - emitir señal al presenter
        self.ui.btn_close.clicked.connect(self.close_application_requested.emit)
        
        # Botón Param — abre panel de parámetros rápidos (desactivado hasta v1.2.3)
        self.ui.btn_tuning.clicked.connect(self._open_quick_params)

        # Botón toggle panel de procesos
        self.ui.btn_toggle_panel.clicked.connect(self._toggle_process_view)
        
        # SpinBoxes para detectar cambios
        self.ui.spinbox_time_hour_piece.valueChanged.connect(self._on_time_changed)
        self.ui.spinbox_time_minute_piece.valueChanged.connect(self._on_time_changed)

        # SelectAll al recibir foco cuando el valor es 0
        self.ui.spinbox_time_hour_piece.installEventFilter(self)
        self.ui.spinbox_time_hour_piece.setProperty("_select_all_if_zero", True)
        self.ui.spinbox_time_minute_piece.installEventFilter(self)
        self.ui.spinbox_time_minute_piece.setProperty("_select_all_if_zero", True)
        
        # Configurar rango extendido para minutos para permitir autoconversión
        self.ui.spinbox_time_minute_piece.setMaximum(999)  # Permitir valores altos para autoconversión
        self.ui.spinbox_time_minute_piece.setToolTip(tr(I18N.MainWindow.TOOLTIP_MINUTES_SPINBOX))
        
        # Campos con delay para evitar spam en logs
        self.ui.spinbox_gram_piece.valueChanged.connect(self._on_weight_changed)
        self.ui.spinbox_cant_piece.valueChanged.connect(self._on_quantity_changed)
        
        # Checkbox de cliente opcional
        self.ui.checkbox_client_optional.toggled.connect(self.customer_optional_changed.emit)
    
    # ── Modos de generación ──────────────────────────────────────────────────
    def _get_generate_modes(self):
        return {
            "pdf": {
                "icon":   ":/resources/resources/icons/sys_file_type_pdf.svg",
                "label":  tr(I18N.MainWindow.GENERATE_PDF_LABEL),
                "menu_label": tr(I18N.MainWindow.GENERATE_PDF_MENU_LABEL),
                "signal": "save_quote_requested",
                "tooltip": tr(I18N.MainWindow.GENERATE_PDF_TOOLTIP),
            },
            "note": {
                "icon":   ":/resources/resources/icons/sys_file_type_note.svg",
                "label":  tr(I18N.MainWindow.GENERATE_NOTE_LABEL),
                "menu_label": tr(I18N.MainWindow.GENERATE_NOTE_MENU_LABEL),
                "signal": "generate_note_requested",
                "tooltip": tr(I18N.MainWindow.GENERATE_NOTE_TOOLTIP),
            },
        }

    def _setup_generate_menu(self):
        """Configura los dos botones de generación como un combo custom.
        btn_select_type_doc despliega menú de tipo; btn_generate ejecuta el modo activo."""
        from PySide6.QtWidgets import QMenu
        from core.managers.app_preferences_manager import AppPreferencesManager

        prefs = AppPreferencesManager()
        initial_mode = prefs.get_default_generate_mode()
        _modes = self._get_generate_modes()
        if initial_mode not in _modes:
            initial_mode = "pdf"

        self._generate_mode = initial_mode
        menu = QMenu(self)
        for mode_key, mode in _modes.items():
            action = menu.addAction(mode["menu_label"])
            action.setData(mode_key)
            action.triggered.connect(lambda checked=False, k=mode_key: self._set_generate_mode(k))

        self.ui.btn_select_type_doc.setMenu(menu)

        # Click en el botón principal → ejecutar modo activo
        self.ui.btn_generate.clicked.connect(self._emit_generate_action)

        # Aplicar estado inicial
        self._set_generate_mode(initial_mode)

    def _set_generate_mode(self, mode_key: str):
        """Cambia el icono, texto y acción activa de btn_generate."""
        from PySide6.QtGui import QIcon
        self._generate_mode = mode_key
        mode = self._get_generate_modes()[mode_key]
        self.ui.btn_generate.setIcon(QIcon(mode["icon"]))
        self.ui.btn_generate.setText(mode["label"])
        self.ui.btn_generate.setToolTip(mode["tooltip"])
        self.ui.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)

    def _emit_generate_action(self):
        """Emite la señal correspondiente al modo activo."""
        mode = self._get_generate_modes().get(self._generate_mode, {})
        signal_name = mode.get("signal")
        if signal_name:
            getattr(self, signal_name).emit()

    def get_generate_mode(self) -> str:
        """Retorna el modo activo del botón de generación ('pdf' o 'note')."""
        return self._generate_mode

    def _setup_keyboard_shortcuts(self):
        """Configura los shortcuts de teclado para las acciones principales"""
        # Ctrl+R - Calcular presupuesto
        self.shortcut_generate = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcut_generate.activated.connect(self.calculate_quote_requested.emit)
        self.ui.btn_calculator.setToolTip(tr(I18N.MainWindow.TOOLTIP_CALCULATE))

        # Ctrl+L - Limpiar formulario
        self.shortcut_clear = QShortcut(QKeySequence("Ctrl+L"), self)
        self.shortcut_clear.activated.connect(self.clear_form_requested.emit)
        self.ui.btn_cleaner.setToolTip(tr(I18N.MainWindow.TOOLTIP_CLEAR_FORM))

        # Ctrl+P - Vista previa
        self.shortcut_preview = QShortcut(QKeySequence("Ctrl+P"), self)
        self.shortcut_preview.activated.connect(self.preview_requested.emit)
        self.ui.btn_preview.setToolTip(tr(I18N.MainWindow.TOOLTIP_PREVIEW))

        # Ctrl+G - Generar (modo activo: PDF o Nota)
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+G"), self)
        self.shortcut_save.activated.connect(self._emit_generate_action)

        # Ctrl+9 - Toggle panel de procesos
        self.shortcut_toggle_process = QShortcut(QKeySequence("Ctrl+9"), self)
        self.shortcut_toggle_process.activated.connect(self._toggle_process_view)

        # Ctrl+I - Acerca de (Info)
        self.shortcut_about = QShortcut(QKeySequence("Ctrl+I"), self)
        self.shortcut_about.activated.connect(self.build_info_requested.emit)

        # Ctrl+D - Donaciones (Soporte)
        self.shortcut_donation = QShortcut(QKeySequence("Ctrl+D"), self)
        self.shortcut_donation.activated.connect(self.donation_requested.emit)

        # Inicialmente solo habilitar si estamos en el tab de presupuestos
        self._update_shortcuts_enabled()

        # Conectar cambio de tab para habilitar/deshabilitar shortcuts
        self.ui.tabWidget.currentChanged.connect(self._update_shortcuts_enabled)

    def _update_shortcuts_enabled(self):
        """Habilita los shortcuts específicos solo si el tab activo es el de presupuestos (tab_one)."""
        current_widget = self.ui.tabWidget.currentWidget()
        is_presupuesto = current_widget == self.ui.tab_one
        self.shortcut_generate.setEnabled(is_presupuesto)
        self.shortcut_clear.setEnabled(is_presupuesto)
        self.shortcut_preview.setEnabled(is_presupuesto)
        self.shortcut_save.setEnabled(is_presupuesto)
    
    def _open_quick_params(self):
        """Abre el panel flotante de Parámetros Rápidos centrado sobre el botón btn_tuning."""
        from presentation.widgets.quick_params_mod.quick_params_widget import QuickParamsWidget
        if not hasattr(self, "_quick_params_widget"):
            self._quick_params_widget = QuickParamsWidget(self)
        widget = self._quick_params_widget
        widget.adjustSize()
        btn_rect = self.ui.btn_tuning.rect()
        btn_center = self.ui.btn_tuning.mapToGlobal(btn_rect.center())
        # Centrar horizontalmente y colocar encima del botón
        x = btn_center.x() - widget.width() // 2
        y = btn_center.y() - widget.height() - 8
        widget.move(x, y)
        widget.show()
        widget.raise_()

    def _toggle_process_view(self):
        """
        Toggle del panel de procesos con animación profesional:
        - Abrir: expandir ancho ventana + ancho panel en paralelo (altura=0), luego animar altura panel.
        - Cerrar: colapsar altura panel, luego colapsar ancho ventana + ancho panel en paralelo.
        """
        if self._process_view_visible:
            def after_close():
                self._process_view_visible = False
                self._update_toggle_panel_icon()
            self.panel_animator.close(on_finished=after_close)
        else:
            def after_open():
                self._process_view_visible = True
                self._update_toggle_panel_icon()
            self.panel_animator.open(on_finished=after_open)

    def _update_toggle_panel_icon(self, hover: bool = False):
        """Actualiza el ícono del botón toggle según el estado del panel y hover."""
        if self._process_view_visible:
            icon = self._icon_panel_expanded_hover if hover else self._icon_panel_expanded
        else:
            icon = self._icon_panel_collapsed_hover if hover else self._icon_panel_collapsed
        if icon:
            self.ui.btn_toggle_panel.setIcon(icon)

    # (El método _run_widths_animation ya no es necesario, lo maneja PanelSizeAnimator)
    
    def _setup_animation_panel(self):
        """Configura el animador para el panel de procesos"""
        try :
            self.panel_animator = PanelSizeAnimator(
                main_window=self,
                panel=self.ui.content_process_view,
                collapsed_width=self._collapsed_width,
                expanded_width=self._expanded_width,
                collapsed_height=self._collapsed_height,
                expanded_height=self._expanded_height
            )
        except Exception as e:
            logger.error("MainWindow", f"Error configurando animación del panel de procesos: {str(e)}")
            logger.log_exception("MainWindow", e, "_setup_animation_panel")
    
    def _setup_initial_state(self):
        """Configura el estado inicial de la UI"""
        # Aplicar configuraciones desde preferencias
        self._apply_app_preferences()
        
        # Mensaje inicial en status - solo log en archivo, no en UI
        logger.debug("MainWindow", "Versión aplicación", version=f"{BUILD_CONFIG.get_full_version()} - {BUILD_CONFIG.build.build_type}")
        logger.debug("MainWindow", "Sistema listo para generar presupuestos de impresión 3D")
        
        self.add_separator()
        self.add_system_log(f"¡Bienvenido a {BUILD_CONFIG.app.display_name}!")
        self.add_system_log("Shortcuts disponibles:")
        self.add_system_log("   • Ctrl+G: Generar presupuesto")
        self.add_system_log("   • Ctrl+L: Limpiar formulario")
        self.add_system_log("   • Ctrl+P: Vista previa")
        self.add_system_log("   • Ctrl+R: Calcular presupuesto")
        self.add_system_log("   • Ctrl+9: Mostrar/Ocultar panel de procesos")
        self.add_system_log("   • Ctrl+D: Soporte/Donaciones")
        self.add_system_log("   • F5: Actualizar todas las tablas")
        self.add_system_log("   • Doble click en tab: Actualizar tabla específica")
        self.add_separator()
        # Crear panel multicolor (oculto por defecto)
        self._setup_multicolor_panel()
    
    def _apply_app_preferences(self):
        """Aplica las configuraciones de preferencias al iniciar la aplicación - DELEGADO AL PRESENTER"""
        # La lógica de preferencias ahora está en el presenter como debe ser
        # Solo aplicar configuraciones específicas de UI aquí
        try:
            # 2. Configurar anticipo por defecto (UI específico)
            self._apply_default_advance()
            
        except Exception as e:
            logger.error("MainWindow", f"Error aplicando preferencias de UI: {str(e)}")
            logger.log_exception("MainWindow", e, "_apply_app_preferences")
            self.add_system_log("Error cargando preferencias de UI")
    
    def _apply_default_advance(self):
        """Aplica la configuración por defecto de anticipo según las preferencias"""
        try:
            # Obtener el presenter de preferencias para consultar las reglas
            if hasattr(self, 'presenter') and self.presenter:
                # Crear una instancia temporal del presenter de preferencias para consultar
                from presentation.modules.main.presenters.app_preferences_presenter import AppPreferencesPresenter
                prefs_presenter = AppPreferencesPresenter(None)
                
                # Obtener el modo configurado
                current_mode = prefs_presenter.get_advance_mode()
                
                # Validar que el modo sea válido (usar números enteros)
                valid_modes = [
                    0,  # Ninguno
                    AdvanceMode.AUTO_START.value,   # 1 - Activar por defecto al iniciar
                    AdvanceMode.MIN_AMOUNT.value,   # 2 - Activar al monto mínimo
                    AdvanceMode.MAX_AMOUNT.value,   # 3 - Activar al monto máximo
                    AdvanceMode.MIN_MAX_AMOUNT.value          # 4 - Ambos
                ]
                
                if current_mode not in valid_modes:
                    # Modo inválido detectado - resetear a "Ninguno" y deshabilitar
                    self.add_system_log(f"⚠️ Modo inválido detectado: '{current_mode}' - Reseteando a 'Ninguno'")
                    prefs_presenter.set_advance_mode(0)  # 0 = Ninguno
                    current_mode = 0
                
                # SOLO aplicar configuración automática para el modo "Activar por defecto al iniciar"
                if current_mode == AdvanceMode.AUTO_START.value:
                    # Aplicar anticipo por defecto al iniciar usando método silencioso
                    percentage = prefs_presenter.get_default_advance_percentage_for_startup()
                    self.set_advance_values_silently(True, percentage)
                    self.add_system_log(f"✅ Anticipo activado al iniciar: {percentage}% (modo: 'Activar por defecto al iniciar')")
                else:
                    # Para TODOS los otros modos (Ninguno, mínimo, máximo), INICIAR en estado desactivado
                    self.set_advance_values_silently(False, 0)
                    if current_mode == 0:  # Ninguno
                        # Modo manual - aplicar silenciosamente sin mensaje de log
                        pass
                    else:
                        # Obtener nombre del modo usando el enum
                        mode_name = AdvanceMode.get_display_name(current_mode)
                        self.add_system_log(f"ℹ️ Modo '{mode_name}': Anticipo desactivado - Se activará según reglas de monto")
            else:
                # NO usar fallback que active por defecto - SIEMPRE deshabilitar si no hay presenter
                self.custom_advance_toggle.setChecked(False)
                self.ui.spinbox_advance.setValue(0)
                self.ui.spinbox_advance.setEnabled(False)
                # Deshabilitar anticipo silenciosamente por seguridad (sin mensaje de log)
                
        except Exception as e:
            logger.error("MainWindow", f"Error aplicando anticipo por defecto: {e}")
            logger.log_exception("MainWindow", e, "_apply_default_advance")
            self.add_system_log("Error aplicando configuración de anticipo")
            # SIEMPRE deshabilitar anticipo en caso de error (seguridad)
            self.custom_advance_toggle.setChecked(False)
            self.ui.spinbox_advance.setValue(0)
            self.ui.spinbox_advance.setEnabled(False)
            self.ui.spinbox_advance.setEnabled(False)
    
    def _apply_advance_rules_after_calculation(self):
        """Aplica las reglas de anticipo basadas en preferencias después de completar un cálculo"""
        try:
            # Si el usuario hizo un override manual, NO aplicar reglas automáticas
            if self._user_manual_override:
                self.add_system_log("🎯 Override manual detectado - Respetando configuración del usuario (sin aplicar reglas automáticas)")
                return
            
            # Obtener el monto total calculado
            if not hasattr(self, 'presenter') or not self.presenter:
                return
                
            last_result = self.presenter.get_last_calculation_result()
            if not last_result or 'total_to_pay' not in last_result:
                return
                
            total_amount = last_result['total_to_pay']
            
            # Crear instancia temporal del presenter de preferencias para consultar reglas
            from presentation.modules.main.presenters.app_preferences_presenter import AppPreferencesPresenter
            prefs_presenter = AppPreferencesPresenter(None)
            
            # Obtener el modo actual
            current_mode = prefs_presenter.get_advance_mode()
            
            # MODO "Ninguno": No aplicar NINGUNA regla automática - control 100% manual
            if current_mode == 0:  # 0 = Ninguno
                self.add_system_log("ℹ️ Modo anticipo: 'Ninguno' - Control manual (sin reglas automáticas)")
                return
            
            # MODO "Activar por defecto al iniciar": NO aplicar reglas durante cálculo
            # (Solo se aplica al iniciar la aplicación)
            if current_mode == AdvanceMode.AUTO_START.value:
                self.add_system_log("ℹ️ Modo anticipo: 'Automático al iniciar' - Sin reglas por monto")
                return
            
            # MODOS de monto (mínimo/máximo): Aplicar reglas según condiciones
            should_apply, percentage_to_use = prefs_presenter.should_apply_advance_for_amount(total_amount)
            
            # Obtener nombre descriptivo del modo para los logs
            mode_name = AdvanceMode.get_display_name(current_mode)
            
            if should_apply:
                # ✅ ACTIVAR anticipo: cumple condiciones del modo
                self.set_advance_values_silently(True, percentage_to_use)
                self.add_system_log(f"✅ Anticipo ACTIVADO por '{mode_name}': {percentage_to_use}% (monto: {CurrencyHelper.format_with_current_currency(total_amount)})")
            else:
                # ❌ DESACTIVAR anticipo: NO cumple condiciones del modo
                self.set_advance_values_silently(False, 0)
                self.add_system_log(f"Anticipo DESACTIVADO por '{mode_name}': monto {CurrencyHelper.format_with_current_currency(total_amount)} no cumple condiciones")
                
        except Exception as e:
            logger.error("MainWindow", f"Error aplicando reglas de anticipo después del cálculo: {e}")
            logger.log_exception("MainWindow", e, "_apply_advance_rules_after_calculation")
            self.add_system_log("Error aplicando reglas de anticipo")
    
    def _on_time_changed(self):
        """Maneja cambios en los spinboxes de tiempo con delay para evitar interrupciones"""
        # ⚡ EMITIR INMEDIATAMENTE la señal de invalidación (0ms delay)
        self.time_changed_immediate.emit()
        
        # 🕒 Programar emisión CON DELAY para auto-cálculo
        # Detener ambos timers
        self.time_timer.stop()
        self.time_conversion_timer.stop()
        
        # Iniciar timer para conversión automática (más largo)
        self.time_conversion_timer.start(1500)  # 1.5 segundos para conversión
        
        # Iniciar timer para emisión de señal (más corto)
        self.time_timer.start(800)  # 0.8 segundos para emisión de señal
    
    def _process_time_conversion(self):
        """Procesa la conversión automática de tiempo después del delay"""
        # Obtener valores actuales
        hours = self.ui.spinbox_time_hour_piece.value()
        minutes = self.ui.spinbox_time_minute_piece.value()
        
        # Aplicar autocompletado si los minutos superan 59
        if minutes > 59:
            # Calcular las horas adicionales y minutos restantes
            additional_hours = minutes // 60
            remaining_minutes = minutes % 60
            original_minutes = minutes
            
            # Actualizar los valores (temporalmente desconectar señales para evitar recursión)
            self.ui.spinbox_time_hour_piece.valueChanged.disconnect()
            self.ui.spinbox_time_minute_piece.valueChanged.disconnect()
            
            # Establecer nuevos valores
            self.ui.spinbox_time_hour_piece.setValue(hours + additional_hours)
            self.ui.spinbox_time_minute_piece.setValue(remaining_minutes)
            
            # Reconectar señales
            self.ui.spinbox_time_hour_piece.valueChanged.connect(self._on_time_changed)
            self.ui.spinbox_time_minute_piece.valueChanged.connect(self._on_time_changed)
            
            # Mostrar feedback visual de la conversión
            self._show_time_conversion_feedback(original_minutes, additional_hours, remaining_minutes)
            
            # Emitir la señal con los valores finales
            final_hours = self.ui.spinbox_time_hour_piece.value()
            final_minutes = self.ui.spinbox_time_minute_piece.value()
            self.time_changed.emit(final_hours, final_minutes)
    
    def _show_time_conversion_feedback(self, original_minutes: int, added_hours: int, final_minutes: int):
        """Muestra feedback visual cuando se realiza una conversión automática de tiempo"""
        # Crear mensaje informativo
        if added_hours == 1:
            hour_text = "1 hora"
        else:
            hour_text = f"{added_hours} horas"
            
        if final_minutes == 1:
            minute_text = "1 minuto"
        else:
            minute_text = f"{final_minutes} minutos"
        
        message = f"Convertido: {original_minutes} min → {hour_text}"
        if final_minutes > 0:
            message += f" + {minute_text}"
        
        # Mostrar tooltip en el campo de minutos por 3 segundos
        self.ui.spinbox_time_minute_piece.setToolTip(message)
        
        # Usar QTimer para limpiar el tooltip después de 3 segundos
        QTimer.singleShot(3000, lambda: self.ui.spinbox_time_minute_piece.setToolTip(tr(I18N.MainWindow.TOOLTIP_MINUTES_SPINBOX)))
    
    def _on_weight_changed(self):
        """Maneja cambios en el peso con delay para evitar spam"""
        # ⚡ EMITIR INMEDIATAMENTE la señal de invalidación (0ms delay)
        self.weight_changed_immediate.emit()
        
        # 🕒 Programar emisión CON DELAY para auto-cálculo (800ms)
        # Detener el timer actual si está corriendo
        self.weight_timer.stop()
        # Iniciar un nuevo timer con delay de 0.8 segundos
        self.weight_timer.start(800)
    
    def _emit_weight_changed(self):
        """Emite la señal de peso cambiado después del delay"""
        weight = self.ui.spinbox_gram_piece.value()
        self.weight_changed.emit(weight)
    
    def _on_quantity_changed(self):
        """Maneja cambios en la cantidad con delay para evitar spam"""
        # ⚡ EMITIR INMEDIATAMENTE la señal de invalidación (0ms delay)
        self.quantity_changed_immediate.emit()
        
        # 🕒 Programar emisión CON DELAY para auto-cálculo (800ms)
        # Detener el timer actual si está corriendo
        self.quantity_timer.stop()
        # Iniciar un nuevo timer con delay de 0.8 segundos
        self.quantity_timer.start(800)
    
    def _emit_quantity_changed(self):
        """Emite la señal de cantidad cambiada después del delay"""
        quantity = self.ui.spinbox_cant_piece.value()
        self.quantity_changed.emit(quantity)
    
    def _on_advance_percentage_changed_with_delay(self, percentage):
        """Maneja el cambio de porcentaje de anticipo con delay"""
        # ⚡ EMITIR INMEDIATAMENTE la señal de invalidación (0ms delay)
        self.advance_percentage_changed_immediate.emit()
        
        # 🕒 Programar emisión CON DELAY para auto-cálculo (800ms)
        self.advance_timer.stop()
        self.advance_timer.start(800)
    
    def _emit_advance_changed(self):
        """Emite la señal de porcentaje de anticipo cambiado después del delay"""
        percentage = self.ui.spinbox_advance.value()
        self._on_advance_percentage_changed(percentage)
    
    def _emit_time_changed(self):
        """Emite la señal de tiempo cambiado después del delay"""
        hours = self.ui.spinbox_time_hour_piece.value()
        minutes = self.ui.spinbox_time_minute_piece.value()
        self.time_changed.emit(hours, minutes)
    
    def show_settings_dialog(self):
        """Muestra el diálogo de configuraciones - MÉTODO PÚBLICO PARA EL PRESENTER"""
        try:
            from presentation.modules.main.views.app_preferences_dialog import AppPreferencesDialog
            
            dialog = AppPreferencesDialog(self)
            
            # Conectar señal para aplicar cambios (nueva señal del patrón refactorizado)
            dialog.preferences_saved.connect(self._on_preferences_changed)
            
            dialog.exec()
            
        except Exception as e:
            logger.error("MainWindow", f"Error abriendo configuraciones: {e}")
            logger.log_exception("MainWindow", e, "show_settings_dialog")
            # Fallback al mensaje anterior
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle(tr(I18N.MainWindow.ERROR_SETTINGS_TITLE))
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(tr(I18N.MainWindow.ERROR_SETTINGS_TEXT))
            msg.setInformativeText(tr(I18N.MainWindow.ERROR_SETTINGS_INFO))
            msg.exec()
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
    
    def _on_preferences_changed(self, preferences: dict):
        """Maneja el cambio de preferencias - DELEGADO AL PRESENTER"""
        try:
            # Recargar las preferencias en el manager
            self.app_preferences = AppPreferencesManager()
            
            logger.info("MainWindow", "Preferencias actualizadas exitosamente")
            
            # Delegar la aplicación de preferencias al presenter (arquitectura correcta)
            if hasattr(self, 'presenter') and self.presenter:
                # Aplicar preferencias de cliente
                self.presenter._apply_customer_preferences()
                # Aplicar preferencias de impresora
                self.presenter._apply_printer_preferences()
                
                self.add_status_message("✅ Configuraciones aplicadas correctamente")
            else:
                self.add_status_message("No se pudo aplicar las configuraciones (sin presenter)")
            
        except Exception as e:
            logger.error("MainWindow", f"Error aplicando preferencias: {e}")
            logger.log_exception("MainWindow", e, "_on_preferences_changed")
            self.add_status_message("Error aplicando configuraciones. Revise el archivo de log.")
    
    def _on_advance_checkbox_changed(self, state):
        """Maneja el cambio de estado del checkbox de anticipo"""
        try:
            checked = state == 2  # Qt.Checked = 2
            
            # Si no es un cambio programático, marcar como override manual
            if not self._programmatic_change:
                self._user_manual_override = True
                status_text = "activado" if checked else "desactivado"
                logger.debug("MainWindow", f"Toggle de anticipo {status_text} manualmente (Override activado)")
            
            # ⚡ EMITIR INMEDIATAMENTE la señal de invalidación (0ms delay)
            self.advance_enabled_changed_immediate.emit()
            
            # Habilitar/deshabilitar el spinbox
            self.ui.spinbox_advance.setEnabled(checked)
            
            # Si se habilita manualmente, usar el porcentaje configurado en preferencias
            if checked:
                try:
                    if self.app_preferences.get_advance_default_enabled():
                        percentage = self.app_preferences.get_advance_default_percentage()
                        self.ui.spinbox_advance.setValue(percentage)
                except Exception:
                    # Si hay error obteniendo preferencias, mantener valor actual
                    pass
            
            # Log del cambio
            status = "habilitado" if checked else "deshabilitado"
            self.add_system_log(f"Anticipo {status}")
            
            # Emitir señal para el presenter
            self.advance_enabled_changed.emit(checked)
            
            # Si se deshabilita, emitir porcentaje 0 para recalcular
            if not checked:
                self.advance_percentage_changed.emit(0)
            else:
                # Si se habilita, emitir el porcentaje actual
                self.advance_percentage_changed.emit(self.ui.spinbox_advance.value())
            
        except Exception as e:
            logger.error("MainWindow", f"Error al manejar checkbox de anticipo: {str(e)}")
            logger.log_exception("MainWindow", e, "_on_advance_checkbox_changed")
    
    def _on_advance_percentage_changed(self, percentage):
        """Maneja el cambio del porcentaje de anticipo"""
        try:
            # Solo emitir señal si el toggle está activado
            if self.is_advance_enabled():
                # Si no es un cambio programático, marcar como override manual
                if not self._programmatic_change:
                    self._user_manual_override = True
                    logger.debug("MainWindow", f"Cambio manual de anticipo detectado: {percentage}% (Override activado)")
                
                self.advance_percentage_changed.emit(percentage)
                
        except Exception as e:
            logger.error("MainWindow", f"Error al manejar cambio de porcentaje de anticipo: {str(e)}")
            logger.log_exception("MainWindow", e, "_on_advance_percentage_changed")
    
    def _on_post_amount_changed_with_delay(self, amount):
        """Maneja el cambio de monto de post-procesado con delay"""
        self.post_amount_changed_immediate.emit()
        
        self.post_timer.stop()
        self.post_timer.start(800)
    
    def _emit_post_changed(self):
        """Emite la señal de monto de post-procesado cambiado después del delay"""
        amount = self.ui.doublespinbox_post_price.value()
        self._on_post_amount_changed(amount)
    
    def _on_post_checkbox_changed(self, state):
        """Maneja el cambio de estado del checkbox de post-procesado"""
        try:
            checked = state == 2  # Qt.Checked = 2
            
            # ⚡ EMITIR INMEDIATAMENTE la señal de invalidación (0ms delay)
            self.post_enabled_changed_immediate.emit()
            
            # Habilitar/deshabilitar el spinbox y combobox
            self.ui.doublespinbox_post_price.setEnabled(checked)
            self.ui.combox_type_post.setEnabled(checked)
            
            # Log del cambio
            status = "habilitado" if checked else "deshabilitado"
            self.add_system_log(f"Post-procesado {status}")
            
            # Emitir señal para el presenter
            self.post_enabled_changed.emit(checked)
            
            # Si se deshabilita, emitir monto 0 para recalcular
            if not checked:
                self.post_amount_changed.emit(0)
            else:
                # Si se habilita, emitir el monto actual
                self.post_amount_changed.emit(self.ui.doublespinbox_post_price.value())
            
        except Exception as e:
            logger.error("MainWindow", f"Error al manejar checkbox de post-procesado: {str(e)}")
            logger.log_exception("MainWindow", e, "_on_post_checkbox_changed")
    
    def _on_post_amount_changed(self, amount):
        """Maneja el cambio del monto de post-procesado"""
        try:
            # Solo emitir señal si el toggle está activado
            if self.is_post_enabled():
                self.post_amount_changed.emit(amount)
                
        except Exception as e:
            logger.error("MainWindow", f"Error al manejar cambio de monto de post-procesado: {str(e)}")
            logger.log_exception("MainWindow", e, "_on_post_amount_changed")
    
    def _on_post_type_changed(self, type_text):
        """Maneja el cambio de tipo de post-procesado"""
        try:
            if self.is_post_enabled():
                # ⚡ EMITIR INMEDIATAMENTE la señal de invalidación (0ms delay)
                self.post_type_changed_immediate.emit()
                
                # Log del cambio
                self.add_system_log(f"Tipo de post-procesado: {type_text}")
                
                # Emitir señal con la clave estable del tipo (independiente del idioma)
                self.post_type_changed.emit(self.ui.combox_type_post.currentData() or type_text)
                
        except Exception as e:
            logger.error("MainWindow", f"Error al manejar cambio de tipo de post-procesado: {str(e)}")
            logger.log_exception("MainWindow", e, "_on_post_type_changed")
    
    # === MÉTODOS PARA ACTUALIZAR LA UI (llamados desde el Presenter) ===
    
    def set_gcode_project(self, file_name: str, thumbnail_data: bytes = b"",
                           layer_height: float = 0.0, nozzle_diameter: float = 0.0,
                           bed_temperature: float = 0.0, hotend_temperature: float = 0.0):
        """Establece el nombre del proyecto G-code, thumbnail y parámetros del slicer"""
        self.ui.linedit_desc_gcode.setText(file_name)
        from PySide6.QtGui import QPixmap, QIcon
        if thumbnail_data:
            pixmap = QPixmap()
            pixmap.loadFromData(thumbnail_data)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.ui.thumbnail_gcode_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.ui.thumbnail_gcode_label.setPixmap(scaled)
            else:
                # Si el thumbnail está corrupto, mostrar SVG por defecto
                self._set_no_thumbnail_svg()
        else:
            # Si no hay thumbnail, mostrar SVG por defecto
            self._set_no_thumbnail_svg()

        # Parámetros del slicer
        lines = []
        if layer_height > 0:
            lines.append(f"Layer H:  {layer_height:.2f} mm")
        if nozzle_diameter > 0:
            lines.append(f"Nozzle:  {nozzle_diameter:.2f} mm")
        if bed_temperature > 0:
            lines.append(f"Bed:  {int(bed_temperature)} °C")
        if hotend_temperature > 0:
            lines.append(f"Hotend:  {int(hotend_temperature)} °C")
        self.ui.textEdit_details_gcode.setText("\n".join(lines) if lines else "")

        self.add_action_log(f"Proyecto G-code cargado: {file_name}")

    def _set_no_thumbnail_svg(self):
        """Muestra el SVG sys_no_thumbnail en el label de thumbnail de G-code"""
        from PySide6.QtSvgWidgets import QSvgWidget
        from PySide6.QtGui import QPixmap
        import os
        # Ruta al recurso SVG compilado
        svg_path = ":/resources/resources/icons/sys_no_thumbnail.svg"
        # QPixmap puede cargar SVG si QtSvg está disponible
        pixmap = QPixmap(svg_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.ui.thumbnail_gcode_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.ui.thumbnail_gcode_label.setPixmap(scaled)
            self.ui.thumbnail_gcode_label.setText("")
        else:
            # Si no puede cargar el SVG, mostrar texto
            self.ui.thumbnail_gcode_label.setText("Sin preview")

    def clear_gcode_project(self):
        """Limpia el proyecto G-code, thumbnail y detalles"""
        self.ui.linedit_desc_gcode.clear()
        self.ui.thumbnail_gcode_label.clear()
        self.ui.thumbnail_gcode_label.setText("")
        self.ui.textEdit_details_gcode.clear()

    def _truncate_display_name(self, name: str) -> str:
        """Trunca el nombre del cliente si excede el límite visual del campo."""
        MAX_LEN = 42  # Límite visual: "Ricahrd Micahel Mequert Espinola Extra abc"
        if len(name) > MAX_LEN:
            return name[:MAX_LEN - 3] + "..."
        return name

    def _truncate_display_ruc_ci(self, ruc_label: str, ruc_ci: str) -> str:
        """Trunca el RUC/CI si el texto completo (label + valor) excede el límite visual.
        El límite es dinámico porque el label varía según la región."""
        MAX_LEN = 26  # Límite visual: "RRCUIT/CID: 01234567890123"
        full_text = f"{ruc_label}: {ruc_ci}"
        if len(full_text) > MAX_LEN:
            prefix_len = len(f"{ruc_label}: ")
            available = MAX_LEN - prefix_len - 3
            if available > 0:
                return ruc_ci[:available] + "..."
            return "..."
        return ruc_ci

    def set_customer_data(self, name: str, ruc_ci: str = ""):
        """Establece los datos del cliente en la UI"""
        display_name = self._truncate_display_name(name)
        self.ui.textEdit_name_client_select.setPlainText(display_name)
        ruc_label = self.LABELS['client_ruc']
        display_ruc_ci = self._truncate_display_ruc_ci(ruc_label, ruc_ci)
        self.ui.textEdit_ruc_ci_client_select.setHtml(
            f"<b>{ruc_label}:</b> {display_ruc_ci}" if ruc_ci else ""
        )
        self.add_selection_log("Cliente", name)
    
    def set_filament_data(self, description: str, filament_type: str, color: str, price: str, quantity: str):
        """Establece los datos del filamento en la UI (selección única)"""
        self.ui.combox_desc_filament.blockSignals(True)
        self.ui.combox_desc_filament.clear()
        self.ui.combox_desc_filament.addItem(description)
        self.ui.combox_desc_filament.setCurrentIndex(0)
        self.ui.combox_desc_filament.setEnabled(True)
        self.ui.combox_desc_filament.blockSignals(False)
        self.ui.textEdit_details_filament_select.setHtml(
            f"<b>{self.LABELS['filament_type']}:</b> {filament_type}<br>"
            f"<b>{self.LABELS['filament_color']}:</b> {color}<br>"
            f"<b>{self.LABELS['filament_price']}:</b> {price}<br>"
            f"<b>{self.LABELS['filament_stock']}:</b> {quantity}"
        )
        self.add_selection_log("Filamento", f"{description} ({filament_type} {color})")

    def update_filament_details(self, filament):
        """Actualiza el text edit de detalles del filamento (modo monofilamento).
        El View maneja el formato de los datos para la UI.
        """
        if not filament:
            self.ui.textEdit_details_filament_select.clear()
            return
        f_type = filament.type.value if hasattr(filament.type, 'value') else str(filament.type) if filament.type else tr(I18N.MainWindow.DETAIL_NOT_SPECIFIED)
        if hasattr(filament, 'color') and filament.color and hasattr(filament.color, 'name'):
            f_color = tr(f"FilamentColor.{filament.color.name}")
        elif filament.color:
            f_color = str(filament.color)
        else:
            f_color = tr(I18N.MainWindow.DETAIL_NOT_SPECIFIED)
        stock_kg = filament.current_stock_grams / 1000.0 if filament.current_stock_grams else 0.0
        price_per_kg = filament.price_per_gram * 1000.0 if filament.price_per_gram else 0.0
        filament_currency = getattr(filament, 'currency_code', 'PYG')

        price_text = f"{CurrencyHelper.format(price_per_kg, filament_currency, include_symbol=False)}{CurrencyHelper.get_symbol(filament_currency)}/kg" if price_per_kg > 0 else tr(I18N.MainWindow.DETAIL_NO_PRICE)
        quantity_text = f"{stock_kg:.2f} kg" if stock_kg >= 0 else tr(I18N.MainWindow.DETAIL_NO_STOCK)

        self.ui.textEdit_details_filament_select.setHtml(
            f"<b>{tr(I18N.MainWindow.DETAIL_FILAMENT_TYPE)}:</b> {f_type}<br>"
            f"<b>{tr(I18N.MainWindow.DETAIL_FILAMENT_COLOR)}:</b> {f_color}<br>"
            f"<b>{tr(I18N.MainWindow.DETAIL_FILAMENT_PRICE)}:</b> {price_text}<br>"
            f"<b>{tr(I18N.MainWindow.DETAIL_FILAMENT_STOCK)}:</b> {quantity_text}"
        )
    
    def set_filament_options(self, options: list, selected_index: int = 0):
        """Carga múltiples opciones de filamento en el combobox.
        Cada opción es una tupla (nombre_display, filament_id).
        """
        self.ui.combox_desc_filament.blockSignals(True)
        self.ui.combox_desc_filament.clear()
        for display_name, filament_id in options:
            self.ui.combox_desc_filament.addItem(display_name, filament_id)
        if options:
            self.ui.combox_desc_filament.setCurrentIndex(selected_index)
            self.ui.combox_desc_filament.setEnabled(True)
        self.ui.combox_desc_filament.blockSignals(False)
    
    def _on_filament_combox_changed(self, index: int):
        """Emite señal cuando el usuario cambia la selección del combobox de filamento"""
        if index >= 0:
            self.filament_combox_changed.emit(index)

    def get_filament_id_at_index(self, index: int):
        """Retorna el filament_id almacenado en el combobox en el índice dado.
        Útil para que el Presenter obtenga el ID sin acceder directamente al UI.
        """
        if index >= 0:
            return self.ui.combox_desc_filament.itemData(index)
        return None

    def get_current_filament_id(self):
        """Retorna el filament_id actualmente seleccionado en el combobox.
        Útil para que el Presenter obtenga el ID sin acceder directamente al UI.
        """
        index = self.ui.combox_desc_filament.currentIndex()
        if index >= 0:
            return self.ui.combox_desc_filament.itemData(index)
        return None

    def get_printer_id_at_index(self, index: int):
        """Retorna el printer_id almacenado en el combobox en el índice dado."""
        if index >= 0:
            return self.ui.combox_desc_printer.itemData(index)
        return None

    def get_current_printer_id(self):
        """Retorna el printer_id actualmente seleccionado en el combobox."""
        index = self.ui.combox_desc_printer.currentIndex()
        if index >= 0:
            return self.ui.combox_desc_printer.itemData(index)
        return None

    def update_printer_details(self, printer):
        """Actualiza el text edit de detalles de la impresora.
        El View maneja el formato de los datos para la UI.
        """
        if not printer:
            self.ui.textEdit_details_printer_select.clear()
            return
        try:
            consumption_watts = float(getattr(printer, 'power_consumption_watts', 0) or 0)
        except Exception:
            consumption_watts = 0.0
        consumption_text = f"{int(round(consumption_watts))}W" if consumption_watts > 0 else tr(I18N.MainWindow.DETAIL_NOT_AVAILABLE)
        self.ui.textEdit_details_printer_select.setHtml(
            f"<b>{tr(I18N.MainWindow.DETAIL_PRINTER_BRAND)}:</b> {printer.brand or tr(I18N.MainWindow.DETAIL_NOT_SPECIFIED_F)}<br>"
            f"<b>{tr(I18N.MainWindow.DETAIL_PRINTER_MODEL)}:</b> {printer.model or tr(I18N.MainWindow.DETAIL_NOT_SPECIFIED)}<br>"
            f"<b>{tr(I18N.MainWindow.DETAIL_PRINTER_CONSUMPTION)}:</b> {consumption_text}"
        )

    def set_printer_data(self, description: str, brand: str, model: str, consumption: str):
        """Establece los datos de la impresora en la UI (selección única)"""
        self.ui.combox_desc_printer.blockSignals(True)
        self.ui.combox_desc_printer.clear()
        self.ui.combox_desc_printer.addItem(description)
        self.ui.combox_desc_printer.setCurrentIndex(0)
        self.ui.combox_desc_printer.setEnabled(True)
        self.ui.combox_desc_printer.blockSignals(False)
        self.ui.textEdit_details_printer_select.setHtml(
            f"<b>{self.LABELS['printer_brand']}:</b> {brand}<br>"
            f"<b>{self.LABELS['printer_model']}:</b> {model}<br>"
            f"<b>{self.LABELS['printer_consumption']}:</b> {consumption}"
        )
        self.add_selection_log("Impresora", f"{description} ({brand} {model})")
    
    def set_printer_options(self, options: list, selected_index: int = 0):
        """Carga múltiples opciones de impresora en el combobox.
        Cada opción es una tupla (nombre_display, printer_id).
        """
        self.ui.combox_desc_printer.blockSignals(True)
        self.ui.combox_desc_printer.clear()
        for display_name, printer_id in options:
            self.ui.combox_desc_printer.addItem(display_name, printer_id)
        if options:
            self.ui.combox_desc_printer.setCurrentIndex(selected_index)
            self.ui.combox_desc_printer.setEnabled(True)
        self.ui.combox_desc_printer.blockSignals(False)
    
    def _on_printer_combox_changed(self, index: int):
        """Emite señal cuando el usuario cambia la selección del combobox de impresora"""
        if index >= 0:
            self.printer_combox_changed.emit(index)
    
    def clear_customer_selection(self):
        """Limpia la selección de cliente"""
        self.ui.textEdit_name_client_select.clear()
        self.ui.textEdit_ruc_ci_client_select.clear()
        self.add_action_log("Selección de cliente limpiada")
    
    def clear_printer_selection(self):
        """Limpia la selección de impresora"""
        self.ui.combox_desc_printer.blockSignals(True)
        self.ui.combox_desc_printer.clear()
        self.ui.combox_desc_printer.setEnabled(False)
        self.ui.combox_desc_printer.blockSignals(False)
        self.ui.textEdit_details_printer_select.clear()
        self.add_action_log("Selección de impresora limpiada")

    def clear_filament_selection(self):
        """Limpia la selección de filamento"""
        self.ui.combox_desc_filament.blockSignals(True)
        self.ui.combox_desc_filament.clear()
        self.ui.combox_desc_filament.setEnabled(False)
        self.ui.combox_desc_filament.blockSignals(False)
        self.ui.textEdit_details_filament_select.clear()
        self.add_action_log("Selección de filamento limpiada")
    
    def clear_all_fields(self):
        """Limpia todos los campos del formulario"""
        # Cliente
        self.ui.textEdit_name_client_select.clear()
        self.ui.textEdit_ruc_ci_client_select.clear()
        self.ui.checkbox_client_optional.setChecked(True)  # Siempre marcado por defecto
        
        # Filamento
        self.ui.combox_desc_filament.blockSignals(True)
        self.ui.combox_desc_filament.clear()
        self.ui.combox_desc_filament.setEnabled(False)
        self.ui.combox_desc_filament.blockSignals(False)
        self.ui.textEdit_details_filament_select.clear()
        
        # Impresora
        self.ui.combox_desc_printer.blockSignals(True)
        self.ui.combox_desc_printer.clear()
        self.ui.combox_desc_printer.setEnabled(False)
        self.ui.combox_desc_printer.blockSignals(False)
        self.ui.textEdit_details_printer_select.clear()
        
        # Pieza
        self.set_piece_parameters(0, 0, 0, 0)
        
        # Anticipo - restablecer a valores por defecto
        self.set_advance_enabled(False)            # Desactivado por defecto
        self.ui.spinbox_advance.setValue(0)         # ✅ Iniciar en 0% por defecto
        self.ui.spinbox_advance.setEnabled(False)   # Deshabilitado por defecto
        
        # Post-procesado - restablecer a valores por defecto
        self.set_post_enabled(False)               # Desactivado por defecto
        self.ui.doublespinbox_post_price.setValue(0.0)
        
        # Resetear flags de control de bucles
        self.reset_advance_manual_override()

        # Volver a modo monofilamento y limpiar estado multicolor de UI
        self.set_multicolor_mode(False)
        self.hide_multicolor_panel()
        
        # 🔇 Comentado para reducir ruido en el log visual (ya se registra en el logger)
        # self.add_action_log("Formulario limpiado", "Todos los campos restablecidos")

    def set_piece_parameters(self, hours: int, minutes: int, grams: int, quantity: int):
        """Establece los parámetros de la pieza (tiempo, peso, cantidad)."""
        self.ui.spinbox_time_hour_piece.setValue(hours)
        self.ui.spinbox_time_minute_piece.setValue(minutes)
        self.ui.spinbox_gram_piece.setValue(grams)
        self.ui.spinbox_cant_piece.setValue(quantity)

    def get_time_hours(self) -> int:
        """Retorna las horas actuales del spinbox."""
        return self.ui.spinbox_time_hour_piece.value()

    def get_time_minutes(self) -> int:
        """Retorna los minutos actuales del spinbox."""
        return self.ui.spinbox_time_minute_piece.value()

    def get_weight_grams(self) -> int:
        """Retorna los gramos actuales del spinbox."""
        return self.ui.spinbox_gram_piece.value()

    def get_quantity(self) -> int:
        """Retorna la cantidad actual del spinbox."""
        return self.ui.spinbox_cant_piece.value()

    def set_post_label(self, text: str):
        """Establece el texto del label de post-procesado."""
        self.ui.label_post.setText(text)

    def get_customer_name(self) -> str:
        """Retorna el nombre del cliente actualmente en el campo de texto."""
        return self.ui.textEdit_name_client_select.toPlainText().strip()

    def set_preview_button_enabled(self, enabled: bool):
        """Habilita o deshabilita el botón de vista previa."""
        self.ui.btn_preview.setEnabled(enabled)

    def set_generate_button_enabled(self, enabled: bool):
        """Habilita o deshabilita el botón de generar PDF."""
        self.ui.btn_generate.setEnabled(enabled)

    def is_preview_button_enabled(self) -> bool:
        """Retorna el estado actual del botón de vista previa."""
        return self.ui.btn_preview.isEnabled()

    def is_generate_button_enabled(self) -> bool:
        """Retorna el estado actual del botón de generar PDF."""
        return self.ui.btn_generate.isEnabled()

    def get_current_tab_index(self) -> int:
        """Retorna el índice del tab actualmente seleccionado."""
        return self.ui.tabWidget.currentIndex()

    def set_current_tab(self, index: int):
        """Establece el tab seleccionado."""
        self.ui.tabWidget.setCurrentIndex(index)

    def get_tab_widget(self):
        """Retorna el widget de tabs para configuración de eventos.
        Nota: En un MVP estricto, esto debería manejarse diferente,
        pero se mantiene por compatibilidad con TabWidgetEventManager.
        """
        return self.ui.tabWidget
    
    def add_status_message(self, message: str):
        """Agrega un mensaje al área de estado con formato mejorado"""
        from PySide6.QtGui import QTextCursor        
        # Usar appendPlainText() para QPlainTextEdit
        self.ui.plaintextedit_status.appendPlainText(message)        
        # Auto-scroll al final
        cursor = self.ui.plaintextedit_status.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.ui.plaintextedit_status.setTextCursor(cursor)
    
    def add_action_log(self, action: str, details: str = ""):
        """Registra una acción del usuario con formato específico"""
        if details:
            message = f"ACCIÓN: {action} - {details}"
        else:
            message = f"ACCIÓN: {action}"
        self.add_status_message(message)
    
    def add_calculation_log(self, calculation_type: str, result: str = ""):
        """Registra un cálculo con formato específico"""
        if result:
            message = f"CÁLCULO: {calculation_type} - {result}"
        else:
            message = f"CÁLCULO: {calculation_type}"
        self.add_status_message(message)
    
    def add_selection_log(self, item_type: str, item_name: str):
        """Registra una selección con formato específico"""
        # 🔇 Comentado para reducir ruido en el log visual
        # message = f"SELECCIÓN: {item_type} → {item_name}"
        # self.add_status_message(message)
        pass
    
    def add_system_log(self, system_event: str):
        """Registra un evento del sistema con formato específico"""
        message = f"SISTEMA: {system_event}"
        self.add_status_message(message)
    
    def add_separator(self, title: str = ""):
        """Agrega un separador visual con título opcional"""
        if title:
            self.add_status_message("=" * 37)
            self.add_status_message(f"{title.upper()}")
            self.add_status_message("=" * 37)
        else:
            self.add_status_message("-" * 63)
    
    def show_calculation_result(self, result_text: str):
        """Muestra el resultado del cálculo con formato mejorado"""
        self.add_status_message("=" * 37)
        self.add_status_message("RESULTADO DEL CÁLCULO")
        self.add_status_message("=" * 37)

        # Dividir el resultado en líneas para mejor formato
        for line in result_text.strip().split('\n'):
            if line.strip():  # Solo agregar líneas no vacías
                self.add_status_message(line.strip())
        
        self.add_status_message("=" * 37)
    
    def show_error_message(self, title: str, message: str):
        """Muestra un mensaje de error con formato mejorado"""
        QMessageBox.critical(self, title, message)
        self.add_status_message("ERROR: " + message)
    
    def show_success_message(self, title: str, message: str):
        """Muestra un mensaje de éxito con formato mejorado"""
        QMessageBox.information(self, title, message)
        self.add_status_message("ÉXITO: " + message)
    
    def show_warning_message(self, title: str, message: str):
        """Muestra un mensaje de advertencia con formato mejorado"""
        QMessageBox.warning(self, title, message)
        self.add_status_message("ADVERTENCIA: " + message)
    
    def show_info_message(self, title: str, message: str):
        """Muestra un mensaje informativo"""
        QMessageBox.information(self, title, message)
        self.add_status_message("INFO: " + message)
    
    def show_question_message(self, title: str, message: str) -> bool:
        """Muestra un mensaje de pregunta y retorna True si el usuario acepta"""
        reply = QMessageBox.question(
            self, 
            title, 
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        return reply == QMessageBox.StandardButton.Yes
    
    # === MÉTODOS PARA OBTENER DATOS DE LA UI (usados por el Presenter) ===
    
    def get_time_values(self) -> tuple[int, int]:
        """Obtiene las horas y minutos ingresados"""
        hours = self.ui.spinbox_time_hour_piece.value()
        minutes = self.ui.spinbox_time_minute_piece.value()
        return hours, minutes
    
    def get_weight_value(self) -> int:
        """Obtiene el peso en gramos"""
        return self.ui.spinbox_gram_piece.value()
    
    def get_quantity_value(self) -> int:
        """Obtiene la cantidad de piezas"""
        return self.ui.spinbox_cant_piece.value()
    
    def get_export_format(self) -> str:
        """Obtiene el formato de exportación - SIEMPRE PDF"""
        return "PDF"  # Forzado a PDF, no depende del combobox
    
    def is_customer_optional(self) -> bool:
        """Verifica si el cliente es opcional"""
        return self.ui.checkbox_client_optional.isChecked()
    
    def set_customer_optional(self, is_optional: bool):
        """Establece el estado del checkbox de cliente opcional"""
        self.ui.checkbox_client_optional.setChecked(is_optional)
    
    def is_advance_enabled(self) -> bool:
        """Verifica si el anticipo está habilitado"""
        if hasattr(self, 'custom_advance_toggle'):
            return self.custom_advance_toggle.isChecked()
        return self.ui.checkbox_advance.isChecked()
    
    def get_advance_percentage(self) -> int:
        """Obtiene el porcentaje de anticipo"""
        return self.ui.spinbox_advance.value() if self.is_advance_enabled() else 0
    
    def set_advance_enabled(self, enabled: bool):
        """Establece el estado del checkbox de anticipo"""
        if hasattr(self, 'custom_advance_toggle'):
            self.custom_advance_toggle.setChecked(enabled)
        else:
            self.ui.checkbox_advance.setChecked(enabled)
    
    def set_advance_percentage(self, percentage: int):
        """Establece el porcentaje de anticipo"""
        self.ui.spinbox_advance.setValue(percentage)
    
    def is_post_enabled(self) -> bool:
        """Verifica si el post-procesado está habilitado"""
        if hasattr(self, 'custom_post_toggle'):
            return self.custom_post_toggle.isChecked()
        return self.ui.checkbox_post.isChecked()
    
    def get_post_amount(self) -> float:
        """Obtiene el monto de post-procesado"""
        return self.ui.doublespinbox_post_price.value() if self.is_post_enabled() else 0
    
    def set_post_enabled(self, enabled: bool):
        """Establece el estado del checkbox de post-procesado"""
        if hasattr(self, 'custom_post_toggle'):
            self.custom_post_toggle.setChecked(enabled)
        else:
            self.ui.checkbox_post.setChecked(enabled)
    
    def set_post_amount(self, amount: float):
        """Establece el monto de post-procesado"""
        self.ui.doublespinbox_post_price.setValue(amount)
    
    def get_post_type(self) -> str:
        """Obtiene el tipo de post-procesado seleccionado"""
        return self.ui.combox_type_post.currentText()
    
    def get_post_multiplier(self) -> int:
        """Calcula el multiplicador según el tipo de post-procesado"""
        if not self.is_post_enabled():
            return 0
            
        post_type = self.ui.combox_type_post.currentData()
        if post_type == "lote":
            # Multiplica por la cantidad de piezas
            return self.get_quantity_value()
        elif post_type == "trabajo":
            # Siempre es 1 para trabajo
            return 1
        else:
            return 1  # Default
    
    def get_post_total_amount(self) -> float:
        """Calcula el monto total de post-procesado (monto base × multiplicador)"""
        if not self.is_post_enabled():
            return 0
        
        base_amount = self.ui.doublespinbox_post_price.value()
        multiplier = self.get_post_multiplier()
        return base_amount * multiplier
    
    def clear_customer_data(self):
        """Limpia solo los datos del cliente"""
        self.ui.textEdit_name_client_select.clear()
        self.ui.textEdit_ruc_ci_client_select.clear()
        self.add_system_log("Datos de cliente limpiados")
    
    def get_customer_data(self) -> dict:
        """Obtiene los datos del cliente"""
        return {
            "name": self.ui.textEdit_name_client_select.toPlainText().strip(),
            "ruc_ci": self.ui.textEdit_ruc_ci_client_select.toPlainText().strip(),
            "is_optional": self.is_customer_optional()
        }
    
    def has_required_calculation_data(self) -> tuple[bool, str]:
        """Verifica si tiene los datos requeridos para el cálculo (sin cliente)."""
        errors = []
        
        if not self.ui.combox_desc_printer.currentText().strip():
            errors.append(tr(I18N.Quote.MSG_SELECT_PRINTER))
        
        # En modo multicolor el filamento se valida por slots (no por el combobox monocolor)
        is_multicolor_mode = (
            hasattr(self.ui, 'stacked_filament_mode') and
            self.ui.stacked_filament_mode.currentIndex() == 0
        )
        if not is_multicolor_mode and not self.ui.combox_desc_filament.currentText().strip():
            errors.append(tr(I18N.Quote.MSG_SELECT_FILAMENT))
        
        hours, minutes = self.get_time_values()
        if hours == 0 and minutes <= 0:
            errors.append(tr(I18N.Quote.MSG_SPECIFY_TIME))
        
        if self.get_weight_value() <= 0:
            errors.append(tr(I18N.Quote.MSG_SPECIFY_WEIGHT))
        
        if errors:
            return False, "\n".join(errors)
        return True, ""

    def has_required_data(self) -> tuple[bool, str]:
        """Verifica si tiene todos los datos requeridos (incluye cliente, para PDF)"""
        errors = []
        
        # Verificar impresora
        if not self.ui.combox_desc_printer.currentText().strip():
            errors.append(tr(I18N.Quote.MSG_SELECT_PRINTER))
        
        # Verificar filamento
        if not self.ui.combox_desc_filament.currentText().strip():
            errors.append(tr(I18N.Quote.MSG_SELECT_FILAMENT))
        
        # Verificar cliente (si no es opcional)
        if not self.is_customer_optional() and not self.ui.textEdit_name_client_select.toPlainText().strip():
            errors.append(tr(I18N.Quote.MSG_SELECT_CUSTOMER))
        
        # Verificar tiempo
        hours, minutes = self.get_time_values()
        if hours == 0 and minutes <= 0:
            errors.append(tr(I18N.Quote.MSG_SPECIFY_TIME))
        
        # Verificar peso
        if self.get_weight_value() <= 0:
            errors.append(tr(I18N.Quote.MSG_SPECIFY_WEIGHT))
        
        if errors:
            return False, "\n".join(errors)
        
        return True, ""
    
    def _clear_hardcoded_styles(self):
        """Limpia los estilos codificados que interfieren con el sistema de temas"""
        try:
            # Limpiar estilos del widget principal (styleSheet)
            if hasattr(self.ui, 'styleSheet'):
                self.ui.styleSheet.setStyleSheet("")
            
            # Limpiar estilos del frame principal (bgApp)
            if hasattr(self.ui, 'bgApp'):
                self.ui.bgApp.setStyleSheet("")
            
            # Limpiar estilos del tabWidget que tiene estilos hardcodeados
            if hasattr(self.ui, 'tabWidget'):
                self.ui.tabWidget.setStyleSheet("")
            
            # Limpiar estilos del content frame
            if hasattr(self.ui, 'content'):
                self.ui.content.setStyleSheet("")
            
            # Limpiar estilos del frame_content
            if hasattr(self.ui, 'frame_content'):
                self.ui.frame_content.setStyleSheet("")
            
            # Limpiar estilos del MainPanel mismo
            self.setStyleSheet("")
            
        except Exception as e:
            logger.warning("MainWindow", f"Error limpiando estilos hardcodeados: {e}")
    
    def apply_theme_to_main_panel(self, qss_content: str = ""):
        """Aplica un tema específico al MainPanel"""
        try:
            # Primero limpiar estilos hardcodeados
            self._clear_hardcoded_styles()
            
            # Aplicar el nuevo tema si se proporciona
            if qss_content and qss_content.strip():
                self.setStyleSheet(qss_content)
                # Tema aplicado silenciosamente
            else:
                self.add_system_log("Estilos limpiados - usando tema por defecto")
                
        except Exception as e:
            logger.warning("MainWindow", f"Error aplicando tema al MainPanel: {e}")
            # Fallback: al menos limpiar los estilos para evitar conflictos
            try:
                self._clear_hardcoded_styles()
            except:
                pass
    
    def reset_advance_manual_override(self):
        """Resetea el flag de override manual para permitir reglas automáticas nuevamente"""   
        if self._user_manual_override:
            logger.debug("MainWindow", "Override manual reseteado - Permitiendo reglas automáticas nuevamente")
        self._user_manual_override = False
        self._programmatic_change = False

    def set_advance_values_silently(self, enabled: bool, percentage: int = 0):
        """Establece valores de anticipo sin emitir señales que disparen cálculos"""
        # Bloquear señales temporalmente
        if hasattr(self, 'custom_advance_toggle'):
            self.custom_advance_toggle.blockSignals(True)
            self.custom_advance_toggle.setChecked(enabled)
            # Forzar la transición visual manualmente
            self.custom_advance_toggle.start_transition(2 if enabled else 0)  # 2 = Qt.Checked, 0 = Qt.Unchecked
            self.custom_advance_toggle.blockSignals(False)
        
        self.ui.spinbox_advance.blockSignals(True)
        self.ui.spinbox_advance.setValue(percentage)
        self.ui.spinbox_advance.setEnabled(enabled)
        self.ui.spinbox_advance.blockSignals(False)
        
        logger.debug("MainWindow", "Valores de anticipo establecidos silenciosamente", 
                         estado="Activo" if enabled else "Inactivo", porcentaje=f"{percentage}%")

    # ================================================================
    # PANEL MULTICOLOR
    # ================================================================

    def _setup_multicolor_panel(self):
        """Conecta y oculta los btn_filament_1..6 inicialmente; se activan con multicolor."""
        try:
            from presentation.common.custom_tooltip import SlotToolTipManager
            self._slot_tooltip_mgr = SlotToolTipManager()
            self._mc_slot_tooltips: dict = {}
            self._mc_active_slot: int = -1

            # Referencias ordenadas: btn_filament_1 = slot 0, ..., btn_filament_6 = slot 5
            self._mc_buttons = [
                self.ui.btn_filament_1,
                self.ui.btn_filament_2,
                self.ui.btn_filament_3,
                self.ui.btn_filament_4,
                self.ui.btn_filament_5,
                self.ui.btn_filament_6,
            ]
            for i, btn in enumerate(self._mc_buttons):
                btn.setVisible(False)
                btn.setEnabled(False)
                btn.setToolTip("")  # suprimir tooltip nativo
                btn.installEventFilter(self)
                slot_idx = i   # captura por valor
                btn.clicked.connect(
                    lambda checked=False, si=slot_idx: self._on_filament_slot_btn_clicked(si)
                )

            self.ui.combox_desc_multi_filament.blockSignals(True)
            self.ui.combox_desc_multi_filament.clear()
            self.ui.combox_desc_multi_filament.setEnabled(False)
            self.ui.combox_desc_multi_filament.blockSignals(False)
            # 'activated' se emite solo por interacción del usuario, nunca en cargas
            # programáticas (blockSignals o setCurrentIndex automático), lo que evita
            # disparar recálculos al cambiar entre slots.
            self.ui.combox_desc_multi_filament.activated.connect(self._on_multicolor_combox_changed)

            # Botón de búsqueda por material (icono ya definido en el UI)
            self.ui.btn_multicolor_search.setEnabled(False)
            self.ui.btn_multicolor_search.clicked.connect(self._on_multicolor_search_clicked)

            self.ui.textEdit_details_multi_filament_select.clear()
        except Exception as e:
            logger.error("MainWindow", f"Error configurando botones multicolor: {e}")

    def _slot_btn_style(self, slot_index: int, colour_hex: str, selected: bool = False,
                        has_match: bool = True) -> str:
        """Genera el inline styleSheet para un botón de slot.

        El fondo ya no usa el color del filamento (se eliminó el pintado por hex).
        - Slot seleccionado:  borde destacado + fondo azul tenue.
        - Slot sin match (has_match=False):  fondo naranja tenue para alertar.
        - Slot normal no seleccionado: fondo neutro del tema.
        """
        n = slot_index + 1   # 1-based para la imagen
        icon = f"url(:/resources/resources/icons/sys_number_{n}.svg)"
        if selected:
            bg = "rgba(100,181,246,0.25)"
            border = "2px solid rgba(100,181,246,0.9)"
        elif not has_match:
            bg = "rgba(255,152,0,0.20)"
            border = "1px solid rgba(255,152,0,0.7)"
        else:
            bg = "rgba(0,109,119,0.55)"
            border = "1px solid rgba(0,109,119,0.8)"
        return (
            f"background-color: {bg}; "
            f"border: {border}; "
            f"border-radius: 3px; "
            f"image: {icon};"
        )

    def _build_multicolor_slot_tooltip(self, slot: dict) -> str:
        """Construye tooltip uniforme para botones de slots multicolor."""
        idx = slot.get('slot_index', 0)
        weight = slot.get('weight_grams', 0.0)
        pct = slot.get('percentage', 0.0)
        ftype = slot.get('filament_type', '—')
        fname = slot.get('filament_name', '—')
        cost = slot.get('slot_cost', None)
        cost_line = ""
        if cost is not None:
            currency = CurrencyHelper.get_current_currency()
            if isinstance(currency, dict):
                symbol = currency.get('symbol', '$')
                code = currency.get('code', 'USD')
            else:
                symbol = str(currency)
                code = str(currency)
            decimals = CurrencyHelper.get_decimals(code)
            cost_line = f"<br>{tr(I18N.MainWindow.SLOT_TOOLTIP_COST).format(symbol=symbol, cost=f'{cost:,.{decimals}f}')}"

        return (
            f"<b>{tr(I18N.MainWindow.SLOT_TOOLTIP_HEADER).format(num=idx+1, ftype=ftype)}</b><br>"
            f"{tr(I18N.MainWindow.SLOT_TOOLTIP_FILAMENT).format(fname=fname)}<br>"
            f"{tr(I18N.MainWindow.SLOT_TOOLTIP_WEIGHT).format(weight=weight, pct=pct)}{cost_line}<br>"
            f"<i>{tr(I18N.MainWindow.SLOT_TOOLTIP_HINT)}</i>"
        )

    def load_multicolor_combobox(self, candidates: list, selected_id: int, slot_index: int = -1):
        """Carga el combobox con los candidatos del slot activo.
        Usa blockSignals para evitar spam/disparar recálculos al cambiar entre slots.
        Si se pasa slot_index >= 0, sincroniza _mc_active_slot con el estado del Presenter.
        """
        try:
            if slot_index >= 0:
                self._mc_active_slot = slot_index

            self.ui.combox_desc_multi_filament.blockSignals(True)
            self.ui.combox_desc_multi_filament.clear()

            selected_index = -1
            for idx, (name, filament_id) in enumerate(candidates):
                self.ui.combox_desc_multi_filament.addItem(name, filament_id)
                if filament_id == selected_id:
                    selected_index = idx

            has_items = bool(candidates)
            self.ui.combox_desc_multi_filament.setEnabled(has_items)
            self.ui.btn_multicolor_search.setEnabled(self._mc_active_slot >= 0)
            if has_items:
                if selected_index < 0:
                    selected_index = 0
                self.ui.combox_desc_multi_filament.setCurrentIndex(selected_index)
            else:
                self.ui.combox_desc_multi_filament.setCurrentIndex(-1)

            self.ui.combox_desc_multi_filament.blockSignals(False)
        except Exception as e:
            logger.error("MainWindow", f"Error cargando combobox multicolor: {e}")
            self.ui.combox_desc_multi_filament.blockSignals(False)

    def update_multicolor_button_style(self, slot_index: int, colour_hex: str, selected: bool,
                                       has_match: bool = True):
        """Actualiza el estilo de un botón de slot."""
        if 0 <= slot_index < len(self._mc_buttons):
            self._mc_buttons[slot_index].setStyleSheet(
                self._slot_btn_style(slot_index, colour_hex, selected, has_match=has_match)
            )

    def update_multicolor_button_tooltip(self, slot_index: int, tooltip_text: str):
        """Actualiza el tooltip de un botón de slot (almacena en dict para el manager custom)."""
        if 0 <= slot_index < len(self._mc_buttons):
            self._mc_slot_tooltips[slot_index] = tooltip_text

    def _update_multicolor_details(self, filament):
        """Actualiza el text edit de detalles con el mismo formato del monofilamento."""
        if not filament:
            self.ui.textEdit_details_multi_filament_select.clear()
            return

        f_type = filament.type.value if hasattr(filament.type, 'value') else str(filament.type) if filament.type else tr(I18N.MainWindow.DETAIL_NOT_SPECIFIED)
        if hasattr(filament, 'color') and filament.color and hasattr(filament.color, 'name'):
            f_color = tr(f"FilamentColor.{filament.color.name}")
        elif filament.color:
            f_color = str(filament.color)
        else:
            f_color = tr(I18N.MainWindow.DETAIL_NOT_SPECIFIED)
        stock_kg = filament.current_stock_grams / 1000.0 if filament.current_stock_grams else 0.0
        price_per_kg = filament.price_per_gram * 1000.0 if filament.price_per_gram else 0.0
        filament_currency = getattr(filament, 'currency_code', 'PYG')

        price_text = f"{CurrencyHelper.format(price_per_kg, filament_currency, include_symbol=False)}{CurrencyHelper.get_symbol(filament_currency)}/kg" if price_per_kg > 0 else tr(I18N.MainWindow.DETAIL_NO_PRICE)
        quantity_text = f"{stock_kg:.2f} kg" if stock_kg >= 0 else tr(I18N.MainWindow.DETAIL_NO_STOCK)

        self.ui.textEdit_details_multi_filament_select.setHtml(
            f"<b>{tr(I18N.MainWindow.DETAIL_FILAMENT_TYPE)}:</b> {f_type}<br>"
            f"<b>{tr(I18N.MainWindow.DETAIL_FILAMENT_COLOR)}:</b> {f_color}<br>"
            f"<b>{tr(I18N.MainWindow.DETAIL_FILAMENT_PRICE)}:</b> {price_text}<br>"
            f"<b>{tr(I18N.MainWindow.DETAIL_FILAMENT_STOCK)}:</b> {quantity_text}"
        )

    def show_multicolor_panel(self, slots_info: list):
        """
        Activa y colorea los btn_filament_N según los slots del G-code.
        slots_info: lista de dicts con keys slot_index, filament_type, colour_hex,
                    weight_grams, percentage, filament_name, candidates, filament_id.
        La Vista NO guarda el estado; el Presenter es el dueño de los datos.
        """
        try:
            if not hasattr(self, '_mc_buttons'):
                self._setup_multicolor_panel()

            self._mc_active_slot = -1
            # Ocultar todos primero
            for btn in self._mc_buttons:
                btn.setVisible(False)
                btn.setEnabled(False)
                btn.setStyleSheet("")

            for slot in slots_info:
                idx = slot.get('slot_index', 0)
                if idx < 0 or idx >= len(self._mc_buttons):
                    continue

                btn = self._mc_buttons[idx]
                colour = slot.get('colour_hex', '')
                has_match = slot.get('has_match', True)
                btn.setStyleSheet(self._slot_btn_style(idx, colour, selected=False, has_match=has_match))
                self._mc_slot_tooltips[idx] = self._build_multicolor_slot_tooltip(slot)
                btn.setVisible(True)
                btn.setEnabled(True)

            # NO seleccionar automáticamente el primer slot; el Presenter lo hará
            # Limpiar combobox y detalles por defecto
            self.ui.combox_desc_multi_filament.blockSignals(True)
            self.ui.combox_desc_multi_filament.clear()
            self.ui.combox_desc_multi_filament.setEnabled(False)
            self.ui.combox_desc_multi_filament.blockSignals(False)
            self.ui.textEdit_details_multi_filament_select.clear()
        except Exception as e:
            logger.error("MainWindow", f"Error mostrando slots multicolor: {e}")

    def set_multicolor_alert(self, visible: bool, tooltip: str = ""):
        """Muestra u oculta el ícono de alerta en el panel multifilamento.

        visible=True  → naranja: algún slot sin filamento compatible.
        visible=False → verde:   todos los slots con match correcto (se oculta al cerrar el panel).
        """
        label = self.ui.alert_mutifilament_label
        from core.utils.path_helper import build_resource_path
        from PySide6.QtGui import QPixmap
        if visible:
            icon_path = build_resource_path("resources/icons/sys_alert_circle_orange.svg")
        else:
            icon_path = build_resource_path("resources/icons/sys_check_circle_green.svg")
        px = QPixmap(icon_path)
        if not px.isNull():
            label.setPixmap(px.scaled(
                label.width(), label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
        label.setToolTip(tooltip)
        label.setVisible(True)

    def _on_filament_slot_btn_clicked(self, slot_index: int):
        """Notifica al Presenter que se seleccionó un slot."""
        try:
            self._mc_active_slot = slot_index
            self.multicolor_slot_selected.emit(slot_index)
        except Exception as e:
            logger.error("MainWindow", f"Error en selección de slot {slot_index}: {e}")

    def _on_multicolor_combox_changed(self, index: int):
        """Notifica al Presenter del cambio de filamento en el slot activo.
        Solo se llama por interacción real del usuario (señal activated).
        """
        try:
            if index < 0 or self._mc_active_slot < 0:
                return

            filament_id = self.ui.combox_desc_multi_filament.itemData(index)
            if filament_id is None:
                return

            self.multicolor_slot_changed.emit(self._mc_active_slot, int(filament_id))
        except Exception as e:
            logger.error("MainWindow", f"Error en combobox multicolor: {e}")

    def _on_multicolor_search_clicked(self):
        """Emite señal para que el Presenter abra el selector de filamento filtrado por tipo."""
        try:
            if self._mc_active_slot >= 0:
                self.multicolor_search_requested.emit(self._mc_active_slot)
        except Exception as e:
            logger.error("MainWindow", f"Error en búsqueda de slot multicolor: {e}")

    def hide_multicolor_panel(self):
        """Oculta todos los botones de slot multicolor y limpia su estado."""
        try:
            if not hasattr(self, '_mc_buttons'):
                return
            for btn in self._mc_buttons:
                btn.setVisible(False)
                btn.setEnabled(False)
                btn.setStyleSheet("")
            self._mc_active_slot = -1
            self._mc_slot_tooltips.clear()
            if hasattr(self, '_slot_tooltip_mgr'):
                self._slot_tooltip_mgr.hide()
            self.ui.combox_desc_multi_filament.blockSignals(True)
            self.ui.combox_desc_multi_filament.clear()
            self.ui.combox_desc_multi_filament.setEnabled(False)
            self.ui.combox_desc_multi_filament.blockSignals(False)
            self.ui.btn_multicolor_search.setEnabled(False)
            self.ui.textEdit_details_multi_filament_select.clear()
            self.ui.alert_mutifilament_label.setVisible(False)
            self.ui.alert_mutifilament_label.setToolTip("")
        except Exception as e:
            logger.error("MainWindow", f"Error ocultando panel multicolor: {e}")

    def set_multicolor_mode(self, enabled: bool):
        """Cambia el stack entre modo monofilamento y multifilamento."""
        self.ui.stacked_filament_mode.setCurrentIndex(0 if enabled else 1)

    def update_multicolor_slot_weights(self, tooltip_updates: list):
        """
        Actualiza los tooltips de los slots con nuevos pesos.
        tooltip_updates: lista de tuplas (slot_index, tooltip_text)
        El Presenter debe construir el tooltip_text usando _build_multicolor_slot_tooltip.
        """
        try:
            for (slot_index, tooltip_text) in tooltip_updates:
                if 0 <= slot_index < len(self._mc_buttons):
                    self._mc_slot_tooltips[slot_index] = tooltip_text
        except Exception as e:
            logger.error("MainWindow", f"Error actualizando pesos multicolor: {e}")

    def update_multicolor_slot_costs(self, tooltip_updates: list):
        """
        Actualiza tooltips con costos estimados por slot tras un cálculo.
        tooltip_updates: lista de tuplas (slot_index, tooltip_text)
        El Presenter debe construir el tooltip_text usando _build_multicolor_slot_tooltip.
        """
        try:
            for (slot_index, tooltip_text) in tooltip_updates:
                if 0 <= slot_index < len(self._mc_buttons):
                    self._mc_slot_tooltips[slot_index] = tooltip_text
        except Exception as e:
            logger.error("MainWindow", f"Error actualizando costos multicolor: {e}")

    def update_multicolor_slot_filament(self, slot_index: int, filament, tooltip_text: str = ""):
        """Actualiza el detalle visible cuando cambia el filamento del combobox.
        El Presenter debe pasar el tooltip_text ya construido.
        """
        try:
            if 0 <= slot_index < len(self._mc_buttons) and tooltip_text:
                self._mc_slot_tooltips[slot_index] = tooltip_text
            
            if self._mc_active_slot == slot_index:
                self._update_multicolor_details(filament)
        except Exception as e:
            logger.error("MainWindow", f"Error actualizando filamento del slot {slot_index}: {e}")
