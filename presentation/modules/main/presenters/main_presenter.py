"""
Presenter para el MainPanel siguiendo patrón MVP
Contiene toda la lógica de negocio y coordina entre la vista y el modelo
"""

from PySide6.QtCore import QObject, Signal, QTimer, QThread
from typing import Optional
from presentation.widgets.animation_mod.button_size_animator import ButtonSizeAnimator
import os
import uuid
import shutil
import threading
from time import perf_counter
from pathlib import Path

from config.build_config import BUILD_CONFIG, get_app_title
from application.facades.voxeprint_facade import VoxeprintFacade
from application.dtos.quote_dtos import QuoteCalculationResponseDTO, QuoteCreateDTO
from application.services.quote_breakdown_service import QuoteBreakdownService
from core.utils.logger import logger
from core.utils.path_helper import app_root
from core.utils.currency_helper import CurrencyHelper
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from application.dtos.base_dtos import ErrorResponseDTO
from domain.models.customer import Customer
from domain.models.filament import Filament
from domain.models.printer import Printer

from presentation.modules.main.views.main_window import MainPanel
from presentation.modules.quotes.views.quote_preview_dialog import QuotePreviewDialog
from presentation.modules.visualizer.views.pdf_viewer_dialog import PDFViewer
from presentation.modules.filaments.presenters.filament_inventory_presenter import FilamentInventoryPresenter
from presentation.modules.printers.presenters.printer_inventory_presenter import PrinterInventoryPresenter
from presentation.modules.customer.presenters.customer_inventory_presenter import CustomerInventoryPresenter
from presentation.modules.quotes.presenters.quote_inventory_presenter import QuoteInventoryPresenter
from presentation.modules.main.presenters.update_checker_presenter import UpdateCheckerPresenter
from core.services.backup_service import get_backup_service
from core.services.gcode_parser_service import parse_file as parse_gcode_file, GcodeData

from core.managers.tab_event_manager import TabWidgetEventManager, TabManagerConfig


class MainPresenter(QObject):
    """
    Presenter principal que maneja la lógica del MainPanel
    """
    
    # Señales para comunicarse con el exterior
    open_customer_selector = Signal()
    open_filament_selector = Signal()
    open_printer_selector = Signal()
    show_quote_preview = Signal(dict)  # datos del presupuesto
    
    # Señales para orquestación multicolor (Presenter -> View via signals)
    multicolor_set_mode = Signal(bool)          # Activar/desactivar modo multicolor
    multicolor_show = Signal(list)              # Mostrar panel con info de slots
    multicolor_hide = Signal()                  # Ocultar panel
    multicolor_update_weights = Signal(list)    # Actualizar pesos de slots
    multicolor_update_costs = Signal(list)      # Actualizar costos de slots
    multicolor_update_filament = Signal(int, object)  # Actualizar filamento de slot
    
    def __init__(self, parent=None):
        # Asegurar inicialización de QObject sin pasar padres no-QObject
        if isinstance(parent, QObject):
            super().__init__(parent)
        else:
            super().__init__()
        self.view = MainPanel()
        self.view.presenter = self
        self.facade = VoxeprintFacade()
        
        # Estado interno
        self.selected_customer: Optional[Customer] = None
        self.selected_filament: Optional[Filament] = None
        self.selected_printer: Optional[Printer] = None
        self.last_calculation_result: Optional[dict] = None
        # Estado multicolor: lista de dicts con la asignación por slot
        # Cada item: {slot_index, filament_type, colour_hex, weight_grams, percentage,
        #             filament_id, filament_name, price_per_gram, candidates}
        self._multicolor_slots_state: list = []
        self._active_multicolor_slot: int = -1
        self._gcode_async_start_ts: float = 0.0
        self._pdf_async_start_ts: float = 0.0
        
        # ✅ Estado de sincronización de cálculos
        self.is_calculating = False  # Flag para saber si está calculando
        self.results_outdated = False  # Flag para saber si los resultados están obsoletos
        
        # Timer para detectar cambios en tiempo real
        self.calculation_timer = QTimer()
        self.calculation_timer.setSingleShot(True)
        self.calculation_timer.timeout.connect(self._auto_calculate)
        
        # Timer para verificación de actualizaciones automática
        self.update_check_timer = QTimer()
        self.update_check_timer.setSingleShot(True)
        self.update_check_timer.timeout.connect(self._check_updates_on_startup)
        
        # Timer para respaldos automáticos
        self.backup_timer = QTimer()
        self.backup_timer.timeout.connect(self._check_automatic_backup)
        self.backup_timer.start(3600000)  # Verificar cada hora (3600000 ms)
        
        # Inicializar presenter del inventario de filamentos
        self.filament_inventory_presenter = FilamentInventoryPresenter(self.view)
        self._connect_filament_inventory_signals()
        
        # Inicializar presenter del inventario de impresoras
        self.printer_inventory_presenter = PrinterInventoryPresenter(self.view)
        self._connect_printer_inventory_signals()
        
        # Inicializar presenter del inventario de clientes
        self.customer_inventory_presenter = CustomerInventoryPresenter(self.view)
        self._connect_customer_inventory_signals()
        
        # Inicializar presenter del inventario de presupuestos
        self.quote_inventory_presenter = QuoteInventoryPresenter(self.view)
        self._connect_quote_inventory_signals()
        
        # === SISTEMA DE ACTUALIZACIONES ===
        self.update_checker = UpdateCheckerPresenter(self.view)
        
        # Referencia al diálogo About para actualizar su botón
        self.about_dialog_ref = None
        
        # Conectar señales del update checker
        self.update_checker.update_available_signal.connect(self._on_update_detector_signal)
        self.update_checker.no_update_signal.connect(self._on_no_update_detected)
        self.update_checker.version_ignored_signal.connect(self._on_version_ignored_notification)
        self.update_checker.check_error_signal.connect(self._on_update_check_error)
        self.update_checker.update_check_blocked.connect(self._on_update_check_blocked)

        # Animadores de botones selección/limpieza del formulario principal
        self.btn_anim_client: Optional[ButtonSizeAnimator] = None
        self.btn_anim_filament: Optional[ButtonSizeAnimator] = None
        self.btn_anim_printer: Optional[ButtonSizeAnimator] = None
        self.btn_anim_gcode: Optional[ButtonSizeAnimator] = None
    
    def run(self):        
        # Conectar señales de la vista
        self._connect_view_signals()        
        # Inicializar vista
        self._initialize_view()       
        
        # Aplicar tema al MainPanel para asegurar coherencia
        self._apply_current_theme_to_view()
        
        # Log de éxito usando el sistema centralizado (solo debug, no visible en consola)
        logger.debug("MainPresenter", "Aplicación iniciada correctamente")
        logger.debug("MainPresenter", "Sistema configurado y listo para usar")
        logger.debug("MainPresenter", "Calculadora de presupuestos 3D disponible")
        logger.debug("MainPresenter", "Inventario de filamentos cargado")
        logger.debug("MainPresenter", "Inventario de impresoras cargado")
        logger.debug("MainPresenter", "Inventario de clientes cargado")
        
        # Inicializar sistema de respaldos automáticos
        self._initialize_backup_system()
        
        # Aplicar preferencias de impresora después de establecer conexiones
        self._apply_printer_preferences()
        
        # Aplicar preferencias de cliente después de establecer conexiones
        self._apply_customer_preferences()
        
        # Aplicar preferencias de anticipo al iniciar
        self._apply_advance_preferences_on_startup()
        logger.debug("MainPresenter", "run: anticipo aplicado")
        
        # ✅ Establecer estado inicial de los botones de acción
        self._update_action_buttons_state()
        logger.debug("MainPresenter", "run: botones de accion actualizados")

        # Configurar animaciones de botones del formulario principal
        self._setup_button_animations()
        logger.debug("MainPresenter", "run: animaciones configuradas")
        
        # 🔄 Verificar actualizaciones de forma asincrónica (después de 5 segundos)
        if BUILD_CONFIG.release.auto_update_enabled:
            self.update_check_timer.start(5000)
        logger.debug("MainPresenter", "run: timer de actualizaciones configurado")
        
        self.view.add_separator()
        logger.debug("MainPresenter", "run: separator agregado")
        self.view.show()
        logger.debug("MainPresenter", "run: view.show() completado")

    def _setup_button_animations(self):
        """Configura las animaciones de intercambio de tamaños para los pares de botones
        selección/limpieza del formulario principal de presupuesto."""
        ui = self.view.ui
        pairs = [
            ("btn_select_client",     "btn_cleaner_client",      "btn_anim_client"),
            ("btn_select_printer_3d", "btn_cleaner_printer_3d",  "btn_anim_printer"),
        ]
        for primary_name, secondary_name, attr in pairs:
            try:
                if not hasattr(ui, primary_name) or not hasattr(ui, secondary_name):
                    logger.warning("MainPresenter", f"Botones no encontrados para animación: {primary_name}/{secondary_name}")
                    continue
                animator = ButtonSizeAnimator(
                    primary_button=getattr(ui, primary_name),
                    secondary_button=getattr(ui, secondary_name),
                    primary_normal_width=95,
                    primary_hover_width=25,
                    secondary_normal_width=25,
                    secondary_hover_width=95,
                    animation_duration=200
                )
                setattr(self, attr, animator)
            except Exception as e:
                logger.error("MainPresenter", f"Error configurando animación {primary_name}/{secondary_name}: {e}")

        # Conectar clicks de los botones cleaner
        ui.btn_cleaner_client.clicked.connect(self._handle_clear_client)
        ui.btn_cleaner_printer_3d.clicked.connect(self._handle_clear_printer)

    def _apply_current_theme_to_view(self):
        """Aplica el tema actual al MainPanel"""
        try:
            # Obtener una referencia al theme manager desde la aplicación
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            
            if hasattr(app, 'palette_manager'):
                # Si la aplicación tiene un theme manager, obtener el QSS actual
                theme_manager = app.palette_manager
                qss_content = theme_manager.load_qss_stylesheet()
                
                # Aplicar el tema al MainPanel
                self.view.apply_theme_to_main_panel(qss_content)
                # Tema aplicado silenciosamente
            else:
                # Si no hay theme manager disponible, limpiar estilos para usar tema por defecto
                self.view.apply_theme_to_main_panel("")
                self.view.add_system_log("🎨 Usando tema por defecto del sistema")
                
        except Exception as e:
            logger.error("MainPresenter", f"Error aplicando tema: {e}")
            self.view.add_system_log("⚠️ Error aplicando tema - usando estilos por defecto")
    
    def apply_theme_change(self, qss_content: str, theme_name: str = ""):
        """Aplica un cambio de tema al MainPanel desde el exterior"""
        try:
            self.view.apply_theme_to_main_panel(qss_content)
            if theme_name:
                self.view.add_system_log(f"🎨 Tema cambiado a: {theme_name}")
            else:
                self.view.add_system_log("🎨 Tema actualizado")
        except Exception as e:
            logger.error("MainPresenter", f"Error aplicando cambio de tema: {e}")
            self.view.add_system_log("⚠️ Error aplicando nuevo tema")

    def _sync_pdf_theme(self, pdf_viewer_dialog):
        """
        Sincroniza el tema del visor PDF con el tema actual de la aplicación
        
        Args:
            pdf_viewer_dialog: Instancia de PDFViewer
        """
        try:
            # Obtener theme manager desde la aplicación
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            
            if hasattr(app, 'palette_manager'):
                theme_manager = app.palette_manager
                
                # Determinar tema a aplicar
                if theme_manager.is_dark_mode:
                    pdf_theme = "dark"
                    theme_name = "Oscuro"
                else:
                    pdf_theme = "light"
                    theme_name = "Claro"
                
                # Aplicar tema al visor PDF
                pdf_viewer_dialog.set_pdf_theme(pdf_theme)
            else:
                # Si no hay theme manager, usar automático
                pdf_viewer_dialog.set_pdf_theme("auto")
                
        except Exception as e:
            logger.error("MainPresenter", f"Error sincronizando tema del PDF: {e}")
            # Fallback a automático
            pdf_viewer_dialog.set_pdf_theme("auto")

    def _connect_view_signals(self):
        """Conecta las señales de la vista con los métodos del presenter"""
        # Búsquedas/Selecciones
        self.view.client_search_requested.connect(self._handle_client_search)
        self.view.filament_search_requested.connect(self._handle_filament_search)
        self.view.printer_search_requested.connect(self._handle_printer_search)
        self.view.load_gcode_requested.connect(self._handle_load_gcode)
        self.view.printer_combox_changed.connect(self._handle_printer_combox_changed)
        self.view.filament_combox_changed.connect(self._handle_filament_combox_changed)
        
        # Operaciones
        self.view.calculate_quote_requested.connect(self._handle_calculate_quote)
        self.view.clear_form_requested.connect(self._handle_clear_form)
        self.view.preview_requested.connect(self._handle_preview_quote)
        self.view.save_quote_requested.connect(self._handle_save_quote)
        self.view.generate_note_requested.connect(self._handle_generate_note)
        self.view.settings_requested.connect(self._handle_settings_request)  # Nueva conexión
        
        # Cierre de aplicación - usar señal desde la vista
        self.view.close_application_requested.connect(self._handle_close_application)
        
        # Elementos clickeables
        self.view.build_info_requested.connect(self._handle_build_info_request)
        self.view.donation_requested.connect(self._handle_donation_request)
        
        self.view.time_changed_immediate.connect(self._invalidate_results_immediately)
        self.view.weight_changed_immediate.connect(self._invalidate_results_immediately)
        self.view.quantity_changed_immediate.connect(self._invalidate_results_immediately)
        self.view.advance_enabled_changed_immediate.connect(self._invalidate_results_immediately)
        self.view.advance_percentage_changed_immediate.connect(self._invalidate_results_immediately)
        self.view.post_enabled_changed_immediate.connect(self._invalidate_results_immediately)
        self.view.post_amount_changed_immediate.connect(self._invalidate_results_immediately)
        self.view.post_type_changed_immediate.connect(self._invalidate_results_immediately)
        
        # Multicolor: slot filament assignment changed
        self.view.multicolor_slot_changed.connect(self._handle_multicolor_slot_changed)
        self.view.multicolor_slot_selected.connect(self._handle_multicolor_slot_selected)
        self.view.multicolor_search_requested.connect(self._handle_multicolor_slot_search)

        # 🕒 PROCESAMIENTO CON DELAY - Para auto-cálculo después de 800ms-1.5s
        self.view.time_changed.connect(self._on_time_changed)
        self.view.weight_changed.connect(self._on_weight_changed)
        self.view.quantity_changed.connect(self._on_quantity_changed)
        self.view.customer_optional_changed.connect(self._on_customer_optional_changed)
        
        # Cambios en sistema de anticipo
        self.view.advance_enabled_changed.connect(self._on_advance_enabled_changed)
        self.view.advance_percentage_changed.connect(self._on_advance_percentage_changed)
        
        # Cambios en sistema de post-procesado
        self.view.post_enabled_changed.connect(self._on_post_enabled_changed)
        self.view.post_amount_changed.connect(self._on_post_amount_changed)
        self.view.post_type_changed.connect(self._on_post_type_changed)
    
    def _connect_filament_inventory_signals(self):
        """Conecta las señales del presenter de inventario de filamentos"""
        self.filament_inventory_presenter.filament_selected.connect(self._on_inventory_filament_selected)
        self.filament_inventory_presenter.filament_deleted.connect(self._on_inventory_filament_deleted)
        self.filament_inventory_presenter.filament_modified.connect(self._on_inventory_filament_modified)
    
    def _connect_printer_inventory_signals(self):
        """Conecta las señales del presenter de inventario de impresoras"""
        self.printer_inventory_presenter.printer_selected.connect(self._on_inventory_printer_selected)
        self.printer_inventory_presenter.printer_deleted.connect(self._on_inventory_printer_deleted)
        self.printer_inventory_presenter.printer_modified.connect(self._on_inventory_printer_modified)
    
    def _connect_customer_inventory_signals(self):
        """Conecta las señales del presenter de inventario de clientes"""
        self.customer_inventory_presenter.customer_selected.connect(self._on_inventory_customer_selected)
        self.customer_inventory_presenter.customer_deleted.connect(self._on_inventory_customer_deleted)
        self.customer_inventory_presenter.customer_modified.connect(self._on_inventory_customer_modified)
    
    def _connect_quote_inventory_signals(self):
        """Conecta las señales del presenter de inventario de presupuestos"""
        self.quote_inventory_presenter.quote_selected.connect(self._on_inventory_quote_selected)
        self.quote_inventory_presenter.quote_deleted.connect(self._on_inventory_quote_deleted)
        self.quote_inventory_presenter.quote_modified.connect(self._on_inventory_quote_modified)
    
    def _update_currency_labels(self):
        """Actualiza los labels de moneda en la interfaz según la moneda actual del sistema"""
        try:
            current_currency = CurrencyHelper.get_current_currency()
            
            # Actualizar label de post-procesado
            post_label = CurrencyHelper.get_label_with_currency("Monto", current_currency)
            self.view.set_post_label(post_label)
            
        except Exception as e:
            logger.error("MainPresenter", f"Error actualizando labels de moneda: {e}")
    
    def _initialize_view(self):
        """Inicializa el estado de la vista"""
        # Pasar el facade a la vista para que pueda usarlo
        self.view.voxeprint_facade = self.facade
        
        # Pasar el facade a los presenters de inventario
        self.filament_inventory_presenter.set_facade(self.facade)
        self.printer_inventory_presenter.set_facade(self.facade)
        self.customer_inventory_presenter.set_facade(self.facade)
        self.quote_inventory_presenter.set_facade(self.facade)
        
        # Actualizar labels de moneda según la configuración actual
        self._update_currency_labels()
        
        self.view.add_system_log("🚀 Sistema listo para calcular presupuestos")
        self.view.add_status_message("Tip: 💡Seleccione impresora, filamento y configure los parámetros")
        
        # Configurar tab manager para doble click y F5
        self._setup_tab_manager()
        
        # ✅ Establecer estado inicial del botón Preview
        self._update_preview_button_state()
    
    # === MANEJADORES DE EVENTOS DE LA VISTA ===
    
    def _handle_client_search(self):
        """Maneja la solicitud de búsqueda de cliente usando el nuevo selector"""
        from presentation.modules.customer.presenters.customer_selector_presenter_new import CustomerSelectorPresenterNew
        
        self.view.add_action_log("Búsqueda de cliente solicitada")
        
        try:
            # Abrir ventana de selección de clientes
            presenter = CustomerSelectorPresenterNew(self.view)
            # Inyectar facade
            presenter.set_facade(self.facade)
            self.view.add_action_log("Ventana de selección de cliente abierta")
            selected = presenter.run()
            if selected:
                self.view.add_action_log(f"Cliente seleccionado: {selected.full_name}")
                self.set_selected_customer(selected)
            else:
                self.view.add_action_log("Selección de cliente cancelada")
                
        except Exception as e:
            self.view.add_error_log(f"Error en selector de clientes: {e}")
            logger.error("MainPresenter", f"Error en selector de clientes: {e}")
    
    def _handle_filament_search(self):
        from presentation.modules.filaments.presenters.filament_selector_presenter_new import FilamentSelectorPresenterNew
        """Maneja la solicitud de búsqueda de filamento"""
        self.view.add_action_log("Búsqueda de filamento solicitada")

        try:            
            # Abrir ventana de selección de filamentos
            presenter = FilamentSelectorPresenterNew(self.view)
            # Inyectar facade
            presenter.set_facade(self.facade)
            self.view.add_action_log("Ventana de selección de filamento abierta")
            selected = presenter.run()
            if selected:
                self.set_selected_filament(selected)
                self.view.add_action_log(f"Filamento seleccionado: {selected.name}")
            else:
                self.view.add_action_log("Selección de filamento cancelada")
        except Exception as e:
            self.view.add_error_log(f"Error en selector de filamentos: {e}")
            logger.error("MainPresenter", f"Error en selector de filamentos: {e}")
    
    def _handle_printer_search(self):
        """Maneja la solicitud de búsqueda de impresora usando el nuevo selector"""
        from presentation.modules.printers.presenters.printer_selector_presenter_new import PrinterSelectorPresenterNew
        
        self.view.add_action_log("Búsqueda de impresora solicitada")
        
        try:
            # Abrir ventana de selección de impresoras
            presenter = PrinterSelectorPresenterNew(self.view)
            # Inyectar facade
            presenter.set_facade(self.facade)
            self.view.add_action_log("Ventana de selección de impresora abierta")
            selected = presenter.run()
            if selected:
                self.view.add_action_log(f"Impresora seleccionada: {selected.name}")
                self.set_selected_printer(selected)
            else:
                self.view.add_action_log("Selección de impresora cancelada")
                
        except Exception as e:
            self.view.add_error_log(f"Error en selector de impresoras: {e}")
            logger.error("MainPresenter", f"Error en selector de impresoras: {e}")

    def _handle_load_gcode(self):
        """Maneja la carga de un archivo G-code o 3MF"""
        from PySide6.QtWidgets import QFileDialog
        from core.utils.path_helper import get_user_start_dir
        
        self.view.add_action_log("Carga de proyecto G-code solicitada")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Seleccionar archivo G-code o 3MF",
            get_user_start_dir(),
            "Archivos de impresión (*.gcode *.3mf);;G-code (*.gcode);;3MF (*.3mf);;Todos (*.*)"
        )
        if not file_path:
            self.view.add_action_log("Carga de G-code cancelada")
            return

        def _on_gcode_parsed(result, error, _file_path=file_path):
            callback_start_ts = perf_counter()
            total_async_ms = (callback_start_ts - self._gcode_async_start_ts) * 1000 if self._gcode_async_start_ts else 0.0
            logger.debug(
                "MainPresenter",
                (
                    "gcode_async_callback_start "
                    f"elapsed_ms={total_async_ms:.1f} qt_thread={id(QThread.currentThread())} "
                    f"py_thread={threading.get_ident()}"
                )
            )

            if error:
                self.view.add_error_log(f"Error al parsear G-code: {error}")
                logger.error("MainPresenter", f"Error al parsear G-code: {error}")
                logger.log_exception("MainPresenter", error, "_handle_load_gcode")
                return

            data = result

            # Verificar si el .3mf no tiene datos de slicing
            if _file_path.lower().endswith('.3mf') and data.print_time_hours == 0 and data.filament_weight_grams == 0:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self.view,
                    tr(I18N.Errors.DATA_INCOMPLETE_TITLE),
                    tr(I18N.Errors.DATA_INCOMPLETE_MSG)
                )
                self.view.add_action_log("3MF sin datos de slicing — archivo no sliceado")

            # Cargar nombre, thumbnail y parámetros del slicer en la UI
            self.view.set_gcode_project(
                data.file_name, data.thumbnail,
                layer_height=data.layer_height,
                nozzle_diameter=data.nozzle_diameter,
                bed_temperature=data.bed_temperature,
                hotend_temperature=data.hotend_temperature
            )
            
            # Auto-fill tiempo si está disponible
            if data.print_time_hours > 0:
                total_minutes = int(data.print_time_hours * 60)
                hours = total_minutes // 60
                minutes = total_minutes % 60
                # Mantener cantidad actual
                current_qty = self.view.get_quantity()
                self.view.set_piece_parameters(hours, minutes, int(round(data.filament_weight_grams)), current_qty)
            
            # Auto-fill peso si está disponible
            elif data.filament_weight_grams > 0:
                # Mantener valores de tiempo y cantidad actuales
                current_hours = self.view.get_time_hours()
                current_minutes = self.view.get_time_minutes()
                current_qty = self.view.get_quantity()
                self.view.set_piece_parameters(current_hours, current_minutes, int(round(data.filament_weight_grams)), current_qty)
            
            self.view.add_action_log(
                f"G-code cargado: {data.file_name} | "
                f"Slicer: {data.slicer or 'Desconocido'} | "
                f"Material: {data.normalized_type or data.filament_type or '—'}"
            )
            
            # Guardar datos del gcode para uso posterior (match de filamento/impresora)
            self._last_gcode_data = data

            # Match de impresora del G-code con la base de datos
            if data.printer_model:
                self._match_printer_from_gcode(data.printer_model)

            if data.is_multicolor and data.filament_slots:
                # MULTICOLOR: auto-asignar cada slot independientemente
                self._auto_assign_multicolor_slots(data.filament_slots)
            elif data.normalized_type or data.filament_type:
                self._multicolor_slots_state = []
                self._active_multicolor_slot = -1
                self.view.hide_multicolor_panel()
                self.view.set_multicolor_mode(False)
                # MONOCOLOR: match único existente
                self._match_filament_from_gcode(
                    data.normalized_type or data.filament_type,
                    data.filament_colour
                )
            else:
                self._multicolor_slots_state = []
                self._active_multicolor_slot = -1
                self.view.hide_multicolor_panel()
                self.view.set_multicolor_mode(False)

            callback_ms = (perf_counter() - callback_start_ts) * 1000
            if callback_ms >= 80:
                logger.warning("MainPresenter", f"gcode_async_callback_end elapsed_ms={callback_ms:.1f}")
            else:
                logger.debug("MainPresenter", f"gcode_async_callback_end elapsed_ms={callback_ms:.1f}")

        # Arrancar animación + hilo secundario via run_async
        from presentation.widgets.animation_mod.rotating_circle import WaitingCircle

        self._gcode_loading = WaitingCircle(parent=self.view)
        self._gcode_loading.superposition(True)
        self._gcode_async_start_ts = perf_counter()
        logger.debug("MainPresenter", f"gcode_async_start file={Path(file_path).name}")

        self._gcode_loading.run_async(
            parse_gcode_file,
            _on_gcode_parsed,
            file_path
        )

    def _match_printer_from_gcode(self, gcode_printer_model: str):
        """Busca impresoras en la BD que coincidan con el modelo del G-code.
        Construye una lista de prioridad:
          1. Preferencia del usuario (si existe)
          2. Mejor match con el G-code
          3. Otras impresoras con parentesco parcial
        """
        try:
            all_printers = self.facade.get_all_printers()
            if not all_printers:
                self.view.add_action_log("Sin impresoras en BD para hacer match")
                return

            gcode_lower = gcode_printer_model.lower().strip()
            gcode_tokens = set(gcode_lower.replace('-', ' ').replace('_', ' ').split())
            generic_tokens = {'3d', 'printer', 'pro', 'plus', 'max', 'mini', 'v2', 'v3', 'se'}

            scored: list[tuple[int, Printer]] = []
            for p in all_printers:
                score = self._score_printer_match(p, gcode_lower, gcode_tokens, generic_tokens)
                if score > 0:
                    scored.append((score, p))

            # Ordenar por score descendente
            scored.sort(key=lambda x: x[0], reverse=True)

            # Determinar preferencia del usuario
            pref_printer: Printer | None = None
            try:
                pref_id = self.view.app_preferences.get_default_printer_id()
                if pref_id and pref_id != "first":
                    pref_printer = self.facade.get_printer_by_id(int(pref_id))
                    if pref_printer and not pref_printer.is_active:
                        pref_printer = None
            except Exception:
                pass

            # Construir lista de opciones (display_name, printer_id)
            options: list[tuple[str, int]] = []
            seen_ids: set[int] = set()

            # 1) Preferencia del usuario primero (si existe y no está ya en matches)
            if pref_printer:
                options.append((pref_printer.name, pref_printer.id))
                seen_ids.add(pref_printer.id)

            # 2) Matches del G-code
            for score, p in scored:
                if p.id not in seen_ids:
                    options.append((p.name, p.id))
                    seen_ids.add(p.id)

            if not options:
                self.view.add_action_log(
                    f"Impresora G-code '{gcode_printer_model}' sin coincidencias en BD"
                )
                return

            # Guardar mapa de id→Printer para selección rápida
            self._printer_options_map = {p.id: p for _, p in scored}
            if pref_printer:
                self._printer_options_map[pref_printer.id] = pref_printer

            # Cargar opciones en el combobox
            self.view.set_printer_options(options, selected_index=0)

            # Seleccionar automáticamente la primera opción
            first_id = options[0][1]
            first_printer = self._printer_options_map.get(first_id)
            if first_printer:
                self._apply_printer_selection(first_printer)

            match_count = len(options)
            best_name = options[0][0]
            self.view.add_action_log(
                f"Match impresora: '{gcode_printer_model}' → {best_name} "
                f"({match_count} opcion{'es' if match_count > 1 else ''})"
            )

        except Exception as e:
            logger.error("MainPresenter", f"Error en match de impresora: {e}")
            self.view.add_error_log(f"Error buscando impresora: {e}")

    def _score_printer_match(self, printer: Printer, gcode_lower: str,
                             gcode_tokens: set, generic_tokens: set) -> int:
        """Calcula un puntaje de coincidencia entre una impresora de BD y el modelo del G-code."""
        score = 0
        p_name = (printer.name or "").lower()
        p_model = (printer.model or "").lower()
        p_brand = (printer.brand or "").lower()
        combined = f"{p_name} {p_model} {p_brand}"

        # Match exacto del modelo
        if gcode_lower == p_model or gcode_lower == p_name:
            return 100

        # El gcode está contenido en nombre/modelo o viceversa
        if gcode_lower in combined or p_model in gcode_lower:
            score += 60

        # Match por tokens significativos
        p_tokens = set(combined.replace('-', ' ').replace('_', ' ').split())
        significant_gcode = gcode_tokens - generic_tokens
        significant_p = p_tokens - generic_tokens
        if significant_gcode and significant_p:
            overlap = significant_gcode & significant_p
            score += len(overlap) * 20

        return score

    def _handle_printer_combox_changed(self, index: int):
        """Maneja el cambio de selección en el combobox de impresora"""
        printer_id = self.view.get_printer_id_at_index(index)
        if printer_id is None:
            return

        printer_map = getattr(self, '_printer_options_map', {})
        printer = printer_map.get(printer_id)
        if not printer:
            # Fallback: buscar en BD
            try:
                printer = self.facade.get_printer_by_id(printer_id)
            except Exception:
                return
        if printer:
            self._apply_printer_selection(printer)
            self.view.add_action_log(f"Impresora seleccionada del menú: {printer.name}")

    def _apply_printer_selection(self, printer: Printer):
        """Aplica una impresora seleccionada actualizando campos y estado interno."""
        self._mark_results_outdated()
        self.selected_printer = printer
        # Delegate UI update to the View (MVP compliant)
        self.view.update_printer_details(printer)
        self._schedule_auto_calculation()

    # === MATCH DE FILAMENTO DESDE G-CODE ===

    def _match_filament_from_gcode(self, gcode_filament_type: str, gcode_colour: str = ""):
        """Busca filamentos en la BD que coincidan con el tipo del G-code.
        Construye una lista de prioridad:
          1. Mejor match por tipo + color
          2. Matches parciales por tipo
        """
        try:
            all_filaments = self.facade.get_all_filaments()
            if not all_filaments:
                self.view.add_action_log("Sin filamentos en BD para hacer match")
                return

            gcode_type_lower = gcode_filament_type.lower().strip()
            gcode_colour_lower = (gcode_colour or "").lower().strip()

            scored: list[tuple[int, object]] = []
            for f in all_filaments:
                score = self._score_filament_match(f, gcode_type_lower, gcode_colour_lower)
                if score > 0:
                    scored.append((score, f))

            scored.sort(key=lambda x: x[0], reverse=True)

            if not scored:
                self.view.add_action_log(
                    f"Filamento G-code '{gcode_filament_type}' sin coincidencias en BD"
                )
                return

            # Construir opciones
            options: list[tuple[str, int]] = []
            seen_ids: set[int] = set()

            for _score, f in scored:
                if f.id not in seen_ids:
                    options.append((f.name, f.id))
                    seen_ids.add(f.id)

            # Guardar mapa de id→Filament
            self._filament_options_map = {f.id: f for _, f in scored}

            # Cargar opciones en el combobox
            self.view.set_filament_options(options, selected_index=0)

            # Seleccionar automáticamente la primera
            first_id = options[0][1]
            first_filament = self._filament_options_map.get(first_id)
            if first_filament:
                self._apply_filament_selection(first_filament)

            match_count = len(options)
            best_name = options[0][0]
            self.view.add_action_log(
                f"Match filamento: '{gcode_filament_type}' → {best_name} "
                f"({match_count} opcion{'es' if match_count > 1 else ''})"
            )

        except Exception as e:
            logger.error("MainPresenter", f"Error en match de filamento: {e}")
            self.view.add_error_log(f"Error buscando filamento: {e}")

    # === MULTICOLOR: asignación automática por slot ===

    def _auto_assign_multicolor_slots(self, slots):
        """Asigna automáticamente filamentos a cada slot usando la misma mecánica del monocolor."""
        logger.debug("MainPresenter", f"_auto_assign_multicolor_slots: {len(slots)} slots detectados")
        try:
            all_filaments = self.facade.get_all_filaments() or []
            if not all_filaments:
                self.view.add_action_log("Sin filamentos en BD para asignar slots multicolor")

            self._multicolor_slots_state = []
            slots_info = []  # Para la vista

            for slot in slots:
                gcode_type = slot.filament_type or ""
                colour = slot.colour_hex or ""
                gcode_type_lower = gcode_type.lower().strip()
                colour_lower = colour.lower().strip()

                scored = []
                for f in all_filaments:
                    if not self._is_filament_type_compatible(f, gcode_type_lower):
                        continue
                    score = self._score_filament_match(f, gcode_type_lower, colour_lower)
                    if score > 0:
                        scored.append((score, f))
                scored.sort(key=lambda x: x[0], reverse=True)

                candidates = [(f.name, f.id) for _, f in scored]
                # Fallback: si no hay candidatos nativos, usar todos los del mismo tipo o cualquier activo
                has_match = bool(candidates)
                if not candidates:
                    same_type = [f for f in all_filaments if getattr(f, 'is_active', True) and self._is_filament_type_compatible(f, gcode_type_lower)]
                    base_pool = same_type if same_type else [f for f in all_filaments if getattr(f, 'is_active', True)]
                    candidates = [(f.name, f.id) for f in base_pool][:12]

                best_id = candidates[0][1] if candidates else 0
                best_name = candidates[0][0] if candidates else "—"
                best_ppg = 0.0
                best_filament = None
                if best_id:
                    fmap = {f.id: f for _, f in scored} if scored else {}
                    if best_id in fmap:
                        best_ppg = fmap[best_id].price_per_gram or 0.0
                        best_filament = fmap[best_id]
                    else:
                        best_filament = next((f for f in all_filaments if f.id == best_id), None)
                        if best_filament:
                            best_ppg = best_filament.price_per_gram or 0.0

                slot_state = {
                    'slot_index': slot.slot_index,
                    'filament_type': slot.filament_type,
                    'colour_hex': slot.colour_hex,
                    'weight_grams': slot.weight_grams,
                    'percentage': slot.percentage,
                    'filament_id': best_id,
                    'filament_name': best_name,
                    'price_per_gram': best_ppg,
                    'candidates': candidates,
                    'filament': best_filament,
                    'has_match': has_match,
                }
                self._multicolor_slots_state.append(slot_state)
                slots_info.append(slot_state)

            self._active_multicolor_slot = 0 if self._multicolor_slots_state else -1
            self.view.set_multicolor_mode(True)
            self.view.show_multicolor_panel(slots_info)
            # Notificar alerta si algún slot no encontró filamento compatible
            unmatched = [s for s in slots_info if not s.get('has_match', True)]
            if unmatched:
                types = ", ".join(s['filament_type'] or '?' for s in unmatched)
                self.view.set_multicolor_alert(
                    True,
                    tr(I18N.MainWindow.MULTICOLOR_ALERT_UNMATCHED, types=types)
                )
            else:
                self.view.set_multicolor_alert(False, tr(I18N.MainWindow.MULTICOLOR_ALERT_OK))
            # Configurar combobox y estilos desde el Presenter (único dueño del estado)
            if self._active_multicolor_slot >= 0 and self._multicolor_slots_state:
                slot = self._multicolor_slots_state[self._active_multicolor_slot]
                self.view.load_multicolor_combobox(slot['candidates'], slot['filament_id'], slot_index=self._active_multicolor_slot)
                # Actualizar estilos de todos los botones
                for i, s in enumerate(self._multicolor_slots_state):
                    self.view.update_multicolor_button_style(
                        i, s['colour_hex'], selected=(i == self._active_multicolor_slot),
                        has_match=s.get('has_match', True)
                    )
                # Actualizar detalles del filamento seleccionado
                self.view._update_multicolor_details(slot.get('filament'))
            self.view.add_action_log(
                f"Multicolor: {len(slots)} slots detectados y asignados automáticamente"
            )
            # Usar el filamento del slot principal (mayor peso) como selección monocolor de referencia
            if self._multicolor_slots_state:
                heaviest = max(self._multicolor_slots_state, key=lambda s: s['weight_grams'])
                if heaviest['filament_id']:
                    ref_fil = self.facade.get_filament_by_id(heaviest['filament_id'])
                    if ref_fil:
                        self._apply_filament_selection(ref_fil)

        except Exception as e:
            logger.error("MainPresenter", f"Error en asignación multicolor: {e}")
            self.view.add_error_log(f"Error en multicolor: {e}")

    def _is_filament_type_compatible(self, filament, gcode_type_lower: str) -> bool:
        """Determina si un filamento de inventario corresponde al tipo del slot detectado."""
        if not gcode_type_lower:
            return True
        f_type = ""
        if hasattr(filament.type, 'value'):
            f_type = str(filament.type.value).lower().strip()
        elif filament.type:
            f_type = str(filament.type).lower().strip()

        return (
            gcode_type_lower == f_type
            or gcode_type_lower in f_type
            or f_type in gcode_type_lower
        )

    def _rebalance_multicolor_slots(self, new_total: int):
        """Redistribuye los gramos entre slots según el % original de cada uno."""
        if not self._multicolor_slots_state or new_total <= 0:
            return
        total_pct = sum(s['percentage'] for s in self._multicolor_slots_state)
        if total_pct <= 0:
            return
        # Repartir con corrección de redondeo en el último slot
        remaining = new_total
        for i, slot in enumerate(self._multicolor_slots_state[:-1]):
            new_g = round(new_total * (slot['percentage'] / total_pct), 2)
            slot['weight_grams'] = new_g
            remaining -= new_g
        # El último slot toma el residuo para que la suma sea exacta
        self._multicolor_slots_state[-1]['weight_grams'] = round(remaining, 2)
        # Actualizar panel de la vista con tooltips ya construidos
        tooltip_updates = [
            (s['slot_index'], self._build_multicolor_slot_tooltip(s))
            for s in self._multicolor_slots_state
        ]
        self.view.update_multicolor_slot_weights(tooltip_updates)

    def _handle_multicolor_slot_changed(self, slot_index: int, filament_id: int):
        """Maneja el cambio de filamento asignado a un slot multicolor desde la UI."""
        logger.debug("MainPresenter", f"_handle_multicolor_slot_changed: slot={slot_index}, filament_id={filament_id}")
        for slot in self._multicolor_slots_state:
            if slot['slot_index'] == slot_index:
                slot['filament_id'] = filament_id
                fil = self.facade.get_filament_by_id(filament_id) if filament_id > 0 else None
                slot['filament_name'] = fil.name if fil else "—"
                slot['price_per_gram'] = (fil.price_per_gram or 0.0) if fil else 0.0
                slot['filament'] = fil
                # Construir tooltip y actualizar vista
                tooltip_text = self._build_multicolor_slot_tooltip(slot)
                self.view.update_multicolor_slot_filament(slot_index, fil, tooltip_text)
                self.view.add_action_log(f"Slot {slot_index}: → {slot['filament_name']}")
                break
        self._mark_results_outdated()
        self._schedule_auto_calculation()

    def _handle_multicolor_slot_selected(self, slot_index: int):
        """Carga el combobox y actualiza estilos al seleccionar un slot."""
        logger.debug("MainPresenter", f"_handle_multicolor_slot_selected: slot={slot_index}, active_slot={self._active_multicolor_slot}")
        self._active_multicolor_slot = slot_index
        # Buscar el slot en el estado
        slot = next((s for s in self._multicolor_slots_state if s['slot_index'] == slot_index), None)
        if not slot:
            return
        # Cargar combobox con candidatos del slot activo
        self.view.load_multicolor_combobox(slot['candidates'], slot['filament_id'], slot_index=slot_index)
        # Actualizar estilos de todos los botones
        for i, s in enumerate(self._multicolor_slots_state):
            self.view.update_multicolor_button_style(
                i, s['colour_hex'], selected=(i == slot_index),
                has_match=s.get('has_match', True)
            )
        # Actualizar detalles del filamento seleccionado
        self.view._update_multicolor_details(slot.get('filament'))

    def _handle_multicolor_slot_search(self, slot_index: int):
        """Abre el selector de filamento filtrado por el tipo de material del slot activo."""
        slot = next((s for s in self._multicolor_slots_state if s['slot_index'] == slot_index), None)
        if not slot:
            return

        material_type = slot.get('filament_type') or ""
        logger.info("MainPresenter", f"Búsqueda de filamento para slot {slot_index}, tipo: {material_type}")

        from presentation.modules.filaments.presenters.filament_selector_presenter_new import FilamentSelectorPresenterNew
        selector = FilamentSelectorPresenterNew(self.view)
        selector.set_facade(self.facade)
        selected = selector.run(initial_filter=material_type)

        if not selected:
            return

        # Actualizar estado del slot con el filamento elegido
        slot['filament_id'] = selected.id
        slot['filament_name'] = selected.name
        slot['price_per_gram'] = selected.price_per_gram or 0.0
        slot['filament'] = selected
        # Si el usuario eligió manualmente, marcamos el slot como resuelto
        slot['has_match'] = True

        # Reconstruir candidatos para que el combobox incluya el recién elegido como primera opción
        existing_ids = {fid for _, fid in slot['candidates']}
        if selected.id not in existing_ids:
            slot['candidates'].insert(0, (selected.name, selected.id))

        # Actualizar combobox y detalles
        self.view.load_multicolor_combobox(slot['candidates'], slot['filament_id'], slot_index=slot_index)
        tooltip_text = self._build_multicolor_slot_tooltip(slot)
        self.view.update_multicolor_slot_filament(slot_index, selected, tooltip_text)

        # Refrescar estilos de todos los botones (puede haber cambiado has_match)
        for i, s in enumerate(self._multicolor_slots_state):
            self.view.update_multicolor_button_style(
                i, s['colour_hex'], selected=(i == slot_index),
                has_match=s.get('has_match', True)
            )

        # Re-evaluar alerta global
        unmatched = [s for s in self._multicolor_slots_state if not s.get('has_match', True)]
        if unmatched:
            types = ", ".join(s['filament_type'] or '?' for s in unmatched)
            self.view.set_multicolor_alert(
                True,
                tr(I18N.MainWindow.MULTICOLOR_ALERT_UNMATCHED, types=types)
            )
        else:
            self.view.set_multicolor_alert(False, tr(I18N.MainWindow.MULTICOLOR_ALERT_OK))

        self.view.add_action_log(f"Slot {slot_index}: filamento actualizado → {selected.name}")
        self._mark_results_outdated()
        self._schedule_auto_calculation()

    def _score_filament_match(self, filament, gcode_type_lower: str, gcode_colour_lower: str) -> int:
        """Calcula un puntaje de coincidencia entre un filamento de BD y el tipo del G-code."""
        score = 0

        # Tipo del filamento en BD
        f_type = ""
        if hasattr(filament.type, 'value'):
            f_type = filament.type.value.lower()
        elif filament.type:
            f_type = str(filament.type).lower()

        f_name = (filament.name or "").lower()
        f_brand = (filament.brand or "").lower()

        # Match exacto de tipo
        if gcode_type_lower == f_type:
            score += 80
        # Tipo contenido en nombre
        elif gcode_type_lower in f_name or f_type in gcode_type_lower:
            score += 40
        # Tipo contenido en tipo (parcial, ej: "pla" en "pla+")
        elif gcode_type_lower in f_type or f_type in gcode_type_lower:
            score += 30

        # Bonus por color (si disponible)
        if gcode_colour_lower and score > 0:
            f_color = ""
            if hasattr(filament.color, 'value'):
                f_color = filament.color.value.lower()
            elif filament.color:
                f_color = str(filament.color).lower()

            # Color hex (#RRGGBB) → no se puede comparar directamente con nombre
            if not gcode_colour_lower.startswith('#') and f_color:
                if gcode_colour_lower == f_color:
                    score += 20
                elif gcode_colour_lower in f_color or f_color in gcode_colour_lower:
                    score += 10

        return score

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

    def _handle_filament_combox_changed(self, index: int):
        """Maneja el cambio de selección en el combobox de filamento"""
        filament_id = self.view.get_filament_id_at_index(index)
        if filament_id is None:
            return

        filament_map = getattr(self, '_filament_options_map', {})
        filament = filament_map.get(filament_id)
        if not filament:
            try:
                filament = self.facade.get_filament_by_id(filament_id)
            except Exception:
                return
        if filament:
            self._apply_filament_selection(filament)
            self.view.add_action_log(f"Filamento seleccionado del menú: {filament.name}")

    def _apply_filament_selection(self, filament):
        """Aplica un filamento seleccionado actualizando campos y estado interno."""
        self._mark_results_outdated()
        self.selected_filament = filament
        # Delegate UI update to the View (MVP compliant)
        self.view.update_filament_details(filament)
        self._schedule_auto_calculation()

    def _handle_calculate_quote(self):
        """Maneja el cálculo manual del presupuesto"""
        # 🚫 CANCELAR auto-cálculo pendiente porque haremos cálculo manual
        self.calculation_timer.stop()
        
        # Resetear override manual al iniciar nuevo cálculo
        if hasattr(self.view, 'reset_advance_manual_override'):
            self.view.reset_advance_manual_override()
        
        self.view.add_action_log("Cálculo manual solicitado")
        self._perform_calculation(manual=True)
    
    def _handle_clear_form(self):
        """Maneja la limpieza del formulario"""
        logger.debug("MainPresenter", "Limpieza de formulario solicitada")
        logger.info("MainPresenter", "Formulario limpiado por usuario")
        self._clear_internal_state()
        self.view.clear_all_fields()
        self.view.clear_gcode_project()
        self._last_gcode_data = None
        self.view.set_customer_optional(True)

    def _handle_clear_client(self):
        """Limpia solo la selección de cliente"""
        self.selected_customer = None
        self.view.clear_customer_selection()

    def _handle_clear_filament(self):
        """Limpia solo la selección de filamento"""
        self.selected_filament = None
        self.view.clear_filament_selection()

    def _handle_clear_printer(self):
        """Limpia solo la selección de impresora"""
        self.selected_printer = None
        self.view.clear_printer_selection()

    def _handle_clear_gcode(self):
        """Limpia el G-code y los parámetros de pieza (tiempo, gramos, cantidad) y filamento.
        No toca impresora ni cliente."""
        self.selected_filament = None
        self._last_gcode_data = None
        self._multicolor_slots_state = []
        self._active_multicolor_slot = -1
        self.view.set_multicolor_mode(False)
        self.view.hide_multicolor_panel()
        self.view.clear_gcode_project()
        self.view.clear_filament_selection()
        self.view.set_piece_parameters(0, 0, 0, 0)
        logger.info("MainPresenter", "G-code y parámetros de pieza limpiados")
    
    def _handle_preview_quote(self):
        """Maneja la vista previa del presupuesto"""
        self.view.add_action_log("Vista previa solicitada")
        
        # ✅ Verificar si está calculando actualmente
        if self.is_calculating:
            self.view.show_warning_message(
                tr(I18N.Quote.MSG_PREVIEW_TITLE),
                tr(I18N.Quote.MSG_CALC_IN_PROGRESS_PREVIEW)
            )
            return
        
        # ✅ Verificar si hay resultados obsoletos
        if self.results_outdated:
            self.view.show_warning_message(
                tr(I18N.Quote.MSG_PREVIEW_TITLE),
                tr(I18N.Quote.MSG_OUTDATED_WAIT_AUTO)
            )
            return
        
        # ✅ Si no hay resultados, mostrar mensaje pidiendo cálculo
        if not self.last_calculation_result:
            self.view.show_warning_message(
                tr(I18N.Quote.MSG_PREVIEW_TITLE),
                tr(I18N.Quote.MSG_REQUIRE_CALC_PREVIEW)
            )
            return
        
        # Mostrar diálogo de vista previa compacto
        try:
            dlg = QuotePreviewDialog(self.view)
            dlg.set_data(self.last_calculation_result)
            dlg.exec()
        except Exception as e:
            # Fallback: emitir señal si algo falla
            self.show_quote_preview.emit(self.last_calculation_result)
    
    def _handle_settings_request(self):
        """Maneja la solicitud de abrir configuraciones"""
        self.view.add_action_log("Configuraciones solicitadas")
        
        try:
            # Delegar al método público del view (responsabilidad de UI)
            self.view.show_settings_dialog()
            self.view.add_action_log("Diálogo de configuraciones mostrado")
            
        except Exception as e:
            self.view.add_action_log(f"Error al abrir configuraciones: {str(e)}")
            logger.error("MainPresenter", f"Error en configuraciones: {e}")
    
    def _handle_close_application(self):
        """Maneja el cierre seguro de la aplicación con confirmación"""
        self.view.add_action_log("Solicitud de cierre de aplicación")
        
        try:
            # 🚨 Mostrar diálogo de confirmación
            from PySide6.QtWidgets import QMessageBox
            
            msg_box = QMessageBox(self.view)
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setWindowTitle(tr(I18N.Dialogs.CLOSE_APP_TITLE, app_name=BUILD_CONFIG.app.name))
            msg_box.setText(tr(I18N.Dialogs.CONFIRM_EXIT))
            msg_box.setInformativeText(tr(I18N.Dialogs.CONFIRM_EXIT_MSG))
            
            # Botones personalizados
            btn_yes = msg_box.addButton(tr(I18N.Dialogs.YES_CLOSE), QMessageBox.ButtonRole.AcceptRole)
            btn_cancel = msg_box.addButton(tr(I18N.Buttons.CANCEL), QMessageBox.ButtonRole.RejectRole)
            msg_box.setDefaultButton(btn_cancel)  # Cancelar por defecto (más seguro)
            
            # Mostrar diálogo y obtener respuesta
            msg_box.exec()
            
            if msg_box.clickedButton() == btn_yes:
                self.view.add_action_log("Cerrando aplicación - Confirmado por usuario")
                self._perform_safe_shutdown()
            else:
                self.view.add_action_log("Cierre de aplicación cancelado por usuario")
                
        except Exception as e:
            self.view.add_action_log(f"Error en cierre de aplicación: {str(e)}")
            logger.error("MainPresenter", f"Error en cierre de aplicación: {e}")
            # En caso de error, proceder con cierre de emergencia
            self._perform_emergency_shutdown()

    def _handle_github_profile_request(self):
        """Maneja la solicitud de abrir el perfil de GitHub"""
        self.view.add_action_log("Abriendo perfil de GitHub")
        
        try:
            from config.build_config import open_github_profile
            success = open_github_profile()
            
            if success:
                self.view.add_system_log(f"✅ Perfil de GitHub de {BUILD_CONFIG.app.author} abierto en el navegador")
            else:
                self.view.add_system_log("❌ Error: No se pudo abrir el perfil de GitHub")
                
        except Exception as e:
            logger.error("MainPresenter", f"Error abriendo perfil GitHub: {e}")
            self.view.add_system_log("❌ Error abriendo perfil de GitHub")
    
    def _handle_build_info_request(self):
        """Maneja la solicitud de mostrar información de build - Acerca de Voxeprint"""
        self.view.add_action_log("Mostrando información 'Acerca de Voxeprint'")
        
        try:
            from presentation.modules.main.views.about_voxeprint_dialog import AboutVoxeprintDialog
            from config.build_config import get_about_info
            
            # Crear y configurar el diálogo
            about_dialog = AboutVoxeprintDialog(self.view)
            about_info = get_about_info()
            about_dialog.set_about_info(about_info)
            
            # Guardar referencia para actualizar botón si hay actualización
            self.about_dialog_ref = about_dialog
            
            # Conectar señales
            about_dialog.github_profile_requested.connect(self._handle_github_profile_request)
            about_dialog.changelog_requested.connect(self._handle_changelog_request)
            about_dialog.license_requested.connect(self._handle_license_request)
            about_dialog.check_updates_requested.connect(self._on_check_updates_manually)
            
            # Conectar señales de estado de verificación al diálogo
            self.update_checker.checking_started.connect(lambda: about_dialog.set_checking_state(True))
            self.update_checker.checking_finished.connect(lambda: about_dialog.set_checking_state(False))
            self.update_checker.update_check_blocked.connect(lambda secs: about_dialog.set_blocked_state(secs))           
            
            # Mostrar diálogo
            about_dialog.exec()
            self.view.add_system_log("Información 'Acerca de Voxeprint' mostrada")
            
            # Limpiar referencia al cerrar
            self.about_dialog_ref = None
                
        except Exception as e:
            logger.error("MainPresenter", f"Error mostrando Acerca de: {e}")
            self.view.add_system_log("Error al mostrar información 'Acerca de'")
    
    def _handle_donation_request(self):
        """Maneja la solicitud para abrir el diálogo de donaciones"""
        self.view.add_action_log("¡Gracias por considerar apoyar Voxeprint!")
        
        try:
            from presentation.modules.donation.presenters.donation_dialog_presenter import DonationDialogPresenter
            
            # Crear y mostrar el diálogo de donaciones
            donation_presenter = DonationDialogPresenter(parent=self.view)
            donation_presenter.run()
            
            self.view.add_system_log("💚 Gracias por visitar las opciones de donación")
                
        except Exception as e:
            logger.error("MainPresenter", f"Error abriendo diálogo de donaciones: {e}")
            self.view.add_system_log(tr(I18N.StatusBar.ERROR_OPEN_DONATION))
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.view,
                tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.Dialogs.ERROR_DONATION_MSG, error=str(e))
            )
    
    # Los métodos de gestión de licencias fueron movidos a LicenseDialogPresenter
    # siguiendo el patrón MVP correctamente (View + Presenter)
    
    # Métodos _handle_request_license y _handle_activate_license
    # movidos a LicenseDialogPresenter (patrón MVP correcto)
    
    def _handle_website_request(self):
        """Maneja la solicitud de abrir el sitio web"""
        try:
            import webbrowser
            from config.build_config import BUILD_CONFIG
            
            # Usar directamente el GitHub profile en lugar de website
            github_url = BUILD_CONFIG.app.github_profile
            webbrowser.open(github_url)
            self.view.add_action_log(f"GitHub abierto: {github_url}")
                
        except Exception as e:
            logger.error("MainPresenter", f"Error abriendo GitHub: {e}")
            self.view.add_system_log("Error al abrir GitHub")

    def _handle_changelog_request(self):
        """Maneja la solicitud de abrir el registro de cambios"""
        try:
            import subprocess
            import platform
            
            # Usar app_root() para obtener la ruta correcta en desarrollo y en build
            changelog_path = app_root() / "docs" / "CHANGELOG.txt"
            
            if not changelog_path.exists():
                self.view.add_system_log("❌ Archivo de registro de cambios no encontrado")
                logger.error("MainPresenter", f"Changelog no encontrado: {changelog_path}")
                return
            
            # Abrir con el programa predeterminado del sistema
            if platform.system() == "Windows":
                # En Windows, usar notepad.exe específicamente
                subprocess.Popen(["notepad.exe", str(changelog_path)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", "TextEdit", str(changelog_path)])
            else:  # Linux
                subprocess.Popen(["xdg-open", str(changelog_path)])
            
            self.view.add_system_log("📄 Registro de cambios abierto")
                
        except Exception as e:
            logger.error("MainPresenter", f"Error abriendo registro de cambios: {e}")
            self.view.add_system_log("❌ Error al abrir registro de cambios")

    def _handle_license_request(self):
        """Maneja la solicitud de abrir el archivo de licencia"""
        try:
            import subprocess
            import platform
            
            # Usar app_root() para obtener la ruta correcta en desarrollo y en build
            license_path = app_root() / "LICENSE.md"
            if not license_path.exists():
                license_path = app_root() / "LICENSE"
            
            if not license_path.exists():
                self.view.add_system_log("❌ Archivo de licencia no encontrado")
                logger.error("MainPresenter", f"Licencia no encontrada: {license_path}")
                return
            
            # Abrir con el programa predeterminado del sistema
            if platform.system() == "Windows":
                # En Windows, usar notepad.exe específicamente
                subprocess.Popen(["notepad.exe", str(license_path)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", "TextEdit", str(license_path)])
            else:  # Linux
                subprocess.Popen(["xdg-open", str(license_path)])
            
            self.view.add_system_log("📜 Licencia abierta")
                
        except Exception as e:
            logger.error("MainPresenter", f"Error abriendo licencia: {e}")
            self.view.add_system_log("❌ Error al abrir licencia")

    def _perform_safe_shutdown(self):
        """Realiza un cierre seguro de la aplicación limpiando recursos"""
        try:
            self.view.add_system_log("🔄 Iniciando cierre seguro de la aplicación...")
            
            # 1. Detener timers activos
            if hasattr(self, 'calculation_timer') and self.calculation_timer:
                self.calculation_timer.stop()
                self.view.add_system_log("✅ Timer de cálculo detenido")
                
            if hasattr(self, 'backup_timer') and self.backup_timer:
                self.backup_timer.stop()
                self.view.add_system_log("✅ Timer de respaldos detenido")
            
            # 2. Limpiar estado interno
            self._clear_internal_state()
            self.view.add_system_log("✅ Estado interno limpiado")
            
            # 3. Limpiar recursos del presenter
            if hasattr(self, 'cleanup'):
                self.cleanup()
                self.view.add_system_log("✅ Recursos del presenter limpiados")
            
            # 4. Cerrar conexiones de base de datos si existen
            try:
                from infrastructure.database.connection import DatabaseConnection
                db_conn = DatabaseConnection()
                if hasattr(db_conn, 'close') and callable(db_conn.close):
                    db_conn.close()
                    self.view.add_system_log("✅ Conexión de base de datos cerrada")
            except Exception as db_error:
                self.view.add_system_log(f"⚠️ Error cerrando BD: {str(db_error)}")
            
            # 5. Mensaje final y cierre
            self.view.add_system_log("✅ Cierre seguro completado")
            self.view.add_action_log("Aplicación cerrada correctamente")
            
            # 6. Cerrar aplicación Qt
            from PySide6.QtWidgets import QApplication
            QApplication.quit()
            
        except Exception as e:
            self.view.add_system_log(f"❌ Error durante cierre seguro: {str(e)}")
            logger.error("MainPresenter", f"Error en cierre seguro: {e}")
            # Fallback a cierre de emergencia
            self._perform_emergency_shutdown()

    def _perform_emergency_shutdown(self):
        """Realiza un cierre de emergencia cuando el cierre seguro falla"""
        try:
            logger.error("MainPresenter", "CIERRE DE EMERGENCIA ACTIVADO")
            
            # Detener timers críticos
            if hasattr(self, 'calculation_timer') and self.calculation_timer:
                self.calculation_timer.stop()
                
            if hasattr(self, 'backup_timer') and self.backup_timer:
                self.backup_timer.stop()
            
            # Forzar cierre de aplicación
            from PySide6.QtWidgets import QApplication
            import sys
            
            QApplication.quit()
            sys.exit(0)  # Forzar salida del sistema
            
        except Exception as e:
            logger.error("MainPresenter", f"Error crítico en cierre de emergencia: {e}")
            # Última alternativa - salida forzada del sistema
            import sys
            sys.exit(1)
    
    def _handle_generate_note(self):
        """Genera una Nota de Precios como imagen PNG (copiar o guardar)."""
        logger.debug("MainPresenter", "Iniciando generación de Nota de Precios")
        if not self.last_calculation_result:
            self.view.show_warning_message(
                tr(I18N.Quote.MSG_GENERATE_NOTE_TITLE),
                tr(I18N.Quote.MSG_REQUIRE_CALC_NOTE)
            )
            logger.warning("MainPresenter", "Generación de nota cancelada: no hay resultados de cálculo")
            return
        if self.results_outdated:
            self.view.show_warning_message(
                tr(I18N.Quote.MSG_OUTDATED_TITLE),
                tr(I18N.Quote.MSG_OUTDATED_NOTE)
            )
            logger.warning("MainPresenter", "Generación de nota cancelada: resultados obsoletos")
            return
        try:
            from presentation.modules.quotes.presenters.quote_note_presenter import QuoteNotePresenter
            from presentation.modules.quotes.views.quote_note_dialog import QuoteNoteDialog

            note_presenter = QuoteNotePresenter()
            pixmap = note_presenter.build_pixmap(self.last_calculation_result)
            logger.debug("MainPresenter", "Pixmap de nota generado correctamente")
            self.view.add_status_message("Nota de Precios generada.")
            dlg = QuoteNoteDialog(
                pixmap,
                note_presenter,
                self.view,
                on_status=self.view.add_status_message,
            )
            dlg.exec()
            logger.info("MainPresenter", "Nota de Precios generada y mostrada correctamente")
        except Exception as e:
            logger.log_exception("MainPresenter", e, "_handle_generate_note")

    def _handle_save_quote(self):
            """Maneja el guardado del presupuesto en PDF"""
            logger.debug("MainPresenter", "Iniciando guardado de presupuesto en PDF")
            
            # ✅ Validar que hay resultados y no están obsoletos
            if not self.last_calculation_result:
                self.view.show_warning_message(
                    tr(I18N.Quote.MSG_SAVE_QUOTE_TITLE), 
                    tr(I18N.Quote.MSG_REQUIRE_CALC_SAVE)
                )
                logger.warning("MainPresenter", "Guardado de PDF cancelado: no hay resultados de cálculo")
                return
            
            # ✅ NUEVA VALIDACIÓN: Verificar que los resultados no estén obsoletos
            if self.results_outdated:
                self.view.show_warning_message(
                    tr(I18N.Quote.MSG_OUTDATED_TITLE), 
                    tr(I18N.Quote.MSG_OUTDATED_SAVE)
                )
                logger.warning("MainPresenter", "Guardado de PDF cancelado: resultados obsoletos")
                return
            
            # ✅ Verificar que no esté calculando actualmente
            if self.is_calculating:
                self.view.show_warning_message(
                    tr(I18N.Quote.MSG_CALC_IN_PROGRESS_TITLE), 
                    tr(I18N.Quote.MSG_CALC_IN_PROGRESS)
                )
                logger.warning("MainPresenter", "Guardado de PDF cancelado: cálculo en progreso")
                return
            
            # ✅ Validar porcentaje de anticipo si está habilitado
            if self.view.is_advance_enabled():
                advance_percentage = self.view.get_advance_percentage()
                if advance_percentage == 0:  # Solo 0% es inválido
                    self.view.show_warning_message(
                        "Anticipo Inválido", 
                        f"El porcentaje de anticipo no puede ser 0%.\n"
                        "Por favor, ingrese un valor válido o desactive el anticipo."
                    )
                    logger.warning("MainPresenter", "Guardado de PDF cancelado: anticipo 0% inválido")
                    return
            
            # ✅ Validar cliente requerido para generación de PDF
            if not self.view.is_customer_optional() and not self.view.get_customer_name():
                self.view.show_warning_message(
                    "Cliente Requerido",
                    "Debe seleccionar un cliente o marcarlo como opcional\n"
                    "para poder generar el presupuesto en PDF."
                )
                logger.warning("MainPresenter", "Guardado de PDF cancelado: cliente requerido")
                return
            
            # Mensaje de inicio del proceso
            self.view.add_action_log("Guardado de presupuesto PDF solicitado")
            self.view.add_status_message("SISTEMA: 📄 Generando PDF...")

            # 1) Preparar datos y generar número de presupuesto
            quote_number = self.facade.get_new_quote_number()

            # 2) Setup PDF manager (único formato soportado)
            from core.managers.quote_pdf_manager import QuotePDFManager
            document_manager = QuotePDFManager()
            
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_filename = f"voxeprint_preview_{uuid.uuid4().hex[:8]}.pdf"
            temp_file_path = os.path.join(temp_dir, temp_filename).replace('\\', '/')

            res = self.last_calculation_result or {}
            fil = res.get('filament_info') or {}
            fil_type = fil.get('type', '')
            fil_color = fil.get('color', '')
            filament_display = f"{fil_type} - {fil_color}" if fil_type and fil_color else fil.get('name', 'N/A')
            ctx = {
                'printer_name': ((res.get('printer_info') or {}).get('name')),
                'filament_name': filament_display,
                'project_name': self._generate_project_name(quote_number)
            }
            amounts = {
                'material': res.get('material_cost', 0),
                'electricity': res.get('electricity_cost', 0),
                'wear': res.get('operation_cost', 0),
                'failure': res.get('failure_margin_cost', 0),
                'subtotal_with_margin': res.get('subtotal_with_margin', 0),
                'commission': res.get('commission_cost', 0),
                'tax': res.get('tax_amount', 0),
                'post_processing': self.view.get_post_total_amount() if self.view.is_post_enabled() else 0,  # ✅ Post-procesado
                'total': res.get('total_to_pay', 0),
            }
            
            # Calcular breakdown usando el servicio, pasando la configuración de
            # visualización del PDF para que las líneas ya salgan en el modo correcto.
            breakdown_service = QuoteBreakdownService()
            pdf_cfg = breakdown_service.config.get_pdf_settings()
            breakdown = breakdown_service.compute_from_amounts(amounts, config_overrides={
                "display_mode":  pdf_cfg.get("display_mode", "detailed"),
                "summary_label": pdf_cfg.get("summary_label", "Servicio de Impresión 3D"),
            })
            
            data_pdf = {
                'context': ctx, 
                'amounts': amounts,
                'breakdown': breakdown, 
                'meta': {'quote_number': quote_number},
                'printer_info': res.get('printer_info', {}),
                'customer_info': self._get_customer_info_for_pdf(),
                'advance_info': {
                    'enabled': self.view.is_advance_enabled(),
                    'percentage': self.view.get_advance_percentage()
                },
                'post_info': {
                    'enabled': self.view.is_post_enabled(),
                    'base_amount': self.view.get_post_amount(),  # Monto base por unidad
                    'type': self.view.get_post_type(),  # "Cobrar por Lote" o "Cobrar por Trabajo"
                    'multiplier': self.view.get_post_multiplier(),  # Cantidad o 1
                    'total_amount': self.view.get_post_total_amount()  # Monto total calculado
                },
                'quantity_info': {
                    'quantity': self.view.get_quantity_value()
                }
            }
            
            try:
                # Generar PDF en hilo secundario con animación de carga
                from presentation.widgets.animation_mod.rotating_circle import WaitingCircle

                self._pdf_loading = WaitingCircle(parent=self.view)
                self._pdf_loading.superposition(True)

                # Guardar contexto necesario para el callback
                self._pdf_gen_context = {
                    'document_manager': document_manager,
                    'temp_file_path': temp_file_path,
                    'data_pdf': data_pdf,
                    'quote_number': quote_number,
                    'res': res,
                }

                def _on_pdf_generated(result, error):
                    ctx = self._pdf_gen_context
                    self._pdf_gen_context = None
                    self._pdf_loading = None

                    if error:
                        logger.log_exception("MainPresenter", error, "_on_pdf_generated")
                        self.view.add_status_message("SISTEMA: ❌ Error al generar PDF")
                        self.view.show_error_message(
                            "Error al generar PDF",
                            "Ocurrió un error al generar el presupuesto.\n"
                            "Revise los logs para más detalles.")
                        return

                    self.view.add_status_message("SISTEMA: ✅ PDF generado correctamente")
                    self._show_pdf_preview(ctx['document_manager'], ctx['temp_file_path'], ctx['quote_number'], ctx['res'])

                self._pdf_loading.run_async(
                    document_manager.generate, _on_pdf_generated,
                    temp_file_path, data_pdf
                )
            except Exception as e:
                logger.log_exception("MainPresenter", e, "_handle_save_quote")
                self.view.add_status_message("SISTEMA: ❌ Error al generar PDF")
                self.view.show_error_message(
                    "Error al generar PDF",
                    "Ocurrió un error al preparar la generación del presupuesto.\n"
                    "Revise los logs para más detalles.")
                return

    def _show_pdf_preview(self, document_manager, temp_file_path, quote_number, res):
        """Muestra la previsualización PDF después de generarlo."""
        save_confirmed = False
        
        try:
            # Función callback para el guardado real
            def save_quote_callback():
                try:
                    # 4) Mover archivo a docs/ y persistir en BD
                    self.view.add_status_message("SISTEMA: 💾 Guardando presupuesto...")
                    
                    # Preparar directorio final y path (solo PDF)
                    final_dir = Path(document_manager.ensure_docs_dir())
                    final_file_path = final_dir / f"{quote_number}.pdf"
                    
                    # Copiar archivo temporal a destino final (mantener el original para preview/descarga/impresión)
                    shutil.copy2(temp_file_path, final_file_path)
                    
                    # Datos UI adicionales (cliente opcional)
                    cust = self.view.get_customer_data()
                    customer_id = self.selected_customer.id if self.selected_customer else None
                    # Tiempo/peso originales ingresados
                    hours, minutes = self.view.get_time_values()
                    weight_grams = self.view.get_weight_value() * max(1, self.view.get_quantity_value())
                    print_minutes = (hours * 60 + minutes) * max(1, self.view.get_quantity_value())

                    dto = QuoteCreateDTO(
                        customer_id=customer_id,
                        printer_id=self.selected_printer.id if self.selected_printer else 0,
                        filament_id=self.selected_filament.id if self.selected_filament else (
                            max(self._multicolor_slots_state, key=lambda s: s.get('percentage', 0))['filament_id']
                            if self._multicolor_slots_state else 0
                        ),
                        project_name=self._generate_project_name(quote_number),
                        description="Presupuesto generado en formato PDF",
                        print_time_minutes=print_minutes,
                        filament_weight_grams=weight_grams,
                        failure_margin_percent=res.get('calculation_details', {}).get('failure_margin_percent', 5.0),
                        profit_margin_percent=res.get('calculation_details', {}).get('profit_margin_percent', 35.0),
                        tax_rate_percent=res.get('calculation_details', {}).get('tax_rate_percent', 10.0),
                        commission_rate_percent=res.get('calculation_details', {}).get('commission_rate_percent', 0.0),
                        file_path=final_file_path,
                        notes="",
                        internal_notes=""
                    )
                    save_res = self.facade.save_quote(dto, self._to_calc_response_dto(res), final_file_path, quote_number=quote_number)
                    if isinstance(save_res, ErrorResponseDTO):
                        self.view.add_status_message("SISTEMA: ❌ Error al guardar en base de datos")
                        self.view.show_error_message("Error al guardar", save_res.message)
                        return False
                    else:
                        self.view.add_status_message("SISTEMA: ✅ Presupuesto guardado exitosamente")
                        self.view.add_action_log(f"Presupuesto N° {quote_number} generado y guardado")
                        # Actualizar el inventario de quotes para que aparezca inmediatamente
                        self.refresh_quotes_tab()
                        return True
                        
                except Exception as e:
                    logger.log_exception("MainPresenter", e, "save_quote_callback")
                    self.view.add_status_message("SISTEMA: ❌ Error durante el guardado")
                    self.view.add_action_log("Error al guardar presupuesto")
                    self.view.show_error_message(
                        "Error al guardar",
                        "Ocurrió un error al guardar el presupuesto.\n"
                        "Revise los logs para más detalles.")
                    return False
            
            # Crear ventana independiente (SIN parent para evitar parpadeo)
            viewer_dialog = PDFViewer(temp_file_path, quote_number, save_callback=save_quote_callback, parent=None)
            
            # 🎨 Sincronizar tema del PDF con el tema de la aplicación
            self._sync_pdf_theme(viewer_dialog)
            
            # Usar método independiente en lugar de exec()
            result = viewer_dialog.exec_independent()
            save_confirmed = (result == 'save')
            
        except Exception as e:
            # Si falla el visor, limpiar y cancelar
            logger.log_exception("MainPresenter", e, "_show_pdf_preview")
            try:
                os.remove(temp_file_path)
            except:
                pass
            self.view.show_error_message(
                "Error en visor PDF",
                "No se pudo abrir la previsualización del presupuesto.\n"
                "Revise los logs para más detalles.")
            return

        # Limpiar archivo temporal después de que el visor se cierre
        # (ya sea que haya guardado o cancelado)
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception as e:
            pass  # Ignorar errores al eliminar temporal
        
        if not save_confirmed:
            self.view.add_action_log("Guardado cancelado por el usuario")
            self.view.add_status_message("SISTEMA: ❌ Guardado cancelado por el usuario")
            return

    def _to_calc_response_dto(self, res: dict) -> QuoteCalculationResponseDTO:
        """Convierte el dict de resultado a DTO para el facade.save_quote."""
        return QuoteCalculationResponseDTO(
            material_cost=res.get('material_cost', 0.0),
            electricity_cost=res.get('electricity_cost', 0.0),
            operation_cost=res.get('operation_cost', 0.0),
            subtotal_base_costs=res.get('subtotal_base_costs', 0.0),
            failure_margin_cost=res.get('failure_margin_cost', 0.0),
            subtotal_with_margin=res.get('subtotal_with_margin', 0.0),
            commission_cost=res.get('commission_cost', 0.0),
            subtotal_before_profit=res.get('subtotal_before_profit', 0.0),
            profit_amount=res.get('profit_amount', 0.0),
            subtotal_before_tax=res.get('subtotal_before_tax', 0.0),
            tax_amount=res.get('tax_amount', 0.0),
            total_to_pay=res.get('total_to_pay', 0.0),
            calculation_timestamp=res.get('calculation_timestamp'),
            printer_info=res.get('printer_info'),
            filament_info=res.get('filament_info'),
            calculation_details=res.get('calculation_details'),
        )
    
    def _on_time_changed(self, hours: int, minutes: int):
        """Maneja cambios en el tiempo de impresión"""
        # Ya no necesita _mark_results_outdated() porque se hace inmediatamente
        total_minutes = hours * 60 + minutes
        self.view.add_status_message(f"⏱️ Tiempo: {hours}h {minutes}m (Total: {total_minutes} min)")
        self._schedule_auto_calculation()

    def _on_weight_changed(self, weight: int):
        """Maneja cambios en el peso del filamento"""
        # Rebalanceo de slots multicolor cuando el total cambia
        if self._multicolor_slots_state and weight > 0:
            self._rebalance_multicolor_slots(weight)
        self.view.add_status_message(f"⚖️ Peso: {weight}g")
        self._schedule_auto_calculation()

    def _on_quantity_changed(self, quantity: int):
        """Maneja cambios en la cantidad de piezas"""
        # Ya no necesita _mark_results_outdated() porque se hace inmediatamente
        self.view.add_status_message(f"🔢 Cantidad: {quantity} unidades")
        self._schedule_auto_calculation()

    def _on_customer_optional_changed(self, is_optional: bool):
        """Maneja el cambio en el estado del checkbox de cliente opcional.
        En modo Nota, este cambio no afecta al botón de generación.
        """
        current_mode = self.view.get_generate_mode()
        
        if is_optional:
            # Si se marca como opcional, limpiar datos del cliente
            self.selected_customer = None
            self.view.clear_customer_data()
            self.view.add_action_log("Cliente marcado como opcional - datos limpiados")
            # Solo recalcular si estamos en modo PDF (Nota no usa cliente)
            if current_mode != "note":
                self._mark_results_outdated()
                self._schedule_auto_calculation()
        else:
            # Si se desmarca, no hacer nada especial, el usuario puede seleccionar un cliente
            self.view.add_action_log("Cliente ya no es opcional - puede seleccionar un cliente")
            # Solo recalcular si estamos en modo PDF (Nota no usa cliente)
            if current_mode != "note":
                self._mark_results_outdated()
                self._schedule_auto_calculation()
    
    def _on_advance_enabled_changed(self, enabled: bool):
        """Maneja el cambio en el estado del checkbox de anticipo"""
        # Ya no necesita _mark_results_outdated() porque se hace inmediatamente
        status = "habilitado" if enabled else "deshabilitado"
        self.view.add_action_log(f"Anticipo {status}")
        
        # ⚡ OPTIMIZACIÓN: Si ya hay resultados calculados, solo recalcular anticipo
        if self.last_calculation_result and not self.results_outdated:
            self._recalculate_advance_only()
        else:
            # Solo hacer cálculo completo si no hay resultados o están obsoletos
            self._schedule_auto_calculation()
    
    def _on_advance_percentage_changed(self, percentage: int):
        """Maneja el cambio en el porcentaje de anticipo"""
        # Ya no necesita _mark_results_outdated() porque se hace inmediatamente
        self.view.add_action_log(f"Porcentaje de anticipo actualizado: {percentage}%")
        
        # ⚡ OPTIMIZACIÓN: Si ya hay resultados calculados, solo recalcular anticipo
        if self.last_calculation_result and not self.results_outdated:
            self._recalculate_advance_only()
        else:
            # Solo hacer cálculo completo si no hay resultados o están obsoletos
            self._schedule_auto_calculation()
    
    def _on_post_enabled_changed(self, enabled: bool):
        """Maneja el cambio en el estado del checkbox de post-procesado"""
        # Ya no necesita _mark_results_outdated() porque se hace inmediatamente
        status = "habilitado" if enabled else "deshabilitado"
        self.view.add_action_log(f"Post-procesado {status}")
        
        # Recalcular para actualizar los montos
        self._schedule_auto_calculation()
    
    def _on_post_amount_changed(self, amount: int):
        """Maneja el cambio en el monto de post-procesado"""
        # Ya no necesita _mark_results_outdated() porque se hace inmediatamente
        self.view.add_action_log(f"Monto de post-procesado actualizado: {amount} Gs.")
        
        # Recalcular para actualizar los montos
        self._schedule_auto_calculation()
    
    def _on_post_type_changed(self, post_type: str):
        """Maneja el cambio en el tipo de post-procesado (Lote/Trabajo)"""
        # Ya no necesita _mark_results_outdated() porque se hace inmediatamente
        self.view.add_action_log(f"Tipo de post-procesado cambiado a: {post_type}")
        
        # Recalcular para actualizar los montos con el nuevo multiplicador
        self._schedule_auto_calculation()
    
    # === MANEJADORES DE SEÑALES DEL INVENTARIO ===
    
    def _on_inventory_filament_selected(self, filament_data: dict):
        """Maneja la selección de filamento desde el inventario"""
        # TODO: Decidir si auto-seleccionar el filamento en el formulario principal
        # self.set_selected_filament(filament)
        filament_name = filament_data.get('name', 'Desconocido')
        logger.debug("MainPresenter", "Filamento seleccionado desde inventario", filament=filament_name)
    
    def _on_inventory_filament_deleted(self, filament_id: int):
        """Maneja la eliminación de filamento desde el inventario"""
        self.view.add_status_message(f"Filamento ID {filament_id} eliminado del inventario")
        
        # Si el filamento eliminado era el seleccionado, limpiar selección
        if self.selected_filament and self.selected_filament.id == filament_id:
            self.selected_filament = None
            self.view.add_status_message("Filamento seleccionado eliminado, limpie el formulario")
    
    def _on_inventory_filament_modified(self, filament_data: dict):
        """Maneja la modificación de filamento desde el inventario"""
        filament_name = filament_data.get('name', f"ID {filament_data.get('id')}")
        self.view.add_status_message(f"✏️ Filamento '{filament_name}' modificado en el inventario")
    
    def _on_inventory_quote_selected(self, quote_data: dict):
        """Maneja la selección de presupuesto desde el inventario"""
        try:
            quote_number = quote_data.get('quote_number', f"ID {quote_data.get('id')}")
            # 🔇 Cambiado a debug para reducir ruido en el log visual
            logger.debug("MainPresenter", "Presupuesto seleccionado desde historial", quote=quote_number)
            
        except Exception as e:
            self.view.add_status_message(f"Error procesando presupuesto del historial: {str(e)}")
            logger.error("MainPresenter", f"Error en selección de presupuesto: {e}")
    
    def _on_inventory_quote_deleted(self, quote_id: int):
        """Maneja la eliminación de presupuesto desde el inventario"""
        self.view.add_status_message(f"Presupuesto ID {quote_id} eliminado del historial")
    
    def _on_inventory_quote_modified(self, quote_data: dict):
        """Maneja la modificación de presupuesto desde el inventario"""
        quote_number = quote_data.get('quote_number', f"ID {quote_data.get('id')}")
        self.view.add_status_message(f"Presupuesto '{quote_number}' modificado en el historial")
    
    # === MANEJADORES DE SEÑALES DEL INVENTARIO DE CLIENTES ===
    
    def _on_inventory_customer_selected(self, customer_data: dict):
        """Maneja cuando se selecciona un cliente desde el inventario"""
        # 🔇 Cambiado a debug para reducir ruido en el log visual
        customer_name = customer_data.get('full_name', 'Desconocido')
        logger.debug("MainPresenter", "Cliente seleccionado desde inventario", customer=customer_name)
        # TODO: Decidir si auto-seleccionar el cliente en el formulario principal
        # self.set_selected_customer_from_data(customer_data)
    
    def _on_inventory_customer_deleted(self, customer_id: int):
        """Maneja cuando se elimina un cliente desde el inventario"""
        self.view.add_action_log(f"Cliente eliminado desde inventario: ID {customer_id}")
        
        # Si el cliente eliminado es el actualmente seleccionado, limpiarlo
        if self.selected_customer and self.selected_customer.id == customer_id:
            self.view.add_action_log("Cliente seleccionado eliminado - limpiando selección")
            self.selected_customer = None
            self.view.clear_customer_selection()
            self._invalidate_results_immediately()
    
    def _on_inventory_customer_modified(self, customer_data: dict):
        """Maneja cuando se modifica un cliente desde el inventario"""
        self.view.add_action_log(f"Cliente modificado: {customer_data.get('full_name', 'Desconocido')}")
        
        # Si el cliente modificado es el actualmente seleccionado, actualizarlo
        if (self.selected_customer and 
            self.selected_customer.id == customer_data.get('id')):
            self.view.add_action_log("Actualizando cliente seleccionado con datos modificados")
            # Actualizar la vista con los nuevos datos
            self.view.update_customer_display(
                customer_data.get('full_name', ''),
                customer_data.get('ruc_ci', ''),
                customer_data.get('email', ''),
                customer_data.get('phone_number', '')
            )
    
    # === MANEJADORES DE SEÑALES DEL INVENTARIO DE IMPRESORAS ===
    
    def _on_inventory_printer_selected(self, printer_data: dict):
        """Maneja cuando se selecciona una impresora desde el inventario"""
        # 🔇 Cambiado a debug para reducir ruido en el log visual
        printer_name = printer_data.get('name', 'Desconocido')
        logger.debug("MainPresenter", "Impresora seleccionada desde inventario", printer=printer_name)
        # TODO: Decidir si auto-seleccionar la impresora en el formulario principal
        # self.set_selected_printer_from_data(printer_data)
    
    def _on_inventory_printer_deleted(self, printer_id: int):
        """Maneja cuando se elimina una impresora desde el inventario"""
        self.view.add_action_log(f"Impresora eliminada desde inventario: ID {printer_id}")
        
        # Si la impresora eliminada es la actualmente seleccionada, limpiarla
        if self.selected_printer and self.selected_printer.id == printer_id:
            self.view.add_action_log("Impresora seleccionada eliminada - limpiando selección")
            self.selected_printer = None
            self.view.clear_printer_selection()
            self._invalidate_results_immediately()
    
    def _on_inventory_printer_modified(self, printer_data: dict):
        """Maneja cuando se modifica una impresora desde el inventario"""
        self.view.add_action_log(f"Impresora modificada: {printer_data.get('name', 'Desconocido')}")
        
        # Si la impresora modificada es la actualmente seleccionada, actualizarla
        if (self.selected_printer and 
            self.selected_printer.id == printer_data.get('id')):
            self.view.add_action_log("Actualizando impresora seleccionada con datos modificados")
            # La impresora se recarga automáticamente al invalidar resultados
            self._invalidate_results_immediately()
    
    # === MÉTODOS PARA ESTABLECER DATOS SELECCIONADOS ===
    
    def set_selected_customer(self, customer: Customer):
        """Establece el cliente seleccionado"""
        self.selected_customer = customer
        # Manejar valores null/vacíos con textos apropiados
        name = customer.full_name or "Sin nombre"
        ruc_ci = customer.ruc_ci or "No especificado"
        self.view.set_customer_data(name, ruc_ci)
        # Cuando se selecciona un cliente específico, desmarcar "opcional"
        self.view.set_customer_optional(False)
        self._schedule_auto_calculation()
    
    def set_selected_filament(self, filament: Filament):
        """Establece el filamento seleccionado.
        Si hay un G-code cargado con matches, combina la selección del usuario
        con las opciones del G-code como secundarias en el combobox.
        """
        self._mark_results_outdated()
        self.selected_filament = filament

        # Verificar si hay gcode cargado con matches disponibles
        gcode_data = getattr(self, '_last_gcode_data', None)
        filament_map = getattr(self, '_filament_options_map', {})

        if gcode_data and (gcode_data.normalized_type or gcode_data.filament_type) and filament_map:
            # Construir lista combinada: selección manual + matches del gcode
            options: list[tuple[str, int]] = []
            seen_ids: set[int] = set()

            # 1) La selección del usuario va primero
            options.append((filament.name, filament.id))
            seen_ids.add(filament.id)

            # 2) Agregar matches del gcode como secundarias
            gcode_type = (gcode_data.normalized_type or gcode_data.filament_type).lower().strip()
            gcode_colour = (gcode_data.filament_colour or "").lower().strip()

            all_filaments = self.facade.get_all_filaments()
            scored = []
            for f in all_filaments:
                if f.id not in seen_ids:
                    score = self._score_filament_match(f, gcode_type, gcode_colour)
                    if score > 0:
                        scored.append((score, f))
            scored.sort(key=lambda x: x[0], reverse=True)

            for _score, f in scored:
                options.append((f.name, f.id))
                seen_ids.add(f.id)
                self._filament_options_map[f.id] = f

            # Asegurar que la selección manual esté en el mapa
            self._filament_options_map[filament.id] = filament

            self.view.set_filament_options(options, selected_index=0)
            self._apply_filament_selection(filament)
        else:
            # Sin gcode: comportamiento original (un solo item)
            filament_type = filament.type.value if hasattr(filament.type, 'value') else str(filament.type) if filament.type else "No especificado"
            filament_color = filament.color.value if hasattr(filament.color, 'value') else str(filament.color) if filament.color else "No especificado"
            stock_kg = filament.current_stock_grams / 1000.0 if filament.current_stock_grams else 0.0
            price_per_kg = filament.price_per_gram * 1000.0 if filament.price_per_gram else 0.0
            filament_currency = getattr(filament, 'currency_code', 'PYG')
            name = filament.name or "Sin nombre"
            price_text = f"{CurrencyHelper.format(price_per_kg, filament_currency, include_symbol=False)}{CurrencyHelper.get_symbol(filament_currency)}/kg" if price_per_kg > 0 else "Sin precio"
            quantity_text = f"{stock_kg:.2f} kg" if stock_kg >= 0 else "Sin stock"
            self.view.set_filament_data(
                description=name,
                filament_type=filament_type,
                color=filament_color,
                price=price_text,
                quantity=quantity_text
            )
        self._schedule_auto_calculation()
    
    def set_selected_printer(self, printer: Printer):
        """Establece la impresora seleccionada.
        Si hay un G-code cargado con matches, combina la selección del usuario
        con las opciones del G-code como secundarias en el combobox.
        """
        self._mark_results_outdated()
        self.selected_printer = printer

        # Verificar si hay gcode cargado con matches disponibles
        gcode_data = getattr(self, '_last_gcode_data', None)
        printer_map = getattr(self, '_printer_options_map', {})

        if gcode_data and gcode_data.printer_model and printer_map:
            # Construir lista combinada: selección manual + matches del gcode
            options: list[tuple[str, int]] = []
            seen_ids: set[int] = set()

            # 1) La selección del usuario va primero
            options.append((printer.name, printer.id))
            seen_ids.add(printer.id)

            # 2) Agregar matches del gcode como secundarias
            gcode_lower = gcode_data.printer_model.lower().strip()
            gcode_tokens = set(gcode_lower.replace('-', ' ').replace('_', ' ').split())
            generic_tokens = {'3d', 'printer', 'pro', 'plus', 'max', 'mini', 'v2', 'v3', 'se'}

            all_printers = self.facade.get_all_printers()
            scored = []
            for p in all_printers:
                if p.id not in seen_ids:
                    score = self._score_printer_match(p, gcode_lower, gcode_tokens, generic_tokens)
                    if score > 0:
                        scored.append((score, p))
            scored.sort(key=lambda x: x[0], reverse=True)

            for _score, p in scored:
                options.append((p.name, p.id))
                seen_ids.add(p.id)
                self._printer_options_map[p.id] = p

            # Asegurar que la selección manual esté en el mapa
            self._printer_options_map[printer.id] = printer

            self.view.set_printer_options(options, selected_index=0)
            self._apply_printer_selection(printer)
        else:
            # Sin gcode: comportamiento original (un solo item)
            try:
                consumption_watts = float(getattr(printer, 'power_consumption_watts', 0) or 0)
            except Exception:
                consumption_watts = 0.0
            consumption_text = f"{int(round(consumption_watts))}W" if consumption_watts > 0 else tr(I18N.MainWindow.DETAIL_NOT_AVAILABLE)
            name = printer.name or "Sin nombre"
            brand = printer.brand or "No especificada"
            model = printer.model or "No especificado"
            self.view.set_printer_data(
                description=name,
                brand=brand,
                model=model,
                consumption=consumption_text
            )
        self._schedule_auto_calculation()
    
    # === LÓGICA DE CÁLCULO ===
    
    def _schedule_auto_calculation(self):
        """Programa un cálculo automático con delay"""
        logger.debug("MainPresenter", f"_schedule_auto_calculation: printer={self.selected_printer is not None}, filament={self.selected_filament is not None}, calculating={self.is_calculating}, outdated={self.results_outdated}")
        # Solo hacer cálculo automático si tenemos los datos mínimos
        if self.selected_printer and self.selected_filament:
            # ⚠️ EVITAR auto-cálculo si ya hay resultados actualizados
            if not self.results_outdated and self.last_calculation_result is not None:
                return
                
            # ✅ NO marcar como obsoleto aquí, ya se hace inmediatamente en _mark_results_outdated
            self.calculation_timer.start(1500)  # 1.5 segundos de delay
    
    def _mark_results_outdated(self):
        """Marca inmediatamente los resultados como obsoletos y actualiza el botón"""
        logger.debug("MainPresenter", f"_mark_results_outdated: has_results={self.last_calculation_result is not None}, outdated={self.results_outdated}, calculating={self.is_calculating}")
        # Solo actuar si hay resultados Y no están ya obsoletos
        if (self.last_calculation_result is not None and 
            not self.results_outdated and 
            not self.is_calculating):
            
            self.results_outdated = True
            self._update_preview_button_state()
        # Si ya está obsoleto o calculando, no hacer nada (evitar spam)

    def _invalidate_results_immediately(self):
        """⚡ Invalida resultados INSTANTÁNEAMENTE al cambiar parámetros"""
        # Solo actuar si hay resultados Y no están ya obsoletos
        if (self.last_calculation_result is not None and 
            not self.results_outdated and 
            not self.is_calculating):
            
            self.results_outdated = True
            self._update_preview_button_state()
        else:
            # Debug: Mostrar por qué no se invalidó (comentar en producción)
            if self.last_calculation_result is None:
                pass  # print(f"🔍 Sin invalidación: No hay resultados previos")
            elif self.results_outdated:
                pass  # print(f"🔍 Sin invalidación: Ya estaba obsoleto")
            elif self.is_calculating:
                pass  # print(f"🔍 Sin invalidación: Ya está calculando")
    
    def _auto_calculate(self):
        """Realiza cálculo automático"""
        logger.debug(
            "MainPresenter",
            (
                "auto_calculate_trigger "
                f"qt_thread={id(QThread.currentThread())} py_thread={threading.get_ident()}"
            )
        )
        # ✅ Marcar como calculando y actualizar botón
        self.is_calculating = True
        self._update_preview_button_state()
        
        self.view.add_calculation_log("Automático iniciado")
        self._perform_calculation(manual=False)
    
    def _perform_calculation(self, manual: bool = True):
        """Realiza el cálculo del presupuesto"""
        calc_start_ts = perf_counter()
        logger.debug("MainPresenter", f"_perform_calculation iniciado: manual={manual}, printer={self.selected_printer.id if self.selected_printer else None}, filament={self.selected_filament.id if self.selected_filament else None}, multicolor_slots={len(self._multicolor_slots_state)}")
        logger.debug(
            "MainPresenter",
            (
                "calc_thread_probe "
                f"qt_thread={id(QThread.currentThread())} py_thread={threading.get_ident()}"
            )
        )
        try:
            # Verificar datos requeridos para cálculo (sin cliente)
            is_valid, error_message = self.view.has_required_calculation_data()
            if not is_valid:
                if manual:  # Solo mostrar error si es cálculo manual
                    self.view.show_error_message(tr(I18N.Quote.MSG_INCOMPLETE_DATA_TITLE), error_message)
                return
            
            # Obtener datos de la vista
            hours, minutes = self.view.get_time_values()
            weight_grams = self.view.get_weight_value()
            quantity = self.view.get_quantity_value()
            
            # Verificar que tenemos las selecciones
            if not self.selected_printer:
                self.view.add_status_message("❌ ERROR: No hay impresora seleccionada")
                return
            
            # En modo multicolor el filamento de referencia se deriva de los slots;
            # solo exigir selected_filament en modo monocolor.
            if not self._multicolor_slots_state and not self.selected_filament:
                self.view.add_status_message("❌ ERROR: No hay filamento seleccionado")
                return
            
            # Convertir tiempo total a minutos (considerando cantidad si aplica)
            total_minutes = (hours * 60 + minutes) * max(1, quantity)
            total_weight_grams = weight_grams * max(1, quantity)

            # Realizar cálculo usando el facade (usa valores por defecto de márgenes/config)
            self.view.add_calculation_log("Enviando solicitud al backend")

            # Construir slots multicolor si los hay
            from application.dtos.quote_dtos import FilamentSlotCalcDTO
            slot_dtos = []
            if self._multicolor_slots_state:
                quantity = max(1, self.view.get_quantity_value())
                for s in self._multicolor_slots_state:
                    fid = s.get('filament_id', 0)
                    w = s.get('weight_grams', 0.0) * quantity
                    if fid > 0 and w > 0:
                        slot_dtos.append(FilamentSlotCalcDTO(
                            slot_index=s['slot_index'],
                            filament_id=fid,
                            weight_grams=w,
                        ))

            # En modo multicolor, usar slot[0] como filament_id de referencia (o el seleccionado)
            ref_filament_id = self.selected_filament.id if self.selected_filament else 0
            if slot_dtos and ref_filament_id == 0:
                ref_filament_id = slot_dtos[0].filament_id

            backend_start_ts = perf_counter()
            response = self.facade.calculate_quote_costs(
                printer_id=self.selected_printer.id,
                filament_id=ref_filament_id,
                print_time_minutes=total_minutes,
                filament_weight_grams=total_weight_grams,
                filament_slots=slot_dtos if slot_dtos else None,
            )
            backend_ms = (perf_counter() - backend_start_ts) * 1000
            if backend_ms >= 80:
                logger.warning("MainPresenter", f"calc_backend_elapsed_ms={backend_ms:.1f}")
            else:
                logger.debug("MainPresenter", f"calc_backend_elapsed_ms={backend_ms:.1f}")

            # Manejar respuesta
            if isinstance(response, ErrorResponseDTO):
                error_msg = response.message or "Error desconocido en el cálculo"
                self.view.show_error_message("Error en Cálculo", error_msg)
                return

            if isinstance(response, QuoteCalculationResponseDTO):
                # Guardar último resultado (como dict sencillo para otras vistas)
                result = {
                    'material_cost': response.material_cost,
                    'electricity_cost': response.electricity_cost,
                    'operation_cost': response.operation_cost,
                    'subtotal_base_costs': response.subtotal_base_costs,
                    'failure_margin_cost': response.failure_margin_cost,
                    'subtotal_with_margin': response.subtotal_with_margin,
                    'commission_cost': response.commission_cost,
                    'subtotal_before_profit': response.subtotal_before_profit,
                    'profit_amount': response.profit_amount,
                    'subtotal_before_tax': response.subtotal_before_tax,
                    'tax_amount': response.tax_amount,
                    'total_to_pay': response.total_to_pay,
                    'calculation_timestamp': response.calculation_timestamp,
                    'printer_info': response.printer_info,
                    'filament_info': response.filament_info,
                    'calculation_details': response.calculation_details,
                }
                # self.last_calculation_result = result  # ✅ Movido después del cálculo completo
                
                # ✅ NUEVO: Calcular anticipo si está habilitado
                advance_enabled = self.view.is_advance_enabled()
                advance_percentage = self.view.get_advance_percentage()
                
                if advance_enabled and advance_percentage > 0:
                    total_amount = result['total_to_pay']
                    advance_amount = (total_amount * advance_percentage) / 100
                    remaining_amount = total_amount - advance_amount
                    
                    # Agregar información de anticipo al resultado
                    result['advance_enabled'] = True
                    result['advance_percentage'] = advance_percentage
                    result['advance_amount'] = advance_amount
                    result['remaining_amount'] = remaining_amount
                else:
                    # Asegurar que los campos estén en False/0 cuando no hay anticipo
                    result['advance_enabled'] = False
                    result['advance_percentage'] = 0
                    result['advance_amount'] = 0
                    result['remaining_amount'] = result['total_to_pay']
                
                # ✅ NUEVO: Agregar post-procesado si está habilitado
                post_enabled = self.view.is_post_enabled()
                post_total_amount = self.view.get_post_total_amount()  # Usa monto total con multiplicador
                
                result['post_enabled'] = post_enabled
                result['post_amount'] = post_total_amount if post_enabled else 0
                
                # ✅ SUMAR post-procesado al total final si está habilitado
                original_total = result['total_to_pay']
                if post_enabled and post_total_amount > 0:
                    result['total_to_pay'] = original_total + post_total_amount
                    result['subtotal_before_post'] = original_total  # Guardar subtotal antes de post-procesado
                    # Recalcular IVA incluido sobre el total completo (producción + post-procesado).
                    # Fórmula "por dentro": IVA = Total - (Total / (1 + tasa))
                    tax_rate = (result.get('calculation_details') or {}).get('tax_rate_percent', 0) or 0
                    if tax_rate > 0:
                        new_total = result['total_to_pay']
                        result['tax_amount'] = round(new_total - (new_total / (1 + tax_rate / 100)), 2)
                
                # ✅ Guardar resultado completo con todos los cálculos aplicados
                self.last_calculation_result = result

                # Actualizar costos por slot multicolor si los hay
                if slot_dtos:
                    breakdown = (result.get('calculation_details') or {}).get('slot_breakdown', [])
                    for b in breakdown:
                        for s in self._multicolor_slots_state:
                            if s['slot_index'] == b['slot_index']:
                                s['slot_cost'] = b.get('slot_cost', 0.0)
                                s['price_per_gram'] = b.get('price_per_gram', 0.0)
                    # Actualizar tooltips en la vista con los nuevos costos
                    if self._multicolor_slots_state:
                        tooltip_updates = [
                            (s['slot_index'], self._build_multicolor_slot_tooltip(s))
                            for s in self._multicolor_slots_state
                        ]
                        self.view.update_multicolor_slot_costs(tooltip_updates)
                
                # ✅ Aplicar reglas de anticipo basadas en preferencias después del cálculo
                self.view._apply_advance_rules_after_calculation()
                
                # ✅ Marcar que el cálculo terminó y los resultados están actualizados
                self.is_calculating = False
                self.results_outdated = False
                self._update_preview_button_state()

                calculation_type = "manual" if manual else "automático"
                
                # Construir texto base con formato de moneda correcto
                base_text = (
                    f"Cálculo {calculation_type} completado:\n"
                    f"• Cantidad: {quantity} pieza(s)\n"
                    f"• Costo de material: {CurrencyHelper.format_with_current_currency(result['material_cost'] or 0)}\n"
                    f"• Costo de energía: {CurrencyHelper.format_with_current_currency(result['electricity_cost'] or 0)}\n"
                    f"• Costo de operación: {CurrencyHelper.format_with_current_currency(result['operation_cost'] or 0)}\n"
                    f"• Subtotal base: {CurrencyHelper.format_with_current_currency(result['subtotal_base_costs'] or 0)}\n"
                    f"• Subtotal con márgenes/comisión: {CurrencyHelper.format_with_current_currency(result['subtotal_before_profit'] or 0)}\n"
                    f"• Impuestos: {CurrencyHelper.format_with_current_currency(result['tax_amount'] or 0)}"
                )
                
                # Agregar subtotal antes de post-procesado si hay post-procesado
                if post_enabled and post_total_amount > 0:
                    base_text += f"\n• Subtotal (antes post-proc.): {CurrencyHelper.format_with_current_currency(result['subtotal_before_post'] or 0)}"
                    
                    # Información detallada del post-procesado
                    post_type = self.view.get_post_type()
                    post_multiplier = self.view.get_post_multiplier()
                    post_base = self.view.get_post_amount()
                    
                    base_text += f"\n• Post-procesado ({post_type}):"
                    base_text += f"\n  - Base: {CurrencyHelper.format_with_current_currency(post_base)} × {post_multiplier} = {CurrencyHelper.format_with_current_currency(post_total_amount)}"
                
                # Total final
                base_text += f"\n• TOTAL A PAGAR: {CurrencyHelper.format_with_current_currency(result['total_to_pay'] or 0)}"
                
                result_text = base_text
                
                # ✅ NUEVO: Agregar información de anticipo al texto de resultado
                if result['advance_enabled']:
                    result_text += (
                        f"\n\n💰 INFORMACIÓN DE ANTICIPO:\n"
                        f"• Porcentaje: {result['advance_percentage']}%\n"
                        f"• Monto del anticipo: {CurrencyHelper.format_with_current_currency(result['advance_amount'])}\n"
                        f"• Saldo restante: {CurrencyHelper.format_with_current_currency(result['remaining_amount'])}"
                    )

                self.view.show_calculation_result(result_text)

                if manual:
                    # Construir mensaje de éxito con información de anticipo y post-procesado si aplica
                    success_message = f"Presupuesto calculado correctamente.\nTotal a pagar: {CurrencyHelper.format_with_current_currency(result['total_to_pay'] or 0)}"
                    
                    # Agregar información de post-procesado si está habilitado
                    if result.get('post_enabled', False) and result.get('post_amount', 0) > 0:
                        subtotal_before_post = result.get('subtotal_before_post', result['total_to_pay'] - result['post_amount'])
                        success_message += (
                            f"\n\nIncluye post-procesado:"
                            f"\nSubtotal: {CurrencyHelper.format_with_current_currency(subtotal_before_post)}"
                            f"\nPost-procesado: {CurrencyHelper.format_with_current_currency(result['post_amount'])}"
                        )
                    
                    if result['advance_enabled']:
                        success_message += (
                            f"\n\nAnticipo requerido ({result['advance_percentage']}%): "
                            f"{CurrencyHelper.format_with_current_currency(result['advance_amount'])}\n"
                            f"Saldo restante: {CurrencyHelper.format_with_current_currency(result['remaining_amount'])}"
                        )
                    
                    self.view.show_success_message("Cálculo Completado", success_message)
                return

            # Caso inesperado
            self.view.show_error_message("Error en Cálculo", "Respuesta de cálculo no reconocida")
                
        except Exception as e:
            error_msg = f"Error inesperado durante el cálculo: {str(e)}"
            logger.log_exception("MainPresenter", e, "calcular presupuesto")
            self.view.show_error_message("Error Inesperado", "Ocurrió un error al calcular el presupuesto.\nRevise los datos e intente nuevamente.")
        finally:
            total_calc_ms = (perf_counter() - calc_start_ts) * 1000
            if total_calc_ms >= 120:
                logger.warning("MainPresenter", f"calc_total_elapsed_ms={total_calc_ms:.1f}")
            else:
                logger.debug("MainPresenter", f"calc_total_elapsed_ms={total_calc_ms:.1f}")
            # ✅ Siempre marcar como no calculando al final (éxito o error)
            self.is_calculating = False
            self._update_preview_button_state()
    
    def _clear_internal_state(self):
        """Limpia el estado interno del presenter"""
        self.selected_customer = None
        self.selected_filament = None
        self.selected_printer = None
        self.last_calculation_result = None
        # ✅ Limpiar ambos flags de estado
        self.is_calculating = False
        self.results_outdated = False
        self.calculation_timer.stop()
        self.backup_timer.stop()  # Detener timer de respaldos
        # Limpiar estado multicolor
        self._multicolor_slots_state = []
        self._active_multicolor_slot = -1
        self.view.set_multicolor_mode(False)
        self.view.hide_multicolor_panel()
        # ✅ Actualizar botón al limpiar
        self._update_preview_button_state()
    
    def _update_preview_button_state(self):
        """Actualiza el estado del botón Preview según el estado actual"""
        self._update_action_buttons_state()

    def _update_action_buttons_state(self):
        """Actualiza el estado de los botones de acción (Preview y PDF) según el estado actual"""
        try:
            # ✅ Lógica unificada para ambos botones:
            # - Si está calculando: DISABLED
            # - Si resultados están obsoletos: DISABLED  
            # - En cualquier otro caso: ENABLED
            
            if self.is_calculating:
                should_enable = False
                reason = "calculando"
            elif self.results_outdated:
                should_enable = False
                reason = "resultados obsoletos"
            else:
                should_enable = True
                reason = "disponible"
            
            # ✅ Actualizar botón PREVIEW
            if self.view.is_preview_button_enabled() != should_enable:
                self.view.set_preview_button_enabled(should_enable)
            
            # ✅ Actualizar botón GENERAR
            if self.view.is_generate_button_enabled() != should_enable:
                self.view.set_generate_button_enabled(should_enable)
                    
        except Exception as e:
            logger.error("MainPresenter", f"Error actualizando estado de botones: {e}")
    
    # === MÉTODOS PÚBLICOS PARA INTEGRACIÓN ===
    
    def get_view(self):
        """Retorna la vista asociada"""
        return self.view
    
    def is_ready_for_calculation(self) -> bool:
        """Verifica si está listo para calcular"""
        return (self.selected_printer is not None and 
                self.selected_filament is not None)
    
    def get_calculation_summary(self) -> str:
        """Obtiene un resumen del estado actual"""
        summary = []
        summary.append("📊 ESTADO ACTUAL DEL SISTEMA")
        summary.append("=" * 50)
        
        if self.selected_customer:
            summary.append(f"👤 Cliente: {self.selected_customer.full_name}")
        else:
            summary.append("👤 Cliente: No seleccionado")
        
        if self.selected_printer:
            summary.append(f"🖨️ Impresora: {self.selected_printer.name}")
        else:
            summary.append("🖨️ Impresora: No seleccionada")
        
        if self.selected_filament:
            summary.append(f"🧵 Filamento: {self.selected_filament.name}")
        else:
            summary.append("🧵 Filamento: No seleccionado")
        
        hours, minutes = self.view.get_time_values()
        weight = self.view.get_weight_value()
        quantity = self.view.get_quantity_value()
        
        summary.append(f"⏱️ Tiempo: {hours}h {minutes}m")
        summary.append(f"⚖️ Peso: {weight}g")
        summary.append(f"🔢 Cantidad: {quantity} piezas")
        
        if self.last_calculation_result:
            result = self.last_calculation_result
            total = result.get('total_to_pay')
            if isinstance(total, (int, float)):
                summary.append(f"💰 Último cálculo: {CurrencyHelper.format_with_current_currency(total)}")
        
        summary.append("=" * 50)
        
        return "\n".join(summary)
    
    # === SISTEMA DE RESPALDOS AUTOMÁTICOS ===
    
    def _initialize_backup_system(self):
        """Inicializa el sistema de respaldos automáticos"""
        try:
            backup_service = get_backup_service()
            status = backup_service.get_backup_status()
            
            if status['enabled']:
                # Log sistema de respaldos sin mostrar en UI (solo debug)
                logger.debug("MainPresenter", "Sistema de respaldos automáticos activado", 
                               frecuencia=f"cada {status['frequency_days']} días",
                               total_respaldos=status['total_backups'])
                
                if status['last_backup_date']:
                    logger.debug("MainPresenter", "Estado de respaldo", 
                                   ultimo_respaldo=status['last_backup_date'],
                                   dias_transcurridos=f"{status['days_since_last']} días atrás")
                
                # Verificar si se necesita un respaldo inicial
                if status['needs_backup']:
                    self.view.add_system_log("⏰ Respaldo pendiente detectado...")
                    result = backup_service.perform_automatic_backup()
                    
                    if result['success']:
                        self.view.add_system_log(f"✅ {result['message']}")
                        if result['cleaned_files'] > 0:
                            self.view.add_system_log(f"{result['cleaned_files']} respaldos antiguos eliminados")
                    else:
                        self.view.add_system_log(f"❌ {result['message']}")
                else:
                    self.view.add_system_log("✅ Respaldos al día")
            else:
                self.view.add_system_log("⚠️ Respaldos automáticos DESACTIVADOS")
                
        except Exception as e:
            self.view.add_system_log(f"❌ Error al inicializar respaldos: {e}")
    
    def _check_automatic_backup(self):
        """Verifica si es necesario realizar un respaldo automático"""
        try:
            backup_service = get_backup_service()
            
            if backup_service.needs_backup():
                self.view.add_system_log("🔄 Ejecutando respaldo automático programado...")
                result = backup_service.perform_automatic_backup()
                
                if result['success']:
                    self.view.add_system_log(f"✅ {result['message']}")
                    if result['cleaned_files'] > 0:
                        self.view.add_system_log(f"{result['cleaned_files']} respaldos antiguos eliminados")
                else:
                    self.view.add_system_log(f"❌ {result['message']}")
                    
        except Exception as e:
            self.view.add_system_log(f"❌ Error al verificar respaldos automáticos: {e}")
    
    def force_backup_now(self):
        """Fuerza un respaldo inmediato (para uso manual/debugging)"""
        self.view.add_system_log("🔧 RESPALDO MANUAL SOLICITADO")
        
        try:
            backup_service = get_backup_service()
            result = backup_service.perform_automatic_backup()
            
            if result['success']:
                self.view.add_system_log(f"✅ {result['message']}")
                if result['cleaned_files'] > 0:
                    self.view.add_system_log(f"{result['cleaned_files']} respaldos antiguos eliminados")
            else:
                self.view.add_system_log(f"❌ {result['message']}")
                
        except Exception as e:
            self.view.add_system_log(f"❌ Error en respaldo manual: {e}")

    def _get_customer_info_for_pdf(self) -> Optional[dict]:
        """
        Obtiene la información del cliente para incluir en el PDF
        Retorna None si no hay cliente seleccionado, dict con info si hay cliente
        """
        if not self.selected_customer:
            return None
        
        customer = self.selected_customer
        
        # Formatear información del cliente con valores por defecto para campos vacíos
        return {
            'full_name': customer.full_name or tr(I18N.MainWindow.DETAIL_NOT_AVAILABLE),
            'ruc_ci': customer.ruc_ci or tr(I18N.MainWindow.DETAIL_NOT_AVAILABLE), 
            'email': customer.email or tr(I18N.MainWindow.DETAIL_NOT_AVAILABLE),
            'phone_number': customer.phone_number or tr(I18N.MainWindow.DETAIL_NOT_AVAILABLE)
        }
    
    # ==================== TAB MANAGER SETUP ====================
    
    def _setup_tab_manager(self):
        """Configura el sistema de gestión de tabs con doble click y F5"""
        try:
            # Configuración del tab manager principal
            tab_config = TabManagerConfig(
                tab_name="MainTabs",
                tab_widget=self.view.get_tab_widget(),
                refresh_button=None,  # No hay botón físico, usamos shortcuts
                tab_action_callback=self.handle_tab_change,
                refresh_callback=self._handle_current_tab_refresh
            )
            
            # Crear el manager
            self.tab_manager = TabWidgetEventManager(tab_config)
            self.tab_manager.setParent(self)
            
            # Configurar shortcut F5 para refresh global
            self._setup_refresh_shortcuts()
            
        except Exception as e:
            logger.error("MainPresenter", f"Error configurando tab manager: {e}")
    
    def _setup_refresh_shortcuts(self):
        """Configura los shortcuts para refresh"""
        from PySide6.QtGui import QShortcut, QKeySequence
        
        # F5 - Refresh todas las tablas
        self.shortcut_refresh_all = QShortcut(QKeySequence("F5"), self.view)
        self.shortcut_refresh_all.activated.connect(self.refresh_all_tabs)
    
    def _handle_current_tab_refresh(self):
        """Maneja el refresh del tab actual (doble click)"""
        current_index = self.view.get_current_tab_index()
        tab_names = ["Presupuesto", "Historial", "Inventario", "Impresoras", "Clientes", "Ajustes"]
        
        if current_index < len(tab_names):
            tab_name = tab_names[current_index]
            
            # Refresh específico según el tab
            if tab_name == "Inventario":
                self.refresh_filaments_tab()
            elif tab_name == "Impresoras":
                self.refresh_printers_tab()
            elif tab_name == "Clientes":
                self.refresh_customers_tab()
            elif tab_name == "Historial":
                self.refresh_quotes_tab()
            else:
                self.view.add_system_log(f"🔄 Tab '{tab_name}' actualizado")
    
    # ==================== TAB MANAGER METHODS ====================
    
    def refresh_filaments_tab(self):
        """Refresca la tabla de filamentos"""
        try:
            if hasattr(self, 'filament_inventory_presenter') and self.filament_inventory_presenter:
                if hasattr(self.filament_inventory_presenter, 'refresh_data'):
                    self.filament_inventory_presenter.refresh_data()
                else:
                    self.filament_inventory_presenter.load_filaments()
                logger.debug("MainPresenter", "Inventario de filamentos actualizado")
                self.view.add_system_log("🔄 Inventario de filamentos actualizado")
        except Exception as e:
            self.view.add_system_log(f"❌ Error actualizando filamentos: {e}")
    
    def refresh_printers_tab(self):
        """Refresca la tabla de impresoras"""
        try:
            if hasattr(self, 'printer_inventory_presenter') and self.printer_inventory_presenter:
                self.printer_inventory_presenter.load_printers()
                logger.debug("MainPresenter", "Inventario de impresoras actualizado")
                self.view.add_system_log("🔄 Inventario de impresoras actualizado")
        except Exception as e:
            self.view.add_system_log(f"❌ Error actualizando impresoras: {e}")
    
    def refresh_customers_tab(self):
        """Refresca la tabla de clientes"""
        try:
            if hasattr(self, 'customer_inventory_presenter') and self.customer_inventory_presenter:
                self.customer_inventory_presenter.load_customers()
                logger.debug("MainPresenter", "Inventario de clientes actualizado")
                self.view.add_system_log("🔄 Inventario de clientes actualizado")
        except Exception as e:
            self.view.add_system_log(f"❌ Error actualizando clientes: {e}")
            
    def refresh_quotes_tab(self):
        """Refresca la tabla de quotes del historial"""
        try:
            self.quote_inventory_presenter.refresh()
            logger.debug("MainPresenter", "Historial de presupuestos actualizado")
            self.view.add_system_log("🔄 Historial de presupuestos actualizado")
        except Exception as e:
            self.view.add_system_log(f"❌ Error actualizando historial: {e}")
    
    def refresh_all_tabs(self):
        """Refresca todas las tablas de inventario (F5)"""
        self.view.add_system_log("🔄 Actualizando todos los inventarios...")
        self.refresh_filaments_tab()
        self.refresh_printers_tab() 
        self.refresh_customers_tab()
        self.refresh_quotes_tab()
        self.view.add_system_log("✅ Todos los inventarios actualizados")
    
    def handle_tab_change(self, current_widget):
        """Maneja el cambio de tab para acciones específicas si es necesario"""
        # Puedes agregar lógica específica por tab aquí
        pass

    def cleanup(self):
        """
        Limpia los recursos del presenter antes de que sea destruido.
        Debe ser llamado antes del cierre de la aplicación.
        """
        try:
            if hasattr(self, 'tab_manager') and self.tab_manager:
                self.tab_manager.cleanup()
                
            # Cleanup de inventory presenters para liberar animaciones
            if hasattr(self, 'filament_inventory_presenter') and self.filament_inventory_presenter:
                self.filament_inventory_presenter.cleanup()
                
            if hasattr(self, 'printer_inventory_presenter') and self.printer_inventory_presenter:
                self.printer_inventory_presenter.cleanup()
                
            if hasattr(self, 'customer_inventory_presenter') and self.customer_inventory_presenter:
                self.customer_inventory_presenter.cleanup()
                
            if hasattr(self, 'quote_inventory_presenter') and self.quote_inventory_presenter:
                self.quote_inventory_presenter.cleanup()
                
        except Exception as e:
            logger.error("MainPresenter", f"Error durante cleanup: {e}")

    def _generate_project_name(self, quote_number: str) -> str:
        """Genera un nombre de proyecto automático basado en la información disponible"""
        parts = []
        
        # Agregar información del cliente si está disponible
        customer_data = self.view.get_customer_data()
        if customer_data and customer_data.get('full_name', '').strip():
            customer_name = customer_data['full_name'].strip()[:20]  # Limitar longitud
            parts.append(customer_name)
        
        # Agregar información de la impresora
        if self.selected_printer:
            printer_name = getattr(self.selected_printer, 'name', 'Impresora')[:15]
            parts.append(printer_name)
        
        # Agregar información del filamento
        if self.selected_filament:
            filament_name = getattr(self.selected_filament, 'name', 'Filamento')[:15]
            parts.append(filament_name)
        
        # Si no hay información específica, usar genérico
        if not parts:
            parts.append("Proyecto de Impresión 3D")
        
        # Combinar partes y agregar número de presupuesto
        project_name = " - ".join(parts)
        project_name = f"{project_name} ({quote_number})"
        
        # Asegurar que no exceda los 100 caracteres del límite
        if len(project_name) > 100:
            project_name = project_name[:97] + "..."
        
        return project_name

    def _apply_printer_preferences(self):
        """Aplica las preferencias de impresora después de que las conexiones estén establecidas"""
        try:
            # Obtener configuraciones desde preferencias usando los métodos correctos
            preferences = self.view.app_preferences
            printer_id = preferences.get_default_printer_id()
            auto_select = preferences.get_auto_select_first_printer()
            
            # Aplicar lógica según las preferencias
            if printer_id is not None:
                if printer_id == "first" or auto_select:
                    self._load_first_available_printer_from_preferences()
                else:
                    # printer_id debe ser un int (ID específico)
                    self._load_printer_by_id_from_preferences(int(printer_id))
            else:
                # Sin preferencias de impresora, no hacer nada
                self.view.add_system_log("• Impresora: Sin selección automática configurada")
                
        except Exception as e:
            logger.error("MainPresenter", f"Error aplicando preferencias de impresora: {e}")
            self.view.add_system_log("⚠️ Error cargando impresora por defecto")
    
    def _load_first_available_printer_from_preferences(self):
        """Carga la primera impresora disponible desde preferencias (lógica de negocio)"""
        try:
            # Obtener primera impresora desde el facade
            printers = self.facade.get_all_printers()
            if not printers:
                self.view.add_system_log("No hay impresoras disponibles en la base de datos")
                return
                
            # Tomar la primera impresora
            first_printer = printers[0]
            
            # Usar el método del presenter para establecer la impresora (el facade retorna objetos Printer directamente)
            self.set_selected_printer(first_printer)
            self.view.add_system_log(f"✅ Impresora por defecto cargada: {first_printer.name}")
                
        except Exception as e:
            self.view.add_system_log(f"Error cargando primera impresora: {str(e)}")
    
    def _load_printer_by_id_from_preferences(self, printer_id: int):
        """Carga una impresora específica por ID desde preferencias (lógica de negocio)"""
        try:
            # Obtener impresora específica desde el facade
            printer = self.facade.get_printer_by_id(printer_id)
            if not printer or not printer.is_active:
                self.view.add_system_log("❌ Impresora guardada en preferencias no encontrada o inactiva")
                # Cargar primera disponible como fallback
                self._load_first_available_printer_from_preferences()
                return
                
            # Usar el método del presenter para establecer la impresora (el facade retorna objeto Printer directamente)
            self.set_selected_printer(printer)
            self.view.add_system_log(f"✅ Impresora desde preferencias: {printer.name}")
                
        except Exception as e:
            self.view.add_system_log("❌ Error cargando impresora guardada en preferencias")
            # Cargar primera disponible como fallback
            self._load_first_available_printer_from_preferences()
    
    def _apply_customer_preferences(self):
        """Aplica las preferencias de cliente después de que las conexiones estén establecidas"""
        try:
            # Obtener configuraciones desde preferencias
            preferences = self.view.app_preferences
            customer_mode = preferences.get_default_customer_mode()
            
            self.view.add_system_log(f"🔧 Aplicando modo de cliente: {customer_mode}")
            
            if customer_mode == "normal":
                # Cliente requerido - campo vacío y checkbox destildado
                self.view.set_customer_optional(False)
                self.view.add_system_log("• Cliente: Campo requerido (vacío)")
                # NO cargar ningún cliente - dejar vacío
                self.selected_customer = None
                self.view.set_customer_data("", "")
                
            elif customer_mode == "optional":
                # Cliente opcional - checkbox tildado, campo vacío
                self.view.set_customer_optional(True)
                self.view.add_system_log("• Cliente: Campo opcional (vacío)")
                # NO cargar ningún cliente - dejar vacío
                self.selected_customer = None
                self.view.set_customer_data("", "")
                
            elif customer_mode == "default":
                # Cargar cliente por defecto si existe
                self.view.add_system_log("• Cliente: Cargando cliente por defecto")
                self._load_default_customer_from_preferences()
                self.view.set_customer_optional(False)  # No opcional cuando hay cliente por defecto
                
        except Exception as e:
            logger.error("MainPresenter", f"Error aplicando preferencias de cliente: {e}")
            self.view.add_system_log("⚠️ Error cargando preferencias de cliente")
    
    def _apply_advance_preferences_on_startup(self):
        """Aplica las preferencias de anticipo al iniciar la aplicación"""
        try:
            # Aplicar preferencias silenciosamente sin mensaje de log
            self.view._apply_app_preferences()
        except Exception as e:
            logger.error("MainPresenter", f"Error aplicando preferencias de anticipo: {e}")
            self.view.add_system_log("⚠️ Error cargando preferencias de anticipo")
    
    def _load_default_customer_from_preferences(self):
        """Carga el cliente marcado como por defecto desde preferencias (lógica de negocio)"""
        try:            
            # Obtener cliente por defecto desde el facade
            result = self.facade.get_default_customer()
            
            if result.success and result.data:
                self.view.add_system_log(f"• Cliente por defecto encontrado: {result.data.full_name}")
                
                # Crear objeto Customer desde el DTO usando solo los campos que existen
                customer_data = result.data
                
                customer = Customer(
                    id=customer_data.id,
                    full_name=customer_data.full_name,
                    ruc_ci=customer_data.ruc_ci,
                    email=customer_data.email,
                    phone_number=customer_data.phone_number,
                    is_default=customer_data.is_default,
                    created_at=customer_data.created_at,
                    updated_at=customer_data.updated_at
                )
                
                # Usar el método del presenter para establecer el cliente
                self.set_selected_customer(customer)
                self.view.add_system_log(f"✅ Cliente por defecto cargado: {customer.full_name}")
            else:
                self.view.add_system_log("• No se encontró cliente por defecto configurado")
                
        except Exception as e:
            self.view.add_system_log(f"Error cargando cliente por defecto: {str(e)}")
            logger.error("MainPresenter", f"Error cargando cliente por defecto: {e}")

    def get_last_calculation_result(self):
        """Devuelve el último resultado de cálculo disponible"""
        return self.last_calculation_result

    def _recalculate_advance_only(self):
        """Recalcula solo la información del anticipo sin hacer un cálculo completo"""
        if not self.last_calculation_result:
            return
            
        try:
            # Obtener datos actuales del anticipo desde la vista
            advance_enabled = self.view.is_advance_enabled()
            advance_percentage = self.view.get_advance_percentage() if advance_enabled else 0
            
            # Usar el total ya calculado
            total_to_pay = self.last_calculation_result.get('total_to_pay', 0)
            
            # Recalcular solo los valores del anticipo
            if advance_enabled and advance_percentage > 0:
                advance_amount = total_to_pay * (advance_percentage / 100)
                remaining_amount = total_to_pay - advance_amount
            else:
                advance_amount = 0
                remaining_amount = total_to_pay
            
            # Actualizar solo los valores del anticipo en el resultado existente
            self.last_calculation_result.update({
                'advance_enabled': advance_enabled,
                'advance_percentage': advance_percentage,
                'advance_amount': advance_amount,
                'remaining_amount': remaining_amount
            })
            
            # Regenerar solo el texto del resultado con los nuevos valores de anticipo
            result = self.last_calculation_result
            
            # Construir el resultado visual actualizado
            result_text = (
                "==============================\n"
                "RESULTADO DEL CÁLCULO\n"
                "==============================\n"
                f"Cálculo automático completado:\n"
                f"• Cantidad: {int(round(result['quantity']))} pieza(s)\n"
                f"• Costo de material: {CurrencyHelper.format_with_current_currency(result['material_cost'])}\n"
                f"• Costo de energía: {CurrencyHelper.format_with_current_currency(result['energy_cost'])}\n"
                f"• Costo de operación: {CurrencyHelper.format_with_current_currency(result['operation_cost'])}\n"
                f"• Subtotal base: {CurrencyHelper.format_with_current_currency(result['subtotal_base'])}\n"
                f"• Subtotal con márgenes/comisión: {CurrencyHelper.format_with_current_currency(result['subtotal_with_margins'])}\n"
                f"• Impuestos: {CurrencyHelper.format_with_current_currency(result['taxes'])}\n"
                f"• TOTAL A PAGAR: {CurrencyHelper.format_with_current_currency(result['total_to_pay'])}\n"
                "=============================="
            )
            
            # Agregar información de post-procesado si está habilitado
            if result.get('post_enabled', False) and result.get('post_amount', 0) > 0:
                result_text += (
                    f"\n\n🔧 INFORMACIÓN DE POST-PROCESADO:\n"
                    f"• Monto: {CurrencyHelper.format_with_current_currency(result['post_amount'])}\n"
                    f"• Subtotal antes del post: {CurrencyHelper.format_with_current_currency(result.get('subtotal_before_post', 0))}"
                )
            
            # Agregar información del anticipo si está habilitado
            if result['advance_enabled']:
                result_text += (
                    f"\n💰 INFORMACIÓN DE ANTICIPO:\n"
                    f"• Porcentaje: {result['advance_percentage']}%\n"
                    f"• Monto del anticipo: {CurrencyHelper.format_with_current_currency(result['advance_amount'])}\n"
                    f"• Saldo restante: {CurrencyHelper.format_with_current_currency(result['remaining_amount'])}"
                )

            
            result_text += "\n=============================="
            
            # Mostrar el resultado actualizado
            self.view.show_calculation_result(result_text)
            
        except Exception as e:
            pass
    
    # === MÉTODOS DE ACTUALIZACIÓN AUTOMÁTICA ===
    
    def _check_updates_on_startup(self):
        """
        Verifica actualizaciones al iniciar la aplicación (modo silencioso)
        Solo notifica si HAY una actualización disponible
        Respeta la configuración del usuario (modo y frecuencia)
        """
        try:
            from core.managers.app_preferences_manager import AppPreferencesManager
            prefs = AppPreferencesManager()
            
            # Verificar si el usuario configuró modo manual
            check_mode = prefs.get_update_check_mode()
            
            if check_mode == "manual":
                logger.info("MainPresenter", "Verificación automática deshabilitada (modo manual)")
                return
            
            # Si es automático, verificar la frecuencia
            frequency = prefs.get_update_check_frequency()
            
            # Determinar los días de caché según la frecuencia
            cache_days_map = {
                "startup": 0,  # Siempre verificar al iniciar
                "7days": 7,
                "15days": 15,
                "30days": 30
            }
            
            cache_days = cache_days_map.get(frequency, 0)
            
            # Verificar si debe hacer la comprobación según la frecuencia
            if cache_days > 0 and not prefs.should_check_updates(cache_days=cache_days):
                logger.info("MainPresenter", f"Omitiendo verificación (frecuencia: cada {cache_days} días)")
                return
            
            self.view.add_system_log("🔄 Verificando actualizaciones...")
            
            # Verificación asincrónica que no bloquea la UI
            # Solo notifica si hay actualización disponible
            self.update_checker.check_for_updates_async(silent=True)
            
        except Exception as e:
            logger.error("MainPresenter", f"Error al verificar actualizaciones: {e}")
            logger.log_exception("MainPresenter", e, "_check_updates_on_startup")
    
    def _on_check_updates_manually(self):
        """
        Verifica actualizaciones cuando el usuario lo solicita explícitamente
        Notifica SIEMPRE, incluso si no hay actualizaciones
        """
        try:
            # Cancelar búsqueda automática pendiente si existe
            if self.update_check_timer.isActive():
                self.update_check_timer.stop()
                logger.info("MainPresenter", "Búsqueda automática cancelada (usuario solicitó búsqueda manual)")
            
            self.view.add_action_log("Buscando actualizaciones...")
            
            # Verificación explícita que siempre notifica el resultado
            self.update_checker.check_for_updates_async(silent=False)
            
        except Exception as e:
            logger.error("MainPresenter", f"Error al verificar actualizaciones manualmente: {e}")
            logger.log_exception("MainPresenter", e, "_on_check_updates_manually")
    
    def _on_update_detector_signal(self, update_info: dict):
        """Maneja la señal cuando el update checker detecta una actualización disponible"""
        try:
            version = update_info.get('version', 'N/A')
            build = update_info.get('build', 'N/A')
            
            # Notificar al usuario en el log del sistema
            self.view.add_system_log(f"✅ Nueva versión disponible: v{version}")
            
            # Si el diálogo About está abierto, actualizar su botón
            if self.about_dialog_ref and not self.about_dialog_ref.isHidden():
                self.about_dialog_ref.set_update_available(update_info)
                logger.info("MainPresenter", "Botón de actualización actualizado en diálogo About")
                
        except Exception as e:
            logger.error("MainPresenter", f"Error actualizando UI de actualización: {e}")
    
    def _on_no_update_detected(self):
        """Maneja la señal cuando no hay actualizaciones disponibles"""
        try:
            self.view.add_system_log("✅ Sistema actualizado - Estás usando la última versión")
        except Exception as e:
            logger.error("MainPresenter", f"Error mostrando mensaje de actualización: {e}")
    
    def _on_version_ignored_notification(self, version: str):
        """Maneja la señal cuando una versión está ignorada"""
        try:
            # Mensaje discreto sin detalles de versión
            self.view.add_system_log("🔕 Actualización disponible")
        except Exception as e:
            logger.error("MainPresenter", f"Error mostrando mensaje de versión ignorada: {e}")
    
    def _on_update_check_error(self, error_msg: str):
        """Maneja errores al verificar actualizaciones"""
        try:
            # Solo mostrar en modo silencioso (automático) para no duplicar con el diálogo
            # En modo manual, el diálogo ya se muestra desde update_checker_presenter
            if "No se pudo conectar" in error_msg:
                logger.warning("MainPresenter", "No se pudo verificar actualizaciones (sin conexión)")
                # No mostrar mensaje al usuario en modo silencioso para no ser intrusivo
            else:
                logger.error("MainPresenter", f"Error verificando actualizaciones: {error_msg}")
        except Exception as e:
            logger.error("MainPresenter", f"Error manejando error de actualización: {e}")
    
    def _on_update_check_started(self):
        """Maneja el inicio de verificación de actualizaciones"""
        try:
            # Si el diálogo About está abierto, deshabilitar su botón
            if self.about_dialog_ref:
                self.about_dialog_ref.set_checking_state(True)
            
            logger.info("MainPresenter", "Iniciando verificación de actualizaciones...")
        except Exception as e:
            logger.error("MainPresenter", f"Error manejando inicio de verificación: {e}")
    
    def _on_update_check_finished(self):
        """Maneja el fin de verificación de actualizaciones"""
        try:
            # Si el diálogo About está abierto, habilitar su botón
            if self.about_dialog_ref:
                self.about_dialog_ref.set_checking_state(False)
            
            logger.info("MainPresenter", "Verificación de actualizaciones finalizada")
        except Exception as e:
            logger.error("MainPresenter", f"Error manejando fin de verificación: {e}")
    
    def _on_update_check_blocked(self, seconds: int):
        """Maneja cuando la verificación es bloqueada por cooldown"""
        try:
            # Si el diálogo About está abierto, bloquear su botón temporalmente
            if self.about_dialog_ref:
                self.about_dialog_ref.set_blocked_state(seconds)
            
            logger.info("MainPresenter", f"Verificación bloqueada por cooldown ({seconds}s)")
        except Exception as e:
            logger.error("MainPresenter", f"Error manejando bloqueo de verificación: {e}")

    def __del__(self):
        """Destructor para asegurar limpieza de recursos."""
        self.cleanup()
