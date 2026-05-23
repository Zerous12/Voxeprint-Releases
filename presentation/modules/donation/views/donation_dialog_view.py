"""
Vista del diálogo de donaciones
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon
from core.managers.theme_manager import PaletteManager
from presentation.common.icon_utils import IconUtils
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class DonationDialogView(QDialog):
    """Diálogo para mostrar opciones de donación"""
    
    # Señales
    crypto_clicked = Signal()
    bank_transfer_clicked = Signal()
    ach_transfer_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr(I18N.Donation.DIALOG_TITLE))
                
        self.resize(500, 380)        
        # Detectar tema actual
        self.theme_manager = PaletteManager()
        self.is_dark_mode = self.theme_manager.is_dark_mode
        
        self.setup_ui()
        self.setFixedSize(self.sizeHint())

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 10, 30, 10)
        
        # Título principal
        title_label = QLabel(tr(I18N.Donation.MESSAGE_THANKS))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Separador
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line1)
        
        # Mensaje de agradecimiento
        message_label = QLabel(tr(I18N.Donation.MESSAGE_MAIN))
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Espaciador
        layout.addSpacing(10)
        
        # Botones de donación
        self.create_donation_card(
            layout,
            tr(I18N.Donation.CARD_ACH_TITLE),
            tr(I18N.Donation.CARD_ACH_DESC),
            ":/resources/resources/icons/sys_ach_transfer_icon_mod.svg",
            "#1565C0",  # Azul USA
            self.ach_transfer_clicked
        )
        
        self.create_donation_card(
            layout,
            tr(I18N.Donation.CARD_BANK_TRANSFER_TITLE),
            tr(I18N.Donation.CARD_BANK_TRANSFER_DESC),
            ":/resources/resources/icons/sys_bank_transfer_icon_mod.svg",
            "#D4AF37",  # Color dorado para bancos
            self.bank_transfer_clicked
        )
        
        self.create_donation_card(
            layout,
            tr(I18N.Donation.CARD_CRYPTO_TITLE),
            tr(I18N.Donation.CARD_CRYPTO_DESC),
            ":/resources/resources/icons/sys_usdt_coin.svg",
            "#8E44AD",  # Color morado para cripto
            self.crypto_clicked
        )
        
        # Espaciador flexible
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Separador
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)
        
        # Nota de agradecimiento
        thanks_label = QLabel(tr(I18N.Donation.MESSAGE_APPRECIATION))
        thanks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thanks_color = "#888" if self.is_dark_mode else "#999"
        thanks_label.setStyleSheet(f"color: {thanks_color}; font-style: italic;")
        layout.addWidget(thanks_label)
        
        # Botón cerrar
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_button = QPushButton(tr(I18N.Buttons.CLOSE))
        close_button.setMinimumSize(90, 30)
        close_button.clicked.connect(self.reject)
        close_layout.addWidget(close_button)
        
        layout.addLayout(close_layout)
    
    def create_donation_card(self, parent_layout, title, description, icon_path, border_color, signal):
        """Crea una tarjeta de donación estilizada con icono y texto"""
        # Frame contenedor
        card_frame = QFrame()
        card_frame.setObjectName("donationCard")
        card_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        card_frame.setMinimumHeight(80)
        card_frame.setMaximumHeight(90)
        
        # Colores según el tema
        if self.is_dark_mode:
            # Tema oscuro - colores actuales
            bg_color = "#2A2A2A"
            hover_bg_color = "#333333"
            title_color = "white"
            desc_color = "#AAAAAA"
        else:
            # Tema claro - colores suaves
            bg_color = "#FFFFFF"
            hover_bg_color = "#F5F5F5"
            title_color = "#2C3E50"
            desc_color = "#7F8C8D"
        
        # Estilo del frame
        card_frame.setStyleSheet(f"""
            QFrame#donationCard {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 10px;
                padding: 10px;
            }}
            QFrame#donationCard:hover {{
                background-color: {hover_bg_color};
                border: 2px solid {self._lighten_color(border_color) if self.is_dark_mode else self._darken_color(border_color)};
            }}
        """)
        
        # Layout horizontal para el contenido
        card_layout = QHBoxLayout(card_frame)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel()
        
        # Solo recolorear en tema claro (en oscuro ya es blanco)
        if self.is_dark_mode:
            # En tema oscuro, cargar directamente (SVG ya es blanco)
            icon = QIcon(icon_path)
            icon_pixmap = icon.pixmap(48, 48)
        else:
            # En tema claro, recolorear a negro para que sea visible
            try:
                icon = IconUtils.recolor_icon_svg(icon_path, "#000000")
                icon_pixmap = icon.pixmap(48, 48)
            except Exception:
                # Fallback: cargar icono sin recolorear
                icon = QIcon(icon_path)
                icon_pixmap = icon.pixmap(48, 48)
        
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(48, 48)
        icon_label.setScaledContents(False)
        card_layout.addWidget(icon_label)
        
        # Layout vertical para texto
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {title_color};")
        text_layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(description)
        desc_font = QFont()
        desc_font.setPointSize(9)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet(f"color: {desc_color};")
        text_layout.addWidget(desc_label)
        
        card_layout.addLayout(text_layout)
        card_layout.addStretch()
        
        # Hacer que el frame sea clickeable
        card_frame.mousePressEvent = lambda event: signal.emit()
        
        parent_layout.addWidget(card_frame)
    
    def create_donation_button(self, parent_layout, text, tooltip, color, signal):
        """Crea un botón de donación estilizado (método legacy)"""
        button = QPushButton(text)
        button.setMinimumSize(200, 50)
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Estilo del botón
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._lighten_color(color)};
            }}
        """)
        
        button.clicked.connect(signal.emit)
        
        # Layout horizontal para centrar el botón
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(button)
        h_layout.addStretch()
        
        parent_layout.addLayout(h_layout)
    
    def _darken_color(self, hex_color):
        """Oscurece un color hex para el hover"""
        # Convertir hex a RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Oscurecer
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _lighten_color(self, hex_color):
        """Aclara un color hex para el pressed"""
        # Convertir hex a RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Aclarar
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        
        return f"#{r:02x}{g:02x}{b:02x}"
