"""
Vista del diálogo de transferencias ACH para donantes de EE.UU.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QGroupBox, QApplication
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QIcon
from core.managers.theme_manager import PaletteManager
from core.managers.theme_manager import PaletteManager
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class AchTransferDialogView(QDialog):
    """Diálogo con datos ACH para donantes de EE.UU."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr(I18N.Donation.ACH_DIALOG_TITLE))
        self.setModal(True)
        self.setFixedSize(480, 380)

        self.theme_manager = PaletteManager()
        self.is_dark_mode = self.theme_manager.is_dark_mode

        self._load_config()
        self.setup_ui()

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def _load_config(self):
        try:
            from config.donation_config import DonationConfig
            info = DonationConfig.get_ach_info()
        except Exception:
            info = {'ach_enabled': False, 'ach': {}}

        self.ach_enabled = info.get('ach_enabled', False)
        self.ach = info.get('ach', {})

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Título
        title_label = QLabel(tr(I18N.Donation.ACH_DIALOG_SUBTITLE))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Separador
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep1)

        # Label beneficiario (igual que Paraguay)
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

        # Grupo ACH
        if self.ach_enabled:
            ach_fields = {
                tr(I18N.Donation.ACH_FIELD_HOLDER):  self.ach.get('holder', ''),
                tr(I18N.Donation.ACH_FIELD_BANK):    self.ach.get('bank', ''),
                tr(I18N.Donation.ACH_FIELD_ROUTING): self.ach.get('routing_number', ''),
                tr(I18N.Donation.ACH_FIELD_ACCOUNT): self.ach.get('account_number', ''),
                tr(I18N.Donation.ACH_FIELD_TYPE):    self.ach.get('account_type', ''),
            }
            copy_text = (
                f"Beneficiary: {self.ach.get('holder', '')}\n"
                f"Bank: {self.ach.get('bank', '')}\n"
                f"Routing: {self.ach.get('routing_number', '')}\n"
                f"Account: {self.ach.get('account_number', '')}\n"
                f"Type: {self.ach.get('account_type', '')}"
            )
            layout.addWidget(self._create_group("ACH", ach_fields, copy_text, "#1565C0"))

        layout.addSpacing(10)

        # Separador
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(sep2)

        # Nota
        note_label = QLabel(tr(I18N.Donation.ACH_NOTE))
        note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note_label.setWordWrap(True)
        note_color = "#888" if self.is_dark_mode else "#555"
        note_label.setStyleSheet(f"color: {note_color}; font-style: italic;")
        layout.addWidget(note_label)

        # Botón cerrar
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton(tr(I18N.Buttons.CLOSE))
        close_btn.setMinimumSize(90, 30)
        close_btn.clicked.connect(self.accept)
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)

    # ------------------------------------------------------------------
    # Group helper
    # ------------------------------------------------------------------

    def _create_group(self, title: str, fields: dict, copy_text: str, color: str):
        group = QGroupBox(title)
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

        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Datos (izquierda)
        data_text = "<br>".join([f"<b>{k}:</b> {v}" for k, v in fields.items()])
        data_label = QLabel(data_text)
        data_label.setStyleSheet("font-size: 11pt;")
        data_label.setMinimumWidth(280)
        data_label.setFixedHeight(100)
        content_layout.addWidget(data_label)

        content_layout.addStretch()

        # Botón copiar (derecha) — mismo estilo que Paraguay
        copy_btn = QPushButton(f" {tr(I18N.Donation.BANK_BTN_COPY)}")
        copy_btn.setIcon(QIcon(":/resources/resources/icons/sys_copy_v1.svg"))
        copy_btn.setToolTip(tr(I18N.Donation.TOOLTIP_COPY_DATA))
        copy_btn.setMinimumWidth(100)
        copy_btn.setFixedHeight(32)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._lighten(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken(color)};
            }}
        """)
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(copy_text))

        buttons_col = QVBoxLayout()
        buttons_col.setSpacing(5)
        buttons_col.addWidget(copy_btn)
        content_layout.addLayout(buttons_col)

        main_layout.addLayout(content_layout)
        group.setLayout(main_layout)
        return group

    # ------------------------------------------------------------------
    # Clipboard + feedback
    # ------------------------------------------------------------------

    def _copy_to_clipboard(self, text: str):
        QApplication.clipboard().setText(text)
        sender = self.sender()
        if sender:
            original_text = sender.text()
            original_icon = sender.icon()
            sender.setText(tr(I18N.Donation.MSG_COPIED))
            sender.setIcon(QIcon())
            sender.setEnabled(False)
            QTimer.singleShot(
                1500,
                lambda: self._restore_button(sender, original_text, original_icon)
            )

    def _restore_button(self, btn: QPushButton, original_text: str, original_icon: QIcon):
        if btn:
            btn.setText(original_text)
            btn.setIcon(original_icon)
            btn.setEnabled(True)

    # ------------------------------------------------------------------
    # Color helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _darken(hex_color: str) -> str:
        h = hex_color.lstrip('#')
        r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        return f"#{max(0,r-30):02x}{max(0,g-30):02x}{max(0,b-30):02x}"

    @staticmethod
    def _lighten(hex_color: str) -> str:
        h = hex_color.lstrip('#')
        r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        return f"#{min(255,r+30):02x}{min(255,g+30):02x}{min(255,b+30):02x}"
