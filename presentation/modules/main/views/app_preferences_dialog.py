"""
Diálogo de preferencias de la aplicación
Interfaz para configurar las preferencias del sistema
Solo m         startup_group = QGroupBox("Configuración de Inicio")       startup_group = QGroupBox("Configuración de Inicio")      startup_group = QGroupBox("Configuración de Inicio")       startup_group = QGroupBox("Configuración de Inicio")neja la UI, la lógica está en AppPreferencesPresenter
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QTabWidget, QWidget, QPushButton, QLabel, QComboBox,
    QGroupBox, QCheckBox, QSpinBox, QDoubleSpinBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from typing import Dict, Any

from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from presentation.modules.main.presenters.app_preferences_presenter import AppPreferencesPresenter
from presentation.widgets.currencyaware_mod.currency_aware_widgets import CurrencyAwareSpinBox, CurrencyAwareLabel


class AppPreferencesDialog(QDialog):
    """Diálogo de preferencias de la aplicación"""
    
    # Señal emitida cuando se guardan las preferencias exitosamente
    preferences_saved = Signal(dict)  # Emite las preferencias guardadas
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Presenter que maneja toda la lógica
        self.presenter = AppPreferencesPresenter(self)
        
        # Widgets de UI (se inicializan en _setup_ui)
        self.tab_widget = None
        self.customer_mode_combo = None
        self.printer_mode_combo = None
        self.theme_combo = None
        
        # Widgets para anticipo por defecto
        self.advance_default_enabled = None
        self.advance_default_percentage = None
        
        # Widgets para anticipo automático mínimo
        self.auto_min_enabled = None
        self.auto_min_amount = None
        self.auto_min_percentage = None
        
        # Widgets para anticipo automático máximo
        self.auto_max_enabled = None
        self.auto_max_amount = None
        self.auto_max_percentage = None
        
        # Widgets para configuración de actualizaciones
        self.update_check_mode = None
        self.update_check_frequency = None
        
        # Widget para modo de generación por defecto
        self.default_generate_mode_combo = None
        
        self.btn_ok = None
        self.btn_cancel = None
        self.btn_reset = None
        
        # Variable para almacenar el tema inicial
        self.initial_theme = None
        
        # Configurar UI
        self._setup_ui()
        self._connect_signals()
        self._load_preferences()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar ventana
        self.setWindowTitle(tr(I18N.App.PREFERENCES_DIALOG_TITLE))
        self.setWindowIcon(QIcon("resources/icons/sys_adm_user.svg"))
        self.setModal(True)
        self.setFixedSize(550, 450)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Título
        title_label = QLabel(tr(I18N.App.PREFERENCES_DIALOG_TITLE))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setContentsMargins(0, 0, 0, 5)
        layout.addWidget(title_label)
        
        # Crear tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumHeight(300)
        self.tab_widget.setMinimumWidth(480)
        
        # Tab 1: Preferencias
        self.tab_widget.addTab(self._create_preferences_tab(), tr(I18N.Prefs.TAB_PREFERENCES))
        
        # Tab 2: Anticipo
        self.tab_widget.addTab(self._create_advance_tab(), tr(I18N.Prefs.TAB_ADVANCE))
        
        layout.addWidget(self.tab_widget)
        
        # Botones
        self._create_buttons(layout)
    
    def _create_preferences_tab(self) -> QWidget:
        """Crea la pestaña de preferencias generales"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # Grupo: Configuración de Inicio (Combina cliente e impresora)
        startup_group = QGroupBox("Configuración de Inicio")
        startup_layout = QFormLayout(startup_group)
        startup_layout.setVerticalSpacing(8)
        
        # Cliente

        self.customer_mode_combo = QComboBox()
        self.customer_mode_combo.addItems([
            tr(I18N.Prefs.OPTION_CLIENT_NORMAL),
            tr(I18N.Prefs.OPTION_CLIENT_OPTIONAL),
            tr(I18N.Prefs.OPTION_CLIENT_DEFAULT)
        ])
        startup_layout.addRow(tr(I18N.Prefs.LABEL_CLIENT_MODE), self.customer_mode_combo)
        
        # Impresora

        self.printer_mode_combo = QComboBox()
        # Las opciones se llenan desde el presenter
        startup_layout.addRow(tr(I18N.Prefs.LABEL_DEFAULT_PRINTER), self.printer_mode_combo)
        
        # Modo de generación por defecto
        self.default_generate_mode_combo = QComboBox()
        self.default_generate_mode_combo.addItem(tr(I18N.Prefs.OPTION_GENERATE_PDF), "pdf")
        self.default_generate_mode_combo.addItem(tr(I18N.Prefs.OPTION_GENERATE_NOTE), "note")
        startup_layout.addRow(tr(I18N.Prefs.LABEL_GENERATE_BTN_MODE), self.default_generate_mode_combo)
        
        layout.addWidget(startup_group)
        
        # Grupo: Tema
        theme_group = QGroupBox(tr(I18N.Prefs.GROUP_THEME))
        theme_layout = QFormLayout(theme_group)
        theme_layout.setVerticalSpacing(8)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            tr(I18N.Prefs.OPTION_THEME_AUTO),
            tr(I18N.Prefs.OPTION_THEME_LIGHT),
            tr(I18N.Prefs.OPTION_THEME_DARK)
        ])
        theme_layout.addRow(tr(I18N.Prefs.LABEL_INTERFACE_THEME), self.theme_combo)
        
        layout.addWidget(theme_group)
        
        # Grupo: Actualizaciones
        updates_group = QGroupBox(tr(I18N.Prefs.GROUP_UPDATES))
        updates_layout = QFormLayout(updates_group)
        updates_layout.setVerticalSpacing(8)
        
        self.update_check_mode = QComboBox()
        self.update_check_mode.addItem(tr(I18N.Prefs.OPTION_UPDATE_AUTO), "auto")
        self.update_check_mode.addItem(tr(I18N.Prefs.OPTION_UPDATE_MANUAL), "manual")
        self.update_check_mode.currentIndexChanged.connect(self._on_update_mode_changed)
        updates_layout.addRow(tr(I18N.Prefs.LABEL_UPDATE_MODE), self.update_check_mode)
        
        self.update_check_frequency = QComboBox()
        self.update_check_frequency.addItem(tr(I18N.Prefs.OPTION_FREQ_AT_START), "startup")
        self.update_check_frequency.addItem(tr(I18N.Prefs.OPTION_FREQ_7_DAYS), "7days")
        self.update_check_frequency.addItem(tr(I18N.Prefs.OPTION_FREQ_15_DAYS), "15days")
        self.update_check_frequency.addItem(tr(I18N.Prefs.OPTION_FREQ_30_DAYS), "30days")
        updates_layout.addRow(tr(I18N.Prefs.LABEL_UPDATE_FREQUENCY), self.update_check_frequency)
        
        layout.addWidget(updates_group)
        
        layout.addStretch()
        return tab
    
    def _on_update_mode_changed(self, index):
        """Maneja el cambio en el modo de actualización"""
        mode = self.update_check_mode.currentData()
        # Habilitar frecuencia solo si está en modo automático
        self.update_check_frequency.setEnabled(mode == "auto")
    
    def _create_advance_tab(self) -> QWidget:
        """Crea la pestaña de configuración de anticipo"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Grupo: Modo de Anticipo
        mode_group = QGroupBox(tr(I18N.Prefs.GROUP_ADVANCE_MODE))
        mode_layout = QFormLayout(mode_group)

        self.advance_mode_combo = QComboBox()
        # Usar claves de traducción para cada opción del modo de anticipo
        self.advance_mode_combo.addItems([
            tr(I18N.Prefs.OPTION_ADVANCE_MODE_0),
            tr(I18N.Prefs.OPTION_ADVANCE_MODE_1),
            tr(I18N.Prefs.OPTION_ADVANCE_MODE_2),
            tr(I18N.Prefs.OPTION_ADVANCE_MODE_3),
            tr(I18N.Prefs.OPTION_ADVANCE_MODE_4),
        ])
        mode_layout.addRow(tr(I18N.Prefs.LABEL_ADVANCE_MODE), self.advance_mode_combo)
        layout.addWidget(mode_group)

        # Grupo: Configuración por defecto
        default_group = QGroupBox(tr(I18N.Prefs.GROUP_ADVANCE_DEFAULT))
        default_layout = QFormLayout(default_group)

        self.advance_default_percentage = QSpinBox()
        self.advance_default_percentage.setRange(1, 100)
        self.advance_default_percentage.setSuffix("%")
        default_layout.addRow(tr(I18N.Prefs.LABEL_ADVANCE_PCT), self.advance_default_percentage)
        layout.addWidget(default_group)

        # Grupo: Anticipo automático para montos bajos
        min_group = QGroupBox(tr(I18N.Prefs.GROUP_ADVANCE_AUTO_MIN))
        min_layout = QGridLayout(min_group)

        self.auto_min_amount = CurrencyAwareSpinBox()
        self.auto_min_amount.setRange(0, 10000000)
        min_layout.addWidget(QLabel(tr(I18N.Prefs.LABEL_ADVANCE_MIN_AMOUNT)), 0, 0)
        min_layout.addWidget(self.auto_min_amount, 0, 1)

        self.auto_min_percentage = QSpinBox()
        self.auto_min_percentage.setRange(1, 100)
        self.auto_min_percentage.setSuffix("%")
        min_layout.addWidget(QLabel(tr(I18N.Prefs.LABEL_ADVANCE_PCT)), 1, 0)
        min_layout.addWidget(self.auto_min_percentage, 1, 1)

        layout.addWidget(min_group)

        # Grupo: Anticipo automático para montos altos
        max_group = QGroupBox(tr(I18N.Prefs.GROUP_ADVANCE_AUTO_MAX))
        max_layout = QGridLayout(max_group)

        self.auto_max_amount = CurrencyAwareSpinBox()
        self.auto_max_amount.setRange(0, 10000000)
        max_layout.addWidget(QLabel(tr(I18N.Prefs.LABEL_ADVANCE_MAX_AMOUNT)), 0, 0)
        max_layout.addWidget(self.auto_max_amount, 0, 1)

        self.auto_max_percentage = QSpinBox()
        self.auto_max_percentage.setRange(1, 100)
        self.auto_max_percentage.setSuffix("%")
        max_layout.addWidget(QLabel(tr(I18N.Prefs.LABEL_ADVANCE_PCT)), 1, 0)
        max_layout.addWidget(self.auto_max_percentage, 1, 1)

        layout.addWidget(max_group)

        # Nota explicativa
        note_label = QLabel(tr(I18N.Prefs.NOTE_ADVANCE_MODE))
        note_label.setWordWrap(True)
        note_label.setStyleSheet("QLabel { color: #888; font-size: 9px; padding: 3px; }")
        layout.addWidget(note_label)

        layout.addStretch()
        return tab
    
    def _create_buttons(self, layout: QVBoxLayout):
        """Crea los botones del diálogo"""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 8, 0, 0)
        
        # Botón Reset
        self.btn_reset = QPushButton(tr(I18N.Prefs.BUTTON_RESET))
        self.btn_reset.setToolTip(tr(I18N.Buttons.TOOLTIP_RESET))
        self.btn_reset.setFixedHeight(30)
        self.btn_reset.setFixedWidth(105)
        
        # Botón Cancel
        self.btn_cancel = QPushButton(tr(I18N.Buttons.CANCEL))
        self.btn_cancel.setFixedHeight(30)
        self.btn_cancel.setFixedWidth(105)
        
        # Botón OK
        self.btn_ok = QPushButton(tr(I18N.Buttons.SAVE))
        self.btn_ok.setDefault(True)
        self.btn_ok.setFixedHeight(30)
        self.btn_ok.setFixedWidth(105)
        
        button_layout.addWidget(self.btn_reset)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_ok)
        button_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Conecta las señales de la UI"""
        # Botones
        self.btn_ok.clicked.connect(self._on_save_clicked)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_reset.clicked.connect(self._on_reset_clicked)

                    
        # Conectar cambio de modo de anticipo para habilitar/deshabilitar campos
        self.advance_mode_combo.currentIndexChanged.connect(self._on_advance_mode_changed)

        # Conectar señales del presenter
        self.presenter.preferences_loaded.connect(self._on_preferences_loaded)
        self.presenter.preferences_saved.connect(self._on_preferences_saved)
    
    def _load_preferences(self):
        """Solicita al presenter que cargue las preferencias"""
        # Cargar opciones de impresora inmediatamente
        self._populate_printer_combo()
        
        # Cargar valores en la UI
        self._load_values_to_ui(self.presenter.current_preferences)
    
    def _on_preferences_loaded(self, preferences: Dict[str, Any]):
        """Maneja cuando el presenter carga las preferencias"""
        # Cargar opciones de impresora
        self._populate_printer_combo()
        
        # Cargar valores en la UI
        self._load_values_to_ui(preferences)
    
    def _populate_printer_combo(self):
        """Llena el combo de impresoras con datos del presenter"""
        self.printer_mode_combo.clear()
        
        printer_options = self.presenter.get_printer_display_options()
        for option in printer_options:
            self.printer_mode_combo.addItem(option["text"], option["value"])
    
    def _load_values_to_ui(self, preferences: Dict[str, Any]):
        """Carga los valores de preferencias en los widgets de UI"""
        # Modo de cliente
        customer_mode = self.presenter.get_customer_mode_display()
        self.customer_mode_combo.setCurrentIndex(customer_mode)

        # Impresora por defecto
        current_printer = self.presenter.get_current_printer_selection()
        for i in range(self.printer_mode_combo.count()):
            if str(self.printer_mode_combo.itemData(i)) == str(current_printer):
                self.printer_mode_combo.setCurrentIndex(i)
                break

        # Tema
        theme_index = self.presenter.get_theme_display()
        self.theme_combo.setCurrentIndex(theme_index)

        # Almacenar el tema inicial para detectar cambios
        theme_names = ["auto", "light", "dark"]
        self.initial_theme = theme_names[theme_index] if theme_index < len(theme_names) else "auto"

        # Cargar modo de anticipo usando el método del presenter
        advance_mode_index = self.presenter.get_advance_mode_display()
        self.advance_mode_combo.setCurrentIndex(advance_mode_index)

        # Configuración por defecto de anticipo
        advance_default = self.presenter.get_advance_default_settings()
        self.advance_default_percentage.setValue(advance_default["percentage"])

        # Anticipo automático mínimo
        auto_min = self.presenter.get_advance_auto_minimum_settings()
        self.auto_min_amount.setValue(auto_min.get("amount", 100000))
        self.auto_min_percentage.setValue(auto_min.get("percentage", 30))

        # Anticipo automático máximo
        auto_max = self.presenter.get_advance_auto_maximum_settings()
        self.auto_max_amount.setValue(auto_max.get("amount", 500000))
        self.auto_max_percentage.setValue(auto_max.get("percentage", 50))
        
        # Configuración de actualizaciones
        update_mode = self.presenter.get_update_check_mode()
        index = self.update_check_mode.findData(update_mode)
        if index >= 0:
            self.update_check_mode.setCurrentIndex(index)
        
        update_frequency = self.presenter.get_update_check_frequency()
        index = self.update_check_frequency.findData(update_frequency)
        if index >= 0:
            self.update_check_frequency.setCurrentIndex(index)
        
        # Actualizar estado de frecuencia según el modo
        self.update_check_frequency.setEnabled(update_mode == "auto")
        
        # Modo de generación por defecto
        default_generate_mode = self.presenter.get_default_generate_mode()
        index = self.default_generate_mode_combo.findData(default_generate_mode)
        if index >= 0:
            self.default_generate_mode_combo.setCurrentIndex(index)
        
        # Aplicar reglas de habilitación/deshabilitación según el modo
        self.presenter.handle_advance_mode_changed(advance_mode_index)
    
    def _on_advance_mode_changed(self):
        """Delega al presenter el manejo del cambio de modo de anticipo"""
        mode_index = self.advance_mode_combo.currentIndex()
        self.presenter.handle_advance_mode_changed(mode_index)

    def _collect_ui_values(self) -> Dict[str, Any]:
        """Recolecta los valores actuales de la UI"""
        # Modo de cliente
        customer_mode_index = self.customer_mode_combo.currentIndex()
        customer_modes = ["normal", "optional", "default"]
        customer_mode = customer_modes[customer_mode_index] if customer_mode_index < len(customer_modes) else "normal"

        # Impresora por defecto
        printer_data = self.printer_mode_combo.currentData()

        # Tema
        theme_index = self.theme_combo.currentIndex()
        themes = ["auto", "light", "dark"]
        theme = themes[theme_index] if theme_index < len(themes) else "auto"

        # Nuevo: modo de anticipo - USAR ÍNDICE NUMÉRICO
        advance_mode_index = self.advance_mode_combo.currentIndex()
        # No convertir a cadena, usar directamente el índice numérico

        # Anticipo por defecto
        advance_default = {
            "percentage": self.advance_default_percentage.value()
        }

        # Anticipo automático mínimo
        advance_auto_minimum = {
            "amount": self.auto_min_amount.value(),
            "percentage": self.auto_min_percentage.value()
        }

        # Anticipo automático máximo
        advance_auto_maximum = {
            "amount": self.auto_max_amount.value(),
            "percentage": self.auto_max_percentage.value()
        }
        
        # Configuración de actualizaciones
        update_mode = self.update_check_mode.currentData()
        update_frequency = self.update_check_frequency.currentData()

        # Modo de generación por defecto
        default_generate_mode = self.default_generate_mode_combo.currentData()

        return {
            "customer_mode": customer_mode,
            "default_printer_id": printer_data,
            "theme": theme,
            "advance_mode_index": advance_mode_index,
            "advance_default": advance_default,
            "advance_auto_minimum": advance_auto_minimum,
            "advance_auto_maximum": advance_auto_maximum,
            "update_check_mode": update_mode,
            "update_check_frequency": update_frequency,
            "default_generate_mode": default_generate_mode,
        }
    
    def _on_save_clicked(self):
        """Maneja el clic en el botón Guardar"""

        # Recolectar datos de la UI
        preferences_data = self._collect_ui_values()

        # =========================
        # Detectar cambios de tema
        # =========================
        new_theme_index = self.theme_combo.currentIndex()
        theme_names = ["auto", "light", "dark"]
        new_theme = theme_names[new_theme_index] if new_theme_index < len(theme_names) else "auto"

        theme_changed = self.initial_theme != new_theme

        restart_required = theme_changed

        # Guardar preferencias
        success = self.presenter.save_preferences(preferences_data)

        if not success:
            return

        # =========================
        # Reinicio obligatorio
        # =========================
        if restart_required:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                tr(I18N.Prefs.DIALOG_RESTART_REQUIRED_TITLE),
                f"La aplicación se reiniciará automáticamente\n"
                "para aplicar los cambios correctamente.",
                QMessageBox.StandardButton.Ok
            )

            self._restart_application()
            return

        # Emitir señal normal
        self.preferences_saved.emit(preferences_data)

        # Cerrar diálogo
        self.accept()
    
    def _on_reset_clicked(self):
        """Maneja el clic en el botón Reset"""
        success = self.presenter.reset_preferences()
        
        if success:
            # Las preferencias se recargarán automáticamente via señales
            pass
    
    def _on_preferences_saved(self, preferences: Dict[str, Any]):
        """Maneja cuando se guardan las preferencias exitosamente"""
        # Emitir nuestra propia señal para notificar a la ventana padre
        self.preferences_saved.emit(preferences)
    
    def _restart_application(self):
        """Reinicia la aplicación"""
        try:
            import sys
            import os
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QTimer
            
            logger.debug("AppPreferencesDialog", "Reiniciando aplicación para aplicar cambios de tema...")
            
            # Obtener argumentos del programa
            if getattr(sys, 'frozen', False):
                # Aplicación empaquetada
                program_path = sys.executable
                args = [program_path]
            else:
                # Aplicación en desarrollo
                program_path = sys.executable
                args = [program_path] + sys.argv
            
            # Programar el reinicio con un pequeño delay para permitir que se cierre el diálogo
            def do_restart():
                try:
                    import subprocess
                    # Usar subprocess.Popen para reiniciar en proceso separado
                    subprocess.Popen(args)
                    
                    # Cerrar la aplicación actual
                    app = QApplication.instance()
                    if app:
                        app.quit()
                        
                except Exception as restart_error:
                    logger.error("AppPreferencesDialog", f"Error en subprocess restart: {restart_error}")
                    # Fallback a os.execl
                    try:
                        if getattr(sys, 'frozen', False):
                            os.execl(program_path, program_path)
                        else:
                            os.execl(program_path, program_path, *sys.argv)
                    except Exception as exec_error:
                        logger.error("AppPreferencesDialog", f"Error en exec restart: {exec_error}")
                        # Si todo falla, solo cerrar la aplicación
                        app = QApplication.instance()
                        if app:
                            app.quit()
            
            # Programar el reinicio después de un breve delay
            QTimer.singleShot(100, do_restart)
                
        except Exception as e:
            logger.error("AppPreferencesDialog", f"Error reiniciando aplicación: {e}")
            # En caso de error, solo cerrar la aplicación
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                app.quit()