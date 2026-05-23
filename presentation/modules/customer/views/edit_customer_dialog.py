"""
Diálogo de formulario para agregar/modificar clientes.
Forma parte del sistema de gestión de clientes.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Optional, Dict, Any
import re

from domain.models.customer import Customer
from infrastructure.database.repositories.customer_repository import CustomerRepository
from infrastructure.database.connection import DatabaseConnection
from core.utils.logger import logger
from core.utils.translation_keys import I18N
from core.utils.translation_helper import tr
from core.managers.locale_manager import LocaleManager


class EditCustomerDialog(QDialog):
    """Diálogo para agregar o modificar clientes"""
    
    # Señal emitida cuando se guarda un cliente
    customer_saved = Signal(dict)  # Emite datos del cliente
    
    def __init__(self, parent=None, customer: Optional[Customer] = None):
        super().__init__(parent)
        
        # Estado
        self.customer = customer
        self.is_edit_mode = customer is not None
        self.customer_repository = CustomerRepository(DatabaseConnection())
        
        # Configurar UI
        self._setup_ui()
        self._setup_validators()
        self._connect_signals()
        
        # Cargar datos si estamos editando
        if self.is_edit_mode:
            self._load_customer_data()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar ventana
        title = tr(I18N.Customer.DIALOG_EDIT_TITLE) if self.is_edit_mode else tr(I18N.Customer.DIALOG_ADD_TITLE)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(450, 290)
        self.resize(450, 290)
        self.setFixedSize(self.size())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        
        # Título
        title_label = QLabel(title)
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
        personal_layout.setVerticalSpacing(6)
        
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
        contact_layout.setVerticalSpacing(6)
        
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
        self.full_name_edit.textChanged.connect(self._validate_form)
        self.email_edit.textChanged.connect(self._validate_form)
        self.phone_edit.textChanged.connect(self._validate_form)
        
        # Validación inicial
        self._validate_form()
    
    def _connect_signals(self):
        """Conecta las señales"""
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self._on_save_clicked)
        
        # Formateo automático de nombre
        self.full_name_edit.editingFinished.connect(self._format_full_name)
        
        # Validación de RUC/CI en tiempo real
        self.ruc_ci_edit.textChanged.connect(self._validate_ruc_ci_format)
    
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
        """Valida el formulario y habilita/deshabilita el botón guardar"""
        name_valid = len(self.full_name_edit.text().strip()) >= 3
        
        # Al menos un método de contacto debe estar presente
        email_text = self.email_edit.text().strip()
        phone_text = self.phone_edit.text().strip()
        contact_valid = len(email_text) > 0 or len(phone_text) > 0
        
        is_valid = name_valid and contact_valid
        self.save_button.setEnabled(is_valid)
    
    def _load_customer_data(self):
        """Carga los datos del cliente a editar"""
        if not self.customer:
            return
        
        self.full_name_edit.setText(self.customer.full_name or "")
        self.ruc_ci_edit.setText(self.customer.ruc_ci or "")
        self.email_edit.setText(self.customer.email or "")
        self.phone_edit.setText(self.customer.phone_number or "")
    
    def _on_save_clicked(self):
        """Maneja el clic en guardar"""
        try:
            # Validar datos
            if not self._validate_data():
                return
            
            # Confirmación simple
            if self.is_edit_mode:
                confirm_title = tr(I18N.Customer.CONFIRM_MODIFY_TITLE)
                confirm_msg = tr(I18N.Customer.CONFIRM_MODIFY_MESSAGE)
            else:
                confirm_title = tr(I18N.Customer.DIALOG_CONFIRM_ADD_TITLE)
                confirm_msg = tr(I18N.Customer.DIALOG_CONFIRM_ADD_MESSAGE)
            reply = QMessageBox.question(
                self,
                confirm_title,
                confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Recopilar datos
                customer_data = self._collect_form_data()
                
                if self.is_edit_mode:
                    # Actualizar cliente existente
                    try:
                        success = self.customer_repository.update(self.customer.id, {
                            'full_name': customer_data['full_name'],
                            'ruc_ci': customer_data['ruc_ci'],
                            'email': customer_data['email'],
                            'phone_number': customer_data['phone'],
                            'is_default': self.customer.is_default  # Mantener valor actual
                        })
                        
                        if success:
                            customer_data['id'] = self.customer.id
                            customer_data['is_default'] = self.customer.is_default
                        else:
                            logger.error("EditCustomerDialog", f"No se pudo actualizar el cliente ID: {self.customer.id}")
                            QMessageBox.critical(
                                self,
                                tr(I18N.Customer.MSG_ERROR_EDITING_TITLE),
                                tr(I18N.Customer.MSG_ERROR_EDITING)
                            )
                            return
                    except Exception as db_error:
                        logger.log_exception("EditCustomerDialog", db_error, f"actualizar cliente ID {self.customer.id}")
                        QMessageBox.critical(
                            self,
                            tr(I18N.Customer.MSG_ERROR_EDITING_TITLE),
                            tr(I18N.Customer.MSG_ERROR_EDITING_DETAIL)
                        )
                        return
                else:
                    # Crear nuevo cliente
                    try:
                        customer_id = self.customer_repository.create({
                            'full_name': customer_data['full_name'],
                            'ruc_ci': customer_data['ruc_ci'],
                            'email': customer_data['email'],
                            'phone_number': customer_data['phone'],
                            'is_default': False
                        })
                        
                        if customer_id:
                            customer_data['id'] = customer_id
                            customer_data['is_default'] = False
                        else:
                            logger.error("EditCustomerDialog", "No se pudo crear el cliente en la base de datos")
                            QMessageBox.critical(
                                self,
                                tr(I18N.Customer.MSG_ERROR_ADDING_TITLE),
                                tr(I18N.Customer.MSG_ERROR_ADDING)
                            )
                            return
                    except Exception as db_error:
                        logger.log_exception("EditCustomerDialog", db_error, "crear cliente en base de datos")
                        QMessageBox.critical(
                            self,
                            tr(I18N.Customer.MSG_ERROR_ADDING_TITLE),
                            tr(I18N.Customer.MSG_ERROR_DETAIL)
                        )
                        return
                
                # Emitir señal
                self.customer_saved.emit(customer_data)
                
                # Cerrar diálogo
                self.accept()
            
        except Exception as e:
            if self.is_edit_mode:
                err_title = tr(I18N.Customer.MSG_ERROR_EDITING_TITLE)
                err_msg = tr(I18N.Customer.MSG_ERROR_EDITING_DETAIL)
            else:
                err_title = tr(I18N.Customer.MSG_ERROR_ADDING_TITLE)
                err_msg = tr(I18N.Customer.MSG_ERROR_DETAIL)
            logger.log_exception("EditCustomerDialog", e, "guardar cliente")
            QMessageBox.critical(self, err_title, err_msg)
    
    def _validate_data(self) -> bool:
        """Valida los datos del formulario"""
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
            
            # Verificar RUC/CI duplicado
            try:
                existing = self.customer_repository.find_by_ruc_ci(ruc_ci_text)
                if existing and (not self.is_edit_mode or existing.id != self.customer.id):
                    QMessageBox.warning(self, tr(I18N.Dialogs.CONFIRM).strip(), tr(I18N.Customer.VALIDATION_RUC_CI_DUPLICATE, ruc_ci=ruc_ci_text))
                    self.ruc_ci_edit.setFocus()
                    return False
            except Exception as e:
                logger.warning("EditCustomerDialog", f"Error al verificar RUC/CI duplicado: {str(e)}")
                # Continuar si hay error en la verificación
        
        return True
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Recopila los datos del formulario"""
        return {
            'full_name': self.full_name_edit.text().strip(),
            'ruc_ci': self.ruc_ci_edit.text().strip() or None,
            'email': self.email_edit.text().strip() or None,
            'phone': self.phone_edit.text().strip() or None,
            'is_edit': self.is_edit_mode
        }
    
    @staticmethod
    def add_customer(parent=None) -> Optional[Dict[str, Any]]:
        """Método estático para agregar un cliente"""
        dialog = EditCustomerDialog(parent)
        result_data = None
        
        def on_saved(data):
            nonlocal result_data
            result_data = data
        
        dialog.customer_saved.connect(on_saved)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return result_data
        return None
    
    @staticmethod
    def edit_customer(parent=None, customer: Customer = None) -> Optional[Dict[str, Any]]:
        """Método estático para editar un cliente"""
        if not customer:
            return None
        
        dialog = EditCustomerDialog(parent, customer)
        result_data = None
        
        def on_saved(data):
            nonlocal result_data
            result_data = data
        
        dialog.customer_saved.connect(on_saved)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return result_data
        return None
