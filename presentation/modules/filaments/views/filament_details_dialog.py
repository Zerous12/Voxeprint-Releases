"""
Diálogo para mostrar información detallada de un filamento.
Muestra todos los datos del filamento de forma organizada y legible.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QGroupBox, QFrame,
    QScrollArea, QWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from typing import Optional
from datetime import datetime

from core.utils.currency_helper import CurrencyHelper
from core.managers.locale_manager import LocaleManager
from domain.models.filament import Filament
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class FilamentDetailsDialog(QDialog):
    """Diálogo para mostrar detalles completos de un filamento"""
    
    def __init__(self, parent=None, filament: Optional[Filament] = None, facade=None):
        super().__init__(parent)
        
        self.filament = filament
        self.facade = facade
        
        # Configurar UI
        self._setup_ui()
        
        # Cargar datos del filamento
        if self.filament:
            self._load_filament_details()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar ventana
        filament_name = self.filament.name if self.filament else tr(I18N.Filament.HEADER_NAME)
        self.setWindowTitle(f"{tr(I18N.Customer.DIALOG_DETAIL_TITLE)}: {filament_name}")
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
        self._setup_characteristics_section(scroll_layout)
        self._setup_pricing_section(scroll_layout)
        self._setup_stock_section(scroll_layout)
        self._setup_rolls_section(scroll_layout)
        self._setup_calculations_section(scroll_layout)
        self._setup_metadata_section(scroll_layout)
        
        # Configurar scroll
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Botón cerrar
        self._setup_close_button(main_layout)
    
    def _setup_header(self, main_layout):
        """Configura el header del diálogo"""
        header_layout = QHBoxLayout()
                
        # Información principal
        info_layout = QVBoxLayout()
        
        # Nombre del filamento
        self.name_label = QLabel(tr(I18N.Filament.HEADER_NAME))
        name_font = QFont()
        name_font.setPointSize(18)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        
        # Marca y tipo
        self.brand_type_label = QLabel(tr(I18N.Filament.HEADER_BRAND_TYPE))
        self.brand_type_label.setStyleSheet("color: #AAA; font-size: 14px;")
        
        # Status
        self.status_label = QLabel(tr(I18N.Filament.STATUS_ACTIVE_ICON))
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.brand_type_label)
        info_layout.addWidget(self.status_label)
        info_layout.addStretch()
                
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
    
    def _setup_basic_info_section(self, main_layout):
        """Configura la sección de información básica"""
        basic_group = QGroupBox(tr(I18N.Filament.GROUP_BASIC_INFO))
        basic_layout = QFormLayout(basic_group)
        
        self.name_detail_label = QLabel()
        self.brand_label = QLabel()
        self.color_label = QLabel()
        
        basic_layout.addRow(tr(I18N.Filament.LABEL_NAME_DETAIL), self.name_detail_label)
        basic_layout.addRow(tr(I18N.Filament.LABEL_BRAND), self.brand_label)
        basic_layout.addRow(tr(I18N.Filament.LABEL_COLOR_DETAIL), self.color_label)
        
        main_layout.addWidget(basic_group)
    
    def _setup_characteristics_section(self, main_layout):
        """Configura la sección de características"""
        char_group = QGroupBox(tr(I18N.Filament.GROUP_CHARACTERISTICS))
        char_layout = QFormLayout(char_group)
        
        self.type_label = QLabel()
        self.weight_label = QLabel()
        self.notes_label = QLabel()
        
        char_layout.addRow(tr(I18N.Filament.LABEL_TYPE_MATERIAL), self.type_label)
        char_layout.addRow(tr(I18N.Filament.LABEL_WEIGHT_PER_ROLL), self.weight_label)
        char_layout.addRow(tr(I18N.Filament.LABEL_NOTES_DETAIL), self.notes_label)
        
        main_layout.addWidget(char_group)
    
    def _setup_pricing_section(self, main_layout):
        """Configura la sección de precios"""
        pricing_group = QGroupBox(tr(I18N.Filament.GROUP_PRICING))
        pricing_layout = QFormLayout(pricing_group)
        
        self.price_per_unit_label = QLabel()
        self.price_per_gram_label = QLabel()
        
        pricing_layout.addRow(tr(I18N.Filament.LABEL_PRICE_PER_ROLL), self.price_per_unit_label)
        pricing_layout.addRow(tr(I18N.Filament.LABEL_PRICE_PER_GRAM), self.price_per_gram_label)
        
        main_layout.addWidget(pricing_group)
    
    def _setup_stock_section(self, main_layout):
        """Configura la sección de inventario"""
        stock_group = QGroupBox(tr(I18N.Filament.GROUP_INVENTORY))
        stock_layout = QFormLayout(stock_group)
        
        self.quantity_rolls_label = QLabel()
        self.current_stock_label = QLabel()
        self.minimum_stock_label = QLabel()
        self.stock_status_label = QLabel()
        
        stock_layout.addRow(tr(I18N.Filament.LABEL_ROLL_COUNT), self.quantity_rolls_label)
        stock_layout.addRow(tr(I18N.Filament.LABEL_CURRENT_STOCK), self.current_stock_label)
        stock_layout.addRow(tr(I18N.Filament.LABEL_MIN_STOCK), self.minimum_stock_label)
        stock_layout.addRow(tr(I18N.Filament.LABEL_STOCK_STATUS), self.stock_status_label)
        
        main_layout.addWidget(stock_group)
    
    def _setup_rolls_section(self, main_layout):
        """Configura la sección de rollos individuales"""
        rolls_group = QGroupBox(tr(I18N.Filament.GROUP_ROLLS_DETAIL))
        rolls_layout = QVBoxLayout(rolls_group)
        
        self.rolls_table = QTableWidget()
        self.rolls_table.setColumnCount(5)
        self.rolls_table.setHorizontalHeaderLabels([
            tr(I18N.Filament.TABLE_COL_SKU),
            tr(I18N.Filament.TABLE_COL_INITIAL_WEIGHT),
            tr(I18N.Filament.TABLE_COL_CURRENT_WEIGHT),
            tr(I18N.Filament.TABLE_COL_USAGE_PCT),
            tr(I18N.Filament.TABLE_COL_PURCHASE_PRICE)
        ])
        self.rolls_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.rolls_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.rolls_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.rolls_table.setFrameShape(QTableWidget.Shape.NoFrame)
        self.rolls_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.rolls_table.setAlternatingRowColors(True)
        self.rolls_table.verticalHeader().setVisible(False)
        
        header = self.rolls_table.horizontalHeader()
        for col in range(5):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        
        self.rolls_table.setMaximumHeight(180)
        
        rolls_layout.addWidget(self.rolls_table)
        main_layout.addWidget(rolls_group)
    
    def _setup_calculations_section(self, main_layout):
        """Configura la sección de cálculos derivados"""
        calc_group = QGroupBox(tr(I18N.Filament.GROUP_CALCULATIONS))
        calc_layout = QFormLayout(calc_group)
        
        self.total_value_label = QLabel()
        self.available_weight_label = QLabel()
        
        calc_layout.addRow(tr(I18N.Filament.LABEL_TOTAL_VALUE), self.total_value_label)
        calc_layout.addRow(tr(I18N.Filament.LABEL_TOTAL_WEIGHT), self.available_weight_label)
        
        main_layout.addWidget(calc_group)
    
    def _setup_metadata_section(self, main_layout):
        """Configura la sección de metadatos"""
        meta_group = QGroupBox(tr(I18N.Filament.GROUP_SYSTEM_INFO))
        meta_layout = QFormLayout(meta_group)
        
        self.created_at_label = QLabel()
        self.updated_at_label = QLabel()
        self.active_status_label = QLabel()
        
        meta_layout.addRow(tr(I18N.Filament.LABEL_REGISTRATION_DATE), self.created_at_label)
        meta_layout.addRow(tr(I18N.Filament.LABEL_LAST_MODIFIED), self.updated_at_label)
        meta_layout.addRow(tr(I18N.Filament.LABEL_STATUS_DETAIL), self.active_status_label)
        
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
    
    def _load_filament_details(self):
        """Carga los detalles del filamento en la interfaz"""
        if not self.filament:
            return
        
        # Header
        self.name_label.setText(self.filament.name or tr(I18N.Filament.DEFAULT_NO_NAME))
        brand_type = f"{self.filament.brand or tr(I18N.Filament.DEFAULT_NO_BRAND)} - {self.filament.type.value if self.filament.type else tr(I18N.Filament.DEFAULT_NO_TYPE)}"
        self.brand_type_label.setText(brand_type)
        
        status_text = tr(I18N.Filament.STATUS_ACTIVE_ICON) if self.filament.is_active else tr(I18N.Filament.STATUS_INACTIVE_ICON)
        status_color = "#4CAF50" if self.filament.is_active else "#F44336"
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        
        # Información básica
        self.name_detail_label.setText(self.filament.name or tr(I18N.Filament.DEFAULT_NO_NAME))
        self.brand_label.setText(self.filament.brand or tr(I18N.Filament.DEFAULT_NOT_SPECIFIED))
        if self.filament.color:
            filament_color_name = self.filament.color.name if hasattr(self.filament.color, 'name') else str(self.filament.color)
            color_key = f"FilamentColor.{filament_color_name}"
            color_display = tr(color_key)
            self.color_label.setText(self.filament.color.value if color_display == color_key else color_display)
        else:
            self.color_label.setText(tr(I18N.Filament.DEFAULT_NOT_SPECIFIED))
        
        # Características
        self.type_label.setText(self.filament.type.value if self.filament.type else tr(I18N.Filament.DEFAULT_NOT_SPECIFIED))
        self.weight_label.setText(f"{self.filament.weight_grams:,.0f} g")
        self.notes_label.setText(self.filament.notes or tr(I18N.Filament.DEFAULT_NO_NOTES))
        self.notes_label.setWordWrap(True)
        
        # Precios
        formatted_price_unit = CurrencyHelper.format(
            self.filament.price_per_unit,
            self.filament.currency_code
        )
        self.price_per_unit_label.setText(formatted_price_unit)
        
        formatted_price_gram = CurrencyHelper.format(
            self.filament.price_per_gram,
            self.filament.currency_code
        )
        self.price_per_gram_label.setText(formatted_price_gram)
        
        # Inventario
        self.quantity_rolls_label.setText(tr(I18N.Filament.FORMAT_ROLL_COUNT, count=f"{self.filament.quantity_rolls:,}"))
        self.current_stock_label.setText(f"{self.filament.current_stock_grams:,.0f} g")
        self.minimum_stock_label.setText(f"{self.filament.minimum_stock_grams:,.0f} g")
        
        # Estado de stock
        stock_percentage = 0
        if self.filament.minimum_stock_grams > 0:
            stock_percentage = (self.filament.current_stock_grams / self.filament.minimum_stock_grams) * 100
        
        if self.filament.current_stock_grams <= 0:
            stock_status = tr(I18N.Filament.STOCK_NONE)
            stock_color = "#F44336"
        elif self.filament.current_stock_grams < self.filament.minimum_stock_grams:
            stock_status = tr(I18N.Filament.STOCK_LOW)
            stock_color = "#FF9800"
        else:
            stock_status = tr(I18N.Filament.STOCK_OK)
            stock_color = "#4CAF50"
        
        self.stock_status_label.setText(stock_status)
        self.stock_status_label.setStyleSheet(f"color: {stock_color}; font-weight: bold;")
        
        # Cálculos derivados
        rolls = []
        if self.facade and self.filament.id:
            rolls = self.facade.get_rolls_for_filament(self.filament.id)
        
        if rolls:
            total_value = sum(r.purchase_price for r in rolls if r.is_active)
        else:
            total_value = self.filament.quantity_rolls * self.filament.price_per_unit
        formatted_total_value = CurrencyHelper.format(
            total_value,
            self.filament.currency_code
        )
        self.total_value_label.setText(formatted_total_value)
        self.total_value_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        
        self.available_weight_label.setText(f"{self.filament.current_stock_grams:,.0f} g")
        
        # Poblar tabla de rollos
        self._load_rolls_table(rolls)
        
        # Metadatos
        date_fmt = LocaleManager().get_date_format_strftime() + " %H:%M"
        if self.filament.created_at:
            try:
                val = self.filament.created_at
                if isinstance(val, str):
                    val = datetime.fromisoformat(val.replace('Z', '+00:00'))
                self.created_at_label.setText(val.strftime(date_fmt))
            except Exception:
                self.created_at_label.setText(str(self.filament.created_at))
        else:
            self.created_at_label.setText(tr(I18N.Filament.DEFAULT_NOT_AVAILABLE))
        
        if self.filament.updated_at:
            try:
                val = self.filament.updated_at
                if isinstance(val, str):
                    val = datetime.fromisoformat(val.replace('Z', '+00:00'))
                self.updated_at_label.setText(val.strftime(date_fmt))
            except Exception:
                self.updated_at_label.setText(str(self.filament.updated_at))
        else:
            self.updated_at_label.setText(tr(I18N.Filament.DEFAULT_NOT_AVAILABLE))
        
        active_text = tr(I18N.Filament.STATUS_ACTIVE_TEXT) if self.filament.is_active else tr(I18N.Filament.STATUS_INACTIVE_TEXT)
        active_color = "#4CAF50" if self.filament.is_active else "#F44336"
        self.active_status_label.setText(active_text)
        self.active_status_label.setStyleSheet(f"color: {active_color}; font-weight: bold;")
    
    def _load_rolls_table(self, rolls):
        """Carga la tabla de rollos individuales"""
        active_rolls = [r for r in rolls if r.is_active] if rolls else []
        self.rolls_table.setRowCount(len(active_rolls))
        
        if not active_rolls:
            self.rolls_table.setRowCount(1)
            no_data = QTableWidgetItem(tr(I18N.Filament.NO_ROLLS_DATA))
            no_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rolls_table.setItem(0, 0, no_data)
            self.rolls_table.setSpan(0, 0, 1, 5)
            return
        
        currency = self.filament.currency_code if self.filament else None
        
        for row, roll in enumerate(active_rolls):
            # SKU
            sku_item = QTableWidgetItem(roll.sku or f"#{roll.id}")
            sku_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            sku_item.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            self.rolls_table.setItem(row, 0, sku_item)

            # Peso Inicial
            initial_item = QTableWidgetItem(f"{roll.initial_weight_grams:,.0f} g")
            initial_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rolls_table.setItem(row, 1, initial_item)
            
            # Peso Actual
            current_item = QTableWidgetItem(f"{roll.current_weight_grams:,.0f} g")
            current_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if roll.current_weight_grams <= 0:
                current_item.setForeground(QColor("#F44336"))
            elif roll.usage_percent >= 80:
                current_item.setForeground(QColor("#FF9800"))
            self.rolls_table.setItem(row, 2, current_item)
            
            # Uso %
            usage_item = QTableWidgetItem(f"{roll.usage_percent:.1f}%")
            usage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if roll.usage_percent >= 80:
                usage_item.setForeground(QColor("#FF9800"))
            self.rolls_table.setItem(row, 3, usage_item)
            
            # Precio Compra
            price_text = CurrencyHelper.format(roll.purchase_price, currency)
            price_item = QTableWidgetItem(price_text)
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rolls_table.setItem(row, 4, price_item)
