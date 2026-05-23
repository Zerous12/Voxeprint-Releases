"""
Diálogo de formulario para agregar/modificar filamentos.
Forma parte del sistema de inventario de filamentos.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox,
    QPushButton, QLabel, QCheckBox, QTextEdit,
    QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Optional, Dict, Any

from presentation.widgets.currencyaware_mod.currency_aware_widgets import CurrencyAwareSpinBox
from domain.models.filament import Filament
from domain.enums.enums import FilamentType, FilamentColor
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class EditFilamentDialog(QDialog):
    """Diálogo para agregar o modificar filamentos"""
    
    # Señal emitida cuando se guarda un filamento
    filament_saved = Signal(dict)  # Emite datos del filamento
    
    def __init__(self, parent=None, filament: Optional[Filament] = None):
        super().__init__(parent)
        
        # Estado
        self.filament = filament
        self.is_edit_mode = filament is not None
        
        # Configurar UI
        self._setup_ui()
        self._setup_validators()
        self._connect_signals()
        
        # Cargar datos si estamos editando
        if self.is_edit_mode:
            self._load_filament_data()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar ventana
        title = tr(I18N.Filament.DIALOG_EDIT_HEADER_TITLE) if self.is_edit_mode else tr(I18N.Filament.DIALOG_ADD_TITLE)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(400, 420 if self.is_edit_mode else 500)
        self.resize(450, 460 if self.is_edit_mode else 550)
        self.setFixedSize(self.size())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Formulario principal
        form_group = QGroupBox(tr(I18N.Filament.GROUP_BASIC_INFO))
        form_layout = QFormLayout(form_group)
        form_layout.setVerticalSpacing(8)
        
        # Campos del formulario
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr(I18N.Filament.PLACEHOLDER_NAME))
        self.name_edit.setToolTip(tr(I18N.Filament.TOOLTIP_NAME_FIELD))
        form_layout.addRow(tr(I18N.Filament.LABEL_DESCRIPTION), self.name_edit)
        
        # Marca
        self.brand_edit = QLineEdit()
        self.brand_edit.setPlaceholderText(tr(I18N.Filament.PLACEHOLDER_BRAND))
        self.brand_edit.setToolTip(tr(I18N.Filament.TOOLTIP_BRAND_FIELD))
        form_layout.addRow(tr(I18N.Filament.LABEL_BRAND), self.brand_edit)
        
        # Tipo de filamento
        self.type_combo = QComboBox()
        for t in FilamentType:
            self.type_combo.addItem(t.value, t.name)
        self.type_combo.setToolTip(tr(I18N.Filament.TOOLTIP_TYPE_FIELD))
        form_layout.addRow(tr(I18N.Filament.LABEL_TYPE), self.type_combo)
        
        # Color
        self.color_combo = QComboBox()
        for c in FilamentColor:
            key = f"FilamentColor.{c.name}"
            display = tr(key)
            self.color_combo.addItem(c.value if display == key else display, c.name)
        self.color_combo.setToolTip(tr(I18N.Filament.TOOLTIP_COLOR_FIELD))
        form_layout.addRow(tr(I18N.Filament.LABEL_COLOR), self.color_combo)
        
        main_layout.addWidget(form_group)
        
        # Sección de rollo solo para modo AGREGAR (nuevo filamento sin rolls)
        if not self.is_edit_mode:
            specs_group = QGroupBox(tr(I18N.Filament.GROUP_FIRST_ROLL_SPECS))
            specs_layout = QFormLayout(specs_group)
            specs_layout.setVerticalSpacing(8)
            
            self.weight_spin = QSpinBox()
            self.weight_spin.setRange(100, 99999)
            self.weight_spin.setValue(1000)
            self.weight_spin.setToolTip(tr(I18N.Filament.TOOLTIP_WEIGHT_FIELD))
            specs_layout.addRow(tr(I18N.Filament.LABEL_WEIGHT), self.weight_spin)
            
            self.price_roll_spin = CurrencyAwareSpinBox()
            self.price_roll_spin.setRange(0, 999999999)
            self.price_roll_spin.setValue(0)
            self.price_roll_spin.setToolTip(tr(I18N.Filament.TOOLTIP_PRICE_FIELD))
            self.price_roll_label = QLabel(tr(I18N.Filament.LABEL_PRICE))
            specs_layout.addRow(self.price_roll_label, self.price_roll_spin)
            
            main_layout.addWidget(specs_group)
        else:
            self.weight_spin = None
            self.price_roll_spin = None
            self.price_roll_label = None
        
        # Configuración
        config_group = QGroupBox(tr(I18N.Filament.GROUP_CONFIG))
        config_layout = QFormLayout(config_group)
        
        # Estado activo
        self.active_check = QCheckBox(tr(I18N.Filament.CHECKBOX_AVAILABLE))
        self.active_check.setChecked(True)
        self.active_check.setToolTip(tr(I18N.Filament.TOOLTIP_AVAILABLE_CHECKBOX))
        config_layout.addRow("", self.active_check)
        
        main_layout.addWidget(config_group)
        
        # Notas Adicionales (Opcional)
        notes_group = QGroupBox(tr(I18N.Filament.GROUP_NOTES_OPTIONAL))
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(tr(I18N.Filament.PLACEHOLDER_NOTES))
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setToolTip(tr(I18N.Filament.TOOLTIP_NOTES_FIELD))
        notes_layout.addWidget(self.notes_edit)
        
        main_layout.addWidget(notes_group)
        
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
        self.name_edit.textChanged.connect(self._validate_form)
        self.brand_edit.textChanged.connect(self._validate_form)
        if self.weight_spin:
            self.weight_spin.valueChanged.connect(self._validate_form)
        if self.price_roll_spin:
            self.price_roll_spin.valueChanged.connect(self._validate_form)
        
        self.brand_edit.editingFinished.connect(self._format_brand)
        self.name_edit.editingFinished.connect(self._format_description)
        
        self._validate_form()
    
    def _connect_signals(self):
        """Conecta las señales"""
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self._on_save_clicked)
    
    def _format_brand(self):
        """Formatea la marca con mayúscula inicial en cada palabra"""
        text = self.brand_edit.text().strip()
        if text:
            formatted = ' '.join(word.capitalize() for word in text.split())
            self.brand_edit.setText(formatted)
    
    def _format_description(self):
        """Formatea la descripción con mayúscula inicial en cada palabra"""
        text = self.name_edit.text().strip()
        if text:
            formatted = ' '.join(word.capitalize() for word in text.split())
            self.name_edit.setText(formatted)
    
    def _validate_form(self):
        """Valida el formulario y habilita/deshabilita el botón guardar"""
        name_valid = len(self.name_edit.text().strip()) > 0
        brand_valid = len(self.brand_edit.text().strip()) > 0
        
        if self.is_edit_mode:
            is_valid = name_valid and brand_valid
        else:
            weight_valid = self.weight_spin.value() >= 100 if self.weight_spin else True
            price_valid = self.price_roll_spin.value() >= 0 if self.price_roll_spin else True
            is_valid = name_valid and brand_valid and weight_valid and price_valid
        
        self.save_button.setEnabled(is_valid)
    
    def _load_filament_data(self):
        """Carga los datos del filamento a editar"""
        if not self.filament:
            return
        
        self.name_edit.setText(self.filament.name)
        self.brand_edit.setText(self.filament.brand)
        
        # Tipo
        type_index = self.type_combo.findData(self.filament.type.name)
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
        # Color
        color_index = self.color_combo.findData(self.filament.color.name)
        if color_index >= 0:
            self.color_combo.setCurrentIndex(color_index)
        
        self.active_check.setChecked(self.filament.is_active)
        
        # Notas
        if hasattr(self.filament, 'notes') and self.filament.notes:
            self.notes_edit.setPlainText(self.filament.notes)
    
    def _on_save_clicked(self):
        """Maneja el clic en guardar"""
        try:
            # Validar datos
            if not self._validate_data():
                return
            
            # Confirmación
            confirm_title = tr(I18N.Filament.DIALOG_CONFIRM_EDIT_TITLE) if self.is_edit_mode else tr(I18N.Filament.DIALOG_CONFIRM_ADD_TITLE)
            confirm_msg = tr(I18N.Filament.DIALOG_CONFIRM_EDIT_MESSAGE) if self.is_edit_mode else tr(I18N.Filament.DIALOG_CONFIRM_ADD_MESSAGE)
            reply = QMessageBox.question(
                self,
                confirm_title,
                confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Recopilar datos
                filament_data = self._collect_form_data()
                
                # Emitir señal
                self.filament_saved.emit(filament_data)
                
                # Cerrar diálogo
                self.accept()
            
        except Exception as e:
            error_msg = tr(I18N.Filament.MSG_ERROR_EDITING) if self.is_edit_mode else tr(I18N.Filament.MSG_ERROR_ADDING)
            QMessageBox.critical(
                self,
                tr(I18N.Dialogs.ERROR_TITLE),
                f"{error_msg}\n\n{str(e)}"
            )
    
    def _validate_data(self) -> bool:
        """Valida los datos del formulario"""
        if len(self.name_edit.text().strip()) < 3:
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Filament.VALIDATION_DESCRIPTION_MIN_CHARS))
            self.name_edit.setFocus()
            return False
        
        if len(self.brand_edit.text().strip()) < 2:
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Filament.VALIDATION_BRAND_MIN_CHARS))
            self.brand_edit.setFocus()
            return False
        
        if not self.is_edit_mode:
            if self.weight_spin and self.weight_spin.value() < 100:
                QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Filament.VALIDATION_WEIGHT_MIN))
                self.weight_spin.setFocus()
                return False
            
            if self.price_roll_spin and self.price_roll_spin.value() < 0:
                QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Filament.VALIDATION_PRICE_NEGATIVE))
                self.price_roll_spin.setFocus()
                return False
        
        return True
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Recopila los datos del formulario"""
        data = {
            'id': self.filament.id if self.filament else None,
            'name': self.name_edit.text().strip(),
            'type': self.type_combo.currentData(),
            'brand': self.brand_edit.text().strip(),
            'color': self.color_combo.currentData(),
            'is_active': self.active_check.isChecked(),
            'notes': self.notes_edit.toPlainText().strip(),
            'is_edit': self.is_edit_mode
        }
        
        if not self.is_edit_mode and self.weight_spin and self.price_roll_spin:
            weight_grams = self.weight_spin.value()
            price_roll = self.price_roll_spin.value()
            data['weight_grams'] = weight_grams
            data['price_per_unit'] = price_roll
            data['price_per_gram'] = price_roll / weight_grams if weight_grams > 0 else 0
            data['current_stock_grams'] = weight_grams
        
        return data
    
    @staticmethod
    def add_filament(parent=None) -> Optional[Dict[str, Any]]:
        """Método estático para agregar un filamento"""
        dialog = EditFilamentDialog(parent)
        result_data = None
        
        def on_saved(data):
            nonlocal result_data
            result_data = data
        
        dialog.filament_saved.connect(on_saved)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return result_data
        return None
    
    @staticmethod
    def edit_filament(parent=None, filament: Filament = None) -> Optional[Dict[str, Any]]:
        """Método estático para editar un filamento"""
        if not filament:
            return None
        
        dialog = EditFilamentDialog(parent, filament)
        result_data = None
        
        def on_saved(data):
            nonlocal result_data
            result_data = data
        
        dialog.filament_saved.connect(on_saved)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return result_data
        return None
