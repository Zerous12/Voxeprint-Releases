"""
Diálogo para modificar impresoras existentes.
Permite editar todos los campos usando el mismo estilo minimalista del diálogo de agregar.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel,
    QGroupBox, QMessageBox, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from typing import Dict, Any, Optional

from presentation.widgets.currencyaware_mod.currency_aware_widgets import CurrencyAwareSpinBox
from application.facades.voxeprint_facade import VoxeprintFacade
from domain.models.printer import Printer
from presentation.widgets.toggle_mod.custom_toggle import PyToggle
from domain.enums.enums import PRINTER_CATALOG


class EditPrinterDialog(QDialog):
    """Diálogo para modificar impresoras existentes"""
    
    # Señal emitida cuando se modifica una impresora exitosamente
    printer_updated = Signal(dict)
    
    def __init__(self, parent=None, printer: Optional[Printer] = None):
        super().__init__(parent)
        
        self.facade = VoxeprintFacade()
        self.printer = printer
        
        if not self.printer:
            raise ValueError("EditPrinterDialog requiere una impresora para modificar")
        
        # Configurar UI
        self._setup_ui()
        self._setup_validators()
        self._connect_signals()
        self._load_printer_data()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar ventana
        self.setWindowTitle(tr(I18N.Printer.DIALOG_EDIT_TITLE))
        self.setModal(True)
        self.setMinimumSize(400, 520)
        self.resize(450, 560)
        self.setFixedSize(self.size())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel(tr(I18N.Printer.DIALOG_EDIT_TITLE))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Formulario principal
        form_group = QGroupBox(tr(I18N.Printer.GROUP_BASIC_INFO))
        form_layout = QFormLayout(form_group)
        form_layout.setVerticalSpacing(8)
        
        # Nombre/Descripción
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr(I18N.Printer.PLACEHOLDER_NAME))
        self.name_edit.setToolTip(tr(I18N.Printer.TOOLTIP_NAME_FIELD))
        form_layout.addRow(tr(I18N.Printer.FORM_LABEL_NAME_REQUIRED), self.name_edit)
        
        # Marca
        self.brand_combo = QComboBox()
        self.brand_combo.setEditable(False)
        self.brand_combo.setToolTip(tr(I18N.Printer.TOOLTIP_BRAND_FIELD))
        self.brand_combo.addItem("")
        for brand in sorted(PRINTER_CATALOG.keys()):
            self.brand_combo.addItem(brand)
        self.brand_combo.currentTextChanged.connect(self._on_brand_changed)
        form_layout.addRow(tr(I18N.Printer.FORM_LABEL_BRAND_REQUIRED), self.brand_combo)
        
        # Modelo
        self.model_combo = QComboBox()
        self.model_combo.setEditable(False)
        self.model_combo.setToolTip(tr(I18N.Printer.TOOLTIP_MODEL_FIELD))
        self.model_combo.addItem("")
        form_layout.addRow(tr(I18N.Printer.FORM_LABEL_MODEL), self.model_combo)
        
        main_layout.addWidget(form_group)
        
        # Estado/Status de la impresora
        status_group = QGroupBox(tr(I18N.Printer.GROUP_STATUS))
        status_layout = QFormLayout(status_group)
        status_layout.setVerticalSpacing(8)
        
        # Toggle para estado activo/inactivo
        status_container = QHBoxLayout()
        
        # Label de estado - más compacto
        self.status_label = QLabel(tr(I18N.Printer.STATUS_INACTIVE_LABEL))
        self.status_label.setFixedWidth(60)
        
        # Toggle switch - más pequeño y compacto
        self.status_toggle = PyToggle(width=40, height=22)
        self.status_toggle.setToolTip(tr(I18N.Printer.TOOLTIP_STATUS_TOGGLE))
        
        # Conectar señal para cambiar el texto
        self.status_toggle.toggled.connect(self._on_status_changed)
        
        status_container.addWidget(self.status_label)
        status_container.addWidget(self.status_toggle)
        status_container.addStretch()
        
        status_layout.addRow(tr(I18N.Printer.FORM_LABEL_STATUS), status_container)
        main_layout.addWidget(status_group)
        
        # Consumo Real
        power_group = QGroupBox(tr(I18N.Printer.GROUP_POWER_CONSUMPTION))
        power_group.setFixedHeight(65)
        power_layout = QFormLayout(power_group)

        self.power_spin = QSpinBox()
        self.power_spin.setRange(0, 9999)  
        self.power_spin.setValue(0)  
        self.power_spin.setSuffix("")  
        self.power_spin.setToolTip(tr(I18N.Printer.TOOLTIP_POWER_FIELD))
        power_layout.addRow(tr(I18N.Printer.FORM_LABEL_POWER_WATTS), self.power_spin)
        
        main_layout.addWidget(power_group)
        
        # Vida Útil y Desgaste
        lifespan_group = QGroupBox(tr(I18N.Printer.GROUP_LIFESPAN))
        lifespan_layout = QFormLayout(lifespan_group)
        
        # Costo de compra
        self.purchase_cost_spin = CurrencyAwareSpinBox()
        self.purchase_cost_spin.setRange(0, 999999999)
        self.purchase_cost_spin.setValue(0)
        self.purchase_cost_spin.setToolTip(tr(I18N.Printer.TOOLTIP_PURCHASE_COST))
        self.purchase_cost_label = QLabel(tr(I18N.Printer.LABEL_PURCHASE_COST))
        lifespan_layout.addRow(self.purchase_cost_label, self.purchase_cost_spin)
        
        # Vida útil estimada
        self.useful_life_combo = QComboBox()
        life_options = [
            (tr(I18N.Printer.LIFESPAN_OPTION_2000), 2000),
            (tr(I18N.Printer.LIFESPAN_OPTION_3000), 3000),
            (tr(I18N.Printer.LIFESPAN_OPTION_5000), 5000),
            (tr(I18N.Printer.LIFESPAN_OPTION_8000), 8000),
            (tr(I18N.Printer.LIFESPAN_OPTION_10000), 10000),
            (tr(I18N.Printer.LIFESPAN_OPTION_15000), 15000),
            (tr(I18N.Printer.LIFESPAN_OPTION_20000), 20000)
        ]
        
        for display_text, hours in life_options:
            self.useful_life_combo.addItem(display_text, hours)
        
        # Seleccionar 5,000 por defecto (más realista)
        self.useful_life_combo.setCurrentIndex(2)
        self.useful_life_combo.setToolTip(tr(I18N.Printer.TOOLTIP_LIFESPAN))
        lifespan_layout.addRow(tr(I18N.Printer.LABEL_LIFESPAN_ESTIMATED), self.useful_life_combo)
        
        main_layout.addWidget(lifespan_group)
        
        # Mantenimiento
        maintenance_group = QGroupBox(tr(I18N.Printer.GROUP_MAINTENANCE))
        maintenance_layout = QFormLayout(maintenance_group)
        
        # Costo de mantenimiento
        self.maintenance_cost_spin = CurrencyAwareSpinBox()
        self.maintenance_cost_spin.setRange(0, 999999999)
        self.maintenance_cost_spin.setValue(0)
        self.maintenance_cost_spin.setToolTip(tr(I18N.Printer.TOOLTIP_MAINTENANCE_COST))
        self.maintenance_cost_label = QLabel(tr(I18N.Printer.LABEL_MAINTENANCE_COST))
        maintenance_layout.addRow(self.maintenance_cost_label, self.maintenance_cost_spin)
        
        # Intervalo de mantenimiento
        self.maintenance_hours_spin = QSpinBox()
        self.maintenance_hours_spin.setRange(1, 99999)
        self.maintenance_hours_spin.setValue(140)
        self.maintenance_hours_spin.setSuffix("")
        self.maintenance_hours_spin.setToolTip(tr(I18N.Printer.TOOLTIP_MAINTENANCE_INTERVAL))
        maintenance_layout.addRow(tr(I18N.Printer.FORM_LABEL_MAINTENANCE_INTERVAL_HOURS), self.maintenance_hours_spin)
        
        main_layout.addWidget(maintenance_group)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton(tr(I18N.Buttons.CANCEL))
        self.cancel_button.setFixedHeight(30)
        self.cancel_button.setFixedWidth(105)
        
        self.save_button = QPushButton(tr(I18N.Buttons.SAVE))
        self.save_button.setDefault(True)
        self.save_button.setFixedHeight(30)
        self.save_button.setFixedWidth(105)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def _setup_validators(self):
        """Configura validadores para los campos"""
        # Conectar validaciones en tiempo real
        self.name_edit.textChanged.connect(self._validate_form)
        self.brand_combo.currentTextChanged.connect(self._validate_form)
        self.power_spin.valueChanged.connect(self._validate_form)
        
        # Formatear nombre al terminar de editar
        self.name_edit.editingFinished.connect(self._format_name)
        
        # Validación inicial
        self._validate_form()
    
    def _connect_signals(self):
        """Conecta las señales"""
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self._on_save_clicked)
    
    def _format_name(self):
        """Formatea el nombre con mayúscula inicial en cada palabra"""
        text = self.name_edit.text().strip()
        if text:
            formatted = ' '.join(word.capitalize() for word in text.split())
            self.name_edit.setText(formatted)
    
    def _on_brand_changed(self, brand: str):
        """Actualiza el combo de modelos al cambiar la marca"""
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        self.model_combo.addItem("")
        models = PRINTER_CATALOG.get(brand, [])
        for m in models:
            self.model_combo.addItem(m)
        self.model_combo.blockSignals(False)
    
    def _on_status_changed(self, checked: bool):
        """Maneja el cambio de estado del toggle"""
        if checked:
            self.status_label.setText(tr(I18N.Printer.STATUS_ACTIVE_LABEL))
            self.status_label.setStyleSheet("color: #16A085; font-weight: bold;")
        else:
            self.status_label.setText(tr(I18N.Printer.STATUS_INACTIVE_LABEL))
            self.status_label.setStyleSheet("color: #be4e4e; font-weight: bold;")
    
    def _validate_form(self):
        """Valida el formulario y habilita/deshabilita el botón guardar"""
        name_valid = len(self.name_edit.text().strip()) > 0
        brand_valid = len(self.brand_combo.currentText().strip()) > 0
        power_valid = self.power_spin.value() >= 10
        
        is_valid = name_valid and brand_valid and power_valid
        self.save_button.setEnabled(is_valid)
    
    def _load_printer_data(self):
        """Carga los datos de la impresora a modificar"""
        if not self.printer:
            return
        
        # Obtener la moneda de la impresora
        printer_currency = getattr(self.printer, 'currency_code', 'PYG')
        
        # Configurar los spinboxes con la moneda de la impresora
        self.purchase_cost_spin.set_currency(printer_currency)
        self.maintenance_cost_spin.set_currency(printer_currency)
        
        # Actualizar labels con la moneda correcta
        from core.utils.currency_helper import CurrencyHelper
        currency_symbol = CurrencyHelper.get_symbol(printer_currency)
        self.purchase_cost_label.setText(tr(I18N.Printer.LABEL_PURCHASE_COST_CURRENCY).format(symbol=currency_symbol))
        self.maintenance_cost_label.setText(tr(I18N.Printer.LABEL_MAINTENANCE_COST_CURRENCY).format(symbol=currency_symbol))
        
        # Cargar datos básicos
        self.name_edit.setText(self.printer.name)
        
        # Seleccionar marca en el combo
        brand = self.printer.brand or ""
        brand_idx = self.brand_combo.findText(brand)
        if brand_idx >= 0:
            self.brand_combo.setCurrentIndex(brand_idx)
        elif brand:
            # Marca no catalogada: agregar temporalmente
            self.brand_combo.addItem(brand)
            self.brand_combo.setCurrentText(brand)
        
        # Seleccionar modelo en el combo
        model = self.printer.model or ""
        if model:
            model_idx = self.model_combo.findText(model)
            if model_idx >= 0:
                self.model_combo.setCurrentIndex(model_idx)
            elif model:
                # Modelo no catalogado: agregar temporalmente
                self.model_combo.addItem(model)
                self.model_combo.setCurrentText(model)
        
        # Cargar consumo
        self.power_spin.setValue(int(self.printer.power_consumption_watts))
        
        # Cargar costo de compra
        self.purchase_cost_spin.setValue(int(self.printer.purchase_cost))
        
        # Cargar vida útil - buscar el valor más cercano en el combo
        current_life = self.printer.useful_life_hours
        best_match = 2  # default index (10000 horas)
        min_diff = float('inf')
        
        for i in range(self.useful_life_combo.count()):
            combo_value = self.useful_life_combo.itemData(i)
            diff = abs(combo_value - current_life)
            if diff < min_diff:
                min_diff = diff
                best_match = i
        
        self.useful_life_combo.setCurrentIndex(best_match)
        
        # Cargar mantenimiento
        self.maintenance_cost_spin.setValue(int(self.printer.maintenance_cost))
        self.maintenance_hours_spin.setValue(int(self.printer.maintenance_interval_hours))
        
        # Cargar estado - establecer el toggle y actualizar el label
        is_active = self.printer.is_active
        self.status_toggle.setChecked(is_active)
        self._on_status_changed(is_active)  # Actualizar el label inmediatamente
    
    def _on_save_clicked(self):
        """Maneja el clic en guardar"""
        try:
            # Validar datos
            if not self._validate_data():
                return
            
            # Confirmación simple
            reply = QMessageBox.question(
                self,
                tr(I18N.Printer.CONFIRM_EDIT_TITLE),
                tr(I18N.Printer.CONFIRM_EDIT_MESSAGE),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Recopilar datos
                printer_data = self._collect_form_data()
                
                # Actualizar impresora usando el repositorio directamente para incluir useful_life_hours
                self.printer.name = printer_data['name']
                self.printer.brand = printer_data['brand']
                self.printer.model = printer_data['model']
                self.printer.power_consumption_watts = printer_data['power_watts']
                self.printer.purchase_cost = printer_data['purchase_cost']
                self.printer.useful_life_hours = printer_data['useful_life_hours']
                self.printer.maintenance_cost = printer_data['maintenance_cost']
                self.printer.maintenance_interval_hours = printer_data['maintenance_hours']
                self.printer.is_active = printer_data['is_active']  # ✅ NUEVO: Campo de estado
                
                # Actualizar timestamp
                from datetime import datetime
                self.printer.updated_at = datetime.now().isoformat()
                
                # Guardar usando el repositorio
                updated_printer = self.facade.printer_repository.save(self.printer)
                
                # Emitir señal
                self.printer_updated.emit({
                    "id": updated_printer.id,
                    "name": updated_printer.name,
                    "power_watts": updated_printer.power_consumption_watts
                })
                
                # Cerrar diálogo
                self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.Printer.MSG_ERROR_EDITING)
            )
    
    def _validate_data(self) -> bool:
        """Valida los datos del formulario"""
        # Nombre
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, tr(I18N.Printer.VALIDATION_TITLE), tr(I18N.Printer.VALIDATION_NAME_REQUIRED))
            self.name_edit.setFocus()
            return False
        
        # Marca
        if not self.brand_combo.currentText().strip():
            QMessageBox.warning(self, tr(I18N.Printer.VALIDATION_TITLE), tr(I18N.Printer.VALIDATION_BRAND_REQUIRED))
            self.brand_combo.setFocus()
            return False
        
        # Consumo mínimo (permitir 0)
        if self.power_spin.value() < 0:
            QMessageBox.warning(self, tr(I18N.Printer.VALIDATION_TITLE), tr(I18N.Printer.VALIDATION_POWER_NEGATIVE))
            self.power_spin.setFocus()
            return False
        
        return True
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Recopila los datos del formulario"""
        return {
            'name': self.name_edit.text().strip(),
            'brand': self.brand_combo.currentText().strip(),
            'model': self.model_combo.currentText().strip(),
            'power_watts': self.power_spin.value(),
            'purchase_cost': self.purchase_cost_spin.value(),
            'useful_life_hours': self.useful_life_combo.currentData(),
            'maintenance_cost': self.maintenance_cost_spin.value(),
            'maintenance_hours': self.maintenance_hours_spin.value(),
            'is_active': self.status_toggle.isChecked()  # ✅ NUEVO: Estado activo/inactivo
        }
    
    @staticmethod
    def edit_printer(parent=None, printer: Printer = None) -> Dict[str, Any]:
        """Método estático para modificar una impresora"""
        if not printer:
            return None
        
        dialog = EditPrinterDialog(parent, printer)
        result_data = None
        
        def on_updated(data):
            nonlocal result_data
            result_data = data
        
        dialog.printer_updated.connect(on_updated)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return result_data
        return None
