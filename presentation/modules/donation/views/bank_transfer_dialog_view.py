"""
Vista del diálogo de transferencias bancarias
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QGroupBox, QApplication, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QClipboard, QIcon
from presentation.common.icon_utils import IconUtils
from core.managers.theme_manager import PaletteManager
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class BankTransferDialogView(QDialog):
    """Diálogo para mostrar información de transferencias bancarias"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr(I18N.Donation.BANK_DIALOG_TITLE))
        self.setModal(True)
        self.setFixedSize(480, 380)
        
        # Detectar tema
        self.theme_manager = PaletteManager()
        self.is_dark_mode = self.theme_manager.is_dark_mode
        
        # Estado de visibilidad de alias
        self.alias_visible = {}

        self._load_bank_config()
        self.setup_ui()
        
    def _load_bank_config(self):
        """Carga los datos bancarios desde DonationConfig. Si no existe, usa valores vacíos."""
        try:
            from config.donation_config import DonationConfig
            info = DonationConfig.get_bank_info()
            self.bank_config_available = info.get('enabled', False)
            self.holder_name = info.get('holder_name', '')
            self.holder_ci = info.get('holder_ci', '')
            banks = info.get('banks', [])
            self.local_bank = banks[0] if banks else {}
        except Exception:
            self.bank_config_available = False
            self.holder_name = ''
            self.holder_ci = ''
            self.local_bank = {}

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Título principal
        title_label = QLabel(tr(I18N.Donation.BANK_DIALOG_SUBTITLE))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Separador
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line1)
        
        # Información general
        holder_label = QLabel(tr(I18N.Donation.BANK_BENEFICIARY_LABEL))
        holder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        holder_label.setStyleSheet("""
            padding: 10px; 
            background-color: rgba(128, 128, 128, 0.2); 
            border: 1px solid rgba(128, 128, 128, 0.3);
            border-radius: 5px;
            font-size: 12pt;
        """)
        layout.addWidget(holder_label)

        layout.addSpacing(10)

        if not self.bank_config_available:
            unavailable_label = QLabel(tr(I18N.Donation.BANK_NOT_AVAILABLE))
            unavailable_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            unavailable_label.setWordWrap(True)
            unavailable_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            layout.addWidget(unavailable_label)
        else:
            # Banco local (SIPAP)
            local_group = self.create_bank_group(
                tr(I18N.Donation.BANK_LOCAL_NAME),
                {
                    tr(I18N.Donation.BANK_FIELD_HOLDER): self.holder_name,
                    tr(I18N.Donation.BANK_FIELD_CI): self.holder_ci,
                    tr(I18N.Donation.BANK_FIELD_ACCOUNT): self.local_bank.get('account_number', ''),
                    tr(I18N.Donation.BANK_FIELD_CURRENCY): self.local_bank.get('currency', ''),
                    tr(I18N.Donation.BANK_FIELD_ENTITY): self.local_bank.get('entity', ''),
                },
                f"CI: {self.holder_ci}",
                "#388E3C",
                "local_bank"
            )
            layout.addWidget(local_group)
        
        # Espaciador
        layout.addSpacing(10)
        
        # Separador
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)
        
        # Nota informativa
        info_label = QLabel(tr(I18N.Donation.BANK_NOTE))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_color = "#888" if self.is_dark_mode else "#555"
        info_label.setStyleSheet(f"color: {info_color}; font-style: italic;")
        layout.addWidget(info_label)
        
        # Botón cerrar
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_button = QPushButton(tr(I18N.Buttons.CLOSE))
        close_button.setMinimumSize(90, 30)
        close_button.clicked.connect(self.accept)
        close_layout.addWidget(close_button)
        
        layout.addLayout(close_layout)
    
    def create_bank_group(self, bank_name, account_data, alias, color, bank_id):
        """Crea un grupo con información bancaria"""
        group = QGroupBox(bank_name)
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 12pt;
                border: 2px solid {color};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                color: {color};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        group.setMaximumHeight(150)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        
        # Layout horizontal: datos a la izquierda, botones a la derecha
        content_layout = QHBoxLayout()
        content_layout.setSpacing(6)
        
        # Datos de la cuenta (izquierda) - stack para no cambiar tamaño al alternar
        stack = QStackedWidget()
        stack.setMinimumWidth(280)
        stack.setFixedHeight(110)
        
        data_text = "<br>".join([f"<b>{k}:</b> {v}" for k, v in account_data.items()])
        data_label = QLabel(data_text)
        data_label.setStyleSheet("font-size: 11pt;")
        data_label.setWordWrap(True)
        data_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        stack.addWidget(data_label)  # index 0
        
        # Contenedor del alias - index 1
        self.alias_visible[bank_id] = False
        alias_container = QFrame()
        alias_container.setObjectName(f"alias_container_{bank_id}")
        alias_container.setMinimumWidth(280)        
        alias_container.setFixedHeight(110)
        alias_container.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 128, 128, 0.15);
                border-radius: 5px;
                padding: 5px;
            }
        """)
        alias_inner_layout = QHBoxLayout(alias_container)
        alias_inner_layout.setContentsMargins(0, 0, 0, 0)
        
        alias_label = QLabel(f"<b>Alias</b> {alias}")
        alias_label.setStyleSheet("font-size: 12pt;")
        alias_inner_layout.addWidget(alias_label)
        stack.addWidget(alias_container)  # index 1
        
        content_layout.addWidget(stack, 1)
        
        content_layout.addStretch()
        
        # Botones (derecha) - vertical
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(5)
        
        # Botón copiar datos
        copy_button = QPushButton(f" {tr(I18N.Donation.BANK_BTN_COPY)}")
        copy_button.setIcon(QIcon(":/resources/resources/icons/sys_copy_v1.svg"))
        copy_button.setToolTip(tr(I18N.Donation.TOOLTIP_COPY_DATA))
        copy_button.setMinimumWidth(100)
        copy_button.setFixedHeight(32)
        copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._lighten_color(color)};
            }}
        """)
        copy_text = "\n".join([f"{k}: {v}" for k, v in account_data.items()])
        copy_button.clicked.connect(lambda: self._copy_to_clipboard(copy_text))
        buttons_layout.addWidget(copy_button)
        
        # Botón ver/ocultar alias con icono y texto
        eye_button = QPushButton(f" {tr(I18N.Donation.BANK_BTN_ALIAS)}")
        eye_button.setObjectName(f"eye_button_{bank_id}")
        eye_button.setToolTip(tr(I18N.Donation.TOOLTIP_SHOW_ALIAS))
        eye_button.setMinimumWidth(100)
        eye_button.setFixedHeight(32)
        eye_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._lighten_color(color)};
            }}
        """)
        self._update_eye_icon(eye_button, False)
        buttons_layout.addWidget(eye_button)
        
        content_layout.addLayout(buttons_layout)
        main_layout.addLayout(content_layout)
        
        # Conectar botón de alias
        eye_button.clicked.connect(
            lambda checked, bid=bank_id, sw=stack, btn=eye_button: 
            self._toggle_alias_visibility(bid, sw, btn)
        )

        group.setLayout(main_layout)
        return group
    
    def _toggle_alias_visibility(self, bank_id, stack, button):
        """Alterna entre datos de cuenta y alias usando QStackedWidget"""
        self.alias_visible[bank_id] = not self.alias_visible[bank_id]
        is_visible = self.alias_visible[bank_id]
        
        stack.setCurrentIndex(1 if is_visible else 0)
        self._update_eye_icon(button, is_visible)
        button.setToolTip(tr(I18N.Donation.TOOLTIP_SHOW_DATA) if is_visible else tr(I18N.Donation.TOOLTIP_SHOW_ALIAS))
    
    def _update_eye_icon(self, button, is_visible):
        """Actualiza el icono del botón de ojo"""
        if is_visible:
            icon_path = ":/resources/resources/icons/sys_eye_crossed.svg"
        else:
            icon_path = ":/resources/resources/icons/sys_eye_view.svg"
       
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(18, 18))
    
    def _copy_to_clipboard(self, text):
        """Copia texto al portapapeles"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # Feedback visual
        sender = self.sender()
        if sender:
            original_text = sender.text()
            original_icon = sender.icon()
            sender.setText(tr(I18N.Donation.MSG_COPIED))
            sender.setIcon(QIcon())
            sender.setEnabled(False)
            
            QTimer.singleShot(1500, lambda: self._restore_button(sender, original_text, original_icon))
    
    def _restore_button(self, button, original_text, original_icon=None):
        """Restaura el texto original del botón"""
        if button:
            button.setText(original_text)
            if original_icon:
                button.setIcon(original_icon)
            button.setEnabled(True)
    
    def _darken_color(self, hex_color):
        """Oscurece un color hex para el hover"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _lighten_color(self, hex_color):
        """Aclara un color hex para el pressed"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        
        return f"#{r:02x}{g:02x}{b:02x}"
