from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QSize

from core.utils.currency_helper import CurrencyHelper
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N

class PreviewColors:
    BASE_COST = "#def2d4"       # Verde agua suave (material, luz, desgaste)
    MARGIN = "#CCECFE"          # Celeste pastel (margen error)
    SUBTOTAL = "#f3d9b4"         # Verde lima claro (subtotal)
    COMMISSION = "#f6c9c1"      # Lila pastel (comisión)
    POST_PROCESS = "#FEF8CC"    # Amarillo pastel (post-procesado)
    TAX = "#F2F2F2"             # Naranja pastel (IVA)
    TOTAL = "#e5b4f3"          # Rojo pastel (total a pagar)
    TEXT = "#222222"

class QuotePreviewDialog(QDialog):
    """Pequeño diálogo de vista previa del cálculo"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr(I18N.Quote.DIALOG_PREVIEW_TITLE))
        self.setModal(True)
        self.setMinimumSize(QSize(360, 410))
        self.setMaximumSize(QSize(380, 410))

        self._build_ui()

    def _build_ui(self):        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Encabezados de contexto (impresora y filamento)
        self.lbl_context = QLabel("")
        self.lbl_context.setWordWrap(True)
        layout.addWidget(self.lbl_context)

        # Grid con resultados
        grid = QGridLayout()
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(2)

        def add_row(row: int, label_text: str):
            lbl = QLabel(label_text)
            val = QLabel("")
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            grid.addWidget(lbl, row, 0)
            grid.addWidget(val, row, 1)
            return lbl, val  # ✅ Devolver ambos para poder ocultarlos

        self.lbl_material, self.val_material = add_row(0, tr(I18N.Quote.PREVIEW_LABEL_MATERIAL))
        self.lbl_electric, self.val_electric = add_row(1, tr(I18N.Quote.PREVIEW_LABEL_ELECTRIC))
        self.lbl_wear, self.val_wear = add_row(2, tr(I18N.Quote.PREVIEW_LABEL_WEAR))
        self.lbl_failure_margin, self.val_failure_margin = add_row(3, tr(I18N.Quote.PREVIEW_LABEL_FAILURE_MARGIN))

        # Separadores visuales mediante labels vacíos
        grid.addWidget(QLabel(""), 4, 0)

        self.lbl_subtotal, self.val_subtotal = add_row(5, tr(I18N.Quote.PREVIEW_LABEL_SUBTOTAL))
        self.lbl_commission, self.val_commission = add_row(6, tr(I18N.Quote.PREVIEW_LABEL_COMMISSION))
        self.lbl_post_processing, self.val_post_processing = add_row(7, tr(I18N.Quote.PREVIEW_LABEL_POST_PROCESSING))  # ✅ Guardamos ambos para ocultar
        self.lbl_tax, self.val_tax = add_row(8, tr(I18N.Quote.PREVIEW_LABEL_TAX))

        grid.addWidget(QLabel(""), 9, 0)

        self.lbl_total, self.val_total = add_row(10, tr(I18N.Quote.PREVIEW_LABEL_TOTAL))
        # Costos base
        self._style_row(self.lbl_material, self.val_material, PreviewColors.BASE_COST)
        self._style_row(self.lbl_electric, self.val_electric, PreviewColors.BASE_COST)
        self._style_row(self.lbl_wear, self.val_wear, PreviewColors.BASE_COST)

        # Margen
        self._style_row(self.lbl_failure_margin, self.val_failure_margin, PreviewColors.MARGIN)

        # Subtotal
        self._style_row(self.lbl_subtotal, self.val_subtotal, PreviewColors.SUBTOTAL, bold=True)

        # Comisión
        self._style_row(self.lbl_commission, self.val_commission, PreviewColors.COMMISSION)

        # Post-procesado
        self._style_row(self.lbl_post_processing, self.val_post_processing, PreviewColors.POST_PROCESS)

        # IVA
        self._style_row(self.lbl_tax, self.val_tax, PreviewColors.TAX)

        # Total
        self._style_row(self.lbl_total, self.val_total, PreviewColors.TOTAL, bold=True)
        layout.addLayout(grid)
        layout.addSpacing(16)
        # Botonera
        btns = QHBoxLayout()
        btns.addStretch()
        self.btn_close = QPushButton(tr(I18N.Buttons.CLOSE))
        self.btn_close.setMinimumSize(QSize(90, 30))
        self.btn_close.clicked.connect(self.accept)
        btns.addWidget(self.btn_close)
        layout.addLayout(btns)

    def set_data(self, result: dict):
        """Puebla los valores de la vista previa"""
        def money(v):
            try:
                value = float(v) if v is not None else 0
                return CurrencyHelper.format_with_current_currency(value)
            except Exception:
                return CurrencyHelper.format_with_current_currency(0)

        printer = (result.get('printer_info') or {})
        filament = (result.get('filament_info') or {})
        p_name = printer.get('name') or tr(I18N.Quote.PREVIEW_DEFAULT_PRINTER)
        fil_type = filament.get('type', '')
        fil_color = filament.get('color', '')
        f_name = f"{fil_type} - {fil_color}" if fil_type and fil_color else (filament.get('name') or tr(I18N.Quote.PREVIEW_DEFAULT_FILAMENT))
        self.lbl_context.setText(f"{p_name} • {f_name}")
        font = self.lbl_context.font()
        font.setPointSize(12)
        self.lbl_context.setFont(font)

        material = result.get('material_cost', 0)
        electric = result.get('electricity_cost', 0)
        wear = result.get('operation_cost', 0)  # Cambiado de machine_wear_cost a operation_cost
        failure_m = result.get('failure_margin_cost', 0)

        subtotal_with_margin = result.get('subtotal_with_margin')
        if subtotal_with_margin is None:
            subtotal_with_margin = (material or 0) + (electric or 0) + (wear or 0) + (failure_m or 0)

        commission = result.get('commission_cost', 0)
        tax = result.get('tax_amount', 0)
        total = result.get('total_to_pay', 0)
        
        # ✅ Obtener post-procesado del resultado
        post_processing = result.get('post_amount', 0)
        
        self.val_material.setText(money(material))
        self.val_electric.setText(money(electric))
        self.val_wear.setText(money(wear))
        self.val_failure_margin.setText(money(failure_m))
        self.val_subtotal.setText(money(subtotal_with_margin))
        self.val_commission.setText(money(commission))
        
        # ✅ Mostrar u ocultar post-procesado según si está activo
        if post_processing > 0:
            self.val_post_processing.setText(money(post_processing))
            self.lbl_post_processing.setVisible(True)
            self.val_post_processing.setVisible(True)
        else:
            # Ocultar completamente la línea de post-procesado
            self.lbl_post_processing.setVisible(False)
            self.val_post_processing.setVisible(False)
        
        self.val_tax.setText(money(tax))
        self.val_total.setText(money(total))

    def _style_row(self, lbl: QLabel, val: QLabel, bg_color: str, bold=False):
        weight = "bold" if bold else "normal"
        style = f"""
            background-color: {bg_color};
            color: {PreviewColors.TEXT};
            padding: 4px 6px;
            font-weight: {weight};
        """
        lbl.setStyleSheet(style)
        val.setStyleSheet(style)