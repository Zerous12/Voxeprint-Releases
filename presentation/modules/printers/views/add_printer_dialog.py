"""
Diálogo para agregar nuevas impresoras al inventario.
Solo campos esenciales: consumo real en watts y mantenimiento.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel,
    QGroupBox, QMessageBox, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Dict, Any

from presentation.widgets.currencyaware_mod.currency_aware_widgets import CurrencyAwareSpinBox
from application.facades.voxeprint_facade import VoxeprintFacade
from domain.enums.enums import PRINTER_CATALOG
from core.utils.translation_keys import I18N
from core.utils.translation_helper import tr


class AddPrinterDialog(QDialog):
    """Diálogo para agregar nuevas impresoras"""
    
    # Señal emitida cuando se agrega una impresora exitosamente
    printer_added = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.facade = VoxeprintFacade()
        
        # Configurar UI
        self._setup_ui()
        self._setup_validators()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar ventana
        self.setWindowTitle(tr(I18N.Printer.DIALOG_ADD_TITLE))
        self.setModal(True)
        self.setMinimumSize(400, 520)
        self.resize(450, 560)
        self.setFixedSize(self.size())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel(tr(I18N.Printer.DIALOG_ADD_HEADER_TITLE))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Formulario principal
        form_group = QGroupBox(tr(I18N.Printer.GROUP_BASIC_INFO))
        form_group.setFixedHeight(120)
        form_layout = QFormLayout(form_group)
        form_layout.setVerticalSpacing(8)
        
        # Nombre/Descripción
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr(I18N.Printer.PLACEHOLDER_NAME))
        self.name_edit.setToolTip(tr(I18N.Printer.TOOLTIP_NAME_FIELD))
        form_layout.addRow(tr(I18N.Printer.FORM_LABEL_DESCRIPTION), self.name_edit)
        
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
        
        # Consumo Real
        power_group = QGroupBox(tr(I18N.Printer.GROUP_POWER_CONSUMPTION))
        power_group.setFixedHeight(65)
        power_layout = QFormLayout(power_group)

        self.power_spin = QSpinBox()
        self.power_spin.setRange(10, 9999)  
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
        lifespan_layout.addRow(tr(I18N.Printer.LABEL_PURCHASE_COST), self.purchase_cost_spin)
        
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
        maintenance_layout.addRow(tr(I18N.Printer.LABEL_MAINTENANCE_COST), self.maintenance_cost_spin)
        
        # Intervalo de mantenimiento
        self.maintenance_hours_spin = QSpinBox()
        self.maintenance_hours_spin.setRange(1, 99999)
        self.maintenance_hours_spin.setValue(150)
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
    
    def _validate_form(self):
        """Valida el formulario y habilita/deshabilita el botón guardar"""
        name_valid = len(self.name_edit.text().strip()) > 0
        brand_valid = len(self.brand_combo.currentText().strip()) > 0
        power_valid = self.power_spin.value() >= 10
        
        is_valid = name_valid and brand_valid and power_valid
        self.save_button.setEnabled(is_valid)
    
    def _on_save_clicked(self):
        """Maneja el clic en guardar"""
        try:
            # Validar datos
            if not self._validate_data():
                return
            
            # Confirmación simple
            reply = QMessageBox.question(
                self,
                tr(I18N.Printer.DIALOG_CONFIRM_ADD_TITLE),
                tr(I18N.Printer.DIALOG_CONFIRM_ADD_MESSAGE),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Recopilar datos
                printer_data = self._collect_form_data()
                
                # Crear impresora
                printer = self.facade.create_printer(
                    name=printer_data['name'],
                    brand=printer_data['brand'],
                    model=printer_data['model'],
                    power_consumption_watts=printer_data['power_watts'],
                    purchase_cost=printer_data['purchase_cost'],
                    useful_life_hours=printer_data['useful_life_hours'],
                    maintenance_cost=printer_data['maintenance_cost'],
                    maintenance_interval_hours=printer_data['maintenance_hours']
                )
                
                # Emitir señal
                self.printer_added.emit({
                    "id": printer.id,
                    "name": printer.name,
                    "power_watts": printer.power_consumption_watts
                })
                
                # Cerrar diálogo
                self.accept()
            
        except Exception as e:            
            QMessageBox.critical(
                self,
                tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.Printer.MSG_ERROR_ADDING)
            )
    
    def _validate_data(self) -> bool:
        """Valida los datos del formulario"""
        # Nombre
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Printer.VALIDATION_NAME_REQUIRED))
            self.name_edit.setFocus()
            return False
        
        # Marca
        if not self.brand_combo.currentText().strip():
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Printer.VALIDATION_BRAND_REQUIRED))
            self.brand_combo.setFocus()
            return False
        
        # Consumo mínimo
        if self.power_spin.value() < 10:
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Printer.VALIDATION_POWER_MIN))
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
            'maintenance_hours': self.maintenance_hours_spin.value()
        }
    
    @staticmethod
    def add_printer(parent=None) -> Dict[str, Any]:
        """Método estático para agregar una impresora"""
        dialog = AddPrinterDialog(parent)
        result_data = None
        
        def on_added(data):
            nonlocal result_data
            result_data = data
        
        dialog.printer_added.connect(on_added)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return result_data
        return None