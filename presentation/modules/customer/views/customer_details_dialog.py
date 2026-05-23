"""
Diálogo para mostrar información detallada de un cliente.
Muestra todos los datos del cliente de forma organizada y legible.
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

from domain.models.customer import Customer
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from core.managers.locale_manager import LocaleManager


class CustomerDetailsDialog(QDialog):
    """Diálogo para mostrar detalles completos de un cliente"""
    
    def __init__(self, parent=None, customer: Optional[Customer] = None):
        super().__init__(parent)
        
        self.customer = customer
        
        # Configurar UI
        self._setup_ui()
        
        # Cargar datos del cliente
        if self.customer:
            self._load_customer_details()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar ventana
        customer_name = self.customer.full_name if self.customer else tr(I18N.Customer.HEADER_CUSTOMER_NAME)
        self.setWindowTitle(f"👤 {tr(I18N.Customer.DIALOG_DETAIL_TITLE)}: {customer_name}")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.resize(550, 400)
        
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
        self._setup_contact_section(scroll_layout)
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
        
        # Nombre del cliente
        self.name_label = QLabel(tr(I18N.Customer.HEADER_CUSTOMER_NAME))
        name_font = QFont()
        name_font.setPointSize(18)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        
        # RUC/CI
        self.ruc_ci_label = QLabel(LocaleManager().get_tax_id_label())
        self.ruc_ci_label.setStyleSheet("color: #AAA; font-size: 14px;")
        
        # Status
        self.status_label = QLabel(tr(I18N.Customer.STATUS_DEFAULT_CUSTOMER))
        self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.ruc_ci_label)
        info_layout.addWidget(self.status_label)
        info_layout.addStretch()
                
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
    
    def _setup_basic_info_section(self, main_layout):
        """Configura la sección de información básica"""
        basic_group = QGroupBox(tr(I18N.Customer.GROUP_BASIC_INFO))
        basic_layout = QFormLayout(basic_group)
        
        self.name_detail_label = QLabel()
        self.ruc_ci_detail_label = QLabel()
        
        basic_layout.addRow(tr(I18N.Customer.LABEL_FULL_NAME), self.name_detail_label)
        basic_layout.addRow(LocaleManager().get_tax_id_label() + ":", self.ruc_ci_detail_label)
        
        main_layout.addWidget(basic_group)
    
    def _setup_contact_section(self, main_layout):
        """Configura la sección de contacto"""
        contact_group = QGroupBox(tr(I18N.Customer.GROUP_CONTACT))
        contact_layout = QFormLayout(contact_group)
        
        self.email_label = QLabel()
        self.phone_label = QLabel()
        
        contact_layout.addRow(tr(I18N.Customer.LABEL_EMAIL), self.email_label)
        contact_layout.addRow(tr(I18N.Customer.LABEL_PHONE), self.phone_label)
        
        main_layout.addWidget(contact_group)
    
    def _setup_metadata_section(self, main_layout):
        """Configura la sección de metadatos"""
        meta_group = QGroupBox(tr(I18N.Customer.GROUP_SYSTEM_INFO))
        meta_layout = QFormLayout(meta_group)
        
        self.created_at_label = QLabel()
        self.updated_at_label = QLabel()
        self.default_status_label = QLabel()
        
        meta_layout.addRow(tr(I18N.Customer.LABEL_REGISTRATION_DATE), self.created_at_label)
        meta_layout.addRow(tr(I18N.Customer.LABEL_LAST_MODIFIED), self.updated_at_label)
        meta_layout.addRow(tr(I18N.Customer.LABEL_STATUS), self.default_status_label)
        
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
    
    def _load_customer_details(self):
        """Carga los detalles del cliente en la interfaz"""
        if not self.customer:
            return
        
        # Header
        self.name_label.setText(self.customer.full_name or tr(I18N.Customer.DEFAULT_NO_NAME))
        self.ruc_ci_label.setText(self.customer.ruc_ci or tr(I18N.Customer.DEFAULT_NO_RUC_CI))
        
        if self.customer.is_default:
            self.status_label.setText(tr(I18N.Customer.STATUS_DEFAULT_CUSTOMER))
            self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
            self.status_label.setVisible(True)
        else:
            self.status_label.setVisible(False)
        
        # Información básica
        self.name_detail_label.setText(self.customer.full_name or tr(I18N.Customer.DEFAULT_NO_NAME))
        self.ruc_ci_detail_label.setText(self.customer.ruc_ci or tr(I18N.Customer.DEFAULT_NOT_SPECIFIED))
        
        # Contacto
        self.email_label.setText(self.customer.email or tr(I18N.Customer.DEFAULT_NOT_SPECIFIED))
        self.phone_label.setText(self.customer.phone_number or tr(I18N.Customer.DEFAULT_NOT_SPECIFIED))
        
        # Metadatos
        if self.customer.created_at:
            try:
                created_date = datetime.fromisoformat(self.customer.created_at.replace('Z', '+00:00'))
                self.created_at_label.setText(created_date.strftime("%d/%m/%Y %H:%M"))
            except:
                self.created_at_label.setText(str(self.customer.created_at))
        else:
            self.created_at_label.setText(tr(I18N.Customer.DEFAULT_NOT_AVAILABLE))
        
        if self.customer.updated_at:
            try:
                updated_date = datetime.fromisoformat(self.customer.updated_at.replace('Z', '+00:00'))
                self.updated_at_label.setText(updated_date.strftime("%d/%m/%Y %H:%M"))
            except:
                self.updated_at_label.setText(str(self.customer.updated_at))
        else:
            self.updated_at_label.setText(tr(I18N.Customer.DEFAULT_NOT_AVAILABLE))
        
        if self.customer.is_default:
            self.default_status_label.setText(tr(I18N.Customer.STATUS_DEFAULT))
            self.default_status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        else:
            self.default_status_label.setText(tr(I18N.Customer.STATUS_REGULAR))
            self.default_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
