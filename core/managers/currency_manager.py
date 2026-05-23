"""
Gestor central del sistema de monedas

Este módulo proporciona un singleton para gestionar el estado global de la moneda
en toda la aplicación y notificar cambios a los componentes interesados.
"""
from PySide6.QtCore import QObject, Signal


class CurrencyManager(QObject):
    """
    Gestor central del sistema de monedas (Singleton)
    
    Maneja el estado global de la moneda base y notifica a toda la aplicación
    cuando se produce un cambio, permitiendo que los widgets se actualicen
    automáticamente.
    
    Ejemplo de uso:
        manager = CurrencyManager()
        manager.currency_changed.connect(mi_funcion_actualizar)
        manager.set_current_currency('USD')
    """
    
    # Singleton instance
    _instance = None
    
    # Señales
    currency_changed = Signal(str)  # Emite el nuevo código de moneda (ej: "USD", "PYG")
    
    def __new__(cls):
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el manager (solo una vez debido al singleton)"""
        # Evitar reinicialización
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._current_currency = None
            self._initialized = True
    
    def get_current_currency(self) -> str:
        """
        Obtiene el código de la moneda actual
        
        Returns:
            str: Código ISO de la moneda (ej: "PYG", "USD", "EUR")
        """
        if self._current_currency is None:
            # Cargar desde preferencias la primera vez
            from core.managers.app_preferences_manager import AppPreferencesManager
            self._current_currency = AppPreferencesManager().get_base_currency()
        
        return self._current_currency
    
    def set_current_currency(self, currency_code: str, emit_signal: bool = True):
        """
        Establece una nueva moneda base y notifica el cambio
        
        Args:
            currency_code: Código ISO de la nueva moneda (ej: "USD", "EUR")
            emit_signal: Si False, no emite la señal currency_changed
        
        Returns:
            bool: True si hubo cambio, False si era la misma moneda
        """
        if self._current_currency != currency_code:
            old_currency = self._current_currency
            self._current_currency = currency_code
            
            # Limpiar caché del helper
            from core.utils.currency_helper import CurrencyHelper
            CurrencyHelper.clear_cache()
            
            # Emitir señal para que los widgets se actualicen
            if emit_signal:
                self.currency_changed.emit(currency_code)
            
            import logging
            logging.getLogger(__name__).info(f"Moneda cambiada: {old_currency} → {currency_code}")
            return True
        
        return False
    
    def reload_currency(self):
        """
        Recarga la moneda desde las preferencias
        Útil después de cambios en la configuración
        """
        from core.managers.app_preferences_manager import AppPreferencesManager
        new_currency = AppPreferencesManager().get_base_currency()
        
        if new_currency != self._current_currency:
            self.set_current_currency(new_currency, emit_signal=True)
    
    def requires_restart(self) -> bool:
        """
        Indica si se requiere reiniciar la aplicación para aplicar cambios
        
        Returns:
            bool: True si se recomienda reiniciar
        
        Note:
            Por ahora siempre retorna True para asegurar que todos los 
            componentes se actualicen correctamente. En el futuro podría
            ser más inteligente detectando qué componentes necesitan reinicio.
        """
        return True
    
    def get_currency_info(self) -> dict:
        """
        Obtiene información completa de la moneda actual
        
        Returns:
            dict: Diccionario con código, símbolo, nombre, decimales, etc.
        """
        from core.utils.currency_helper import CurrencyHelper
        return CurrencyHelper._get_currency_config(self.get_current_currency())
