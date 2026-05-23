"""
Diálogo para añadir rollos de filamento a un filamento EXISTENTE.
Permite solo editar peso, precio y notas del nuevo rollo.
Los datos del filamento (nombre, marca, tipo, color) se muestran como solo lectura.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox,
    QPushButton, QLabel, QCheckBox, QTextEdit,
    QGroupBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Dict, Any, Optional

from presentation.widgets.currencyaware_mod.currency_aware_widgets import CurrencyAwareSpinBox
from domain.models.filament import Filament
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class MoreFilamentDialog(QDialog):
    """Diálogo para añadir más filamento (rollos) a un filamento EXISTENTE con promedio ponderado"""
    
    # Señal emitida cuando se añade un rollo exitosamente
    roll_added = Signal(dict)  # Emite datos del nuevo rollo
    
    def __init__(self, parent=None, existing_filament: Optional[Filament] = None):
        super().__init__(parent)
        
        # Filamento existente al que se añadirá el rollo
        self.existing_filament = existing_filament
        
        if not self.existing_filament:
            raise ValueError("MoreFilamentDialog requiere un filamento existente")
        
        # Configurar UI
        self._setup_ui()
        self._setup_validators()
        self._connect_signals()
        self._populate_existing_data()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario para añadir rollos a filamento existente"""
        # Configurar ventana
        self.setWindowTitle(tr(I18N.AddMoreFilament.DIALOG_TITLE))
        self.setModal(True)
        self.setMinimumSize(500, 500)  # Altura más compacta
        self.resize(550, 530)  # Tamaño más compacto
        self.setFixedSize(self.size())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)  # Espaciado entre secciones más compacto
        
        # Título
        title_label = QLabel(tr(I18N.AddMoreFilament.TITLE_LABEL))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Sección del filamento existente (solo lectura)
        self._setup_existing_filament_section(main_layout)
        
        # Sección del nuevo rollo (editable)
        self._setup_new_roll_section(main_layout)
        self._setup_notes_section(main_layout)
        # Botones de acción
        self._setup_buttons_section(main_layout)
    
    def _setup_existing_filament_section(self, main_layout):
        """Muestra información del filamento existente (solo lectura)"""
        existing_group = QGroupBox(tr(I18N.AddMoreFilament.GROUP_EXISTING))
        existing_layout = QFormLayout(existing_group)
        existing_layout.setVerticalSpacing(6)  # Espaciado más compacto
        
        # Campos de solo lectura para mostrar datos existentes
        self.existing_name_label = QLabel()
        self.existing_name_label.setStyleSheet("font-weight: bold;")
        existing_layout.addRow(tr(I18N.AddMoreFilament.LABEL_NAME), self.existing_name_label)
        
        self.existing_brand_label = QLabel()
        existing_layout.addRow(tr(I18N.AddMoreFilament.LABEL_BRAND), self.existing_brand_label)
        
        self.existing_type_label = QLabel()
        existing_layout.addRow(tr(I18N.AddMoreFilament.LABEL_TYPE), self.existing_type_label)
        
        self.existing_color_label = QLabel()
        existing_layout.addRow(tr(I18N.AddMoreFilament.LABEL_COLOR), self.existing_color_label)
        
        self.existing_current_stock_label = QLabel()
        existing_layout.addRow(tr(I18N.AddMoreFilament.LABEL_CURRENT_STOCK), self.existing_current_stock_label)
        
        self.existing_current_price_label = QLabel()
        existing_layout.addRow(tr(I18N.AddMoreFilament.LABEL_CURRENT_PRICE), self.existing_current_price_label)
        
        self.existing_rolls_label = QLabel()
        existing_layout.addRow(tr(I18N.AddMoreFilament.LABEL_CURRENT_ROLLS), self.existing_rolls_label)
        
        main_layout.addWidget(existing_group)
    
    def _setup_new_roll_section(self, main_layout):
        """Configura la sección para el nuevo rollo (solo peso, precio y notas)"""
        new_roll_group = QGroupBox(tr(I18N.AddMoreFilament.GROUP_NEW_ROLL))
        new_roll_group.setFixedHeight(96)  # Altura fija para mantener consistencia
        new_roll_layout = QFormLayout(new_roll_group)
        new_roll_layout.setVerticalSpacing(6)  # Espaciado vertical más compacto
        
        # Peso del rollo con botones de acceso rápido
        weight_layout = QHBoxLayout()
        self.weight_spin = QSpinBox()
        self.weight_spin.setRange(1, 10000)
        self.weight_spin.setValue(1000)  # Default 1kg
        self.weight_spin.setSuffix("")
        self.weight_spin.setToolTip(tr(I18N.AddMoreFilament.TOOLTIP_WEIGHT))
        
        # Botones de acceso rápido para peso
        weight_250_btn = QPushButton("250g")
        weight_500_btn = QPushButton("500g")
        weight_1kg_btn = QPushButton("1kg")
        
        # Conectar botones
        weight_250_btn.clicked.connect(lambda: self.weight_spin.setValue(250))
        weight_500_btn.clicked.connect(lambda: self.weight_spin.setValue(500))
        weight_1kg_btn.clicked.connect(lambda: self.weight_spin.setValue(1000))
        
        # Estilo para botones pequeños
        for btn in [weight_250_btn, weight_500_btn, weight_1kg_btn]:
            btn.setMaximumWidth(60)
        
        weight_layout.addWidget(self.weight_spin)
        weight_layout.addSpacing(15)  # Espacio más considerable hacia derecha
        weight_layout.addWidget(QLabel(tr(I18N.AddMoreFilament.LABEL_WEIGHT_COMMON)))
        weight_layout.addWidget(weight_250_btn)
        weight_layout.addWidget(weight_500_btn)
        weight_layout.addWidget(weight_1kg_btn)
        weight_layout.addStretch()
        
        new_roll_layout.addRow(tr(I18N.AddMoreFilament.LABEL_WEIGHT), weight_layout)
        
        # Precio del rollo
        self.price_roll_spin = CurrencyAwareSpinBox()
        self.price_roll_spin.setRange(0, 999999999)  # Permitir desde 0
        self.price_roll_spin.setValue(0)  # Valor por defecto más realista
        self.price_roll_spin.setToolTip(tr(I18N.Filament.TOOLTIP_PRICE_FIELD))
        self.price_roll_label = QLabel(tr(I18N.AddMoreFilament.LABEL_PRICE, symbol=""))
        new_roll_layout.addRow(self.price_roll_label, self.price_roll_spin)
                        
        main_layout.addWidget(new_roll_group)
    
    def _setup_notes_section(self, main_layout):
        """Configura la sección de notas opcionales"""
        notes_group = QGroupBox(tr(I18N.AddMoreFilament.GROUP_NOTES))
        notes_group.setFixedHeight(110)
        notes_layout = QVBoxLayout(notes_group)
        
        self.roll_notes_edit = QTextEdit()
        self.roll_notes_edit.setMaximumHeight(80)  # Altura más compacta
        self.roll_notes_edit.setPlaceholderText(tr(I18N.AddMoreFilament.PLACEHOLDER_NOTES))
        self.roll_notes_edit.setToolTip(tr(I18N.AddMoreFilament.TOOLTIP_NOTES))
        notes_layout.addWidget(self.roll_notes_edit)

        main_layout.addWidget(notes_group)
    
    def _setup_buttons_section(self, main_layout):
        """Configura la sección de botones"""
        buttons_layout = QHBoxLayout()
        
        # Botón Limpiar
        clear_btn = QPushButton(tr(I18N.Buttons.CLEAR))
        clear_btn.clicked.connect(self._clear_form)
        clear_btn.setToolTip(tr(I18N.AddMoreFilament.TOOLTIP_CLEAR))
        clear_btn.setFixedHeight(30)
        clear_btn.setFixedWidth(105)
        
        # Botón Cancelar
        cancel_btn = QPushButton(tr(I18N.Buttons.CANCEL))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setToolTip(tr(I18N.AddMoreFilament.TOOLTIP_CANCEL))
        cancel_btn.setFixedHeight(30)
        cancel_btn.setFixedWidth(105)
        
        # Botón Añadir
        self.add_button = QPushButton(tr(I18N.Buttons.SAVE))
        self.add_button.clicked.connect(self._on_add_clicked)
        self.add_button.setDefault(True)
        self.add_button.setToolTip(tr(I18N.AddMoreFilament.TOOLTIP_ADD))
        self.add_button.setFixedHeight(30)
        self.add_button.setFixedWidth(105)
        
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def _setup_validators(self):
        """Configura validadores para los campos"""
        # Los validadores son mínimos porque solo hay peso y precio
        pass
    
    def _connect_signals(self):
        """Conecta las señales de los widgets"""
        # Validación en tiempo real
        self.weight_spin.valueChanged.connect(self._validate_form)
        self.price_roll_spin.valueChanged.connect(self._validate_form)
        
        # Enter para añadir
        self.price_roll_spin.lineEdit().returnPressed.connect(self._on_add_clicked)
    
    def _populate_existing_data(self):
        """Pobla los campos con los datos del filamento existente"""
        if not self.existing_filament:
            return
        
        # Obtener la moneda del filamento
        from core.utils.currency_helper import CurrencyHelper
        filament_currency = getattr(self.existing_filament, 'currency_code', 'PYG')
        currency_symbol = CurrencyHelper.get_symbol(filament_currency)
        
        # Configurar el spinbox con la moneda del filamento
        self.price_roll_spin.set_currency(filament_currency)
        
        # Actualizar label con la moneda correcta
        self.price_roll_label.setText(tr(I18N.AddMoreFilament.LABEL_PRICE, symbol=currency_symbol))
        
        # Mostrar información del filamento existente (solo lectura)
        self.existing_name_label.setText(self.existing_filament.name)
        self.existing_brand_label.setText(self.existing_filament.brand or tr(I18N.Filament.DEFAULT_NO_BRAND))
        
        # Mostrar tipo y color con traducción dinámica
        filament_type_name = self.existing_filament.type.name if hasattr(self.existing_filament.type, 'name') else str(self.existing_filament.type)
        filament_color_name = self.existing_filament.color.name if hasattr(self.existing_filament.color, 'name') else str(self.existing_filament.color)

        type_key = f"FilamentType.{filament_type_name}"
        type_display = tr(type_key)
        self.existing_type_label.setText(self.existing_filament.type.value if type_display == type_key else type_display)

        color_key = f"FilamentColor.{filament_color_name}"
        color_display = tr(color_key)
        self.existing_color_label.setText(self.existing_filament.color.value if color_display == color_key else color_display)
        
        # Mostrar stock y precio actuales con la moneda correcta
        stock_kg = self.existing_filament.current_stock_grams / 1000.0 if self.existing_filament.current_stock_grams else 0.0
        self.existing_current_stock_label.setText(f"{stock_kg:.2f} kg ({self.existing_filament.current_stock_grams}g)")
        
        price_per_kg = self.existing_filament.price_per_gram * 1000.0 if self.existing_filament.price_per_gram else 0.0
        price_formatted = CurrencyHelper.format(price_per_kg, filament_currency)
        self.existing_current_price_label.setText(f"{price_formatted}/kg")
        
        self.existing_rolls_label.setText(tr(I18N.AddMoreFilament.FORMAT_ROLLS, count=self.existing_filament.quantity_rolls))
        
        # Configurar el título de la ventana con información específica
        self.setWindowTitle(tr(I18N.AddMoreFilament.DIALOG_TITLE_SPECIFIC, name=self.existing_filament.name))
    
    def _validate_form(self):
        """Valida el formulario para añadir rollo (solo peso y precio del nuevo rollo)"""
        weight_valid = self.weight_spin.value() >= 10  # Mínimo 100g
        price_valid = self.price_roll_spin.value() >= 1  # Permitir desde 0
        
        form_valid = weight_valid and price_valid
        
        # Actualizar estado del botón
        self.add_button.setEnabled(form_valid)
        
        return form_valid
    
    def _clear_form(self):
        """Limpia los campos editables del formulario"""
        reply = QMessageBox.question(
            self,
            tr(I18N.AddMoreFilament.DIALOG_CLEAR_TITLE),
            tr(I18N.AddMoreFilament.DIALOG_CLEAR_MESSAGE),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.weight_spin.setValue(1000)
            self.price_roll_spin.setValue(0)
            self.roll_notes_edit.clear()
            self.weight_spin.setFocus()
    
    def _on_add_clicked(self):
        """Maneja el clic en el botón añadir"""
        try:
            # Validación final
            if not self._validate_form():
                QMessageBox.warning(
                    self,
                    tr(I18N.AddMoreFilament.DIALOG_INCOMPLETE_TITLE),
                    tr(I18N.AddMoreFilament.DIALOG_INCOMPLETE_MESSAGE)
                )
                return
            
            # Recopilar datos
            roll_data = self._collect_form_data()
            
            # Calcular precio por gramo del nuevo rollo
            price_per_kg_new_roll = (roll_data['price_roll'] / roll_data['weight_grams']) * 1000
            
            # Confirmar adición
            reply = QMessageBox.question(
                self,
                tr(I18N.AddMoreFilament.DIALOG_CONFIRM_TITLE),
                tr(I18N.AddMoreFilament.DIALOG_CONFIRM_MESSAGE),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Emitir señal con los datos
                self.roll_added.emit(roll_data)
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.AddMoreFilament.ERROR_MESSAGE, error=str(e))
            )
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """
        Recopila datos para añadir rollo a filamento existente.
        Usa los datos del filamento existente + peso y precio del nuevo rollo.
        """
        if not self.existing_filament:
            raise ValueError("No hay filamento existente seleccionado")
        
        # Tomar datos del filamento existente (no editables)
        filament_type = self.existing_filament.type.value if hasattr(self.existing_filament.type, 'value') else str(self.existing_filament.type)
        filament_color = self.existing_filament.color.value if hasattr(self.existing_filament.color, 'value') else str(self.existing_filament.color)
        
        # Solo el peso, precio y notas son del nuevo rollo
        weight_grams = self.weight_spin.value()
        price_roll = self.price_roll_spin.value()
        price_per_gram = price_roll / weight_grams if weight_grams > 0 else 0
        
        return {
            # Datos del filamento existente (para identificación)
            'description': self.existing_filament.name,
            'type': filament_type,
            'brand': self.existing_filament.brand,
            'color': filament_color,
            # Datos del nuevo rollo
            'weight_grams': weight_grams,
            'price_roll': price_roll,
            'price_per_gram': price_per_gram,
            'is_active': True,  # Los rollos añadidos están siempre activos
            'notes': self.roll_notes_edit.toPlainText().strip(),
            'is_edit': False,
            'existing_filament_id': self.existing_filament.id  # Para identificar el filamento
        }
    
    @staticmethod
    def add_filament_roll(parent=None, existing_filament: Optional[Filament] = None) -> Optional[Dict[str, Any]]:
        """Método estático para mostrar el diálogo y añadir rollo a filamento existente"""
        if not existing_filament:
            raise ValueError("add_filament_roll requiere un filamento existente")
            
        dialog = MoreFilamentDialog(parent, existing_filament)
        result_data = None
        
        def on_added(data):
            nonlocal result_data
            result_data = data
        
        dialog.roll_added.connect(on_added)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return result_data
        return None
