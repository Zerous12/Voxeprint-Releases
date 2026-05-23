"""
Diálogo específico para agregar nuevos clientes al sistema.
Interfaz optimizada para la creación rápida de clientes.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QPushButton, QLabel, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Dict, Any
import re

from infrastructure.database.repositories.customer_repository import CustomerRepository
from infrastructure.database.connection import DatabaseConnection
from domain.models.customer import Customer
from core.utils.logger import logger
from core.utils.translation_keys import I18N
from core.utils.translation_helper import tr
from core.managers.locale_manager import LocaleManager


class AddCustomerDialog(QDialog):
    """Diálogo especializado para agregar nuevos clientes"""
    
    # Señal emitida cuando se agrega un cliente exitosamente
    customer_added = Signal(dict)  # Emite datos del nuevo cliente
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Servicios
        self.customer_repository = CustomerRepository(DatabaseConnection())
        
        # Configurar UI
        self._setup_ui()
        self._setup_validators()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario optimizada para agregar"""
        # Configurar ventana
        self.setWindowTitle(tr(I18N.Customer.DIALOG_ADD_TITLE))
        self.setModal(True)
        self.setMinimumSize(450, 290)  # Altura más compacta
        self.resize(450, 290)  # Tamaño más compacto
        self.setFixedSize(self.size())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)  # Espaciado entre secciones más compacto
        
        # Título
        title_label = QLabel(tr(I18N.Customer.DIALOG_ADD_HEADER_TITLE))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Sección de datos personales
        self._setup_personal_data_section(main_layout)
        
        # Sección de datos de contacto
        self._setup_contact_data_section(main_layout)
        
        # Botones de acción
        self._setup_action_buttons(main_layout)
    
    def _setup_personal_data_section(self, main_layout):
        """Configura la sección de datos personales"""
        personal_group = QGroupBox(tr(I18N.Customer.GROUP_PERSONAL_INFO))
        personal_group.setFixedHeight(90)
        personal_layout = QFormLayout(personal_group)
        personal_layout.setVerticalSpacing(6)  # Espaciado más compacto
        
        # Razón social / Nombre completo
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText(tr(I18N.Customer.FIELD_NAME_PLACEHOLDER))
        self.full_name_edit.setToolTip(tr(I18N.Customer.TOOLTIP_NAME_FIELD))
        personal_layout.addRow(tr(I18N.Customer.LABEL_SOCIAL_REASON_REQUIRED), self.full_name_edit)
        
        # RUC o CI
        self.ruc_ci_edit = QLineEdit()
        self.ruc_ci_edit.setPlaceholderText(tr(I18N.Customer.PLACEHOLDER_RUC_CI))
        self.ruc_ci_edit.setToolTip(tr(I18N.Customer.FIELD_TAX_ID_PLACEHOLDER))
        personal_layout.addRow(LocaleManager().get_tax_id_label() + ":", self.ruc_ci_edit)
        
        main_layout.addWidget(personal_group)
    
    def _setup_contact_data_section(self, main_layout):
        """Configura la sección de datos de contacto"""
        contact_group = QGroupBox(tr(I18N.Customer.GROUP_CONTACT))
        contact_group.setFixedHeight(90)
        contact_layout = QFormLayout(contact_group)
        contact_layout.setVerticalSpacing(6)  # Espaciado más compacto
        
        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText(tr(I18N.Customer.PLACEHOLDER_EMAIL))
        self.email_edit.setToolTip(tr(I18N.Customer.TOOLTIP_EMAIL_FIELD))
        contact_layout.addRow(tr(I18N.Customer.LABEL_EMAIL), self.email_edit)
        
        # Teléfono
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText(tr(I18N.Customer.PLACEHOLDER_PHONE))
        self.phone_edit.setToolTip(tr(I18N.Customer.TOOLTIP_PHONE_FIELD))
        contact_layout.addRow(tr(I18N.Customer.LABEL_PHONE), self.phone_edit)
        
        main_layout.addWidget(contact_group)
    
    def _setup_action_buttons(self, main_layout):
        """Configura los botones de acción"""
        # Layout de botones
        buttons_layout = QHBoxLayout()
        
        # Botón limpiar formulario
        self.clear_button = QPushButton(tr(I18N.Buttons.CLEAR))
        self.clear_button.setToolTip(tr(I18N.Customer.TOOLTIP_CLEAR_BTN))
        self.clear_button.setFixedHeight(30)
        self.clear_button.setFixedWidth(105)
        
        # Botón cancelar
        self.cancel_button = QPushButton(tr(I18N.Buttons.CANCEL))
        self.cancel_button.setToolTip(tr(I18N.Customer.TOOLTIP_CANCEL_BTN))
        self.cancel_button.setFixedHeight(30)
        self.cancel_button.setFixedWidth(105)
        
        # Botón agregar
        self.add_button = QPushButton(tr(I18N.Buttons.SAVE))
        self.add_button.setDefault(True)
        self.add_button.setToolTip(tr(I18N.Customer.TOOLTIP_ADD_BTN))
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
        self.full_name_edit.textChanged.connect(self._validate_form)
        self.email_edit.textChanged.connect(self._validate_form)
        self.phone_edit.textChanged.connect(self._validate_form)
        
        # Validación inicial
        self._validate_form()
    
    def _connect_signals(self):
        """Conecta las señales de los widgets"""
        self.cancel_button.clicked.connect(self.reject)
        self.clear_button.clicked.connect(self._clear_form)
        self.add_button.clicked.connect(self._on_add_clicked)
        
        # Formateo automático de nombre
        self.full_name_edit.editingFinished.connect(self._format_full_name)
        
        # Validación de RUC/CI en tiempo real
        self.ruc_ci_edit.textChanged.connect(self._validate_ruc_ci_format)
        
        # Enter en campos principales también ejecuta agregar
        self.full_name_edit.returnPressed.connect(self._on_add_clicked)
        self.email_edit.returnPressed.connect(self._on_add_clicked)
        self.phone_edit.returnPressed.connect(self._on_add_clicked)
    
    def _format_full_name(self):
        """Formatea el nombre completo con mayúscula inicial en cada palabra"""
        text = self.full_name_edit.text().strip()
        if text:
            # Capitalizar cada palabra
            formatted = ' '.join(word.capitalize() for word in text.split())
            self.full_name_edit.setText(formatted)
    
    def _validate_ruc_ci_format(self, text: str):
        """Valida el formato de RUC/CI en tiempo real"""
        # Validación silenciosa, sin indicador visual
        pass
    
    def _validate_form(self):
        """Valida el formulario y habilita/deshabilita el botón agregar"""
        name_valid = len(self.full_name_edit.text().strip()) >= 3
        
        # Al menos un método de contacto debe estar presente
        email_text = self.email_edit.text().strip()
        phone_text = self.phone_edit.text().strip()
        contact_valid = len(email_text) > 0 or len(phone_text) > 0
        
        is_valid = name_valid and contact_valid
        self.add_button.setEnabled(is_valid)
    
    def _clear_form(self):
        """Limpia todos los campos del formulario"""
        reply = QMessageBox.question(
            self,
            tr(I18N.Customer.DIALOG_CLEAR_TITLE),
            tr(I18N.Customer.DIALOG_CLEAR_MESSAGE),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.full_name_edit.clear()
            self.ruc_ci_edit.clear()
            self.email_edit.clear()
            self.phone_edit.clear()
            self.full_name_edit.setFocus()
    
    def _on_add_clicked(self):
        """Maneja el clic en el botón agregar"""
        try:
            # Validación final
            if not self._validate_data():
                return
            
            # Recopilar datos
            customer_data = self._collect_form_data()
            
            # Confirmar adición
            reply = QMessageBox.question(
                self,
                tr(I18N.Customer.DIALOG_CONFIRM_ADD_TITLE),
                tr(I18N.Customer.DIALOG_CONFIRM_ADD_MESSAGE),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Crear customer usando el repositorio
                try:
                    customer_id = self.customer_repository.create({
                        'full_name': customer_data['full_name'],
                        'ruc_ci': customer_data['ruc_ci'],
                        'email': customer_data['email'],
                        'phone_number': customer_data['phone'],
                        'is_default': False
                    })
                    
                    if customer_id:
                        # Emitir señal
                        self.customer_added.emit({
                            'id': customer_id,
                            'full_name': customer_data['full_name'],
                            'ruc_ci': customer_data['ruc_ci'],
                            'email': customer_data['email'],
                            'phone': customer_data['phone'],
                            'is_default': False
                        })
                        
                        # Mostrar mensaje de éxito
                        QMessageBox.information(
                            self,
                            tr(I18N.Customer.MSG_ADDED_SUCCESSFULLY),
                            tr(I18N.Customer.MSG_CUSTOMER_ADDED_DETAIL, name=customer_data['full_name'])
                        )
                        
                        # Cerrar diálogo
                        self.accept()
                    else:
                        logger.error("AddCustomerDialog", "No se pudo crear el cliente en la base de datos")
                        QMessageBox.critical(
                            self,
                            tr(I18N.Customer.MSG_ERROR_ADDING_TITLE),
                            tr(I18N.Customer.MSG_ERROR_ADDING)
                        )
                except Exception as db_error:
                    logger.log_exception("AddCustomerDialog", db_error, "crear cliente en base de datos")
                    QMessageBox.critical(
                        self,
                        tr(I18N.Customer.MSG_ERROR_ADDING_TITLE),
                        tr(I18N.Customer.MSG_ERROR_DETAIL)
                    )
            
        except Exception as e:
            logger.log_exception("AddCustomerDialog", e, "agregar cliente")
            QMessageBox.critical(
                self,
                "Error al agregar cliente",
                tr(I18N.Customer.MSG_ERROR_DETAIL)
            )
    
    def _validate_data(self) -> bool:
        """Validación final antes de guardar"""
        # Nombre
        if len(self.full_name_edit.text().strip()) < 3:
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Customer.VALIDATION_NAME_MIN_CHARS))
            self.full_name_edit.setFocus()
            return False
        
        # Al menos un método de contacto
        email_text = self.email_edit.text().strip()
        phone_text = self.phone_edit.text().strip()
        
        if not email_text and not phone_text:
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Customer.VALIDATION_CONTACT_REQUIRED))
            self.email_edit.setFocus()
            return False
        
        # Validación de email si se proporciona
        if email_text and '@' not in email_text:
            QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Customer.VALIDATION_EMAIL_INVALID))
            self.email_edit.setFocus()
            return False
        
        # Validar formato de RUC/CI si se proporciona
        ruc_ci_text = self.ruc_ci_edit.text().strip()
        if ruc_ci_text:
            # Patrón para CI: solo números (ej: 1223344)
            ci_pattern = r'^\d+$'
            # Patrón para RUC: números-número (ej: 1223344-5)
            ruc_pattern = r'^\d+-\d+$'
            
            if not (re.match(ci_pattern, ruc_ci_text) or re.match(ruc_pattern, ruc_ci_text)):
                QMessageBox.warning(
                    self,
                    tr(I18N.Dialogs.CONFIRM).strip(),
                    tr(I18N.Customer.VALIDATION_RUC_CI_FORMAT)
                )
                self.ruc_ci_edit.setFocus()
                return False
            
            # Verificar que el RUC/CI no existe
            try:
                existing = self.customer_repository.find_by_ruc_ci(ruc_ci_text)
                if existing:
                    QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Customer.VALIDATION_RUC_CI_DUPLICATE, ruc_ci=ruc_ci_text))
                    self.ruc_ci_edit.setFocus()
                    return False
            except Exception as e:
                logger.warning("AddCustomerDialog", f"Error al verificar RUC/CI duplicado: {str(e)}")
                # Continuar si hay error en la verificación
        
        return True
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Recopila todos los datos del formulario para NUEVO cliente"""
        return {
            'full_name': self.full_name_edit.text().strip(),
            'ruc_ci': self.ruc_ci_edit.text().strip() or None,
            'email': self.email_edit.text().strip() or None,
            'phone': self.phone_edit.text().strip() or None,
            'is_edit': False  # Siempre False para este diálogo
        }
    
    @staticmethod
    def add_new_customer(parent=None) -> Dict[str, Any]:
        """Método estático para mostrar el diálogo y obtener datos del nuevo cliente"""
        dialog = AddCustomerDialog(parent)
        result_data = None
        
        def on_added(data):
            nonlocal result_data
            result_data = data
        
        dialog.customer_added.connect(on_added)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return result_data
        return None
