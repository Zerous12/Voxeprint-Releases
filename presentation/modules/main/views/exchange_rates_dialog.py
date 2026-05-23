"""
Diálogo para configurar tasas de cambio entre monedas
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from infrastructure.database.repositories.currency_repository import CurrencyRepository
from infrastructure.database.repositories.exchange_rate_repository import ExchangeRateRepository
from core.managers.app_preferences_manager import AppPreferencesManager
from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class ExchangeRatesDialog(QDialog):
    """Diálogo para gestionar tasas de cambio"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.currency_repo = CurrencyRepository()
        self.exchange_repo = ExchangeRateRepository()
        self.prefs = AppPreferencesManager()
        
        self.base_currency = self.prefs.get_base_currency()
        
        self._setup_ui()
        self._load_exchange_rates()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        self.setWindowTitle(tr(I18N.App.EXCHANGE_RATES_TITLE))
        self.setModal(True)
        self.setMinimumSize(650, 450)
        
        layout = QVBoxLayout(self)
        
        # Título con sistema pivote resaltado
        title = QLabel(tr(I18N.ExchangeRates.TITLE_LABEL))
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Nota informativa mejorada con sistema pivote
        info = QLabel(tr(I18N.ExchangeRates.INFO_LABEL))
        info.setWordWrap(True)
        info.setStyleSheet("QLabel { color: #888; font-size: 9px; padding: 8px; margin-bottom: 10px; background: rgba(100,100,100,0.1); border-radius: 4px; }")
        layout.addWidget(info)
        
        # Tabla de tasas
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            tr(I18N.ExchangeRates.COL_INDEX),
            tr(I18N.ExchangeRates.COL_CURRENCY),
            tr(I18N.ExchangeRates.COL_CODE),
            tr(I18N.ExchangeRates.COL_SYMBOL),
            tr(I18N.ExchangeRates.COL_RATE),
            tr(I18N.ExchangeRates.COL_STATUS),
        ])
        
        # Configurar selección por celda
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Configurar tabla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID (oculta)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Moneda (más ancho)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Código
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Símbolo (más ancho)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Tasa de Cambio (más ancho)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Estado (ancho fijo pequeño)
        self.table.setColumnWidth(5, 100)  # Estado: 80px
        
        # Ocultar columna de ID
        self.table.setColumnHidden(0, True)
        
        # Ocultar números de fila (vertical header)
        self.table.verticalHeader().setVisible(False)
        
        # Conectar señal para actualizar colores de ComboBox según selección
        self.table.itemSelectionChanged.connect(self._update_combobox_colors)
        
        layout.addWidget(self.table)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.btn_save = QPushButton(tr(I18N.Buttons.SAVE))
        self.btn_save.setMinimumSize(105, 30)
        self.btn_save.clicked.connect(self._on_save)
        
        self.btn_cancel = QPushButton(tr(I18N.Buttons.CANCEL))
        self.btn_cancel.setMinimumSize(105, 30)
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        
        
        layout.addLayout(button_layout)
    
    def _load_exchange_rates(self):
        """Carga las tasas de cambio en la tabla - Solo desde USD (pivote)"""
        try:
            PIVOT = "USD"  # Moneda pivote del sistema FinTech
            
            # Obtener todas las monedas (activas e inactivas)
            currencies = self.currency_repo.get_all()
            
            # Ordenar: USD primero, luego alfabéticamente
            currencies_sorted = sorted(
                currencies, 
                key=lambda c: (c.code != PIVOT, c.code)
            )
            
            # Llenar tabla
            self.table.setRowCount(0)
            
            for idx, currency in enumerate(currencies_sorted, start=1):
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # ID (número de fila)
                id_item = QTableWidgetItem(str(idx))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if currency.code == PIVOT:
                    id_item.setBackground(Qt.GlobalColor.darkGreen)
                self.table.setItem(row, 0, id_item)
                
                # Nombre de moneda (no editable)
                name_item = QTableWidgetItem(currency.name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if currency.code == PIVOT:
                    name_item.setBackground(Qt.GlobalColor.darkGreen)
                self.table.setItem(row, 1, name_item)
                
                # Código (no editable)
                code_item = QTableWidgetItem(currency.code)
                code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                code_item.setFlags(code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if currency.code == PIVOT:
                    code_item.setBackground(Qt.GlobalColor.darkGreen)
                self.table.setItem(row, 2, code_item)
                
                # Símbolo (no editable)
                symbol_item = QTableWidgetItem(currency.symbol)
                symbol_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                symbol_item.setFlags(symbol_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if currency.code == PIVOT:
                    symbol_item.setBackground(Qt.GlobalColor.darkGreen)
                self.table.setItem(row, 3, symbol_item)
                
                # Tasa de cambio desde USD
                if currency.code == PIVOT:
                    # El pivote siempre es 1
                    rate_item = QTableWidgetItem("1.00")
                    rate_item.setFlags(rate_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    rate_item.setBackground(Qt.GlobalColor.darkGreen)
                    rate_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    # Obtener tasa USD → currency
                    rate_obj = self.exchange_repo.get_by_currencies(PIVOT, currency.code)
                    rate = rate_obj.rate if rate_obj else 0.0
                    rate_text = f"{rate:.8f}".rstrip('0')
                    if rate_text.endswith('.'):
                        rate_text += "00"
                    elif len(rate_text.split('.')[1]) < 2:
                        rate_text += '0' * (2 - len(rate_text.split('.')[1]))
                    rate_item = QTableWidgetItem(rate_text)
                    rate_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                rate_item.setData(Qt.ItemDataRole.UserRole, currency.code)
                self.table.setItem(row, 4, rate_item)
                
                # Estado (ComboBox)
                status_combo = QComboBox()
                status_combo.setObjectName("statusComboBox")  # Nombre para identificarlo
                status_combo.addItem(tr(I18N.ExchangeRates.STATUS_ACTIVE), True)
                status_combo.addItem(tr(I18N.ExchangeRates.STATUS_INACTIVE), False)
                status_combo.setCurrentIndex(0 if currency.is_active else 1)
                status_combo.setEnabled(currency.code != PIVOT)  # USD siempre activo
                
                # Establecer propiedad inicial
                status_combo.setProperty("selected", False)
                
                # Estilo completo con selector de propiedad para color dinámico
                status_combo.setStyleSheet("""
                    QComboBox {
                        border: none;
                        border-radius: 5px;
                        padding: 2px 2px 2px 8px;
                        background-color: transparent;
                        color: black;
                    }
                    QComboBox[selected="true"] {
                        color: white;
                    }
                    QComboBox:disabled {
                        border-radius: 5px;
                        padding: 2px 2px 2px 8px;
                        background-color: transparent;
                        color: gray;
                    }
                    QComboBox::drop-down {
                        subcontrol-origin: padding;
                        subcontrol-position: top right;
                        width: 0px;
                        padding: 3px 2px 3px 2px;
                        border-radius: 3px;
                        background-color: transparent;
                    }
                    QComboBox QAbstractItemView {
                        border-radius: 3px;
                        background-color: rgb(33, 37, 43);
                        color: rgb(255, 255, 255);
                    }
                """)
                
                self.table.setCellWidget(row, 5, status_combo)
            
        except Exception as e:
            logger.log_exception("ExchangeRatesDialog", e, "cargar tasas de cambio")
            QMessageBox.critical(
                self, 
                tr(I18N.Dialogs.ERROR_TITLE), 
                tr(I18N.ExchangeRates.MSG_LOAD_ERROR)
            )
    
    def _update_combobox_colors(self):
        """Actualiza los colores del ComboBox según la selección de fila"""
        # Obtener índices de todas las celdas seleccionadas
        selected_indexes = self.table.selectionModel().selectedIndexes()
        
        # Crear set de tuplas (fila, columna) para búsqueda rápida
        selected_cells = set((index.row(), index.column()) for index in selected_indexes)
        
        # Recorrer todas las filas de la tabla
        for row in range(self.table.rowCount()):
            combo_widget = self.table.cellWidget(row, 5)  # Columna Estado
            
            if combo_widget is not None and combo_widget.objectName() == "statusComboBox":
                # Verificar si la celda específica de la columna 5 está seleccionada
                is_selected = (row, 5) in selected_cells
                
                # Cambiar solo la propiedad 'selected' y refrescar el estilo
                combo_widget.setProperty("selected", is_selected)
                combo_widget.style().unpolish(combo_widget)
                combo_widget.style().polish(combo_widget)
            
    
    def _on_save(self):
        """Guarda los cambios de tasas de cambio y estados - Solo desde USD"""
        try:
            PIVOT = "USD"
            
            # Recorrer tabla y actualizar tasas y estados
            for row in range(self.table.rowCount()):
                code_item = self.table.item(row, 2)  # Código ahora está en columna 2
                rate_item = self.table.item(row, 4)  # Tasa ahora está en columna 4
                status_combo = self.table.cellWidget(row, 5)  # Estado en columna 5
                
                if code_item and rate_item:
                    currency_code = code_item.text()
                    
                    # Saltar si es el pivote USD
                    if currency_code == PIVOT:
                        continue
                    
                    # Actualizar tasa de cambio
                    new_rate_text = rate_item.text().strip()
                    if new_rate_text:
                        try:
                            new_rate = float(new_rate_text)
                            
                            if new_rate <= 0:
                                QMessageBox.warning(
                                    self,
                                    tr(I18N.ExchangeRates.MSG_RATE_ZERO_TITLE),
                                    tr(I18N.ExchangeRates.MSG_RATE_ZERO_TEXT, currency_code=currency_code)
                                )
                                return
                            
                            # Guardar solo la tasa USD → currency
                            self.exchange_repo.update_rate(PIVOT, currency_code, new_rate)
                            
                        except ValueError:
                            QMessageBox.warning(
                                self,
                                tr(I18N.ExchangeRates.MSG_INVALID_RATE_TITLE),
                                tr(I18N.ExchangeRates.MSG_INVALID_RATE_TEXT,
                                   currency_code=currency_code, rate_text=new_rate_text)
                            )
                            return
                    
                    # Actualizar estado activo/inactivo
                    if status_combo:
                        is_active = status_combo.currentData()  # True o False
                        success = self.currency_repo.update_active_status(currency_code, is_active)
                        if not success:
                            logger.warning("ExchangeRatesDialog", f"No se pudo actualizar el estado de {currency_code}")
            
            # Limpiar cache del CurrencyHelper
            from core.utils.currency_helper import CurrencyHelper
            CurrencyHelper.clear_cache()
            
            QMessageBox.information(
                self,
                tr(I18N.StatusBar.SUCCESS),
                tr(I18N.ExchangeRates.MSG_SAVE_SUCCESS)
            )
            self.accept()
            
        except ValueError as e:
            # Errores de validación - mostrar al usuario
            logger.warning("ExchangeRatesDialog", f"Error de validación guardando tasas: {str(e)}")
            QMessageBox.warning(
                self,
                tr(I18N.ExchangeRates.MSG_VALIDATION_ERROR_TITLE),
                str(e)
            )
        except Exception as e:
            # Errores técnicos - log detallado, mensaje genérico
            logger.log_exception("ExchangeRatesDialog", e, "guardar tasas de cambio")
            QMessageBox.critical(
                self,
                tr(I18N.Dialogs.ERROR_TITLE),
                tr(I18N.ExchangeRates.MSG_SAVE_ERROR)
            )
