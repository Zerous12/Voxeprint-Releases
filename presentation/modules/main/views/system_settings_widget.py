"""
Vista de Ajustes del Sistema
Permite configurar los parámetros del sistema, empresa, impuestos, etc.
"""
from presentation.widgets.currencyaware_mod.currency_aware_widgets import CurrencyAwareLabel
from presentation.widgets.crop_tool_mod.logo_crop_tool import LogoCropDialog
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                               QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, 
                               QPushButton, QGridLayout, QComboBox,
                               QCheckBox, QTextEdit, QTabWidget, QMessageBox,
                               QFileDialog, QSpacerItem, QSizePolicy,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QFrame, QAbstractItemView, QProgressBar,
                               QColorDialog)
from PySide6.QtCore import Signal, Qt, QSize, QTimer, QRegularExpression
from PySide6.QtGui import QFont, QIcon, QPixmap, QCursor, QColor, QRegularExpressionValidator
from typing import Dict, Any
import os
import shutil
import random
import tempfile
from PIL import Image
from core.utils.path_helper import logos_dir, build_resource_path, logs_dir
from core.utils.logger import VoxeprintLogger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N

logger = VoxeprintLogger()


class SystemSettingsWidget(QWidget):
    """Widget para gestionar todas las configuraciones del sistema"""
    
    # Señales
    settings_changed = Signal(dict)  # Emitida cuando cambian las configuraciones
    save_requested = Signal(dict)   # Emitida cuando se solicita guardar
    open_log_requested = Signal()   # Emitida cuando se solicita abrir el log
    language_zip_requested = Signal()  # Emitida cuando se solicita importar idioma ZIP
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_data = {}
        self.is_editing = False
        self.current_logo_path = None
        self._original_tab_index = None  # Para recordar el tab al entrar en modo edición
        self.setup_ui()
        self.setup_connections()
        
        # Asegurar que los campos inicien bloqueados
        self.disable_editing()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(1)

        # Reducir tamaño del indicador de todos los QCheckBox del widget
        self.setStyleSheet("QCheckBox::indicator { width: 12px; height: 12px; border-radius: 9px; }")

        # Título de la sección
        title_label = QLabel(tr(I18N.Systemsettings.SECTION_TITLE))
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Tab widget para organizar las configuraciones
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("systemTabWidget")
        self.tab_widget.setMinimumHeight(500)  # ✅ Aumentar altura mínima para mejor disposición
        self.tab_widget.setStyleSheet("""                                    
                                    QTabWidget > QTabBar::tab {
                                    font-weight: bold;
                                    border: 2px solid transparent;                                     
                                    padding: 6px;
                                    border-top-left-radius: 5px;
                                    border-top-right-radius: 5px;}

                                    QTabWidget > QTabBar::tab:selected {	
                                        border-top-color: #00aaff;
                                        min-width: 120px;
                                    }
                                    QTabWidget > QTabBar::tab:hover {	
                                        border-top-color: #ffaa00;}""")
        
        # Tab 1: Información de Empresa
        self.company_tab = self.create_company_tab()
        self.tab_widget.addTab(self.company_tab, tr(I18N.Systemsettings.TAB_COMPANY))
        
        # Tab 2: Configuraciones de Costos
        self.costs_tab = self.create_costs_tab()
        self.tab_widget.addTab(self.costs_tab, tr(I18N.Systemsettings.TAB_COSTS))
        
        # Tab 3: Configuraciones de PDF
        self.pdf_tab = self.create_pdf_tab()
        self.tab_widget.addTab(self.pdf_tab, tr(I18N.Systemsettings.TAB_PDF))

        # Tab 4: Configuraciones de Nota de Precios
        self.note_tab = self.create_note_tab()
        self.tab_widget.addTab(self.note_tab, tr(I18N.Systemsettings.TAB_NOTE))

        # Tab 5: Idioma y Región
        self.language_tab = self.create_language_tab()
        self.tab_widget.addTab(self.language_tab, tr(I18N.Systemsettings.TAB_LANGUAGE))

        # Tab 6: Configuraciones del Sistema
        self.system_tab = self.create_system_tab()
        self.tab_widget.addTab(self.system_tab, tr(I18N.Systemsettings.TAB_SYSTEM))

        # Tab 7: Base de Datos
        self.database_tab = self.create_database_tab()
        self.tab_widget.addTab(self.database_tab, tr(I18N.Systemsettings.TAB_DATABASE))

        # Widget para los botones de control (debajo del tab widget)
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 15, 0, 0)
        buttons_layout.setSpacing(20)
        
        # Contenedor para botones de control (izquierda)
        control_buttons_widget = QWidget()
        control_buttons_layout = QHBoxLayout(control_buttons_widget)
        control_buttons_layout.setContentsMargins(10, 0, 10, 0)
        control_buttons_layout.setSpacing(10)
        
        # Botón para desbloquear (con icono)
        self.btn_edit = QPushButton(tr(I18N.Systemsettings.BUTTON_UNLOCK))
        self.btn_edit.setObjectName("unlockButton")
        self.btn_edit.setFixedHeight(33)
        self.btn_edit.setFixedWidth(130)
        unlock_icon = QIcon("resources/icons/sys_unlock_alt.svg")
        self.btn_edit.setIcon(unlock_icon)
        self.btn_edit.setIconSize(QSize(16, 16))
        self.btn_edit.setStyleSheet("""
            QPushButton {
                color: #e6fdff;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                background-color: #be7dff;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #aa00ff;
                border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #ffffff;
                background-color: #ffaa00;
                border: 1px solid #69cdff;
            }
        """)
        
        # Botón para refrescar (con icono)
        self.btn_reload = QPushButton(tr(I18N.Systemsettings.BUTTON_REFRESH))
        self.btn_reload.setObjectName("refreshButton")
        self.btn_reload.setFixedHeight(33)
        self.btn_reload.setFixedWidth(120)
        refresh_icon = QIcon("resources/icons/sys_refresh.svg")
        self.btn_reload.setIcon(refresh_icon)
        self.btn_reload.setIconSize(QSize(16, 16))
        self.btn_reload.setStyleSheet("""
            QPushButton {
                color: #e6fdff;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                background-color: #46aac4;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #009dc4;
                border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #ffffff;
                background-color: #ffaa00;
                border: 1px solid #69cdff;
            }
        """)
        
        # Agregar botones de control al contenedor
        control_buttons_layout.addWidget(self.btn_edit)
        control_buttons_layout.addWidget(self.btn_reload)
        control_buttons_layout.addStretch()
        
        # Contenedor para botones de acción (derecha)
        action_buttons_widget = QWidget()
        action_buttons_layout = QHBoxLayout(action_buttons_widget)
        action_buttons_layout.setContentsMargins(10, 0, 10, 0)
        action_buttons_layout.setSpacing(10)
        
        # Botón guardar
        self.btn_save = QPushButton(tr(I18N.Systemsettings.BUTTON_SAVE_CHANGES))
        self.btn_save.setObjectName("saveButton")
        self.btn_save.setFixedHeight(33)
        self.btn_save.setFixedWidth(150)
        self.btn_save.setEnabled(False)
        self.btn_save.setVisible(False)  # Inicialmente invisible
        self.btn_save.setStyleSheet("""
            QPushButton {
                color: #e6fdff;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                background-color: #6cb86c;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #00aa00;
                border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #ffffff;
                background-color: #ffaa00;
                border: 1px solid #69cdff;
            }
            QPushButton:disabled {
                color: #d5d5d5;
                background-color: #6a6a6a;
                border: 1px solid #00aa00;
            }
        """)
        
        # Botón cancelar
        self.btn_cancel = QPushButton(tr(I18N.Buttons.CANCEL))
        self.btn_cancel.setObjectName("cancelButton")
        self.btn_cancel.setFixedHeight(33)
        self.btn_cancel.setFixedWidth(110)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setVisible(False)  # Inicialmente invisible
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                color: #e6fdff;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                background-color: #f09292;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #be0000;
                border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #ffffff;
                background-color: #ff0000;
                border: 1px solid #69cdff;
            }
            QPushButton:disabled {
                color: #d5d5d5;
                background-color: #6a6a6a;
                border: 1px solid #00aa00;
            }
        """)
        
        # Agregar botones de acción al contenedor
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(self.btn_save)
        action_buttons_layout.addWidget(self.btn_cancel)
        
        # Agregar ambos contenedores al layout principal de botones
        buttons_layout.addWidget(control_buttons_widget)
        buttons_layout.addWidget(action_buttons_widget)
               
        # Agregar todo al layout principal
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(buttons_widget)

    def create_company_tab(self) -> QWidget:
        """Crea el tab de información de empresa"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grupo: Información de la Empresa
        company_group = QGroupBox(tr(I18N.Systemsettings.LABEL_COMPANY_INFO))
        company_group.setFixedHeight(190)
        company_layout = QGridLayout(company_group)
        
        # Campos de empresa
        self.company_fields = {}
        
        fields = [
            ("company_name", tr(I18N.Systemsettings.LABEL_COMPANY_NAME), "text"),
            ("company_address", tr(I18N.Systemsettings.LABEL_ADDRESS), "text"),
            ("company_city", tr(I18N.Systemsettings.LABEL_CITY), "text"),
            ("company_phone", tr(I18N.Systemsettings.LABEL_PHONE), "text"),
            ("company_email", tr(I18N.Systemsettings.LABEL_EMAIL), "text"),
            ("company_website", tr(I18N.Systemsettings.LABEL_WEBSITE), "text"),
        ]
        
        for i, (key, label, field_type) in enumerate(fields):
            company_layout.addWidget(QLabel(label), i, 0)
            
            if field_type == "text":
                field = QLineEdit()
                field.setReadOnly(True)
            
            self.company_fields[key] = field
            company_layout.addWidget(field, i, 1)
        
        layout.addWidget(company_group)
        
        # Grupo: Gestión de Logo
        logo_group = QGroupBox(tr(I18N.Systemsettings.GROUP_LOGO_MGMT))
        logo_group.setMinimumHeight(240)
        logo_group.setMaximumHeight(290)
        logo_group.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        logo_layout = QGridLayout(logo_group)
        
        # Label para mostrar el logo actual
        logo_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_CURRENT_LOGO)), 0, 0)
        self.current_logo_label = QLabel(tr(I18N.Systemsettings.LABEL_NO_LOGO))
        self.current_logo_label.setStyleSheet("QLabel { color: #7c8005; font-style: italic; }")
        logo_layout.addWidget(self.current_logo_label, 0, 1)
        
        # Contenedor para los dos QLabels superpuestos (actual y vista previa)
        logo_display_container = QWidget()
        logo_display_container.setFixedSize(480, 120)
        
        # Layout absoluto para superposición
        logo_display_layout = QVBoxLayout(logo_display_container)
        logo_display_layout.setContentsMargins(0, 0, 0, 0)
        
        # QLabel para logo actual (visible cuando no está en modo edición)
        self.current_logo_display = QLabel(logo_display_container)
        self.current_logo_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_logo_display.setFixedSize(480, 120)
        self.current_logo_display.setStyleSheet("""
            QLabel {
                border: 2px solid #4CAF50;
                background-color: #f8f8f8;
                text-align: center;
                color: #800580;
                border-radius: 5px;
            }
        """)
        self.current_logo_display.setText("Sin logo\n(720x210 px)")
        
        # QLabel para vista previa (visible cuando está en modo edición)
        self.logo_preview = QLabel(logo_display_container)
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview.setFixedSize(480, 120) 
        self.logo_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #FF9800;
                background-color: #fff8e1;
                text-align: center;
                color: #7c8005;
                border-radius: 5px;
            }
        """)
        self.logo_preview.setText("Seleccione un logo\n(720x210 px)")
        self.logo_preview.setVisible(False)  # Inicialmente oculto
        
        # Asegurar que el logo actual esté visible inicialmente
        self.current_logo_display.setVisible(True)
        
        # Posicionar los QLabels en la misma ubicación (superpuestos)
        self.current_logo_display.move(0, 0)
        self.logo_preview.move(0, 0)
        logo_layout.addWidget(logo_display_container, 1, 0, 1, 2)
        logo_buttons_layout = QHBoxLayout()
        
        self.select_logo_btn = QPushButton(tr(I18N.Systemsettings.BUTTON_UPLOAD_LOGO))
        self.select_logo_btn.setToolTip(tr(I18N.Systemsettings.TOOLTIP_SELECT_LOGO))
        self.select_logo_btn.setMinimumSize(110, 26)  # 10px más ancho, 30px de alto
        self.select_logo_btn.setStyleSheet("""
            QPushButton {
                color: #e6fdff;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                background-color: #46aa8f;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #00aa7f;
                border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #ffffff;
                background-color: #ffaa00;
                border: 1px solid #69cdff;
            }
            QPushButton:disabled {
                color: #d5d5d5;
                background-color: transparent;
                border: 1px solid #bcbcbc;
            }
        """)
        self.select_logo_btn.clicked.connect(self.select_logo_file)
        
        self.remove_logo_btn = QPushButton(tr(I18N.Systemsettings.BUTTON_REMOVE_LOGO))
        self.remove_logo_btn.setToolTip(tr(I18N.Systemsettings.TOOLTIP_REMOVE_LOGO))
        self.remove_logo_btn.setMinimumSize(110, 26)  # 10px más ancho, 30px de alto
        self.remove_logo_btn.setStyleSheet("""
            QPushButton {
                color: #e6fdff;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                background-color: #f09292;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #be0000;
                border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #ffffff;
                background-color: #ff0000;
                border: 1px solid #69cdff;
            }
            QPushButton:disabled {
                color: #d5d5d5;
                background-color: transparent;
                border: 1px solid #bcbcbc;
            }
        """)
        self.remove_logo_btn.clicked.connect(self.remove_logo_file)
        self.remove_logo_btn.setEnabled(False)
        
        logo_buttons_layout.addWidget(self.select_logo_btn)
        logo_buttons_layout.addWidget(self.remove_logo_btn)
        logo_buttons_layout.addStretch(8)        
        logo_layout.addLayout(logo_buttons_layout, 3, 0, 1, 2)  
        
        # Información sobre requisitos del logo
        requirements_label = QLabel(tr(I18N.Systemsettings.LABEL_LOGO_REQUIREMENTS))
        requirements_label.setFixedHeight(40)
        requirements_label.setStyleSheet("QLabel { color: #9db5bf; font-size: 11px; }")
        logo_layout.addWidget(requirements_label, 4, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)
        
         # Agregar grupo de logo al layout principal del tab
        
        layout.addWidget(logo_group)
        
        layout.addStretch()
        
        return tab
    
    def create_costs_tab(self) -> QWidget:
        """Crea el tab de configuraciones de costos"""
        from PySide6.QtWidgets import QScrollArea

        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(10)
        layout.setContentsMargins(6, 6, 6, 6)

        # ── GroupBox 1: Tarifas Base ──────────────────────────────────────────
        costs_group = QGroupBox(tr(I18N.Systemsettings.GROUP_BASE_RATES))
        costs_layout = QGridLayout(costs_group)

        self.cost_fields = {}
        self.cost_labels = {}

        cost_configs = [
            ("electricity_rate", tr(I18N.Systemsettings.LABEL_ELECTRICITY_RATE), "double", 0, 99999, 265.0),
            ("default_failure_margin", tr(I18N.Systemsettings.LABEL_DEFAULT_FAILURE_MARGIN), "double", 0, 50, 5),
            ("default_profit_margin", tr(I18N.Systemsettings.LABEL_DEFAULT_PROFIT_MARGIN), "double", 0, 100, 35),
            ("tax_rate", tr(I18N.Systemsettings.LABEL_TAX_RATE), "double", 0, 50, 10),
        ]

        # Filas reales en el grid: electricity_rate→0, peak_multiplier→1,
        # default_failure_margin→2, default_profit_margin→3,
        # commission_tax_shield→4, tax_rate→5
        grid_rows = [0, 2, 3, 5]

        _cost_tooltips = {
            "electricity_rate": tr(I18N.Systemsettings.TOOLTIP_ELECTRICITY_RATE),
            "default_failure_margin": tr(I18N.Systemsettings.TOOLTIP_DEFAULT_FAILURE_MARGIN),
            "default_profit_margin": tr(I18N.Systemsettings.TOOLTIP_DEFAULT_PROFIT_MARGIN),
            "tax_rate": tr(I18N.Systemsettings.TOOLTIP_TAX_RATE),
        }

        for i, (key, label_template, field_type, min_val, max_val, default) in enumerate(cost_configs):
            if "{symbol}" in label_template:
                label_widget = CurrencyAwareLabel(label_template)
                self.cost_labels[key] = label_widget
            else:
                label_widget = QLabel(label_template)

            if key in _cost_tooltips:
                label_widget.setToolTip(_cost_tooltips[key])

            costs_layout.addWidget(label_widget, grid_rows[i], 0)

            if field_type == "double":
                field = QDoubleSpinBox()
                field.setRange(min_val, max_val)

                if key == "electricity_rate":
                    from core.utils.currency_helper import CurrencyHelper
                    current_currency = CurrencyHelper.get_current_currency()
                    decimals = CurrencyHelper.get_decimals(current_currency)
                    field.setDecimals(decimals)
                else:
                    field.setDecimals(0)

                field.setValue(default)
                field.setEnabled(False)
                if key in _cost_tooltips:
                    field.setToolTip(_cost_tooltips[key])

            self.cost_fields[key] = field
            costs_layout.addWidget(field, grid_rows[i], 1)

        # Factor de corrección eléctrica
        lbl_peak = QLabel(tr(I18N.Systemsettings.LABEL_ELECT_CORRECTION))
        lbl_peak.setToolTip(tr(I18N.Systemsettings.TOOLTIP_ELECT_CORRECTION))
        costs_layout.addWidget(lbl_peak, 1, 0)
        self.electricity_peak_multiplier = QDoubleSpinBox()
        self.electricity_peak_multiplier.setRange(1.0, 5.0)
        self.electricity_peak_multiplier.setDecimals(2)
        self.electricity_peak_multiplier.setSingleStep(0.1)
        self.electricity_peak_multiplier.setValue(1.6)
        self.electricity_peak_multiplier.setEnabled(False)
        self.electricity_peak_multiplier.setToolTip(tr(I18N.Systemsettings.TOOLTIP_ELECT_CORRECTION))
        self.electricity_peak_multiplier.valueChanged.connect(self._on_peak_multiplier_changed)
        costs_layout.addWidget(self.electricity_peak_multiplier, 1, 1)

        # Blindar Comisión
        self.lbl_shield = QLabel(tr(I18N.Systemsettings.LABEL_COMMISSION_SHIELD))
        costs_layout.addWidget(self.lbl_shield, 4, 0)
        self.commission_tax_shield = QCheckBox(tr(I18N.Systemsettings.CHECKBOX_COMMISSION_SHIELD))
        self.commission_tax_shield.setEnabled(False)
        costs_layout.addWidget(self.commission_tax_shield, 4, 1)

        layout.addWidget(costs_group)

        # ── GroupBox 2: Gastos Fijos del Negocio ─────────────────────────────
        overhead_group = QGroupBox(tr(I18N.Systemsettings.GROUP_FIXED_COSTS))
        overhead_layout = QGridLayout(overhead_group)

        from core.utils.currency_helper import CurrencyHelper
        _oh_currency = CurrencyHelper.get_current_currency()
        _oh_decimals = CurrencyHelper.get_decimals(_oh_currency)

        _overhead_fields = [
            ("overhead_rent",       tr(I18N.Systemsettings.LABEL_OVERHEAD_RENT),
             tr(I18N.Systemsettings.TOOLTIP_OVERHEAD_RENT)),
            ("overhead_water",      tr(I18N.Systemsettings.LABEL_OVERHEAD_WATER),
             tr(I18N.Systemsettings.TOOLTIP_OVERHEAD_WATER)),
            ("overhead_internet",   tr(I18N.Systemsettings.LABEL_OVERHEAD_INTERNET),
             tr(I18N.Systemsettings.TOOLTIP_OVERHEAD_INTERNET)),
            ("overhead_accounting", tr(I18N.Systemsettings.LABEL_OVERHEAD_ACCOUNTING),
             tr(I18N.Systemsettings.TOOLTIP_OVERHEAD_ACCOUNTING)),
            ("overhead_salary",     tr(I18N.Systemsettings.LABEL_OVERHEAD_SALARY),
             tr(I18N.Systemsettings.TOOLTIP_OVERHEAD_SALARY)),
            ("overhead_transport",  tr(I18N.Systemsettings.LABEL_OVERHEAD_TRANSPORT),
             tr(I18N.Systemsettings.TOOLTIP_OVERHEAD_TRANSPORT)),
            ("overhead_other",      tr(I18N.Systemsettings.LABEL_OVERHEAD_OTHER),
             tr(I18N.Systemsettings.TOOLTIP_OVERHEAD_OTHER)),
        ]

        for i, (key, lbl_tmpl, tooltip) in enumerate(_overhead_fields):
            lbl = CurrencyAwareLabel(lbl_tmpl)
            lbl.setToolTip(tooltip)
            overhead_layout.addWidget(lbl, i, 0)
            spin = QDoubleSpinBox()
            spin.setRange(0.0, 99_999_999.0)
            spin.setDecimals(_oh_decimals)
            spin.setValue(0.0)
            spin.setEnabled(False)
            spin.setToolTip(tooltip)
            setattr(self, f"spin_{key}", spin)
            overhead_layout.addWidget(spin, i, 1)

        # Separador visual
        _sep = QFrame()
        _sep.setFrameShape(QFrame.Shape.HLine)
        _sep.setStyleSheet("QFrame { color: #444; }")
        overhead_layout.addWidget(_sep, len(_overhead_fields), 0, 1, 2)

        # Total mensual
        overhead_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_OVERHEAD_MONTHLY_TOTAL)), len(_overhead_fields) + 1, 0)
        self.lbl_overhead_monthly_total = QLabel("—")
        self.lbl_overhead_monthly_total.setStyleSheet("QLabel { font-weight: bold; color: #64B5F6; }")
        overhead_layout.addWidget(self.lbl_overhead_monthly_total, len(_overhead_fields) + 1, 1)

        layout.addWidget(overhead_group)

        # Timer debounce para recalcular overhead en tiempo real (~400 ms)
        # Se crea aquí porque el GroupBox 3 necesita conectarse a él
        self._overhead_recalc_timer = QTimer(self)
        self._overhead_recalc_timer.setSingleShot(True)
        self._overhead_recalc_timer.setInterval(400)
        self._overhead_recalc_timer.timeout.connect(self._recalc_overhead_display)

        # ── GroupBox 3: Parámetros de Operación ──────────────────────────────
        params_group = QGroupBox(tr(I18N.Systemsettings.GROUP_OPERATION_PARAMS))
        params_layout = QGridLayout(params_group)

        _lbl_hours_day = QLabel(tr(I18N.Systemsettings.LABEL_HOURS_DAY))
        _lbl_hours_day.setToolTip(tr(I18N.Systemsettings.TOOLTIP_HOURS_DAY))
        params_layout.addWidget(_lbl_hours_day, 0, 0)
        self.spin_overhead_hours_per_day = QSpinBox()
        self.spin_overhead_hours_per_day.setRange(1, 24)
        self.spin_overhead_hours_per_day.setValue(12)
        self.spin_overhead_hours_per_day.setEnabled(False)
        self.spin_overhead_hours_per_day.setToolTip(tr(I18N.Systemsettings.TOOLTIP_HOURS_DAY))
        params_layout.addWidget(self.spin_overhead_hours_per_day, 0, 1)

        _lbl_days_month = QLabel(tr(I18N.Systemsettings.LABEL_DAYS_MONTH))
        _lbl_days_month.setToolTip(tr(I18N.Systemsettings.TOOLTIP_DAYS_MONTH))
        params_layout.addWidget(_lbl_days_month, 1, 0)
        self.spin_overhead_days_per_month = QSpinBox()
        self.spin_overhead_days_per_month.setRange(1, 31)
        self.spin_overhead_days_per_month.setValue(30)
        self.spin_overhead_days_per_month.setEnabled(False)
        self.spin_overhead_days_per_month.setToolTip(tr(I18N.Systemsettings.TOOLTIP_DAYS_MONTH))
        params_layout.addWidget(self.spin_overhead_days_per_month, 1, 1)

        # ── Impresoras activas ───────────────────────────────────────────────
        _lbl_printers = QLabel(tr(I18N.Systemsettings.LABEL_ACTIVE_PRINTERS))
        _lbl_printers.setToolTip(tr(I18N.Systemsettings.TOOLTIP_ACTIVE_PRINTERS_LBL))
        params_layout.addWidget(_lbl_printers, 2, 0)

        # Contenedor horizontal: combo modo + spinbox manual + label BD
        _printers_container = QWidget()
        _printers_layout = QHBoxLayout(_printers_container)
        _printers_layout.setContentsMargins(0, 0, 0, 0)
        _printers_layout.setSpacing(6)

        self.combo_overhead_printers_mode = QComboBox()
        self.combo_overhead_printers_mode.addItem(tr(I18N.Systemsettings.COMBO_AUTO_BD), "auto")
        self.combo_overhead_printers_mode.addItem(tr(I18N.Systemsettings.COMBO_MANUAL), "manual")
        self.combo_overhead_printers_mode.setEnabled(False)
        self.combo_overhead_printers_mode.setToolTip(tr(I18N.Systemsettings.TOOLTIP_PRINTERS_MODE_COMBO))
        _printers_layout.addWidget(self.combo_overhead_printers_mode)

        self.spin_overhead_active_printers = QSpinBox()
        self.spin_overhead_active_printers.setRange(1, 99)
        self.spin_overhead_active_printers.setValue(1)
        self.spin_overhead_active_printers.setEnabled(False)
        self.spin_overhead_active_printers.setVisible(False)
        self.spin_overhead_active_printers.setToolTip(tr(I18N.Systemsettings.TOOLTIP_ACTIVE_PRINTERS_SPIN))
        _printers_layout.addWidget(self.spin_overhead_active_printers)

        self.lbl_overhead_printers_count = QLabel("")
        self.lbl_overhead_printers_count.setStyleSheet("QLabel { color: #64B5F6; }")
        _printers_layout.addWidget(self.lbl_overhead_printers_count)
        _printers_layout.addStretch()

        params_layout.addWidget(_printers_container, 2, 1)

        # Conectar cambio de modo para mostrar/ocultar spinbox
        self.combo_overhead_printers_mode.currentIndexChanged.connect(
            self._on_overhead_printers_mode_changed
        )

        _lbl_monthly_hours = QLabel(tr(I18N.Systemsettings.LABEL_MONTHLY_HOURS))
        _lbl_monthly_hours.setToolTip(tr(I18N.Systemsettings.TOOLTIP_MONTHLY_HOURS))
        params_layout.addWidget(_lbl_monthly_hours, 3, 0)
        self.lbl_overhead_monthly_hours = QLabel(f"360 {tr(I18N.Systemsettings.UNIT_H_MONTH)}")
        self.lbl_overhead_monthly_hours.setStyleSheet("QLabel { color: #64B5F6; }")
        self.lbl_overhead_monthly_hours.setToolTip(tr(I18N.Systemsettings.TOOLTIP_MONTHLY_HOURS))
        params_layout.addWidget(self.lbl_overhead_monthly_hours, 3, 1)

        layout.addWidget(params_group)

        # ── GroupBox 4: Calculadora de Overhead ──────────────────────────────
        calc_group = QGroupBox(tr(I18N.Systemsettings.GROUP_OVERHEAD_CALC))
        calc_layout = QGridLayout(calc_group)

        calc_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_OVERHEAD_PER_HOUR_LBL)), 0, 0)
        self.lbl_overhead_per_hour = QLabel("—")
        self.lbl_overhead_per_hour.setStyleSheet(
            "QLabel { font-weight: bold; font-size: 14px; color: #64B5F6; }"
        )
        calc_layout.addWidget(self.lbl_overhead_per_hour, 0, 1)

        _calc_info = QLabel(tr(I18N.Systemsettings.LABEL_OVERHEAD_CALC_INFO))
        _calc_info.setStyleSheet("QLabel { color: #888; font-size: 9px; }")
        _calc_info.setWordWrap(True)
        calc_layout.addWidget(_calc_info, 1, 0, 1, 2)

        layout.addWidget(calc_group)
        layout.addStretch()

        # Conectar spinboxes de overhead al timer
        for _key, _, _tt in _overhead_fields:
            getattr(self, f"spin_{_key}").valueChanged.connect(
                self._overhead_recalc_timer.start
            )
        self.spin_overhead_hours_per_day.valueChanged.connect(self._overhead_recalc_timer.start)
        self.spin_overhead_days_per_month.valueChanged.connect(self._overhead_recalc_timer.start)
        self.spin_overhead_active_printers.valueChanged.connect(self._overhead_recalc_timer.start)

        scroll.setWidget(scroll_content)
        tab_layout.addWidget(scroll)

        return tab

    def create_pdf_tab(self) -> QWidget:
        """Crea el tab de configuraciones de PDF"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # ── Grupo 1: Formato del Documento ──────────────────────────────────
        format_group = QGroupBox(tr(I18N.Systemsettings.GROUP_DOC_FORMAT))
        format_group.setToolTip(tr(I18N.Systemsettings.TOOLTIP_FORMAT_GROUP))
        format_layout = QGridLayout(format_group)

        self.pdf_fields = {}

        # Título del documento
        format_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_DOC_TITLE)), 0, 0)
        self.pdf_title = QLineEdit("PRESUPUESTO")
        self.pdf_title.setReadOnly(True)
        format_layout.addWidget(self.pdf_title, 0, 1)

        # Subtítulo del documento
        format_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_DOC_SUBTITLE)), 1, 0)
        self.pdf_subtitle = QLineEdit("Impresión 3D")
        self.pdf_subtitle.setReadOnly(True)
        format_layout.addWidget(self.pdf_subtitle, 1, 1)

        # Fuente del PDF
        format_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_DOC_FONT)), 2, 0)
        self.pdf_font_family = QComboBox()
        from core.managers.quote_pdf_manager import QuotePDFManager
        available_fonts = QuotePDFManager.get_available_fonts()
        self.pdf_font_family.addItems(available_fonts)
        self.pdf_font_family.setToolTip(tr(I18N.Systemsettings.TOOLTIP_PDF_FONT))
        self.pdf_font_family.setEnabled(False)
        format_layout.addWidget(self.pdf_font_family, 2, 1)

        # Color primario del PDF
        format_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_PRIMARY_COLOR)), 3, 0)
        self.pdf_primary_color = QLineEdit()
        self.pdf_primary_color.setReadOnly(True)
        self.pdf_primary_color.setPlaceholderText(tr(I18N.Systemsettings.PLACEHOLDER_COLOR))
        self.pdf_primary_color.setMaxLength(7)
        _pdf_hex_validator = QRegularExpressionValidator(
            QRegularExpression(r"^(|#[0-9A-Fa-f]{0,6})$")
        )
        self.pdf_primary_color.setValidator(_pdf_hex_validator)
        self.pdf_primary_color.setToolTip(tr(I18N.Systemsettings.TOOLTIP_PRIMARY_COLOR))
        self.pdf_color_swatch = QFrame()
        self.pdf_color_swatch.setObjectName("pdfColorSwatch")
        self.pdf_color_swatch.setFixedSize(24, 24)
        self.pdf_color_swatch.setStyleSheet("#pdfColorSwatch { background-color: transparent; border: 1px solid #888; }")
        self.pdf_color_pick_btn = QPushButton(tr(I18N.Systemsettings.BUTTON_CHOOSE_COLOR))
        self.pdf_color_pick_btn.setFixedWidth(60)
        self.pdf_color_pick_btn.setEnabled(False)
        self.pdf_color_pick_btn.setToolTip(tr(I18N.Systemsettings.TOOLTIP_COLOR_PICK))
        _pdf_color_row = QHBoxLayout()
        _pdf_color_row.setSpacing(4)
        _pdf_color_row.setContentsMargins(0, 0, 0, 0)
        _pdf_color_row.addWidget(self.pdf_primary_color)
        _pdf_color_row.addWidget(self.pdf_color_swatch)
        _pdf_color_row.addWidget(self.pdf_color_pick_btn)
        _pdf_color_container = QWidget()
        _pdf_color_container.setLayout(_pdf_color_row)
        format_layout.addWidget(_pdf_color_container, 3, 1)

        layout.addWidget(format_group)

        # ── Grupo 2: Contenido del Documento ────────────────────────────────
        content_group = QGroupBox(tr(I18N.Systemsettings.GROUP_DOC_CONTENT))
        content_group.setToolTip(tr(I18N.Systemsettings.TOOLTIP_CONTENT_GROUP))
        content_layout = QGridLayout(content_group)

        # Modo de visualización
        content_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_DISPLAY_MODE)), 0, 0)
        self.pdf_display_mode = QComboBox()
        self.pdf_display_mode.addItem(tr(I18N.Systemsettings.OPTION_DETAILED), "detailed")
        self.pdf_display_mode.addItem(tr(I18N.Systemsettings.OPTION_SUMMARY), "summary")
        self.pdf_display_mode.setCurrentIndex(0)  # Detallado por defecto
        self.pdf_display_mode.setEnabled(False)
        self.pdf_display_mode.setToolTip(tr(I18N.Systemsettings.TOOLTIP_DISPLAY_MODE))
        content_layout.addWidget(self.pdf_display_mode, 0, 1)

        # Etiqueta de servicio (modo resumido)
        content_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_SERVICE_LABEL)), 1, 0)
        self.pdf_summary_label = QLineEdit("Servicio de Impresión 3D")
        self.pdf_summary_label.setReadOnly(True)
        self.pdf_summary_label.setToolTip(tr(I18N.Systemsettings.TOOLTIP_SERVICE_LABEL))
        content_layout.addWidget(self.pdf_summary_label, 1, 1)

        # IVA
        content_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_IVA)), 2, 0)
        self.include_iva = QCheckBox(tr(I18N.Systemsettings.CHECKBOX_SHOW_IVA_DOC))
        self.include_iva.setChecked(True)
        self.include_iva.setEnabled(False)
        content_layout.addWidget(self.include_iva, 2, 1)

        # Margen de error
        content_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_ERROR_MARGIN_FIELD)), 3, 0)
        self.include_error_margin = QCheckBox(tr(I18N.Systemsettings.CHECKBOX_INTEGRATE_ERROR_MARGIN))
        self.include_error_margin.setEnabled(False)
        content_layout.addWidget(self.include_error_margin, 3, 1)

        # Post-Procesado
        content_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_POST_PROCESSING_FIELD)), 4, 0)
        self.include_post_processing = QCheckBox(tr(I18N.Systemsettings.CHECKBOX_INTEGRATE_POST_PROCESSING))
        self.include_post_processing.setEnabled(False)
        content_layout.addWidget(self.include_post_processing, 4, 1)

        # Conectar cambio de modo para habilitar/deshabilitar etiqueta
        self.pdf_display_mode.currentIndexChanged.connect(self._on_pdf_display_mode_changed)

        layout.addWidget(content_group)

        # ── Grupo 3: Comentarios del Pie de Página ──────────────────────────
        comments_group = QGroupBox(tr(I18N.Systemsettings.GROUP_DOC_COMMENTS))
        comments_group.setToolTip(tr(I18N.Systemsettings.TOOLTIP_COMMENTS_GROUP))
        comments_group.setFixedHeight(150)
        comments_layout = QVBoxLayout(comments_group)
        comments_layout.setContentsMargins(6, 6, 6, 6)

        self.footer_comments = QTextEdit()
        self.footer_comments.setReadOnly(True)
        self.footer_comments.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.footer_comments.setPlaceholderText(tr(I18N.Systemsettings.PLACEHOLDER_FOOTER_COMMENTS))
        comments_layout.addWidget(self.footer_comments)

        layout.addWidget(comments_group)
        layout.addStretch()

        return tab

    def create_note_tab(self) -> QWidget:
        """Crea el tab de parámetros de la Nota de Precios"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # ── Grupo 1: Formato de la Nota ──────────────────────────────────────
        note_format_group = QGroupBox(tr(I18N.Systemsettings.GROUP_NOTE_FORMAT))
        note_format_group.setToolTip(tr(I18N.Systemsettings.TOOLTIP_NOTE_FORMAT_GROUP))
        note_format_layout = QGridLayout(note_format_group)

        # Título de la nota
        note_format_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_NOTE_TITLE)), 0, 0)
        self.note_title = QLineEdit("Nota de Precios")
        self.note_title.setReadOnly(True)
        self.note_title.setToolTip(tr(I18N.Systemsettings.TOOLTIP_NOTE_TITLE))
        note_format_layout.addWidget(self.note_title, 0, 1)

        # Fuente de la nota
        note_format_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_DOC_FONT)), 1, 0)
        self.note_font_family = QComboBox()
        from core.managers.quote_pdf_manager import QuotePDFManager
        available_fonts = QuotePDFManager.get_available_fonts()
        self.note_font_family.addItems(available_fonts)
        self.note_font_family.setToolTip(tr(I18N.Systemsettings.TOOLTIP_NOTE_FONT))
        self.note_font_family.setEnabled(False)
        note_format_layout.addWidget(self.note_font_family, 1, 1)

        # Color primario
        note_format_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_PRIMARY_COLOR)), 2, 0)
        self.note_primary_color = QLineEdit()
        self.note_primary_color.setReadOnly(True)
        self.note_primary_color.setPlaceholderText(tr(I18N.Systemsettings.PLACEHOLDER_NOTE_COLOR))
        self.note_primary_color.setMaxLength(7)
        _hex_validator = QRegularExpressionValidator(
            QRegularExpression(r"^(|#[0-9A-Fa-f]{0,6})$")
        )
        self.note_primary_color.setValidator(_hex_validator)
        self.note_primary_color.setToolTip(tr(I18N.Systemsettings.TOOLTIP_NOTE_COLOR))
        self.note_color_swatch = QFrame()
        self.note_color_swatch.setObjectName("noteColorSwatch")
        self.note_color_swatch.setFixedSize(24, 24)
        self.note_color_swatch.setStyleSheet("#noteColorSwatch { background-color: transparent; border: 1px solid #888; }")
        self.note_color_pick_btn = QPushButton(tr(I18N.Systemsettings.BUTTON_CHOOSE_COLOR))
        self.note_color_pick_btn.setFixedWidth(60)
        self.note_color_pick_btn.setEnabled(False)
        self.note_color_pick_btn.setToolTip(tr(I18N.Systemsettings.TOOLTIP_COLOR_PICK))
        color_row = QHBoxLayout()
        color_row.setSpacing(4)
        color_row.setContentsMargins(0, 0, 0, 0)
        color_row.addWidget(self.note_primary_color)
        color_row.addWidget(self.note_color_swatch)
        color_row.addWidget(self.note_color_pick_btn)
        color_container = QWidget()
        color_container.setLayout(color_row)
        note_format_layout.addWidget(color_container, 2, 1)

        layout.addWidget(note_format_group)

        # ── Grupo 2: Configurar Contenido de la Nota ─────────────────────────
        note_present_group = QGroupBox(tr(I18N.Systemsettings.GROUP_NOTE_CONTENT))
        note_present_group.setToolTip(tr(I18N.Systemsettings.TOOLTIP_NOTE_PRESENT_GROUP))
        note_present_layout = QGridLayout(note_present_group)
        note_present_layout.setSpacing(8)

        # Modo de visualización
        note_present_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_DISPLAY_MODE)), 0, 0)
        self.note_display_mode = QComboBox()
        self.note_display_mode.addItem(tr(I18N.Systemsettings.OPTION_DETAILED), "detailed")
        self.note_display_mode.addItem(tr(I18N.Systemsettings.OPTION_SUMMARY), "summary")
        self.note_display_mode.setCurrentIndex(1)  # Resumido por defecto
        self.note_display_mode.setEnabled(False)
        self.note_display_mode.setToolTip(tr(I18N.Systemsettings.TOOLTIP_DISPLAY_MODE))
        note_present_layout.addWidget(self.note_display_mode, 0, 1)

        # Etiqueta del concepto resumido
        note_present_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_SERVICE_LABEL)), 1, 0)
        self.note_summary_label = QLineEdit("Servicio de Impresión 3D")
        self.note_summary_label.setReadOnly(True)
        self.note_summary_label.setToolTip(tr(I18N.Systemsettings.TOOLTIP_SERVICE_LABEL))
        note_present_layout.addWidget(self.note_summary_label, 1, 1)

        # Post-Procesado
        note_present_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_POST_PROCESSING_FIELD)), 2, 0)
        self.note_postprocessing_mode = QCheckBox(tr(I18N.Systemsettings.CHECKBOX_INTEGRATE_POST_PROCESSING))
        self.note_postprocessing_mode.setEnabled(False)
        self.note_postprocessing_mode.setToolTip(tr(I18N.Systemsettings.TOOLTIP_POST_PROCESSING_MODE))
        note_present_layout.addWidget(self.note_postprocessing_mode, 2, 1)

        # Margen de Error
        note_present_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_ERROR_MARGIN_FIELD)), 3, 0)
        self.note_failure_margin_mode = QCheckBox(tr(I18N.Systemsettings.CHECKBOX_INTEGRATE_ERROR_MARGIN))
        self.note_failure_margin_mode.setEnabled(False)
        self.note_failure_margin_mode.setToolTip(tr(I18N.Systemsettings.TOOLTIP_FAILURE_MARGIN_MODE))
        note_present_layout.addWidget(self.note_failure_margin_mode, 3, 1)

        # Mostrar IVA
        note_present_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_IVA_NOTE)), 4, 0)
        self.note_show_tax = QCheckBox(tr(I18N.Systemsettings.CHECKBOX_SHOW_IVA_NOTE))
        self.note_show_tax.setChecked(True)
        self.note_show_tax.setEnabled(False)
        note_present_layout.addWidget(self.note_show_tax, 4, 1)

        # Validez de la nota
        note_present_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_NOTE_VALIDITY_ENABLED)), 5, 0)
        self.note_validity_enabled = QCheckBox(tr(I18N.Systemsettings.CHECKBOX_SHOW_VALIDITY))
        self.note_validity_enabled.setChecked(True)
        self.note_validity_enabled.setEnabled(False)
        self.note_validity_enabled.setToolTip(tr(I18N.Systemsettings.TOOLTIP_VALIDITY_ENABLED))
        note_present_layout.addWidget(self.note_validity_enabled, 5, 1)

        note_present_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_NOTE_VALIDITY_DAYS)), 6, 0)
        self.note_validity_days = QSpinBox()
        self.note_validity_days.setRange(1, 30)
        self.note_validity_days.setValue(30)
        self.note_validity_days.setEnabled(False)
        self.note_validity_days.setToolTip(tr(I18N.Systemsettings.TOOLTIP_VALIDITY_DAYS))
        note_present_layout.addWidget(self.note_validity_days, 6, 1)

        # Conectar cambio de modo para habilitar/deshabilitar etiqueta de resumen
        self.note_display_mode.currentIndexChanged.connect(self._on_note_display_mode_changed)
        self.note_validity_enabled.toggled.connect(self._on_note_validity_toggled)

        layout.addWidget(note_present_group)

        # ── Grupo 3: Texto de Observación (OBS) ─────────────────────────────
        note_obs_group = QGroupBox(tr(I18N.Systemsettings.GROUP_NOTE_OBS))
        note_obs_group.setToolTip(tr(I18N.Systemsettings.TOOLTIP_NOTE_OBS_GROUP))
        note_obs_layout = QVBoxLayout(note_obs_group)

        self.note_obs_text = QTextEdit()
        self.note_obs_text.setReadOnly(True)
        self.note_obs_text.setFixedHeight(80)
        self.note_obs_text.setPlaceholderText(tr(I18N.Systemsettings.PLACEHOLDER_NOTE_OBS))
        self.note_obs_text.textChanged.connect(self._limit_obs_text)
        note_obs_layout.addWidget(self.note_obs_text)

        layout.addWidget(note_obs_group)
        layout.addStretch()

        return tab

    def create_system_tab(self) -> QWidget:
        """Crea el tab de configuraciones del sistema"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # ── Grupo: Configuraciones del Sistema ──────────────────────────────
        system_group = QGroupBox(tr(I18N.Systemsettings.GROUP_SYS_CONFIG))
        system_layout = QGridLayout(system_group)

        self.system_fields = {}

        # Auto-guardado
        system_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_AUTOSAVE_INTERVAL)), 0, 0)
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(30, 3600)
        self.auto_save_interval.setValue(300)
        self.auto_save_interval.setEnabled(False)
        system_layout.addWidget(self.auto_save_interval, 0, 1)

        # Respaldos
        system_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_BACKUP_ENABLED)), 1, 0)
        self.backup_enabled = QCheckBox(tr(I18N.Systemsettings.CHECKBOX_AUTO_BACKUP))
        self.backup_enabled.setChecked(True)
        self.backup_enabled.setEnabled(False)
        system_layout.addWidget(self.backup_enabled, 1, 1)

        # Frecuencia de respaldos
        system_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_BACKUP_FREQ)), 2, 0)
        self.backup_frequency = QSpinBox()
        self.backup_frequency.setRange(1, 30)
        self.backup_frequency.setValue(7)
        self.backup_frequency.setEnabled(False)
        system_layout.addWidget(self.backup_frequency, 2, 1)

        layout.addWidget(system_group)

        # ── Grupo: Sistema de Moneda ─────────────────────────────────────────
        currency_group = QGroupBox(tr(I18N.Systemsettings.GROUP_CURRENCY))
        currency_layout = QGridLayout(currency_group)

        currency_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_MAIN_CURRENCY)), 0, 0)
        self.currency_combo = QComboBox()
        self.currency_combo.setEnabled(False)
        currency_layout.addWidget(self.currency_combo, 0, 1)

        empty_label = QLabel()
        currency_layout.addWidget(empty_label, 1, 0)

        exchange_container = QWidget()
        exchange_layout_h = QHBoxLayout(exchange_container)
        exchange_layout_h.setContentsMargins(0, 0, 0, 0)
        exchange_layout_h.setSpacing(0)
        exchange_layout_h.addStretch()

        self.lbl_exchange_rates = QLabel(tr(I18N.Systemsettings.LABEL_EXCHANGE_RATES))
        self.lbl_exchange_rates.setFixedHeight(32)
        self.lbl_exchange_rates.setToolTip(tr(I18N.Systemsettings.TOOLTIP_EXCHANGE_RATES))
        self.lbl_exchange_rates.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.lbl_exchange_rates.setEnabled(False)
        self.lbl_exchange_rates.setStyleSheet("""
            QLabel {
                font-weight: bold;
                padding: 2px 6px 2px 6px;
                border: 1px solid #FF9800;
                border-radius: 6px;
            }
            QLabel:hover:enabled {
                color: #64B5F6;
            }
            QLabel:disabled {
                color: #555;
                border-color: #555;
            }
        """)
        self.lbl_exchange_rates.mousePressEvent = self._on_exchange_rates_label_clicked
        exchange_layout_h.addWidget(self.lbl_exchange_rates)
        currency_layout.addWidget(exchange_container, 1, 1)

        currency_info_label = QLabel(tr(I18N.Systemsettings.INFO_CURRENCY_MAIN))
        currency_info_label.setWordWrap(True)
        currency_info_label.setStyleSheet(
            "QLabel { color: #888; font-size: 9px; padding: 8px; "
            "background: rgba(100,100,100,0.1); border-radius: 4px; }"
        )
        currency_layout.addWidget(currency_info_label, 2, 0, 1, 2)

        layout.addWidget(currency_group)

        # ── Grupo: Diagnóstico ───────────────────────────────────────────────
        diag_group = QGroupBox(tr(I18N.Systemsettings.GROUP_DIAGNOSTIC))
        diag_layout = QGridLayout(diag_group)

        diag_layout.addWidget(QLabel(tr(I18N.Systemsettings.LABEL_LOG_FILE)), 0, 0)

        self.btn_open_log = QPushButton(tr(I18N.Systemsettings.BUTTON_OPEN_LOG))
        self.btn_open_log.setToolTip(tr(I18N.Systemsettings.TOOLTIP_OPEN_LOG))
        self.btn_open_log.clicked.connect(self.open_log_requested.emit)
        diag_layout.addWidget(self.btn_open_log, 0, 1)

        log_info_label = QLabel(tr(I18N.Systemsettings.INFO_LOG_FILE))
        log_info_label.setWordWrap(True)
        log_info_label.setStyleSheet(
            "QLabel { color: #888; font-size: 9px; padding: 4px; }"
        )
        diag_layout.addWidget(log_info_label, 1, 0, 1, 2)

        layout.addWidget(diag_group)
        layout.addStretch()

        return tab

    def create_database_tab(self) -> QWidget:
        """Crea el tab de gestión de Base de Datos"""
        from PySide6.QtWidgets import QScrollArea
        
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 3, 0)

        # ── Grupo: Información de la Base de Datos ──────────────────────────
        info_group = QGroupBox(tr(I18N.Systemsettings.GROUP_DB_INFO))
        info_layout = QGridLayout(info_group)
        info_layout.setSpacing(4)
        info_layout.setContentsMargins(10, 8, 10, 8)

        self.db_info_labels = {}
        bold_style = "QLabel { font-weight: bold; }"

        # Fila 0: Versión | Schema
        info_layout.addWidget(self._make_label(tr(I18N.Systemsettings.LABEL_DB_VERSION), bold_style), 0, 0)
        self.db_info_labels["db_version"] = self._make_value_label()
        info_layout.addWidget(self.db_info_labels["db_version"], 0, 1)

        info_layout.addWidget(self._make_label(tr(I18N.Systemsettings.LABEL_DB_SCHEMA), bold_style), 0, 2)
        self.db_info_labels["schema_version"] = self._make_value_label()
        info_layout.addWidget(self.db_info_labels["schema_version"], 0, 3)

        # Fila 1: Tamaño | Creada
        info_layout.addWidget(self._make_label(tr(I18N.Systemsettings.LABEL_DB_SIZE), bold_style), 1, 0)
        self.db_info_labels["db_size"] = self._make_value_label()
        info_layout.addWidget(self.db_info_labels["db_size"], 1, 1)

        info_layout.addWidget(self._make_label(tr(I18N.Systemsettings.LABEL_DB_CREATED), bold_style), 1, 2)
        self.db_info_labels["db_created"] = self._make_value_label()
        info_layout.addWidget(self.db_info_labels["db_created"], 1, 3)

        # Fila 2: Ubicación (spanning 4 cols)
        info_layout.addWidget(self._make_label(tr(I18N.Systemsettings.LABEL_DB_LOCATION), bold_style), 2, 0)
        path_label = self._make_value_label()
        path_label.setWordWrap(True)
        path_label.setStyleSheet("QLabel { color: #888; font-size: 10px; }")
        self.db_info_labels["db_path"] = path_label
        info_layout.addWidget(path_label, 2, 1, 1, 3)

        # Fila 3: Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("QFrame { color: #444; }")
        info_layout.addWidget(sep, 3, 0, 1, 4)

        # Fila 4: Registros totales y conteo detallado en línea
        info_layout.addWidget(self._make_label(tr(I18N.Systemsettings.LABEL_DB_TOTAL_RECORDS), bold_style), 4, 0)
        self.db_info_labels["total_records"] = self._make_value_label()
        info_layout.addWidget(self.db_info_labels["total_records"], 4, 1)

        self.db_record_labels = {}
        record_tables = [
            (tr(I18N.Systemsettings.DB_RECORD_CUSTOMERS), "customers"),
            (tr(I18N.Systemsettings.DB_RECORD_PRINTERS), "printers"),
            (tr(I18N.Systemsettings.DB_RECORD_FILAMENTS), "filaments"),
            (tr(I18N.Systemsettings.DB_RECORD_QUOTES), "quotes"),
        ]
        records_widget = QWidget()
        records_grid = QGridLayout(records_widget)
        records_grid.setContentsMargins(0, 0, 0, 0)
        records_grid.setSpacing(4)
        for i, (display_name, key) in enumerate(record_tables):
            row = i // 2
            col = (i % 2) * 2
            lbl = QLabel(f"{display_name}:")
            lbl.setStyleSheet("QLabel { color: #aaa; }")
            records_grid.addWidget(lbl, row, col)
            val = QLabel("0")
            val.setStyleSheet("QLabel { color: #64B5F6; font-weight: bold; }")
            self.db_record_labels[key] = val
            records_grid.addWidget(val, row, col + 1)
        info_layout.addWidget(records_widget, 4, 2, 2, 2)

        layout.addWidget(info_group)

        # ── Grupo: Gestión de Respaldos ─────────────────────────────────────
        backup_group = QGroupBox(tr(I18N.Systemsettings.GROUP_BACKUP_MGMT))
        backup_layout = QVBoxLayout(backup_group)
        backup_layout.setSpacing(8)
        
        # Resumen de backups
        backup_summary_layout = QHBoxLayout()
        
        self.lbl_backup_count = QLabel("Respaldos disponibles: 0")
        self.lbl_backup_count.setStyleSheet("QLabel { font-weight: bold; }")
        backup_summary_layout.addWidget(self.lbl_backup_count)
        
        self.lbl_last_backup = QLabel("Último respaldo: —")
        self.lbl_last_backup.setStyleSheet("QLabel { color: #aaa; }")
        backup_summary_layout.addWidget(self.lbl_last_backup)
        
        backup_summary_layout.addStretch()
        backup_layout.addLayout(backup_summary_layout)
        
        # Tabla de backups
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(5)
        self.backup_table.setHorizontalHeaderLabels([
            tr(I18N.Systemsettings.TABLE_COL_FILE),
            tr(I18N.Systemsettings.TABLE_COL_DATE),
            tr(I18N.Systemsettings.TABLE_COL_VERSION),
            tr(I18N.Systemsettings.TABLE_COL_SIZE),
            tr(I18N.Systemsettings.TABLE_COL_STATUS)
        ])
        self.backup_table.setMinimumHeight(160)
        self.backup_table.setMaximumHeight(220)
        self.backup_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.backup_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.backup_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.backup_table.setAlternatingRowColors(True)
        self.backup_table.verticalHeader().setVisible(False)  # Ocultar números de fila
        
        # Ajustar columnas
        header = self.backup_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)                
        backup_layout.addWidget(self.backup_table)
        
        # Botones de acción de backups
        backup_buttons_layout = QHBoxLayout()
        backup_buttons_layout.setSpacing(8)
        
        self.btn_create_backup = QPushButton(tr(I18N.Systemsettings.BUTTON_CREATE_BACKUP))
        self.btn_create_backup.setFixedHeight(30)
        self.btn_create_backup.setFixedWidth(140)
        self.btn_create_backup.setEnabled(False)  # Requiere desbloqueo
        self.btn_create_backup.setToolTip(tr(I18N.Systemsettings.TOOLTIP_CREATE_BACKUP))
        self.btn_create_backup.setStyleSheet("""
            QPushButton {
                color: #e6fdff; border: 1px solid #bcbcbc;
                border-radius: 5px; background-color: #46aa8f; font-weight: bold;
            }
            QPushButton:hover {
                color: #fff; background-color: #00aa7f; border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #fff; background-color: #ffaa00; border: 1px solid #69cdff;
            }
            QPushButton:disabled {
                color: #d5d5d5; background-color: transparent; border: 1px solid #bcbcbc;
            }
        """)
        
        self.btn_restore_backup = QPushButton(tr(I18N.Systemsettings.BUTTON_RESTORE_BACKUP))
        self.btn_restore_backup.setFixedHeight(30)
        self.btn_restore_backup.setFixedWidth(120)
        self.btn_restore_backup.setToolTip(tr(I18N.Systemsettings.TOOLTIP_RESTORE_BACKUP))
        self.btn_restore_backup.setEnabled(False)
        self.btn_restore_backup.setStyleSheet("""
            QPushButton {
                color: #e6fdff; border: 1px solid #bcbcbc;
                border-radius: 5px; background-color: #be7dff; font-weight: bold;
            }
            QPushButton:hover {
                color: #fff; background-color: #aa00ff; border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #fff; background-color: #ffaa00; border: 1px solid #69cdff;
            }
            QPushButton:disabled {
                color: #d5d5d5; background-color: #6a6a6a; border: 1px solid #555;
            }
        """)
        
        self.btn_delete_backup = QPushButton(tr(I18N.Systemsettings.BUTTON_DELETE_BACKUP))
        self.btn_delete_backup.setFixedHeight(30)
        self.btn_delete_backup.setFixedWidth(110)
        self.btn_delete_backup.setToolTip(tr(I18N.Systemsettings.TOOLTIP_DELETE_BACKUP))
        self.btn_delete_backup.setEnabled(False)
        self.btn_delete_backup.setStyleSheet("""
            QPushButton {
                color: #e6fdff; border: 1px solid #bcbcbc;
                border-radius: 5px; background-color: #f09292; font-weight: bold;
            }
            QPushButton:hover {
                color: #fff; background-color: #be0000; border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #fff; background-color: #ff0000; border: 1px solid #69cdff;
            }
            QPushButton:disabled {
                color: #d5d5d5; background-color: #6a6a6a; border: 1px solid #555;
            }
        """)
        
        self.btn_open_backup_folder = QPushButton(tr(I18N.Systemsettings.BUTTON_OPEN_BACKUP_FOLDER))
        self.btn_open_backup_folder.setFixedHeight(30)
        self.btn_open_backup_folder.setFixedWidth(120)
        self.btn_open_backup_folder.setToolTip(tr(I18N.Systemsettings.TOOLTIP_OPEN_BACKUP_FOLDER))
        self.btn_open_backup_folder.setStyleSheet("""
            QPushButton {
                color: #e6fdff; border: 1px solid #bcbcbc;
                border-radius: 5px; background-color: #46aac4; font-weight: bold;
            }
            QPushButton:hover {
                color: #fff; background-color: #009dc4; border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #fff; background-color: #ffaa00; border: 1px solid #69cdff;
            }
            QPushButton:disabled {
                color: #d5d5d5; background-color: transparent; border: 1px solid #bcbcbc;
            }
        """)
        
        backup_buttons_layout.addWidget(self.btn_create_backup)
        backup_buttons_layout.addWidget(self.btn_restore_backup)
        backup_buttons_layout.addWidget(self.btn_delete_backup)
        backup_buttons_layout.addStretch()
        backup_buttons_layout.addWidget(self.btn_open_backup_folder)
        
        backup_layout.addLayout(backup_buttons_layout)
        
        layout.addWidget(backup_group)

        layout.addStretch()
        
        scroll.setWidget(scroll_content)
        
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)
        
        # Conectar señales del tab de base de datos
        self._setup_database_tab_connections()
        
        return tab
    
    def _make_label(self, text: str, style: str = "") -> QLabel:
        """Crea un QLabel con texto y estilo opcional"""
        lbl = QLabel(text)
        if style:
            lbl.setStyleSheet(style)
        return lbl
    
    def _make_value_label(self, text: str = "—") -> QLabel:
        """Crea un QLabel para valores, seleccionable con el mouse"""
        lbl = QLabel(text)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return lbl

    def create_language_tab(self) -> QWidget:
        """Crea el tab de Idioma y Región"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # GroupBox: Idioma de la Aplicación
        app_lang_group = QGroupBox(tr(I18N.Systemsettings.GROUP_APP_LANGUAGE))
        app_lang_layout = QGridLayout(app_lang_group)
        app_lang_layout.setContentsMargins(10, 15, 10, 10)
        app_lang_layout.setSpacing(8)

        lbl_language = QLabel(tr(I18N.Systemsettings.LABEL_LANGUAGE))
        self.language_combo = QComboBox()
        self.language_combo.setEnabled(False)
        app_lang_layout.addWidget(lbl_language, 0, 0)
        app_lang_layout.addWidget(self.language_combo, 0, 1)

        self.btn_add_language = QPushButton(tr(I18N.Systemsettings.BTN_ADD_LANGUAGE))
        self.btn_add_language.setToolTip(tr(I18N.Systemsettings.TOOLTIP_ADD_LANGUAGE))
        app_lang_layout.addWidget(self.btn_add_language, 1, 1)

        layout.addWidget(app_lang_group)

        # GroupBox: Región / Localización
        region_group = QGroupBox(tr(I18N.Systemsettings.GROUP_REGION))
        region_layout = QGridLayout(region_group)
        region_layout.setContentsMargins(10, 15, 10, 10)
        region_layout.setSpacing(8)

        lbl_locale = QLabel(tr(I18N.Systemsettings.LABEL_LOCALE))
        self.locale_combo = QComboBox()
        self.locale_combo.setEnabled(False)
        region_layout.addWidget(lbl_locale, 0, 0)
        region_layout.addWidget(self.locale_combo, 0, 1)

        lbl_preview_tax = QLabel(tr(I18N.Systemsettings.LABEL_PREVIEW_TAX_ID))
        self.preview_tax_id = QLabel("—")
        region_layout.addWidget(lbl_preview_tax, 1, 0)
        region_layout.addWidget(self.preview_tax_id, 1, 1)

        lbl_preview_date = QLabel(tr(I18N.Systemsettings.LABEL_PREVIEW_DATE_FMT))
        self.preview_date_fmt = QLabel("—")
        region_layout.addWidget(lbl_preview_date, 2, 0)
        region_layout.addWidget(self.preview_date_fmt, 2, 1)

        layout.addWidget(region_group)

        lang_info_label = QLabel(tr(I18N.Systemsettings.INFO_LANG_MAIN))
        lang_info_label.setWordWrap(True)
        lang_info_label.setTextFormat(Qt.TextFormat.RichText)
        lang_info_label.setStyleSheet(
            "QLabel { color: #888; font-size: 9px; padding: 8px; "
            "background: rgba(100,100,100,0.1); border-radius: 4px; }"
        )
        layout.addWidget(lang_info_label)

        layout.addStretch()
        return tab

    def _setup_database_tab_connections(self):
        """Configura las conexiones de señales del tab de base de datos"""
        self.btn_create_backup.clicked.connect(self._on_create_backup)
        self.btn_restore_backup.clicked.connect(self._on_restore_backup)
        self.btn_delete_backup.clicked.connect(self._on_delete_backup)
        self.btn_open_backup_folder.clicked.connect(self._on_open_backup_folder)
        self.backup_table.itemSelectionChanged.connect(self._on_backup_selection_changed)
    
    def _on_backup_selection_changed(self):
        """Actualiza los botones según la selección en la tabla de backups"""
        selected = self.backup_table.selectedItems()
        has_selection = len(selected) > 0
        
        if has_selection:
            row = self.backup_table.currentRow()
            # Verificar compatibilidad del backup seleccionado
            status_item = self.backup_table.item(row, 4)
            is_compatible = status_item and status_item.text() == "Compatible"
            self.btn_restore_backup.setEnabled(is_compatible)
        else:
            self.btn_restore_backup.setEnabled(False)
        
        self.btn_delete_backup.setEnabled(has_selection)
    
    def _on_create_backup(self):
        """Maneja la creación de un backup manual"""
        if hasattr(self, 'presenter') and self.presenter:
            self.presenter.create_manual_backup()
    
    def _on_restore_backup(self):
        """Maneja la restauración de un backup seleccionado"""
        selected = self.backup_table.selectedItems()
        if not selected:
            QMessageBox.information(self, tr(I18N.Systemsettings.MSG_SELECT_REQUIRED_TITLE), 
                tr(I18N.Systemsettings.MSG_SELECT_REQUIRED_TEXT))
            return
        
        row = self.backup_table.currentRow()
        # Obtener la ruta del backup (almacenada como dato del item de la primera columna)
        filename_item = self.backup_table.item(row, 0)
        if not filename_item:
            return
        
        backup_path = filename_item.data(Qt.ItemDataRole.UserRole)
        if not backup_path:
            return
        
        # Confirmación doble
        version_item = self.backup_table.item(row, 2)
        date_item = self.backup_table.item(row, 1)
        
        reply = QMessageBox.warning(
            self,
            tr(I18N.Systemsettings.MSG_RESTORE_TITLE),
            tr(I18N.Systemsettings.MSG_RESTORE_TEXT).format(
                filename=filename_item.text(),
                date=date_item.text() if date_item else '—',
                version=version_item.text() if version_item else '—'
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, 'presenter') and self.presenter:
                self.presenter.restore_backup(backup_path)
    
    def _on_delete_backup(self):
        """Maneja la eliminación de un backup seleccionado"""
        selected = self.backup_table.selectedItems()
        if not selected:
            return
        
        row = self.backup_table.currentRow()
        filename_item = self.backup_table.item(row, 0)
        if not filename_item:
            return
        
        backup_path = filename_item.data(Qt.ItemDataRole.UserRole)
        if not backup_path:
            return
        
        reply = QMessageBox.question(
            self,
            tr(I18N.Systemsettings.MSG_DELETE_BACKUP_TITLE),
            tr(I18N.Systemsettings.MSG_DELETE_BACKUP_TEXT).format(filename=filename_item.text()),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, 'presenter') and self.presenter:
                self.presenter.delete_backup(backup_path)
    
    def _on_open_backup_folder(self):
        """Abre la carpeta de backups en el explorador"""
        if hasattr(self, 'presenter') and self.presenter:
            self.presenter.open_backup_folder()
    
    def update_database_info(self, stats: dict):
        """Actualiza la información de la base de datos en la UI"""
        try:
            # Info general
            if 'db_version' in stats:
                self.db_info_labels['db_version'].setText(f"v{stats['db_version']}")
            if 'schema_version' in stats:
                self.db_info_labels['schema_version'].setText(
                    f"v{stats['schema_version']}"
                )
            if 'db_size_mb' in stats:
                self.db_info_labels['db_size'].setText(
                    f"{stats['db_size_mb']:.2f} MB"
                )
            if 'db_path' in stats:
                self.db_info_labels['db_path'].setText(str(stats['db_path']))
            if 'created_at' in stats and stats['created_at']:
                self.db_info_labels['db_created'].setText(str(stats['created_at']))
            if 'total_records' in stats:
                self.db_info_labels['total_records'].setText(
                    str(stats['total_records'])
                )
            
            # Conteo de registros
            record_counts = stats.get('record_counts', {})
            for table_key, lbl in self.db_record_labels.items():
                if table_key in record_counts:
                    lbl.setText(str(record_counts[table_key]))
            
            # Info de backups
            if 'total_backups' in stats:
                self.lbl_backup_count.setText(
                    f"Respaldos disponibles: {stats['total_backups']}"
                )
            if 'last_backup_date' in stats and stats['last_backup_date']:
                date = stats['last_backup_date']
                if hasattr(date, 'strftime'):
                    self.lbl_last_backup.setText(
                        f"Último respaldo: {date.strftime('%d/%m/%Y %H:%M')}"
                    )
                else:
                    self.lbl_last_backup.setText(f"Último respaldo: {date}")
            
        except Exception as e:
            logger.error("SystemSettings", f"Error actualizando info de BD: {e}")
    
    def update_backups_table(self, backups: list):
        """Actualiza la tabla de backups con datos nuevos"""
        try:
            self.backup_table.setRowCount(0)
            
            for backup_info in backups:
                row = self.backup_table.rowCount()
                self.backup_table.insertRow(row)
                
                # Columna 0: Archivo
                filename_item = QTableWidgetItem(backup_info.get('filename', ''))
                filename_item.setData(
                    Qt.ItemDataRole.UserRole, 
                    backup_info.get('filepath', '')
                )
                filename_item.setToolTip(backup_info.get('filepath', ''))
                self.backup_table.setItem(row, 0, filename_item)
                
                # Columna 1: Fecha
                date = backup_info.get('date')
                if date and hasattr(date, 'strftime'):
                    date_text = date.strftime('%d/%m/%Y %H:%M')
                else:
                    date_text = str(date) if date else '—'
                self.backup_table.setItem(row, 1, QTableWidgetItem(date_text))
                
                # Columna 2: Versión
                version = backup_info.get('db_version', '?')
                version_text = f"v{version}" if version else "?"
                self.backup_table.setItem(row, 2, QTableWidgetItem(version_text))
                
                # Columna 3: Tamaño
                size_mb = backup_info.get('size_mb', 0)
                self.backup_table.setItem(
                    row, 3, QTableWidgetItem(f"{size_mb:.2f} MB")
                )
                
                # Columna 4: Estado (compatible / incompatible)
                is_compatible = backup_info.get('is_compatible', False)
                status_item = QTableWidgetItem(
                    "Compatible" if is_compatible else "Incompatible"
                )
                if is_compatible:
                    status_item.setForeground(QColor("#4CAF50"))
                else:
                    status_item.setForeground(QColor("#FF5252"))
                    reason = backup_info.get('compatibility_reason', '')
                    status_item.setToolTip(reason)
                
                self.backup_table.setItem(row, 4, status_item)
            
            # Actualizar conteo
            self.lbl_backup_count.setText(
                f"Respaldos disponibles: {len(backups)}"
            )
            
            # Reset selection
            self.btn_restore_backup.setEnabled(False)
            self.btn_delete_backup.setEnabled(False)
            
        except Exception as e:
            logger.error("SystemSettings", f"Error actualizando tabla de backups: {e}")
    
    def _notify_status(self, message: str):
        """Envía un mensaje de estado al panel de procesos de la ventana principal."""
        try:
            main_window = self.window()
            if hasattr(main_window, 'add_system_log'):
                main_window.add_system_log(f"⚙️ Ajustes: {message}")
        except Exception:
            pass

    def _open_color_picker(self):
        """Abre el selector de color y carga el código HEX en el campo de color primario."""
        current_hex = self.note_primary_color.text().strip()
        initial = QColor(current_hex) if current_hex and QColor(current_hex).isValid() else QColor("#0070C0")
        color = QColorDialog.getColor(initial, self, "Seleccionar Color Primario")
        if color.isValid():
            self.note_primary_color.setText(color.name().upper())

    def _update_color_swatch(self, hex_code: str):
        """Actualiza el swatch de previsualización con el color indicado."""
        if hex_code and QColor(hex_code).isValid():
            self.note_color_swatch.setStyleSheet(
                f"#noteColorSwatch {{ background-color: {hex_code}; border: 1px solid #888; }}"
            )
        else:
            self.note_color_swatch.setStyleSheet("#noteColorSwatch { background-color: transparent; border: 1px solid #888; }")

    def _open_pdf_color_picker(self):
        """Abre el selector de color para el color primario del PDF."""
        current_hex = self.pdf_primary_color.text().strip()
        initial = QColor(current_hex) if current_hex and QColor(current_hex).isValid() else QColor("#0070C0")
        color = QColorDialog.getColor(initial, self, "Seleccionar Color Primario PDF")
        if color.isValid():
            self.pdf_primary_color.setText(color.name().upper())

    def _update_pdf_color_swatch(self, hex_code: str):
        """Actualiza el swatch de previsualización del color primario del PDF."""
        if hex_code and QColor(hex_code).isValid():
            self.pdf_color_swatch.setStyleSheet(
                f"#pdfColorSwatch {{ background-color: {hex_code}; border: 1px solid #888; }}"
            )
        else:
            self.pdf_color_swatch.setStyleSheet("#pdfColorSwatch { background-color: transparent; border: 1px solid #888; }")

    def _on_pdf_display_mode_changed(self):
        """Habilita o deshabilita pdf_summary_label según el modo seleccionado."""
        is_summary = self.pdf_display_mode.currentData() == "summary"
        if self.is_editing:
            self.pdf_summary_label.setReadOnly(not is_summary)

    def _populate_language_combo(self):
        """Llena el combo de idiomas con datos del presenter"""
        if not hasattr(self, 'presenter') or self.presenter is None:
            return
        self.language_combo.blockSignals(True)
        self.language_combo.clear()
        languages = self.presenter.get_available_languages()
        for lang in languages:
            self.language_combo.addItem(lang.get("language", lang["code"]), lang["code"])
        current = self.presenter.get_current_language()
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current:
                self.language_combo.setCurrentIndex(i)
                break
        self.language_combo.blockSignals(False)

    def _populate_locale_combo(self):
        """Llena el combo de regiones con bandera e información de moneda"""
        if not hasattr(self, 'presenter') or self.presenter is None:
            return
        self.locale_combo.blockSignals(True)
        self.locale_combo.clear()
        locales = self.presenter.get_available_locales()
        for locale in locales:
            country = locale.get('country', locale['code'])
            label = country
            icon_name = locale.get('flag_icon', '')
            icon_path = build_resource_path(f"resources/icons/{icon_name}.svg")
            icon = QIcon(icon_path) if icon_name and os.path.exists(icon_path) else QIcon()
            self.locale_combo.addItem(icon, label, locale["code"])
        current = self.presenter.get_current_locale()
        for i in range(self.locale_combo.count()):
            if self.locale_combo.itemData(i) == current:
                self.locale_combo.setCurrentIndex(i)
                break
        self.locale_combo.blockSignals(False)
        self._on_locale_combo_changed()

    def _on_locale_combo_changed(self):
        """Actualiza los labels de preview cuando cambia el locale seleccionado"""
        if not hasattr(self, 'presenter') or self.presenter is None:
            return
        locale_code = self.locale_combo.currentData()
        if not locale_code:
            return
        preview = self.presenter.get_locale_preview(locale_code)
        self.preview_tax_id.setText(preview.get("tax_id_label", "—"))
        self.preview_date_fmt.setText(preview.get("date_format", "—"))

    def _handle_add_language_zip(self):
        """Importa un pack de idioma comunitario desde un archivo ZIP"""
        from core.utils.path_helper import app_root
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr(I18N.Systemsettings.MSG_LANG_ZIP_TITLE),
            "",
            tr(I18N.Systemsettings.MSG_LANG_ZIP_FILTER)
        )
        if not file_path:
            return
        try:
            import zipfile as _zipfile
            dest_dir = app_root() / "translations" / "packs"
            dest_dir.mkdir(parents=True, exist_ok=True)
            with _zipfile.ZipFile(file_path, 'r') as zf:
                json_files = [n for n in zf.namelist() if n.endswith('.json') and '/' not in n]
                if not json_files:
                    raise ValueError("El ZIP no contiene un archivo .json en la raíz")
                zf.extractall(dest_dir, members=json_files)
            QMessageBox.information(self, tr(I18N.Systemsettings.MSG_LANG_ZIP_TITLE),
                                    tr(I18N.Systemsettings.MSG_LANG_ZIP_OK))
            self._populate_language_combo()
            logger.info("SystemSettings", f"Idioma importado desde: {file_path}")
        except Exception as e:
            logger.error("SystemSettings", f"Error importando idioma ZIP: {e}")
            QMessageBox.warning(self, tr(I18N.Systemsettings.MSG_LANG_ZIP_TITLE),
                                tr(I18N.Systemsettings.MSG_LANG_ZIP_ERROR))

    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.btn_edit.clicked.connect(self.toggle_editing)
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_cancel.clicked.connect(self.cancel_editing)
        self.btn_reload.clicked.connect(self.reload_settings)
        self.note_color_pick_btn.clicked.connect(self._open_color_picker)
        self.note_primary_color.textChanged.connect(self._update_color_swatch)
        self.pdf_color_pick_btn.clicked.connect(self._open_pdf_color_picker)
        self.pdf_primary_color.textChanged.connect(self._update_pdf_color_swatch)
        self.cost_fields['tax_rate'].valueChanged.connect(self._update_tax_shield_label)
        self.locale_combo.currentIndexChanged.connect(self._on_locale_combo_changed)
        self.btn_add_language.clicked.connect(self._handle_add_language_zip)

    def _update_tax_shield_label(self, tax_rate: float):
        """Actualiza el texto y tooltip del checkbox de blindaje según el IVA configurado"""
        multiplier = 1 + (tax_rate / 100)
        self.commission_tax_shield.setText(f"Aplicar ×{multiplier:.2f} a la comisión deseada")
        tooltip = (
            f"Precio Final = Costo Materiales + (Comisión Deseada × {multiplier:.2f})\n"
            f"Con IVA del {tax_rate:.0f}%, la comisión cobrada queda íntegra tras el impuesto."
        )
        self.commission_tax_shield.setToolTip(tooltip)
        self.lbl_shield.setToolTip(tooltip)

    def _on_peak_multiplier_changed(self, value: float):
        """Garantiza que el multiplicador de hora punta nunca sea menor a 1.0"""
        if value < 1.0:
            self.electricity_peak_multiplier.setValue(1.0)

    def _on_overhead_printers_mode_changed(self, index: int):
        """Muestra u oculta el spinbox manual según el modo seleccionado."""
        is_manual = self.combo_overhead_printers_mode.currentData() == "manual"
        self.spin_overhead_active_printers.setVisible(is_manual)
        self.spin_overhead_active_printers.setEnabled(is_manual and self.is_editing)
        self.lbl_overhead_printers_count.setVisible(not is_manual)
        self._overhead_recalc_timer.start()

    def _recalc_overhead_display(self):
        """Recalcula y actualiza los labels de overhead en tiempo real."""
        from core.utils.currency_helper import CurrencyHelper
        _overhead_keys = [
            "overhead_rent", "overhead_water", "overhead_internet",
            "overhead_accounting", "overhead_salary", "overhead_transport",
            "overhead_other"
        ]
        total_monthly = sum(getattr(self, f"spin_{k}").value() for k in _overhead_keys)
        hours_day = self.spin_overhead_hours_per_day.value()
        days_month = self.spin_overhead_days_per_month.value()

        # Determinar impresoras activas
        mode = self.combo_overhead_printers_mode.currentData() or "auto"
        if mode == "manual":
            active_printers = max(1, self.spin_overhead_active_printers.value())
        else:
            # Leer el conteo almacenado por el presenter en el label de BD
            try:
                active_printers = max(1, int(self.lbl_overhead_printers_count.text().split()[0]))
            except (ValueError, IndexError):
                active_printers = 1

        monthly_hours = hours_day * days_month * active_printers
        hours_label_text = f"{hours_day * days_month} {tr(I18N.Systemsettings.UNIT_H_MONTH)}"
        if active_printers > 1:
            hours_label_text += f" {tr(I18N.Systemsettings.UNIT_PRINTERS_X).format(n=active_printers, total=monthly_hours)}"
        self.lbl_overhead_monthly_hours.setText(hours_label_text)

        self.lbl_overhead_monthly_total.setText(
            CurrencyHelper.format_with_current_currency(total_monthly)
        )

        if monthly_hours > 0 and total_monthly > 0:
            per_hour = total_monthly / monthly_hours
            self.lbl_overhead_per_hour.setText(
                f"{CurrencyHelper.format_with_current_currency(per_hour)} {tr(I18N.Systemsettings.UNIT_PER_HOUR)}"
            )
        else:
            self.lbl_overhead_per_hour.setText("—")

    def get_overhead_settings(self) -> dict:
        """Recopila los valores de los campos de overhead para guardar."""
        _overhead_keys = [
            "overhead_rent", "overhead_water", "overhead_internet",
            "overhead_accounting", "overhead_salary", "overhead_transport",
            "overhead_other"
        ]
        result = {k: getattr(self, f"spin_{k}").value() for k in _overhead_keys}
        result["overhead_hours_per_day"]  = self.spin_overhead_hours_per_day.value()
        result["overhead_days_per_month"] = self.spin_overhead_days_per_month.value()
        result["overhead_active_printers_mode"] = self.combo_overhead_printers_mode.currentData() or "auto"
        result["overhead_active_printers"] = self.spin_overhead_active_printers.value()
        return result

    def set_overhead_settings(self, settings_data: dict):
        """Carga los valores de overhead en los campos de la UI."""
        _overhead_keys = [
            "overhead_rent", "overhead_water", "overhead_internet",
            "overhead_accounting", "overhead_salary", "overhead_transport",
            "overhead_other"
        ]
        for k in _overhead_keys:
            getattr(self, f"spin_{k}").setValue(float(settings_data.get(k, 0.0)))
        self.spin_overhead_hours_per_day.setValue(
            int(settings_data.get("overhead_hours_per_day", 12))
        )
        self.spin_overhead_days_per_month.setValue(
            int(settings_data.get("overhead_days_per_month", 30))
        )
        # Modo de impresoras
        _mode = settings_data.get("overhead_active_printers_mode", "auto")
        _mode_idx = self.combo_overhead_printers_mode.findData(_mode)
        if _mode_idx >= 0:
            self.combo_overhead_printers_mode.setCurrentIndex(_mode_idx)
        self.spin_overhead_active_printers.setValue(
            max(1, int(settings_data.get("overhead_active_printers", 1)))
        )
        # Mostrar conteo de BD si viene en los datos
        if "overhead_active_printers_db_count" in settings_data:
            self.lbl_overhead_printers_count.setText(
                f"{settings_data['overhead_active_printers_db_count']} impresoras"
            )
        self._recalc_overhead_display()

    def toggle_editing(self):
        """Alterna entre modo edición y solo lectura"""
        self.is_editing = not self.is_editing
        
        if self.is_editing:
            self.enable_editing()
        else:
            self.disable_editing()
    
    def enable_editing(self):
        """Habilita el modo de edición"""
        self.is_editing = True
        
        # Actualizar botones - Mostrar botones de acción, ocultar botones de control
        self.btn_save.setEnabled(True)
        self.btn_save.setVisible(True)
        self.btn_cancel.setEnabled(True)
        self.btn_cancel.setVisible(True)
        self.btn_edit.setVisible(False)  # Ocultar desbloquear
        self.btn_reload.setVisible(False)  # Ocultar refrescar
        
        # Bloquear navegación del tab principal y botón de preferencias
        self._block_main_navigation(True)
        
        # Habilitar campos de empresa
        for field in self.company_fields.values():
            field.setReadOnly(False)
        
        # Habilitar campos de costos
        for field in self.cost_fields.values():
            field.setEnabled(True)
        self.electricity_peak_multiplier.setEnabled(True)
        self.commission_tax_shield.setEnabled(True)

        # Habilitar campos de overhead
        for _k in ['overhead_rent', 'overhead_water', 'overhead_internet',
                   'overhead_accounting', 'overhead_salary', 'overhead_transport',
                   'overhead_other']:
            getattr(self, f'spin_{_k}').setEnabled(True)
        self.spin_overhead_hours_per_day.setEnabled(True)
        self.spin_overhead_days_per_month.setEnabled(True)
        self.combo_overhead_printers_mode.setEnabled(True)
        if self.combo_overhead_printers_mode.currentData() == "manual":
            self.spin_overhead_active_printers.setEnabled(True)
        self.currency_combo.setEnabled(True)
        self.lbl_exchange_rates.setEnabled(True)
        self.pdf_title.setReadOnly(False)
        self.pdf_subtitle.setReadOnly(False)
        self.pdf_font_family.setEnabled(True)
        self.pdf_primary_color.setReadOnly(False)
        self.pdf_color_pick_btn.setEnabled(True)
        self.include_iva.setEnabled(True)
        self.include_error_margin.setEnabled(True)
        self.include_post_processing.setEnabled(True)  # Ahora se puede habilitar en modo edición
        self.pdf_display_mode.setEnabled(True)
        self.pdf_summary_label.setReadOnly(
            self.pdf_display_mode.currentData() != "summary"
        )
        self.footer_comments.setReadOnly(False)

        # Habilitar campos de Nota
        self.note_title.setReadOnly(False)
        self.note_font_family.setEnabled(True)
        self.note_primary_color.setReadOnly(False)
        self.note_color_pick_btn.setEnabled(True)
        self.note_show_tax.setEnabled(True)
        self.note_display_mode.setEnabled(True)
        self.note_postprocessing_mode.setEnabled(True)
        self.note_failure_margin_mode.setEnabled(True)
        # Etiqueta de resumen solo si el modo es Resumido
        self.note_summary_label.setReadOnly(
            self.note_display_mode.currentData() != "summary"
        )
        self.note_validity_enabled.setEnabled(True)
        self.note_validity_days.setEnabled(self.note_validity_enabled.isChecked())

        # Habilitar OBS de nota
        self.note_obs_text.setReadOnly(False)
        self.auto_save_interval.setEnabled(True)
        self.backup_enabled.setEnabled(True)
        self.backup_frequency.setEnabled(True)

        # Habilitar combos de idioma y región
        self.language_combo.setEnabled(True)
        self.locale_combo.setEnabled(True)

        # Cambiar visibilidad de QLabels de logo (mostrar vista previa)
        self.current_logo_display.setVisible(False)
        self.logo_preview.setVisible(True)
        
        # Habilitar botones de gestión de logo
        self.select_logo_btn.setEnabled(True)
        # El botón de eliminar se habilita si hay un logo actualmente
        has_logo = self.current_logo_path is not None and os.path.exists(self.current_logo_path)
        self.remove_logo_btn.setEnabled(has_logo)
        
        # Habilitar botones de gestión de base de datos
        self.btn_create_backup.setEnabled(True)
        self.btn_delete_backup.setEnabled(False)  # Se habilita al seleccionar un backup
        self.btn_restore_backup.setEnabled(False)  # Se habilita al seleccionar backup compatible
        self.btn_open_backup_folder.setEnabled(True)
        self.backup_table.setEnabled(True)
        
        # Notificar al panel de procesos
        self._notify_status("Modo edición habilitado")
    
    def disable_editing(self):
        """Deshabilita el modo de edición"""
        self.is_editing = False
        
        # Actualizar botones - Ocultar botones de acción, mostrar botones de control
        self.btn_save.setEnabled(False)
        self.btn_save.setVisible(False)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setVisible(False)
        self.btn_edit.setVisible(True)  # Mostrar desbloquear
        self.btn_reload.setVisible(True)  # Mostrar refrescar
        
        # Desbloquear navegación del tab principal y botón de preferencias
        self._block_main_navigation(False)
        
        # Deshabilitar campos de empresa
        for field in self.company_fields.values():
            field.setReadOnly(True)
        
        # Deshabilitar campos de costos
        for field in self.cost_fields.values():
            field.setEnabled(False)
        self.electricity_peak_multiplier.setEnabled(False)
        self.commission_tax_shield.setEnabled(False)

        # Deshabilitar campos de overhead
        for _k in ['overhead_rent', 'overhead_water', 'overhead_internet',
                   'overhead_accounting', 'overhead_salary', 'overhead_transport',
                   'overhead_other']:
            getattr(self, f'spin_{_k}').setEnabled(False)
        self.spin_overhead_hours_per_day.setEnabled(False)
        self.spin_overhead_days_per_month.setEnabled(False)
        self.combo_overhead_printers_mode.setEnabled(False)
        self.spin_overhead_active_printers.setEnabled(False)

        # Deshabilitar otros campos
        self.currency_combo.setEnabled(False)
        self.lbl_exchange_rates.setEnabled(False)
        self.pdf_title.setReadOnly(True)
        self.pdf_subtitle.setReadOnly(True)
        self.pdf_font_family.setEnabled(False)
        self.pdf_primary_color.setReadOnly(True)
        self.pdf_color_pick_btn.setEnabled(False)
        self.include_iva.setEnabled(False)
        self.include_error_margin.setEnabled(False)
        self.include_post_processing.setEnabled(False)  # Deshabilitado en modo solo lectura
        self.pdf_display_mode.setEnabled(False)
        self.pdf_summary_label.setReadOnly(True)
        self.footer_comments.setReadOnly(True)

        # Deshabilitar campos de Nota
        self.note_title.setReadOnly(True)
        self.note_font_family.setEnabled(False)
        self.note_primary_color.setReadOnly(True)
        self.note_color_pick_btn.setEnabled(False)
        self.note_show_tax.setEnabled(False)
        self.note_display_mode.setEnabled(False)
        self.note_postprocessing_mode.setEnabled(False)
        self.note_failure_margin_mode.setEnabled(False)
        self.note_summary_label.setReadOnly(True)
        self.note_validity_enabled.setEnabled(False)
        self.note_validity_days.setEnabled(False)

        # Deshabilitar OBS de nota
        self.note_obs_text.setReadOnly(True)

        self.auto_save_interval.setEnabled(False)
        self.backup_enabled.setEnabled(False)
        self.backup_frequency.setEnabled(False)

        # Deshabilitar combos de idioma y región
        self.language_combo.setEnabled(False)
        self.locale_combo.setEnabled(False)

        # Cambiar visibilidad de QLabels de logo (mostrar logo actual)
        self.current_logo_display.setVisible(True)
        self.logo_preview.setVisible(False)
        
        # Deshabilitar botones de gestión de logo
        self.select_logo_btn.setEnabled(False)
        self.remove_logo_btn.setEnabled(False)
        
        # Deshabilitar botones de gestión de base de datos
        self.btn_create_backup.setEnabled(False)
        self.btn_restore_backup.setEnabled(False)
        self.btn_delete_backup.setEnabled(False)
        self.btn_open_backup_folder.setEnabled(False)
        self.backup_table.setEnabled(False)
        self.backup_table.clearSelection()
        
        # Notificar al panel de procesos
        self._notify_status("Modo solo lectura")
    
    def save_settings(self):
        """Guarda las configuraciones"""
        if not self.is_editing:
            return
        
        try:
            # Recopilar todos los datos
            settings_data = self.collect_all_settings()
            
            # Emitir señal para guardar
            self.save_requested.emit(settings_data)
            
            # Deshabilitar edición
            self.disable_editing()

            self._notify_status("Configuraciones guardadas exitosamente ✅")
           
            
        except Exception as e:
            logger.error("SystemSettings", f"Error al guardar configuraciones: {str(e)}")
            QMessageBox.critical(self, tr(I18N.Dialogs.ERROR_TITLE), 
                tr(I18N.Systemsettings.MSG_SAVE_CRITICAL_TEXT))
    
    def show_save_confirmation(self, success: bool):
        """Muestra confirmación de que se guardaron las configuraciones"""
        if success:
            # Mostrar mensaje de éxito
            self._notify_status("💾 Configuraciones guardadas")
            # Mostrar mensaje emergente de confirmación
            QMessageBox.information(
                self, 
                tr(I18N.Systemsettings.MSG_SAVED_TITLE),                
                tr(I18N.Systemsettings.MSG_SAVED_TEXT)
            )
        else:
            self._notify_status("❌ Error al guardar configuraciones")
            
            # Mostrar mensaje emergente de error
            QMessageBox.critical(
                self, 
                tr(I18N.Systemsettings.MSG_SAVE_ERROR_TITLE),                
                tr(I18N.Systemsettings.MSG_SAVE_ERROR_TEXT)
            )
    
    def cancel_editing(self):
        """Cancela la edición y restaura valores originales"""
        if not self.is_editing:
            return
        
        # Restaurar valores originales
        self.load_settings(self.settings_data)
        
        # Deshabilitar edición
        self.disable_editing()
        
        # Notificar al panel de procesos
        self._notify_status("Cambios cancelados, valores restaurados")
    
    def reload_settings(self):
        """Recarga las configuraciones desde la base de datos"""
        # Emitir señal para recargar (el presenter manejará esto)
        self.settings_changed.emit({})
        
        self._notify_status("Configuraciones recargadas desde la base de datos")
    
    def _populate_currency_combo(self):
        """Llena el combo de monedas con datos del presenter"""
        if not hasattr(self, 'presenter') or self.presenter is None:
            return
        
        self.currency_combo.clear()
        
        currency_options = self.presenter.get_currency_options()
        for option in currency_options:
            self.currency_combo.addItem(option["text"], option["code"])
        
        # Seleccionar moneda actual
        current_currency = self.presenter.get_base_currency()
        currency_found = False
        
        for i in range(self.currency_combo.count()):
            if self.currency_combo.itemData(i) == current_currency:
                self.currency_combo.setCurrentIndex(i)
                currency_found = True
                break
        
        # Si la moneda actual no está disponible (fue deshabilitada), seleccionar USD por defecto
        if not currency_found:
            for i in range(self.currency_combo.count()):
                if self.currency_combo.itemData(i) == "USD":
                    self.currency_combo.setCurrentIndex(i)
                    logger.info("SystemSettings", 
                        f"La moneda {current_currency} fue deshabilitada. "
                        "Se seleccionó USD (moneda pivote) por defecto.")
                    break
    
    def _on_exchange_rates_label_clicked(self, event):
        """Abre el diálogo de ajuste de tasas de cambio al hacer clic en el label"""
        if not self.lbl_exchange_rates.isEnabled():
            return
            
        from presentation.modules.main.views.exchange_rates_dialog import ExchangeRatesDialog
        
        dialog = ExchangeRatesDialog(self)
        if dialog.exec():
            # Recargar las monedas después de modificar las tasas
            self._populate_currency_combo()
    
    def collect_all_settings(self) -> Dict[str, Any]:
        """Recopila todas las configuraciones de la UI"""
        settings = {}
        
        # Datos de empresa
        for key, field in self.company_fields.items():
            settings[key] = field.text().strip()
        
        # Datos de costos
        for key, field in self.cost_fields.items():
            settings[key] = field.value()
        settings['electricity_peak_multiplier'] = self.electricity_peak_multiplier.value()
        settings['commission_tax_shield'] = self.commission_tax_shield.isChecked()

        # Overhead del negocio
        settings.update(self.get_overhead_settings())

        # Moneda base seleccionada
        if hasattr(self, 'currency_combo') and self.currency_combo.count() > 0:
            settings['base_currency'] = self.currency_combo.currentData()
        
        # Otros campos
        settings['pdf_title'] = self.pdf_title.text().strip()
        settings['pdf_subtitle'] = self.pdf_subtitle.text().strip()
        settings['pdf_font_family'] = self.pdf_font_family.currentText()
        settings['include_iva'] = self.include_iva.isChecked()
        
        # Margen de error
        settings['include_error_margin'] = self.include_error_margin.isChecked()
        
        # Post-Procesado (funcionalidad futura)
        settings['include_post_processing'] = self.include_post_processing.isChecked()
        
        settings['footer_comments'] = self.footer_comments.toPlainText().strip()
        settings['pdf_primary_color'] = self.pdf_primary_color.text().strip()
        settings['pdf_display_mode'] = self.pdf_display_mode.currentData() or "detailed"
        settings['pdf_summary_label'] = self.pdf_summary_label.text().strip()

        # Configuraciones de Nota de Precios
        settings['note_title'] = self.note_title.text().strip()
        settings['note_font_family'] = self.note_font_family.currentText()
        settings['note_primary_color'] = self.note_primary_color.text().strip()
        settings['note_display_mode'] = self.note_display_mode.currentData() or "summary"
        settings['note_summary_label'] = self.note_summary_label.text().strip()
        settings['note_postprocessing_mode'] = "in_commission" if self.note_postprocessing_mode.isChecked() else "separate"
        settings['note_failure_margin_mode'] = "in_operation" if self.note_failure_margin_mode.isChecked() else "separate"
        settings['note_show_tax'] = self.note_show_tax.isChecked()
        settings['note_validity_enabled'] = self.note_validity_enabled.isChecked()
        settings['note_validity_days'] = self.note_validity_days.value()
        settings['note_obs_text'] = self.note_obs_text.toPlainText().strip()

        settings['auto_save_interval'] = self.auto_save_interval.value()
        settings['backup_enabled'] = self.backup_enabled.isChecked()
        settings['backup_frequency'] = self.backup_frequency.value()
        
        # Configuración de logo
        logo_settings = self.get_logo_settings()
        settings.update(logo_settings)

        # Idioma y región
        if hasattr(self, 'language_combo') and self.language_combo.count() > 0:
            settings['language'] = self.language_combo.currentData()
        if hasattr(self, 'locale_combo') and self.locale_combo.count() > 0:
            settings['locale'] = self.locale_combo.currentData()

        return settings
    
    def load_settings(self, settings_data: Dict[str, Any]):
        """Carga las configuraciones en la UI"""
        self.settings_data = settings_data.copy()  # Guardar para cancelar
        
        # Cargar datos de empresa
        for key, field in self.company_fields.items():
            value = settings_data.get(key, "")
            field.setText(str(value))
        
        # Cargar datos de costos
        for key, field in self.cost_fields.items():
            value = settings_data.get(key, 0.0)
            field.setValue(float(value))
        self.electricity_peak_multiplier.setValue(max(1.0, float(settings_data.get('electricity_peak_multiplier', 1.6))))
        self.commission_tax_shield.setChecked(bool(settings_data.get('commission_tax_shield', False)))
        # Actualizar label del blindaje con el IVA cargado
        self._update_tax_shield_label(float(settings_data.get('tax_rate', 10.0)))

        # Cargar overhead
        self.set_overhead_settings(settings_data)

        # Cargar monedas disponibles en el ComboBox
        self._populate_currency_combo()

        # Cargar combos de idioma y región
        self._populate_language_combo()
        self._populate_locale_combo()

        # Cargar otros campos
        self.pdf_title.setText(settings_data.get('pdf_title', 'PRESUPUESTO'))
        self.pdf_subtitle.setText(settings_data.get('pdf_subtitle', 'Impresión 3D'))
        
        # Cargar fuente del PDF
        pdf_font = settings_data.get('pdf_font_family', 'Lato')
        index = self.pdf_font_family.findText(pdf_font)
        if index >= 0:
            self.pdf_font_family.setCurrentIndex(index)
        
        self.include_iva.setChecked(settings_data.get('include_iva', True))
        
        # Margen de error
        self.include_error_margin.setChecked(settings_data.get('include_error_margin', False))
        
        # Post-Procesado (funcionalidad futura)
        self.include_post_processing.setChecked(settings_data.get('include_post_processing', False))
        
        self.footer_comments.setPlainText(settings_data.get('footer_comments', ''))
        self.pdf_primary_color.setText(settings_data.get('pdf_primary_color', ''))
        _pdf_mode = settings_data.get('pdf_display_mode', 'detailed')
        _pdf_mode_idx = self.pdf_display_mode.findData(_pdf_mode)
        self.pdf_display_mode.setCurrentIndex(_pdf_mode_idx if _pdf_mode_idx >= 0 else 0)
        self.pdf_summary_label.setText(settings_data.get('pdf_summary_label', 'Servicio de Impresión 3D'))

        # Cargar configuraciones de Nota de Precios
        self.note_title.setText(settings_data.get('note_title', 'Nota de Precios'))
        note_font = settings_data.get('note_font_family', 'Lato')
        note_font_index = self.note_font_family.findText(note_font)
        if note_font_index >= 0:
            self.note_font_family.setCurrentIndex(note_font_index)
        self.note_primary_color.setText(settings_data.get('note_primary_color', ''))
        _mode = settings_data.get('note_display_mode', 'summary')
        _mode_idx = self.note_display_mode.findData(_mode)
        self.note_display_mode.setCurrentIndex(_mode_idx if _mode_idx >= 0 else 1)
        self.note_summary_label.setText(settings_data.get('note_summary_label', 'Servicio de Impresión 3D'))
        _pp = settings_data.get('note_postprocessing_mode', 'separate')
        self.note_postprocessing_mode.setChecked(_pp == 'in_commission')
        _fm = settings_data.get('note_failure_margin_mode', 'separate')
        self.note_failure_margin_mode.setChecked(_fm == 'in_operation')
        self.note_show_tax.setChecked(settings_data.get('note_show_tax', True))
        self.note_validity_enabled.setChecked(settings_data.get('note_validity_enabled', True))
        self.note_validity_days.setValue(settings_data.get('note_validity_days', 30))
        self.note_obs_text.setPlainText(settings_data.get('note_obs_text', ''))

        self.auto_save_interval.setValue(settings_data.get('auto_save_interval', 300))
        self.backup_enabled.setChecked(settings_data.get('backup_enabled', True))
        self.backup_frequency.setValue(settings_data.get('backup_frequency', 7))
        
        # Cargar configuración de logo
        self.load_logo_settings(settings_data)
        
        # Asegurar visibilidad correcta basada en el modo actual
        if self.is_editing:
            self.current_logo_display.setVisible(False)
            self.logo_preview.setVisible(True)
        else:
            self.current_logo_display.setVisible(True)
            self.logo_preview.setVisible(False)
    
    def select_logo_file(self):
        """Abre el diálogo para seleccionar un archivo de logo"""
        if not self.is_editing:
            QMessageBox.information(self, tr(I18N.Systemsettings.MSG_EDIT_REQUIRED_TITLE), 
                                  tr(I18N.Systemsettings.MSG_EDIT_REQUIRED_LOGO_TEXT))
            return
        
        # Filtro para archivos PNG
        from core.utils.path_helper import get_user_start_dir
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Seleccionar Logo para PDF",
            get_user_start_dir(),
            "Archivos PNG (*.png);;Todos los archivos (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # Validar que sea un archivo PNG
            if not file_path.lower().endswith('.png'):
                QMessageBox.warning(self, tr(I18N.Systemsettings.MSG_INVALID_FORMAT_TITLE), 
                                  tr(I18N.Systemsettings.MSG_INVALID_FORMAT_TEXT))
                return
            
            # Abrir herramienta de recorte automáticamente
            logger.info("SystemSettings", f"Abriendo herramienta de recorte para: {file_path}")
            crop_dialog = LogoCropDialog(file_path, parent=self)
            
            # Si el usuario acepta el recorte
            if crop_dialog.exec() == crop_dialog.DialogCode.Accepted:
                cropped_path = crop_dialog.cropped_path
                
                if not cropped_path or not os.path.exists(cropped_path):
                    QMessageBox.warning(self, tr(I18N.Dialogs.ERROR_TITLE), 
                                      "No se pudo obtener la imagen recortada.")
                    return
                
                # Validar el archivo recortado
                if not self.validate_logo_file(cropped_path):
                    return
                
                # Copiar archivo recortado a la carpeta de logos
                new_logo_path = self.copy_logo_to_resources(cropped_path)
                
                # Actualizar configuración
                self.current_logo_path = new_logo_path
                
                # Actualizar vista previa (visible en modo edición)
                self.update_logo_preview_display(new_logo_path)
                
                # Actualizar también el display del logo actual (aunque esté oculto)
                self.update_current_logo_display(new_logo_path)
                
                # Actualizar interfaz
                self.current_logo_label.setText(f"Logo: {os.path.basename(new_logo_path)}")
                self.remove_logo_btn.setEnabled(True)
                
                logger.info("SystemSettings", f"Logo procesado y guardado: {new_logo_path}")
                QMessageBox.information(self, tr(I18N.StatusBar.SUCCESS), 
                                      "Logo recortado y guardado correctamente.\nUse 'Guardar' para confirmar los cambios.")
            else:
                logger.info("SystemSettings", "Usuario canceló el recorte de logo")
            
        except Exception as e:
            logger.log_exception("SystemSettings", e, "procesar el logo")
            QMessageBox.critical(self, tr(I18N.Dialogs.ERROR_TITLE), 
                "No se pudo procesar el archivo de logo.\n\n"
                "Por favor, verifique que el archivo sea válido e intente nuevamente.")
    
    def remove_logo_file(self):
        """Elimina el logo actual"""
        if not self.is_editing:
            QMessageBox.information(self, tr(I18N.Systemsettings.MSG_EDIT_REQUIRED_TITLE), 
                                  tr(I18N.Systemsettings.MSG_EDIT_REQUIRED_REMOVE_TEXT))
            return
        
        reply = QMessageBox.question(
            self, tr(I18N.Buttons.CONFIRM), 
            "¿Está seguro de que desea eliminar el logo actual?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Eliminar archivo físico si existe
                if hasattr(self, 'current_logo_path') and self.current_logo_path:
                    if os.path.exists(self.current_logo_path):
                        os.remove(self.current_logo_path)
                
                # Resetear configuración
                self.current_logo_path = None
                
                # Actualizar interfaz
                self.current_logo_label.setText("No hay logo configurado")
                
                # Actualizar ambos displays
                self.current_logo_display.clear()
                self.current_logo_display.setText("Sin logo\n(720x210 px)")
                
                self.logo_preview.clear()
                self.logo_preview.setText("Seleccione un logo\n(720x210 px)")
                
                self.remove_logo_btn.setEnabled(False)
                
                QMessageBox.information(self, tr(I18N.StatusBar.SUCCESS), 
                                      "Logo eliminado correctamente.\nUse 'Guardar' para confirmar los cambios.")
                
            except Exception as e:
                logger.error("SystemSettings", f"Error al eliminar el logo: {str(e)}")
                QMessageBox.critical(self, tr(I18N.Dialogs.ERROR_TITLE), 
                    "No se pudo eliminar el logo.\n\n"
                    "Por favor, intente nuevamente o contacte al soporte técnico.")
    
    def validate_logo_file(self, file_path: str) -> bool:
        """Valida que el archivo de logo cumpla con los requisitos"""
        try:
            # Verificar que es PNG
            if not file_path.lower().endswith('.png'):
                QMessageBox.warning(self, tr(I18N.Systemsettings.MSG_WRONG_FORMAT_TITLE), 
                                  tr(I18N.Systemsettings.MSG_WRONG_FORMAT_TEXT))
                return False
            
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                QMessageBox.warning(self, tr(I18N.Systemsettings.MSG_FILE_NOT_FOUND_TITLE), 
                                  tr(I18N.Systemsettings.MSG_FILE_NOT_FOUND_TEXT))
                return False
            
            # Verificar tamaño del archivo (máximo 5MB)
            file_size = os.path.getsize(file_path)
            if file_size > 5 * 1024 * 1024:  # 5MB
                QMessageBox.warning(self, tr(I18N.Systemsettings.MSG_FILE_TOO_BIG_TITLE), 
                                  tr(I18N.Systemsettings.MSG_FILE_TOO_BIG_TEXT))
                return False
            
            # Verificar dimensiones usando PIL
            with Image.open(file_path) as img:
                width, height = img.size
                
                if width != 720 or height != 210:
                    reply = QMessageBox.question(
                        self, tr(I18N.Systemsettings.MSG_WRONG_DIMENSIONS_TITLE),
                        tr(I18N.Systemsettings.MSG_WRONG_DIMENSIONS_TEXT).format(width=width, height=height),
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        return self.resize_logo(file_path)
                    else:
                        return False
            
            return True
            
        except Exception as e:
            logger.error("SystemSettings", f"Error al validar archivo de logo: {str(e)}")
            QMessageBox.critical(self, tr(I18N.Systemsettings.MSG_VALIDATION_ERROR_TITLE), 
                tr(I18N.Systemsettings.MSG_VALIDATION_ERROR_TEXT))
            return False
    
    def resize_logo(self, file_path: str) -> bool:
        """Redimensiona el logo a las dimensiones correctas"""
        temp_path = None
        try:
            with Image.open(file_path) as img:
                # Redimensionar manteniendo aspecto y agregando padding si es necesario
                img_resized = img.resize((720, 210), Image.Resampling.LANCZOS)
                
                # Crear archivo temporal en carpeta temporal del sistema (siempre hay permisos)
                temp_fd, temp_path = tempfile.mkstemp(suffix='.png', prefix='logo_resize_')
                os.close(temp_fd)  # Cerrar el descriptor de archivo
                
                # Guardar imagen redimensionada en archivo temporal
                img_resized.save(temp_path, 'PNG')
                
                # Sobrescribir el archivo original con el redimensionado
                shutil.copy2(temp_path, file_path)
                
                QMessageBox.information(self, tr(I18N.Systemsettings.MSG_RESIZED_TITLE), 
                                      tr(I18N.Systemsettings.MSG_RESIZED_TEXT))
                return True
        
        except PermissionError as e:
            logger.error("SystemSettings", f"Error de permisos al redimensionar logo: {str(e)}")
            QMessageBox.critical(self, tr(I18N.Systemsettings.MSG_PERMISSIONS_ERROR_TITLE), 
                tr(I18N.Systemsettings.MSG_PERMISSIONS_ERROR_TEXT))
            return False
                
        except Exception as e:
            logger.error("SystemSettings", f"Error al redimensionar logo: {str(e)}")
            QMessageBox.critical(self, tr(I18N.Systemsettings.MSG_RESIZE_ERROR_TITLE), 
                tr(I18N.Systemsettings.MSG_RESIZE_ERROR_TEXT))
            return False
        finally:
            # Limpiar archivo temporal si existe
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass  # Si falla la limpieza, no es crítico
    
    def copy_logo_to_resources(self, source_path: str) -> str:
        """Copia el logo a la carpeta de usuario con nombre único"""
        try:
            logos_path = logos_dir()
            # Generar nombre único
            random_id = random.randint(100000, 999999)
            filename = f"logo_for_PDF_company_{random_id}.png"
            dest_path = logos_path / filename

            while dest_path.exists():
                random_id = random.randint(100000, 999999)
                filename = f"logo_for_PDF_company_{random_id}.png"
                dest_path = logos_path / filename

            shutil.copy2(source_path, dest_path)
            # Retornar ruta absoluta para la configuración
            return str(dest_path)
        except Exception as e:
            logger.error("SystemSettings", f"Error al copiar logo a recursos: {str(e)}")
            raise Exception("No se pudo copiar el archivo de logo a la carpeta de recursos.")
    
   

    def load_logo_settings(self, settings: Dict[str, Any]):
        """Carga la configuración del logo, usando logo_default si logo_path no existe"""
        try:
            document_settings = settings.get("document_settings", {})
            logo_path = document_settings.get("logo_path", "")
            logo_default_rel = document_settings.get("logo_default", "resources/images/logo_for_PDF_company.png")
            logo_default_abs = build_resource_path(logo_default_rel)

            # Si la ruta es relativa, conviértela a absoluta usando logos_dir
            if logo_path and not os.path.isabs(logo_path):
                logo_path_abs = str(logos_dir() / os.path.basename(logo_path))
            else:
                logo_path_abs = logo_path

            # Si no existe el logo_path, intenta con logo_default absoluto
            if not logo_path_abs or not os.path.exists(logo_path_abs):
                logo_path_abs = logo_default_abs

            if logo_path_abs and os.path.exists(logo_path_abs):
                self.current_logo_path = logo_path_abs
                self.current_logo_label.setText(f"Logo: {os.path.basename(logo_path_abs)}")
                self.update_current_logo_display(logo_path_abs)
                self.update_logo_preview_display(logo_path_abs)
                # Solo habilitar el botón si estamos en modo edición
                self.remove_logo_btn.setEnabled(self.is_editing)
            else:
                self.current_logo_path = None
                self.current_logo_label.setText("No hay logo configurado")
                self.current_logo_display.clear()
                self.current_logo_display.setText("Sin logo\n(720x210 px)")
                self.logo_preview.clear()
                self.logo_preview.setText("Seleccione un logo\n(720x210 px)")
                self.remove_logo_btn.setEnabled(False)
        except Exception as e:
            logger.error("SystemSettings", f"Error al cargar configuración de logo: {str(e)}")
    
    def get_logo_settings(self) -> Dict[str, Any]:
        """Obtiene la configuración actual del logo"""
        if hasattr(self, 'current_logo_path') and self.current_logo_path:
            return {"logo_path": self.current_logo_path}
        return {"logo_path": ""}
    
    def update_logo_preview_display(self, logo_path: str):
        """Actualiza el display de vista previa del logo"""
        try:
            if logo_path and os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    # Escalar para que quepa en el widget manteniendo proporción
                    scaled_pixmap = pixmap.scaled(
                        self.logo_preview.size(), 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.logo_preview.setPixmap(scaled_pixmap)
                else:
                    self.logo_preview.setText("Error al\ncargar vista previa")
            else:
                self.logo_preview.clear()
                self.logo_preview.setText("Seleccione un logo\n(720x210 px)")
        except Exception as e:
            logger.error("SystemSettings", f"Error al actualizar vista previa de logo: {str(e)}")
            self.logo_preview.setText("Error al cargar\nvista previa")
    
    def update_current_logo_display(self, logo_path: str):
        """Actualiza el display del logo actual"""
        try:
            if logo_path and os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    # Escalar para que quepa en el widget manteniendo proporción
                    scaled_pixmap = pixmap.scaled(
                        self.current_logo_display.size(), 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.current_logo_display.setPixmap(scaled_pixmap)
                else:
                    self.current_logo_display.setText("Error al\ncargar logo")
            else:
                self.current_logo_display.clear()
                self.current_logo_display.setText("Sin logo\n(720x210 px)")
        except Exception as e:
            logger.error("SystemSettings", f"Error al actualizar display de logo: {str(e)}")
            self.current_logo_display.setText("Error al cargar\nlogo")
    
    def _block_main_navigation(self, block: bool):
        """Bloquea/desbloquea la navegación del tab principal y el botón de preferencias"""
        try:
            import winsound
            from PySide6.QtWidgets import QMessageBox
            
            # Buscar el main_window navegando por los padres
            parent = self.parent()
            while parent is not None:
                if hasattr(parent, 'ui'):
                    # Manejar el tabWidget principal (Presupuesto, Historial, etc.)
                    if hasattr(parent.ui, 'tabWidget'):
                        if block:
                            # Guardar el índice actual y conectar señal para bloquear cambios
                            self._original_tab_index = parent.ui.tabWidget.currentIndex()
                            parent.ui.tabWidget.currentChanged.connect(self._on_main_tab_change_attempt)
                        else:
                            # Desconectar señal y permitir navegación
                            try:
                                parent.ui.tabWidget.currentChanged.disconnect(self._on_main_tab_change_attempt)
                            except:
                                pass
                    
                    # Manejar el botón de preferencias
                    if hasattr(parent.ui, 'btn_settings_app'):
                        if block:
                            # Desconectar señal original y conectar la nuestra con alerta
                            try:
                                parent.ui.btn_settings_app.clicked.disconnect()
                            except:
                                pass
                            parent.ui.btn_settings_app.clicked.connect(self._on_preferences_button_attempt)
                        else:
                            # Reconectar señal original
                            try:
                                parent.ui.btn_settings_app.clicked.disconnect(self._on_preferences_button_attempt)
                            except:
                                pass
                            # Reconectar señal original del parent
                            if hasattr(parent, 'settings_requested'):
                                parent.ui.btn_settings_app.clicked.connect(parent.settings_requested.emit)
                    
                    break
                parent = parent.parent()
        except Exception as e:
            # Si hay algún error, simplemente continuar
            pass
    
    def _on_main_tab_change_attempt(self, index):
        """Maneja intentos de cambiar de tab principal durante edición"""
        try:
            import winsound
            from PySide6.QtWidgets import QMessageBox
            
            if self.is_editing:
                # Emitir sonido de alerta de Windows
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                
                # Mostrar mensaje informativo
                QMessageBox.information(
                    self,
                    tr(I18N.Systemsettings.MSG_EDITING_TITLE),
                    tr(I18N.Systemsettings.MSG_EDITING_TAB_TEXT)
                )
                
                # Regresar al tab original (Ajustes)
                parent = self.parent()
                while parent is not None:
                    if hasattr(parent, 'ui') and hasattr(parent.ui, 'tabWidget'):
                        parent.ui.tabWidget.blockSignals(True)
                        parent.ui.tabWidget.setCurrentIndex(self._original_tab_index)
                        parent.ui.tabWidget.blockSignals(False)
                        break
                    parent = parent.parent()
        except Exception as e:
            pass
    
    def _on_note_display_mode_changed(self):
        """Habilita o deshabilita note_summary_label según el modo seleccionado."""
        is_summary = self.note_display_mode.currentData() == "summary"
        if self.is_editing:
            self.note_summary_label.setReadOnly(not is_summary)

    def _on_note_validity_toggled(self, checked: bool):
        """Habilita o deshabilita note_validity_days según el estado del checkbox."""
        self.note_validity_days.setEnabled(self.is_editing and checked)

    _OBS_MAX_CHARS = 162

    def _limit_obs_text(self):
        """Recorta el texto de OBS si supera el límite de caracteres."""
        text = self.note_obs_text.toPlainText()
        if len(text) > self._OBS_MAX_CHARS:
            cursor = self.note_obs_text.textCursor()
            pos = cursor.position()
            self.note_obs_text.blockSignals(True)
            self.note_obs_text.setPlainText(text[:self._OBS_MAX_CHARS])
            cursor.setPosition(min(pos, self._OBS_MAX_CHARS))
            self.note_obs_text.setTextCursor(cursor)
            self.note_obs_text.blockSignals(False)

    def _on_preferences_button_attempt(self):
        """Maneja intentos de abrir preferencias durante edición"""
        try:
            import winsound
            from PySide6.QtWidgets import QMessageBox
            
            if self.is_editing:
                # Emitir sonido de alerta de Windows
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                
                # Mostrar mensaje informativo
                QMessageBox.information(
                    self,
                    tr(I18N.Systemsettings.MSG_EDITING_TITLE),
                    tr(I18N.Systemsettings.MSG_EDITING_PREFS_TEXT)
                )
        except Exception as e:
            pass

