"""
Diálogo específico para agregar nuevos filamentos al inventario.
Interfaz optimizada para la creación rápida de filamentos.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox,
    QPushButton, QLabel, QCheckBox, QTextEdit,
    QGroupBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from PySide6.QtGui import QFont, QIcon
from typing import Dict, Any

from core.utils.logger import logger
from presentation.widgets.currencyaware_mod.currency_aware_widgets import CurrencyAwareSpinBox
from domain.enums.enums import FilamentType, FilamentColor
from domain.models.filament import Filament
from infrastructure.database.connection import DatabaseConnection
from infrastructure.database.repositories.filament_repository import FilamentRepository


class AddFilamentDialog(QDialog):
    """Diálogo especializado para agregar nuevos filamentos"""
    
    # Señal emitida cuando se agrega un filamento exitosamente
    filament_added = Signal(dict)  # Emite datos del nuevo filamento
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Inicializar repositorio para guardar filamentos
        self.filament_repository = FilamentRepository(DatabaseConnection())
        
        # Configurar UI
        self._setup_ui()
        self._setup_validators()
        self._connect_signals()
        self._set_defaults()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario optimizada para agregar"""
        # Configurar ventana
        self.setWindowTitle(tr(I18N.Filament.DIALOG_ADD_TITLE))
        self.setModal(True)
        self.setMinimumSize(500, 520)  # Altura más compacta
        self.resize(550, 560)  # Tamaño más compacto
        self.setFixedSize(self.size())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)  # Espaciado entre secciones más compacto
        
        # Título
        title_label = QLabel(tr(I18N.Filament.DIALOG_ADD_HEADER_TITLE))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Sección de información básica
        self._setup_basic_info_section(main_layout)
        
        # Sección de especificaciones técnicas
        self._setup_technical_specs_section(main_layout)
        
        # Sección de inventario
        self._setup_inventory_section(main_layout)
        
        # Sección de notas opcionales
        self._setup_notes_section(main_layout)
        
        # Botones de acción
        self._setup_action_buttons(main_layout)
    
    def _setup_basic_info_section(self, main_layout):
        """Configura la sección de información básica"""
        basic_group = QGroupBox(tr(I18N.Filament.GROUP_BASIC_INFO))
        basic_layout = QFormLayout(basic_group)
        basic_layout.setVerticalSpacing(6)  # Espaciado más compacto
        
        # Nombre del filamento
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr(I18N.Filament.PLACEHOLDER_NAME))
        self.name_edit.setToolTip(tr(I18N.Filament.TOOLTIP_NAME_FIELD))
        basic_layout.addRow(tr(I18N.Filament.LABEL_DESCRIPTION), self.name_edit)
        
        # Marca
        self.brand_edit = QLineEdit()
        self.brand_edit.setPlaceholderText(tr(I18N.Filament.PLACEHOLDER_BRAND))
        self.brand_edit.setToolTip(tr(I18N.Filament.TOOLTIP_BRAND_FIELD))
        basic_layout.addRow(tr(I18N.Filament.LABEL_BRAND), self.brand_edit)
        
        # Tipo de filamento — userData = FilamentType.name (clave enum, no depende del idioma)
        self.type_combo = QComboBox()
        for t in FilamentType:
            self.type_combo.addItem(t.value, t.name)
        self.type_combo.setToolTip(tr(I18N.Filament.TOOLTIP_TYPE_FIELD))
        basic_layout.addRow(tr(I18N.Filament.LABEL_TYPE), self.type_combo)
        
        # Color — userData = FilamentColor.name (clave enum, independiente del idioma)
        self.color_combo = QComboBox()
        for c in FilamentColor:
            key = f"FilamentColor.{c.name}"
            display = tr(key)
            self.color_combo.addItem(c.value if display == key else display, c.name)
        self.color_combo.setToolTip(tr(I18N.Filament.TOOLTIP_COLOR_FIELD))
        basic_layout.addRow(tr(I18N.Filament.LABEL_COLOR), self.color_combo)
        
        main_layout.addWidget(basic_group)
    
    def _setup_technical_specs_section(self, main_layout):
        """Configura la sección de especificaciones del primer rollo"""
        tech_group = QGroupBox(tr(I18N.Filament.GROUP_FIRST_ROLL_SPECS))
        tech_group.setFixedHeight(90)  # Altura más compacta
        tech_layout = QFormLayout(tech_group)
        tech_layout.setVerticalSpacing(6)  # Espaciado más compacto
        
        # Peso del rollo con botones comunes
        weight_layout = QHBoxLayout()
        self.weight_spin = QSpinBox()
        self.weight_spin.setRange(1, 10000)
        self.weight_spin.setValue(1000)  # 1kg por defecto
        self.weight_spin.setSuffix("")
        self.weight_spin.setToolTip(tr(I18N.Filament.TOOLTIP_WEIGHT_FIELD))
        
        # Botones de pesos comunes
        weight_250_btn = QPushButton("250g")
        weight_500_btn = QPushButton("500g")
        weight_1kg_btn = QPushButton("1kg")
        
        weight_250_btn.clicked.connect(lambda: self.weight_spin.setValue(250))
        weight_500_btn.clicked.connect(lambda: self.weight_spin.setValue(500))
        weight_1kg_btn.clicked.connect(lambda: self.weight_spin.setValue(1000))
        
        for btn in [weight_250_btn, weight_500_btn, weight_1kg_btn]:
            btn.setMaximumWidth(60)
        
        weight_layout.addWidget(self.weight_spin)
        weight_layout.addSpacing(15)  # Espacio más considerable hacia derecha
        weight_layout.addWidget(QLabel(tr(I18N.Ui.COMMON_WEIGHTS_LABEL)))
        weight_layout.addWidget(weight_250_btn)
        weight_layout.addWidget(weight_500_btn)
        weight_layout.addWidget(weight_1kg_btn)
        weight_layout.addStretch()
        
        tech_layout.addRow(tr(I18N.Filament.LABEL_WEIGHT), weight_layout)
        
        # Precio del rollo
        self.price_roll_spin = CurrencyAwareSpinBox()
        self.price_roll_spin.setRange(0, 999999999)
        self.price_roll_spin.setValue(0)
        self.price_roll_spin.setToolTip(tr(I18N.Filament.TOOLTIP_PRICE_FIELD))
        tech_layout.addRow(tr(I18N.Filament.LABEL_PRICE), self.price_roll_spin)
        
        main_layout.addWidget(tech_group)
    
    def _setup_inventory_section(self, main_layout):
        """Configura la sección de configuración inicial"""
        inventory_group = QGroupBox(tr(I18N.Filament.GROUP_CONFIG))
        inventory_layout = QFormLayout(inventory_group)
        inventory_layout.setVerticalSpacing(4)  # Espaciado muy compacto para un solo elemento
        
        # Estado activo
        self.active_check = QCheckBox(tr(I18N.Filament.CHECKBOX_AVAILABLE))
        self.active_check.setChecked(True)
        self.active_check.setToolTip(tr(I18N.Filament.TOOLTIP_AVAILABLE_CHECKBOX))
        inventory_layout.addRow("", self.active_check)
        
        main_layout.addWidget(inventory_group)
    
    def _setup_notes_section(self, main_layout):
        """Configura la sección de notas opcionales"""
        notes_group = QGroupBox(tr(I18N.Filament.GROUP_NOTES_OPTIONAL))
        notes_group.setFixedHeight(110)
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(tr(I18N.Filament.PLACEHOLDER_NOTES))
        self.notes_edit.setMaximumHeight(80)  # Altura más compacta
        self.notes_edit.setToolTip(tr(I18N.Filament.TOOLTIP_NOTES_FIELD))
        notes_layout.addWidget(self.notes_edit)
        
        main_layout.addWidget(notes_group)
    
    def _setup_action_buttons(self, main_layout):
        """Configura los botones de acción"""
        # Layout de botones
        buttons_layout = QHBoxLayout()
        
        # Botón limpiar formulario
        self.clear_button = QPushButton(tr(I18N.Buttons.CLEAR))
        self.clear_button.setToolTip(tr(I18N.Filament.TOOLTIP_CLEAR_BTN))
        self.clear_button.setFixedHeight(30)
        self.clear_button.setFixedWidth(105)
        
        # Botón cancelar
        self.cancel_button = QPushButton(tr(I18N.Buttons.CANCEL))
        self.cancel_button.setToolTip(tr(I18N.Filament.TOOLTIP_CANCEL_BTN))
        self.cancel_button.setFixedHeight(30)
        self.cancel_button.setFixedWidth(105)
        
        # Botón guardar
        self.add_button = QPushButton(tr(I18N.Buttons.SAVE))
        self.add_button.setDefault(True)
        self.add_button.setToolTip(tr(I18N.Filament.TOOLTIP_ADD_BTN))
        self.add_button.setFixedHeight(30)
        self.add_button.setFixedWidth(105)
        
        
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
    
    def _setup_validators(self):
        """Configura validadores y validación en tiempo real"""
        # Conectar validación en tiempo real
        self.name_edit.textChanged.connect(self._validate_form)
        self.brand_edit.textChanged.connect(self._validate_form)
        self.weight_spin.valueChanged.connect(self._validate_form)
        self.price_roll_spin.valueChanged.connect(self._validate_form)
        
        # Formatear marca y descripción al terminar de editar
        self.brand_edit.editingFinished.connect(self._format_brand)
        self.name_edit.editingFinished.connect(self._format_description)
        
        # Validación inicial
        self._validate_form()
    
    def _connect_signals(self):
        """Conecta las señales de los widgets"""
        self.cancel_button.clicked.connect(self.reject)
        self.clear_button.clicked.connect(self._clear_form)
        self.add_button.clicked.connect(self._on_add_clicked)
        
        # Enter en campos principales también ejecuta agregar
        self.name_edit.returnPressed.connect(self._on_add_clicked)
    
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
        self.brand_edit.returnPressed.connect(self._on_add_clicked)
    
    def _set_defaults(self):
        """Configura valores por defecto inteligentes"""
        # Tipo más común — busca por userData (nombre del enum, independiente del idioma)
        pla_index = self.type_combo.findData("PLA")
        if pla_index >= 0:
            self.type_combo.setCurrentIndex(pla_index)
        
        # Color más común — busca por userData (nombre del enum, independiente del idioma)
        negro_index = self.color_combo.findData("BLACK")
        if negro_index >= 0:
            self.color_combo.setCurrentIndex(negro_index)
    
    def _validate_form(self):
        """Valida el formulario y habilita/deshabilita el botón agregar"""
        name_valid = len(self.name_edit.text().strip()) >= 3
        brand_valid = len(self.brand_edit.text().strip()) >= 2
        weight_valid = self.weight_spin.value() >= 100  # Mínimo 100g
        price_valid = self.price_roll_spin.value() > 0  # Debe ser mayor a 0
        
        is_valid = name_valid and brand_valid and weight_valid and price_valid
        self.add_button.setEnabled(is_valid)
    
    def _clear_form(self):
        """Limpia todos los campos del formulario"""
        reply = QMessageBox.question(
            self,
            tr(I18N.Filament.DIALOG_CLEAR_TITLE),
            tr(I18N.Filament.DIALOG_CLEAR_MESSAGE),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.name_edit.clear()
            self.brand_edit.clear()
            self.notes_edit.clear()
            self.weight_spin.setValue(1000)
            self.price_roll_spin.setValue(0)
            self.active_check.setChecked(True)
            self._set_defaults()
            self.name_edit.setFocus()
    
    def _on_add_clicked(self):
        """Maneja el clic en el botón agregar"""
        try:
            # Validación final
            if not self._validate_data():
                return
            
            # Recopilar datos
            filament_data = self._collect_form_data()
            
            # Confirmar adición
            price_per_kg = (filament_data['price_per_unit'] / filament_data['weight_grams']) * 1000
            
            reply = QMessageBox.question(
                self,
                tr(I18N.Filament.DIALOG_CONFIRM_ADD_TITLE),
                tr(I18N.Filament.DIALOG_CONFIRM_ADD_MESSAGE),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Obtener moneda actual del sistema
                from core.utils.currency_helper import CurrencyHelper
                current_currency = CurrencyHelper.get_current_currency()
                
                # Crear entidad Filament
                filament = Filament(
                    name=filament_data['name'],
                    brand=filament_data['brand'],
                    type=FilamentType[filament_data['type']],
                    color=FilamentColor[filament_data['color']],
                    weight_grams=filament_data['weight_grams'],
                    price_per_unit=filament_data['price_per_unit'],
                    price_per_gram=filament_data['price_per_gram'],
                    quantity_rolls=filament_data.get('quantity_rolls', 1),
                    current_stock_grams=filament_data['current_stock_grams'],
                    minimum_stock_grams=100,  # Valor por defecto
                    notes=filament_data.get('notes', ''),
                    is_active=filament_data.get('is_active', True),
                    currency_code=current_currency  # Guardar con moneda del sistema
                )
                
                # Guardar en la base de datos
                saved_filament = self.filament_repository.save(filament)
                logger.info("AddFilamentDialog", f"Filamento guardado con ID: {saved_filament.id}")
                
                # Crear registro del primer rollo individual
                try:
                    from domain.models.filament_roll import FilamentRoll
                    from infrastructure.database.repositories.filament_roll_repository import FilamentRollRepository
                    roll_repo = FilamentRollRepository(self.filament_repository.db_connection)
                    sku = roll_repo.generate_next_sku(saved_filament.id)
                    roll = FilamentRoll(
                        filament_id=saved_filament.id,
                        sku=sku,
                        initial_weight_grams=saved_filament.weight_grams,
                        current_weight_grams=saved_filament.weight_grams,
                        purchase_price=saved_filament.price_per_unit,
                        notes="Rollo inicial"
                    )
                    roll.update_price_per_gram()
                    roll_repo.save(roll)
                    logger.info("AddFilamentDialog", f"Rollo inicial creado para filamento {saved_filament.id}")
                except Exception as roll_err:
                    logger.error("AddFilamentDialog", f"Error creando rollo inicial: {roll_err}")
                
                # Emitir señal con datos del filamento guardado (incluyendo ID)
                self.filament_added.emit({
                    'id': saved_filament.id,
                    'name': saved_filament.name,
                    'brand': saved_filament.brand,
                    'type': saved_filament.type.value,
                    'color': saved_filament.color.value,
                    'weight_grams': saved_filament.weight_grams,
                    'price_per_unit': saved_filament.price_per_unit,
                    'price_per_gram': saved_filament.price_per_gram,
                    'quantity_rolls': saved_filament.quantity_rolls,
                    'current_stock_grams': saved_filament.current_stock_grams,
                    'notes': saved_filament.notes,
                    'is_active': saved_filament.is_active
                })
                
                # Mostrar mensaje de éxito
                QMessageBox.information(
                    self,
                    tr(I18N.StatusBar.SUCCESS),
                    tr(I18N.Filament.MSG_ADDED_SUCCESSFULLY)
                )
                
                # Cerrar diálogo
                self.accept()
            
        except Exception as e:
            # Loguear detalles técnicos completos
            logger.error("AddFilamentDialog", f"Error agregando filamento: {str(e)}", 
                        filament_data={
                            "name": self.name_edit.text(),
                            "brand": self.brand_edit.text(),
                            "type": self.type_combo.currentText()
                        })
            logger.log_exception("AddFilamentDialog", e, "_save_filament")
            
            # Mostrar mensaje genérico al usuario
            QMessageBox.critical(
                self,
                tr(I18N.Dialogs.ERROR_TITLE),
                "Ocurrió un error al agregar el filamento.\n\nRevise el archivo de log para más detalles."
            )
    
    def _validate_data(self) -> bool:
        """Validación final antes de guardar"""
        # Nombre
        if len(self.name_edit.text().strip()) < 3:
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Filament.VALIDATION_DESCRIPTION_MIN_CHARS))
            self.name_edit.setFocus()
            return False
        
        # Marca
        if len(self.brand_edit.text().strip()) < 2:
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Filament.VALIDATION_BRAND_MIN_CHARS))
            self.brand_edit.setFocus()
            return False
        
        # Peso del rollo
        if self.weight_spin.value() < 100:
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Filament.VALIDATION_WEIGHT_MIN))
            self.weight_spin.setFocus()
            return False
        
        # Precio del rollo - permitir desde 0
        if self.price_roll_spin.value() < 0:
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Filament.VALIDATION_PRICE_NEGATIVE))
            self.price_roll_spin.setFocus()
            return False
        
        return True
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """
        Recopila todos los datos del formulario para NUEVO filamento.
        CÁLCULO SIMPLE: precio_por_gramo = precio_rollo / peso_rollo
        NO aplicar promedio ponderado aquí.
        """
        weight_grams = self.weight_spin.value()
        price_roll = self.price_roll_spin.value()
        
        # CÁLCULO DIRECTO Y SIMPLE (sin promedio ponderado)
        price_per_gram = price_roll / weight_grams if weight_grams > 0 else 0
        
        return {
            'name': self.name_edit.text().strip(),
            'type': self.type_combo.currentData(),
            'brand': self.brand_edit.text().strip(),
            'color': self.color_combo.currentData(),
            'weight_grams': weight_grams,
            'price_per_unit': price_roll,  # Precio por rollo
            'price_per_gram': price_per_gram,  # Cálculo directo simple
            'current_stock_grams': weight_grams,  # Stock inicial = peso del primer rollo
            'quantity_rolls': 1,  # Siempre 1 rollo para nuevo filamento
            'is_active': self.active_check.isChecked(),
            'notes': self.notes_edit.toPlainText().strip(),
            'is_edit': False  # Siempre False para este diálogo
        }
    
    @staticmethod
    def add_new_filament(parent=None) -> Dict[str, Any]:
        """Método estático para mostrar el diálogo y obtener datos del nuevo filament"""
        dialog = AddFilamentDialog(parent)
        result_data = None
        
        def on_added(data):
            nonlocal result_data
            result_data = data
        
        dialog.filament_added.connect(on_added)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return result_data
        return None
