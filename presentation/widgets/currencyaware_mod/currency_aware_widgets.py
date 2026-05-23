"""
Widgets inteligentes que se adaptan automáticamente a cambios de moneda

Estos widgets se actualizan automáticamente cuando cambia la moneda del sistema,
conectándose al signal currency_changed del CurrencyManager.
"""
from PySide6.QtWidgets import QDoubleSpinBox, QLabel
from PySide6.QtCore import Slot
from typing import Optional

from core.managers.currency_manager import CurrencyManager
from core.utils.currency_helper import CurrencyHelper


class CurrencyAwareSpinBox(QDoubleSpinBox):
    """
    QDoubleSpinBox que se adapta automáticamente a la moneda actual
    
    Características:
    - Configura decimales según la moneda (0 para PYG, 2 para USD/EUR)
    - Configura prefijo/sufijo según la posición del símbolo
    - Se actualiza automáticamente cuando cambia la moneda
    
    Example:
        >>> spinbox = CurrencyAwareSpinBox()
        >>> spinbox.setValue(150000)
        >>> # Si la moneda es PYG: muestra "Gs. 150000"
        >>> # Si cambia a USD: muestra "$ 12.00"
    """
    
    def __init__(self, parent=None, currency_code: Optional[str] = None):
        """
        Inicializa el SpinBox con moneda específica o actual
        
        Args:
            parent: Widget padre
            currency_code: Código de moneda específico (None para usar actual)
        """
        super().__init__(parent)
        
        self._currency_code = currency_code
        self._currency_manager = CurrencyManager()
        
        # Configurar con la moneda inicial
        self._apply_currency_config()
        
        # Conectar al signal de cambio de moneda
        if self._currency_code is None:
            # Solo reconectar si usa la moneda actual (no una específica)
            self._currency_manager.currency_changed.connect(self._on_currency_changed)
    
    def _apply_currency_config(self):
        """Aplica la configuración de la moneda actual al spinbox"""
        currency = self._currency_code or self._currency_manager.get_current_currency()
        CurrencyHelper.configure_spinbox(self, currency)
    
    @Slot(str)
    def _on_currency_changed(self, new_currency: str):
        """
        Callback cuando cambia la moneda del sistema
        
        Args:
            new_currency: Código de la nueva moneda
        """
        # Guardar valor actual
        current_value = self.value()
        
        # Aplicar nueva configuración
        self._apply_currency_config()
        
        # Restaurar valor (los decimales pueden cambiar)
        self.setValue(current_value)
    
    def set_currency(self, currency_code: str):
        """
        Cambia la moneda específica de este spinbox
        
        Args:
            currency_code: Nuevo código de moneda
        """
        if self._currency_code is None:
            # Desconectar si estaba usando moneda actual
            self._currency_manager.currency_changed.disconnect(self._on_currency_changed)
        
        self._currency_code = currency_code
        self._apply_currency_config()
        
        # No reconectar (ahora usa moneda específica)
    
    def use_current_currency(self):
        """
        Configura el spinbox para usar la moneda actual del sistema
        """
        if self._currency_code is not None:
            self._currency_code = None
            self._apply_currency_config()
            # Reconectar al signal
            self._currency_manager.currency_changed.connect(self._on_currency_changed)


class CurrencyAwareLabel(QLabel):
    """
    QLabel que actualiza su texto automáticamente cuando cambia la moneda
    
    Características:
    - Usa plantillas con {currency} o {symbol}
    - Se actualiza automáticamente cuando cambia la moneda
    - Soporta formato simple o con símbolo
    
    Examples:
        >>> label = CurrencyAwareLabel("Precio ({symbol})")
        >>> # Si moneda es PYG: muestra "Precio (Gs.)"
        >>> # Si cambia a USD: muestra "Precio ($)"
        
        >>> label = CurrencyAwareLabel("Total en {currency}")
        >>> # Si moneda es PYG: muestra "Total en PYG"
        >>> # Si cambia a USD: muestra "Total en USD"
    """
    
    def __init__(self, text_template: str = "", parent=None):
        """
        Inicializa el label con una plantilla de texto
        
        Args:
            text_template: Plantilla con {currency} y/o {symbol}
            parent: Widget padre
        """
        super().__init__(parent)
        
        self._text_template = text_template
        self._currency_manager = CurrencyManager()
        
        # Actualizar texto inicial
        self._update_text()
        
        # Conectar al signal de cambio de moneda
        self._currency_manager.currency_changed.connect(self._on_currency_changed)
    
    def _update_text(self):
        """Actualiza el texto del label según la moneda actual"""
        if not self._text_template:
            return
        
        current_currency = self._currency_manager.get_current_currency()
        symbol = CurrencyHelper.get_symbol(current_currency)
        
        # Reemplazar placeholders
        text = self._text_template
        text = text.replace("{currency}", current_currency)
        text = text.replace("{symbol}", symbol)
        
        self.setText(text)
    
    @Slot(str)
    def _on_currency_changed(self, new_currency: str):
        """
        Callback cuando cambia la moneda del sistema
        
        Args:
            new_currency: Código de la nueva moneda
        """
        self._update_text()
    
    def set_template(self, text_template: str):
        """
        Cambia la plantilla de texto
        
        Args:
            text_template: Nueva plantilla con {currency} y/o {symbol}
        """
        self._text_template = text_template
        self._update_text()
    
    def get_template(self) -> str:
        """
        Obtiene la plantilla actual
        
        Returns:
            Plantilla de texto
        """
        return self._text_template


class CurrencyAwareFormattedLabel(QLabel):
    """
    QLabel que muestra montos formateados con la moneda actual
    
    Características:
    - Formatea montos automáticamente según la moneda
    - Se actualiza cuando cambia la moneda
    - Incluye símbolo y formato apropiado
    
    Example:
        >>> label = CurrencyAwareFormattedLabel()
        >>> label.set_amount(150000)
        >>> # Si moneda es PYG: muestra "Gs. 150.000"
        >>> # Si cambia a USD: muestra "$ 150,000.00"
    """
    
    def __init__(self, amount: float = 0.0, parent=None):
        """
        Inicializa el label con un monto
        
        Args:
            amount: Monto a mostrar
            parent: Widget padre
        """
        super().__init__(parent)
        
        self._amount = amount
        self._currency_manager = CurrencyManager()
        
        # Actualizar texto inicial
        self._update_text()
        
        # Conectar al signal de cambio de moneda
        self._currency_manager.currency_changed.connect(self._on_currency_changed)
    
    def _update_text(self):
        """Actualiza el texto del label con el monto formateado"""
        formatted = CurrencyHelper.format_with_current_currency(self._amount)
        self.setText(formatted)
    
    @Slot(str)
    def _on_currency_changed(self, new_currency: str):
        """
        Callback cuando cambia la moneda del sistema
        
        Args:
            new_currency: Código de la nueva moneda
        """
        self._update_text()
    
    def set_amount(self, amount: float):
        """
        Cambia el monto mostrado
        
        Args:
            amount: Nuevo monto
        """
        self._amount = amount
        self._update_text()
    
    def get_amount(self) -> float:
        """
        Obtiene el monto actual
        
        Returns:
            Monto almacenado
        """
        return self._amount
