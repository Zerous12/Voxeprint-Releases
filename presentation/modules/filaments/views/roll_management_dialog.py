"""
Diálogo para gestionar los rollos individuales de un filamento.
Muestra tabla de rollos con opciones de editar peso, eliminar rollo, y ajustar stock.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSpinBox, QPushButton, QLabel, QTextEdit,
    QGroupBox, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QDoubleSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from typing import List, Optional

from domain.models.filament import Filament
from domain.models.filament_roll import FilamentRoll
from presentation.widgets.currencyaware_mod.currency_aware_widgets import CurrencyAwareSpinBox
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class RollManagementDialog(QDialog):
    """Diálogo para gestionar rollos individuales de un filamento"""

    rolls_changed = Signal()  # Se emite cuando se modifica cualquier rollo

    def __init__(self, parent=None, filament: Filament = None, facade=None):
        super().__init__(parent)
        self.filament = filament
        self.facade = facade
        self._rolls: List[FilamentRoll] = []

        if not self.filament or not self.facade:
            raise ValueError("RollManagementDialog requiere filament y facade")

        self._setup_ui()
        self._connect_signals()
        self._load_rolls()

    def _setup_ui(self):
        self.setWindowTitle(tr(I18N.RollManagement.DIALOG_TITLE, name=self.filament.name))
        self.setModal(True)
        self.setMinimumSize(700, 520)
        self.resize(750, 560)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # Header
        header = QLabel(tr(I18N.RollManagement.HEADER_LABEL, name=self.filament.name, brand=self.filament.brand))
        header_font = QFont()
        header_font.setPointSize(13)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # Resumen
        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label.setStyleSheet("color: gray; font-size: 11px;")
        main_layout.addWidget(self.summary_label)

        # Tabla de rollos
        self._setup_table(main_layout)

        # Barra inferior: Operaciones + Cerrar
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        # Grupo de operaciones (izquierda)
        self._setup_roll_actions(bottom_layout)

        # Spacer horizontal
        bottom_layout.addStretch()

        # Grupo de acción cerrar (derecha, compacto)
        close_group = QGroupBox(tr(I18N.RollManagement.GROUP_ACTION))
        close_group_layout = QHBoxLayout(close_group)
        close_group_layout.setContentsMargins(6, 4, 6, 4)
        self.btn_close = QPushButton(tr(I18N.Buttons.CLOSE))
        self.btn_close.setFixedHeight(30)
        self.btn_close.setFixedWidth(105)
        self.btn_close.setStyleSheet(
            "QPushButton { color: #e6fdff; font-weight: bold; border: 1px solid #bcbcbc; "
            "border-radius: 5px; background-color: #f09292; }"
            "QPushButton:hover { color: #ffffff; background-color: #be0000; "
            "border: 1px solid #00aaff; }"
            "QPushButton:pressed { color: #ffffff; background-color: #ff0000; "
            "border: 1px solid #69cdff; }"
        )
        self.btn_close.clicked.connect(self.accept)
        close_group_layout.addWidget(self.btn_close)
        close_group.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        bottom_layout.addWidget(close_group)

        main_layout.addLayout(bottom_layout)

    def _setup_table(self, main_layout):
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            tr(I18N.RollManagement.COL_ID),
            tr(I18N.RollManagement.COL_SKU),
            tr(I18N.RollManagement.COL_INITIAL_WEIGHT),
            tr(I18N.RollManagement.COL_CURRENT_WEIGHT),
            tr(I18N.RollManagement.COL_USAGE_PCT),
            tr(I18N.RollManagement.COL_PURCHASE_PRICE),
            tr(I18N.RollManagement.COL_PRICE_PER_GRAM),
            tr(I18N.RollManagement.COL_NOTES),
        ])
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setFrameShape(QTableWidget.Shape.NoFrame)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnHidden(0, True)  # Ocultar ID interno

        main_layout.addWidget(self.table)

    def _setup_roll_actions(self, parent_layout):
        actions_group = QGroupBox(tr(I18N.RollManagement.GROUP_OPERATIONS))
        actions_layout = QHBoxLayout(actions_group)

        # Estilo btn_add_more_filament (naranja) → Ajustar Peso
        style_adjust = (
            "QPushButton { color: #e6fdff; font-weight: bold; border: 1px solid #bcbcbc; "
            "border-radius: 5px; background-color: #f6b565; }"
            "QPushButton:hover { color: #ffffff; background-color: #ffaa00; "
            "border: 1px solid #00aaff; }"
            "QPushButton:pressed { color: #ffffff; background-color: #ffaa00; "
            "border: 1px solid #69cdff; }"
        )
        # Estilo btn_mod_filament (azul) → Editar Precio
        style_edit = (
            "QPushButton { color: #e6fdff; font-weight: bold; border: 1px solid #bcbcbc; "
            "border-radius: 5px; background-color: #46aac4; }"
            "QPushButton:hover { color: #ffffff; background-color: #009dc4; "
            "border: 1px solid #00aaff; }"
            "QPushButton:pressed { color: #ffffff; background-color: #ffaa00; "
            "border: 1px solid #69cdff; }"
        )
        # Estilo btn_delete_filament (rojo) → Eliminar Rollo
        style_delete = (
            "QPushButton { color: #e6fdff; font-weight: bold; border: 1px solid #bcbcbc; "
            "border-radius: 5px; background-color: #f09292; }"
            "QPushButton:hover { color: #ffffff; background-color: #be0000; "
            "border: 1px solid #00aaff; }"
            "QPushButton:pressed { color: #ffffff; background-color: #ff0000; "
            "border: 1px solid #69cdff; }"
        )

        self.btn_adjust_weight = QPushButton(tr(I18N.RollManagement.BTN_ADJUST_WEIGHT))
        self.btn_adjust_weight.setFixedHeight(30)
        self.btn_adjust_weight.setFixedWidth(105)
        self.btn_adjust_weight.setStyleSheet(style_adjust)
        self.btn_adjust_weight.setToolTip(tr(I18N.RollManagement.TOOLTIP_ADJUST_WEIGHT))

        self.btn_edit_roll = QPushButton(tr(I18N.RollManagement.BTN_EDIT_PRICE))
        self.btn_edit_roll.setFixedHeight(30)
        self.btn_edit_roll.setFixedWidth(105)
        self.btn_edit_roll.setStyleSheet(style_edit)
        self.btn_edit_roll.setToolTip(tr(I18N.RollManagement.TOOLTIP_EDIT_PRICE))

        self.btn_delete_roll = QPushButton(tr(I18N.RollManagement.BTN_DELETE_ROLL))
        self.btn_delete_roll.setFixedHeight(30)
        self.btn_delete_roll.setFixedWidth(105)
        self.btn_delete_roll.setStyleSheet(style_delete)
        self.btn_delete_roll.setToolTip(tr(I18N.RollManagement.TOOLTIP_DELETE_ROLL))

        actions_layout.addWidget(self.btn_adjust_weight)
        actions_layout.addWidget(self.btn_edit_roll)
        actions_layout.addWidget(self.btn_delete_roll)

        parent_layout.addWidget(actions_group)

    def _connect_signals(self):
        self.btn_adjust_weight.clicked.connect(self._on_adjust_weight)
        self.btn_edit_roll.clicked.connect(self._on_edit_price)
        self.btn_delete_roll.clicked.connect(self._on_delete_roll)

    # ── Data ──────────────────────────────────────────────

    def _load_rolls(self):
        self._rolls = self.facade.get_rolls_for_filament(self.filament.id)
        self._populate_table()
        self._update_summary()

    def _populate_table(self):
        self.table.setRowCount(0)
        for roll in self._rolls:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(roll.id)))

            item_sku = QTableWidgetItem(roll.sku or f"#{roll.id}")
            item_sku.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_sku.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            self.table.setItem(row, 1, item_sku)

            item_initial = QTableWidgetItem(f"{roll.initial_weight_grams:,.0f}")
            item_initial.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, item_initial)

            item_current = QTableWidgetItem(f"{roll.current_weight_grams:,.0f}")
            item_current.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            # Color visual por nivel de uso
            if roll.current_weight_grams <= 0:
                item_current.setForeground(QColor("#e74c3c"))
            elif roll.usage_percent > 80:
                item_current.setForeground(QColor("#e67e22"))
            self.table.setItem(row, 3, item_current)

            item_usage = QTableWidgetItem(f"{roll.usage_percent:.0f}%")
            item_usage.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, item_usage)

            item_price = QTableWidgetItem(f"{roll.purchase_price:,.0f}")
            item_price.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, item_price)

            item_ppg = QTableWidgetItem(f"{roll.price_per_gram:,.2f}")
            item_ppg.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 6, item_ppg)

            self.table.setItem(row, 7, QTableWidgetItem(roll.notes or ""))

    def _update_summary(self):
        summary = self.facade.get_roll_stock_summary(self.filament.id)
        count = summary['roll_count']
        stock = summary['total_stock_grams']
        ppg = summary['weighted_price_per_gram']
        self.summary_label.setText(
            tr(I18N.RollManagement.SUMMARY_TEXT,
               count=count,
               stock=f"{stock:,.0f}",
               ppg=f"{ppg:,.2f}")
        )

    def _get_selected_roll(self) -> Optional[FilamentRoll]:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._rolls):
            QMessageBox.warning(self,
                                tr(I18N.RollManagement.NO_SELECTION_TITLE),
                                tr(I18N.RollManagement.NO_SELECTION_MSG))
            return None
        return self._rolls[row]

    # ── Actions ───────────────────────────────────────────

    def _on_adjust_weight(self):
        roll = self._get_selected_roll()
        if not roll:
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(tr(I18N.RollManagement.ADJUST_WEIGHT_TITLE))
        dlg.setFixedSize(380, 160)
        layout = QVBoxLayout(dlg)

        sku_label = roll.sku or f"#{roll.id}"
        info = QLabel(tr(I18N.RollManagement.ADJUST_WEIGHT_INFO,
                         sku=sku_label,
                         weight=f"{roll.initial_weight_grams:,.0f}"))
        layout.addWidget(info)

        form = QFormLayout()
        spin = QDoubleSpinBox()
        spin.setRange(0, roll.initial_weight_grams)
        spin.setValue(roll.current_weight_grams)
        spin.setSuffix(" g")
        spin.setDecimals(1)
        form.addRow(tr(I18N.RollManagement.LABEL_NEW_CURRENT_WEIGHT), spin)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btn_ok = QPushButton(tr(I18N.Buttons.SAVE))
        btn_cancel = QPushButton(tr(I18N.Buttons.CANCEL))
        btn_ok.clicked.connect(dlg.accept)
        btn_cancel.clicked.connect(dlg.reject)
        btns.addStretch()
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_weight = spin.value()
            self.facade.adjust_roll_weight(roll.id, new_weight, self.filament.id)
            self._load_rolls()
            self.rolls_changed.emit()

    def _on_edit_price(self):
        roll = self._get_selected_roll()
        if not roll:
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(tr(I18N.RollManagement.EDIT_PRICE_TITLE))
        dlg.setFixedSize(380, 160)
        layout = QVBoxLayout(dlg)

        sku_label = roll.sku or f"#{roll.id}"
        info = QLabel(tr(I18N.RollManagement.EDIT_PRICE_INFO,
                         sku=sku_label,
                         weight=f"{roll.initial_weight_grams:,.0f}"))
        layout.addWidget(info)

        form = QFormLayout()
        spin = CurrencyAwareSpinBox()
        spin.setRange(0, 999999999)
        spin.setValue(int(roll.purchase_price))
        form.addRow(tr(I18N.RollManagement.LABEL_PURCHASE_PRICE), spin)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btn_ok = QPushButton(tr(I18N.Buttons.SAVE))
        btn_cancel = QPushButton(tr(I18N.Buttons.CANCEL))
        btn_ok.clicked.connect(dlg.accept)
        btn_cancel.clicked.connect(dlg.reject)
        btns.addStretch()
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            roll.purchase_price = spin.value()
            roll.update_price_per_gram()
            self.facade.update_filament_roll(roll)
            self._load_rolls()
            self.rolls_changed.emit()

    def _on_delete_roll(self):
        roll = self._get_selected_roll()
        if not roll:
            return

        remaining = len(self._rolls)
        if remaining <= 1:
            QMessageBox.warning(
                self,
                tr(I18N.RollManagement.LAST_ROLL_TITLE),
                tr(I18N.RollManagement.LAST_ROLL_MESSAGE)
            )
            return

        sku_label = roll.sku or f"#{roll.id}"
        answer = QMessageBox.question(
            self,
            tr(I18N.RollManagement.CONFIRM_DELETE_TITLE),
            tr(I18N.RollManagement.CONFIRM_DELETE_MESSAGE,
               sku=sku_label,
               weight=f"{roll.current_weight_grams:,.0f}",
               price=f"{roll.purchase_price:,.0f}"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.facade.delete_filament_roll(roll.id, self.filament.id)
            self._load_rolls()
            self.rolls_changed.emit()

    # ── Static helper ─────────────────────────────────────

    @staticmethod
    def manage_rolls(parent, filament, facade) -> bool:
        """Abre el diálogo y retorna True si hubo cambios"""
        dlg = RollManagementDialog(parent, filament, facade)
        dlg.exec()
        # Consideramos que siempre puede haber cambios si se abrió
        return True
