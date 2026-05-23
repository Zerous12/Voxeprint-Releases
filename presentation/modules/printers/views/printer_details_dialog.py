"""
Diálogo para mostrar información detallada de una impresora.
Muestra todos los datos de la impresora de forma organizada y legible.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QGroupBox, QFrame,
    QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Optional
from datetime import datetime

from core.utils.currency_helper import CurrencyHelper
from core.managers.locale_manager import LocaleManager
from domain.models.printer import Printer
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class PrinterDetailsDialog(QDialog):
    """Diálogo para mostrar detalles completos de una impresora"""
    
    def __init__(self, parent=None, printer: Optional[Printer] = None):
        super().__init__(parent)
        
        self.printer = printer
        
        # Configurar UI
        self._setup_ui()
        
        # Cargar datos de la impresora
        if self.printer:
            self._load_printer_details()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar ventana
        printer_name = self.printer.name if self.printer else tr(I18N.Printer.HEADER_PRINTER_NAME)
        self.setWindowTitle(f" {tr(I18N.Customer.DIALOG_DETAIL_TITLE)}: {printer_name}")
        self.setModal(True)
        self.setMinimumSize(500, 480)
        self.resize(550, 480)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Header
        self._setup_header(main_layout)
        
        # Área de scroll para el contenido
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Widget contenedor del scroll
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        
        # Secciones de información
        self._setup_basic_info_section(scroll_layout)
        self._setup_technical_specs_section(scroll_layout)
        self._setup_costs_section(scroll_layout)
        self._setup_maintenance_section(scroll_layout)
        self._setup_calculations_section(scroll_layout)
        self._setup_metadata_section(scroll_layout)
        
        # Configurar scroll
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Botón cerrar
        self._setup_close_button(main_layout)
    
    def _setup_header(self, main_layout):
        """Configura el header del diálogo SIN QFrame"""
        header_layout = QHBoxLayout()
                
        # Información principal
        info_layout = QVBoxLayout()
        
        # Nombre de la impresora
        self.name_label = QLabel(tr(I18N.Printer.HEADER_PRINTER_NAME))
        name_font = QFont()
        name_font.setPointSize(18)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        
        # Marca y modelo
        self.brand_model_label = QLabel(tr(I18N.Printer.HEADER_BRAND_MODEL))
        self.brand_model_label.setStyleSheet("color: #AAA; font-size: 14px;")
        
        # Status
        self.status_label = QLabel(tr(I18N.Printer.STATUS_ACTIVE_ICON))
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.brand_model_label)
        info_layout.addWidget(self.status_label)
        info_layout.addStretch()
                
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
    
    def _setup_basic_info_section(self, main_layout):
        """Configura la sección de información básica"""
        basic_group = QGroupBox(tr(I18N.Printer.GROUP_BASIC_INFO))
        basic_layout = QFormLayout(basic_group)
        
        self.name_detail_label = QLabel()
        self.brand_label = QLabel()
        self.model_label = QLabel()
        
        basic_layout.addRow(tr(I18N.Printer.LABEL_NAME_DETAIL), self.name_detail_label)
        basic_layout.addRow(tr(I18N.Printer.LABEL_BRAND), self.brand_label)
        basic_layout.addRow(tr(I18N.Printer.LABEL_MODEL_DETAIL), self.model_label)
        
        main_layout.addWidget(basic_group)
    
    def _setup_technical_specs_section(self, main_layout):
        """Configura la sección de especificaciones técnicas"""
        tech_group = QGroupBox(tr(I18N.Printer.GROUP_TECHNICAL_SPECS))
        tech_layout = QFormLayout(tech_group)
        
        self.purchase_cost_label = QLabel()
        self.depreciation_rate_label = QLabel()
        self.estimated_power_label = QLabel()
        
        tech_layout.addRow(tr(I18N.Printer.LABEL_PURCHASE_COST), self.purchase_cost_label)
        tech_layout.addRow(tr(I18N.Printer.LABEL_LIFESPAN_ESTIMATED), self.depreciation_rate_label)
        tech_layout.addRow(tr(I18N.Printer.LABEL_REAL_CONSUMPTION), self.estimated_power_label)
        
        main_layout.addWidget(tech_group)
    
    def _setup_costs_section(self, main_layout):
        """Configura la sección de costos operativos"""
        costs_group = QGroupBox(tr(I18N.Printer.GROUP_COSTS))
        costs_layout = QFormLayout(costs_group)
        
        self.electricity_cost_label = QLabel()
        self.wear_rate_label = QLabel()
        self.total_operational_cost_label = QLabel()
        
        costs_layout.addRow(tr(I18N.Printer.LABEL_ELECTRICAL_COST_HOUR), self.electricity_cost_label)
        costs_layout.addRow(tr(I18N.Printer.LABEL_WEAR_HOUR), self.wear_rate_label)
        costs_layout.addRow(tr(I18N.Printer.LABEL_TOTAL_COST_HOUR), self.total_operational_cost_label)
        
        main_layout.addWidget(costs_group)
    
    def _setup_maintenance_section(self, main_layout):
        """Configura la sección de mantenimiento"""
        maint_group = QGroupBox(tr(I18N.Printer.GROUP_MAINTENANCE))
        maint_layout = QFormLayout(maint_group)
        
        self.maintenance_cost_label = QLabel()
        self.maintenance_interval_label = QLabel()
        self.maintenance_cost_per_hour_label = QLabel()
        
        maint_layout.addRow(tr(I18N.Printer.LABEL_MAINTENANCE_COST), self.maintenance_cost_label)
        maint_layout.addRow(tr(I18N.Printer.LABEL_MAINTENANCE_INTERVAL), self.maintenance_interval_label)
        maint_layout.addRow(tr(I18N.Printer.LABEL_MAINTENANCE_COST_HOUR), self.maintenance_cost_per_hour_label)
        
        main_layout.addWidget(maint_group)
    
    def _setup_calculations_section(self, main_layout):
        """Configura la sección de cálculos derivados"""
        calc_group = QGroupBox(tr(I18N.Printer.GROUP_CALCULATIONS))
        calc_layout = QFormLayout(calc_group)
        
        self.total_cost_per_hour_label = QLabel()
        self.cost_per_minute_label = QLabel()
        self.daily_operation_cost_label = QLabel()
        
        calc_layout.addRow(tr(I18N.Printer.LABEL_TOTAL_COST_HOUR_FULL), self.total_cost_per_hour_label)
        calc_layout.addRow(tr(I18N.Printer.LABEL_COST_MINUTE), self.cost_per_minute_label)
        calc_layout.addRow(tr(I18N.Printer.LABEL_DAILY_COST), self.daily_operation_cost_label)
        
        main_layout.addWidget(calc_group)
    
    def _setup_metadata_section(self, main_layout):
        """Configura la sección de metadatos"""
        meta_group = QGroupBox(tr(I18N.Printer.GROUP_SYSTEM_INFO))
        meta_layout = QFormLayout(meta_group)
        
        self.created_at_label = QLabel()
        self.updated_at_label = QLabel()
        self.active_status_label = QLabel()
        
        meta_layout.addRow(tr(I18N.Printer.LABEL_REGISTRATION_DATE), self.created_at_label)
        meta_layout.addRow(tr(I18N.Printer.LABEL_LAST_MODIFIED), self.updated_at_label)
        meta_layout.addRow(tr(I18N.Printer.LABEL_ACTIVE_STATUS), self.active_status_label)
        
        main_layout.addWidget(meta_group)
    
    def _setup_close_button(self, main_layout):
        """Configura el botón de cerrar"""
        button_layout = QHBoxLayout()
        
        close_button = QPushButton(tr(I18N.Buttons.CLOSE))
        close_button.setDefault(True)
        close_button.setFixedHeight(30)
        close_button.setFixedWidth(105)
        close_button.clicked.connect(self.accept)
       
        
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
    
    def _load_printer_details(self):
        """Carga los detalles de la impresora en la interfaz"""
        if not self.printer:
            return
        
        # Header
        self.name_label.setText(self.printer.name or tr(I18N.Printer.DEFAULT_NO_NAME))
        brand_model = f"{self.printer.brand or tr(I18N.Printer.DEFAULT_NO_BRAND)} - {self.printer.model or tr(I18N.Printer.DEFAULT_NO_MODEL)}"
        self.brand_model_label.setText(brand_model)
        
        status_text = tr(I18N.Printer.STATUS_ACTIVE_ICON) if self.printer.is_active else tr(I18N.Printer.STATUS_INACTIVE_ICON)
        status_color = "#4CAF50" if self.printer.is_active else "#F44336"
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        
        # Información básica
        self.name_detail_label.setText(self.printer.name or tr(I18N.Printer.DEFAULT_NO_NAME))
        self.brand_label.setText(self.printer.brand or tr(I18N.Printer.DEFAULT_NOT_SPECIFIED))
        self.model_label.setText(self.printer.model or tr(I18N.Printer.DEFAULT_NOT_SPECIFIED))
        
        # Especificaciones técnicas
        formatted_purchase_cost = CurrencyHelper.format(
            self.printer.purchase_cost,
            self.printer.currency_code
        )
        self.purchase_cost_label.setText(formatted_purchase_cost)
        # Mostrar vida útil en lugar de depreciation_rate
        self.depreciation_rate_label.setText(f"{self.printer.useful_life_hours:,.0f} {tr(I18N.Printer.UNIT_HOURS)}")
        
        # Mostrar consumo real en watts
        self.estimated_power_label.setText(f"{self.printer.power_consumption_watts:.0f} W")
        
        # Costos operativos con nueva estructura
        formatted_elec = CurrencyHelper.format(
            self.printer.electricity_cost_per_hour,
            self.printer.currency_code
        )
        self.electricity_cost_label.setText(formatted_elec)
        # Mostrar desgaste individual (componente del costo de operación)
        formatted_wear = CurrencyHelper.format(
            self.printer.machine_wear_cost_per_hour,
            self.printer.currency_code
        )
        self.wear_rate_label.setText(formatted_wear)
        
        # Costo de servicio total (desgaste + mantenimiento)
        formatted_service = CurrencyHelper.format(
            self.printer.service_cost_per_hour,
            self.printer.currency_code
        )
        self.total_operational_cost_label.setText(formatted_service)
        self.total_operational_cost_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        
        # Mantenimiento
        formatted_maint = CurrencyHelper.format(
            self.printer.maintenance_cost,
            self.printer.currency_code
        )
        self.maintenance_cost_label.setText(formatted_maint)
        self.maintenance_interval_label.setText(f"{self.printer.maintenance_interval_hours:.0f} {tr(I18N.Printer.UNIT_HOURS)}")
        
        # Costo de mantenimiento por hora
        maint_per_hour = 0
        if self.printer.maintenance_interval_hours > 0:
            maint_per_hour = self.printer.maintenance_cost / self.printer.maintenance_interval_hours
        formatted_maint_per_hour = CurrencyHelper.format(
            maint_per_hour,
            self.printer.currency_code
        )
        self.maintenance_cost_per_hour_label.setText(formatted_maint_per_hour)
        
        # Cálculos derivados - usar el costo total de la impresora
        total_cost_per_hour = self.printer.electricity_cost_per_hour + self.printer.service_cost_per_hour
        formatted_total_hour = CurrencyHelper.format(
            total_cost_per_hour,
            self.printer.currency_code
        )
        self.total_cost_per_hour_label.setText(formatted_total_hour)
        self.total_cost_per_hour_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        
        cost_per_minute = total_cost_per_hour / 60
        formatted_per_minute = CurrencyHelper.format(
            cost_per_minute,
            self.printer.currency_code
        )
        self.cost_per_minute_label.setText(formatted_per_minute)
        
        daily_cost = total_cost_per_hour * 8  # 8 horas de trabajo
        formatted_daily = CurrencyHelper.format(
            daily_cost,
            self.printer.currency_code
        )
        self.daily_operation_cost_label.setText(formatted_daily)
        
        # Metadatos
        date_fmt = LocaleManager().get_date_format_strftime() + " %H:%M"
        if self.printer.created_at:
            try:
                val = self.printer.created_at
                if isinstance(val, str):
                    val = datetime.fromisoformat(val.replace('Z', '+00:00'))
                self.created_at_label.setText(val.strftime(date_fmt))
            except Exception:
                self.created_at_label.setText(str(self.printer.created_at))
        else:
            self.created_at_label.setText(tr(I18N.Printer.DEFAULT_NOT_AVAILABLE))
        
        if self.printer.updated_at:
            try:
                val = self.printer.updated_at
                if isinstance(val, str):
                    val = datetime.fromisoformat(val.replace('Z', '+00:00'))
                self.updated_at_label.setText(val.strftime(date_fmt))
            except Exception:
                self.updated_at_label.setText(str(self.printer.updated_at))
        else:
            self.updated_at_label.setText(tr(I18N.Printer.DEFAULT_NOT_AVAILABLE))
        
        active_text = tr(I18N.Printer.STATUS_ACTIVE_TEXT) if self.printer.is_active else tr(I18N.Printer.STATUS_INACTIVE_TEXT)
        active_color = "#4CAF50" if self.printer.is_active else "#F44336"
        self.active_status_label.setText(active_text)
        self.active_status_label.setStyleSheet(f"color: {active_color}; font-weight: bold;")
