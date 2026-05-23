"""
Gestor de preferencias de la aplicación
"""
import json
from typing import Dict, Any, Optional
from pathlib import Path
from core.utils.path_helper import config_dir
from core.utils.logger import logger


class AppPreferencesManager:
    """Maneja las preferencias de la aplicación"""
    
    def __init__(self, config_path: str = None):
        """
        Inicializa el gestor de preferencias
        
        Args:
            config_path: Ruta personalizada del archivo de preferencias
        """
        if config_path is None:
            config_path = config_dir() / "app_preferences.json"
        self.config_path = str(config_path)
        self._preferences = self._load_preferences()
        
        # Asegurar que el directorio existe
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Retorna las preferencias por defecto"""
        return {
            "startup": {
                "default_customer_mode": "normal",  # "normal", "optional", "default"
                "default_printer_id": None,  # None = ninguna, "first" = primera disponible, int = ID de impresora
                "auto_select_first_printer": False,
                "auto_select_first_customer": False
            },
            "appearance": {
                "theme": "auto",  # "dark", "light", "auto"
                "language": "es",  # "es", "en", etc.
                "locale": "PY"  # "PY", "AR", "CL", "US", "ES", etc.
            },
            
            "advance": {
                "mode": 0,  # 0=Manual, 1=Activar al iniciar, 2=Monto mínimo, 3=Monto máximo, 4=Ambos
                "default_enabled": False,
                "default_percentage": 50,
                "currency": "PYG",  # Moneda en la que se guardaron los montos
                "auto_enable_minimum": {
                    "enabled": False,
                    "amount": 20000,  # monto mínimo
                    "percentage": 75
                },
                "auto_enable_maximum": {
                    "enabled": False,
                    "amount": 100000,  # monto máximo
                    "percentage": 60
                }
            },
            "calculations": {
                "auto_calculate_on_change": True
            },
            "updates": {
                "ignored_version": None,  # Versión que el usuario prefiere ignorar
                "last_check_date": None,  # Última fecha de verificación (ISO format)
                "cached_update_info": None,  # Información de actualización en caché
                "cached_app_version": None,  # Versión de la app cuando se guardó el caché
                "cached_app_build": None,  # Build de la app cuando se guardó el caché
                "check_mode": "auto",  # Modo de búsqueda: "auto" o "manual"
                "check_frequency": "30days"  # Frecuencia: "startup", "7days", "15days", "30days"
            }
            
        }
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Carga las preferencias desde el archivo"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                    # Combinar con defaults para asegurar que existan todas las claves
                    defaults = self._get_default_preferences()
                    merged = self._merge_preferences(defaults, preferences)
                    
                    # Verificar que advance.currency existe (migración de archivos antiguos)
                    if "advance" in merged and "currency" not in merged["advance"]:
                        merged["advance"]["currency"] = self.get_base_currency()
                        # Guardar para actualizar el archivo
                        self._preferences = merged
                        self.save_preferences()
                    
                    return merged
            else:
                # Crear archivo con preferencias por defecto
                defaults = self._get_default_preferences()
                self._preferences = defaults
                self.save_preferences()
                return defaults
        except Exception as e:
            logger.error("AppPreferences", f"Error cargando preferencias: {e}")
            return self._get_default_preferences()
    
    def _merge_preferences(self, defaults: Dict[str, Any], user_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Combina preferencias del usuario con los valores por defecto"""
        result = defaults.copy()
        for key, value in user_prefs.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_preferences(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_preferences(self) -> bool:
        """Guarda las preferencias al archivo"""
        try:
            # Asegurar que el directorio existe
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._preferences, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error("AppPreferences", f"Error guardando preferencias: {e}")
            return False
    
    # Métodos de acceso general
    def get_preference(self, section: str, key: str, default=None):
        """Obtiene una preferencia específica"""
        return self._preferences.get(section, {}).get(key, default)
    
    def set_preference(self, section: str, key: str, value: Any):
        """Establece una preferencia específica"""
        if section not in self._preferences:
            self._preferences[section] = {}
        self._preferences[section][key] = value
    
    # Métodos específicos para startup
    def get_default_customer_mode(self) -> str:
        """Obtiene el modo de cliente por defecto"""
        return self.get_preference("startup", "default_customer_mode", "normal")
    
    def set_default_customer_mode(self, mode: str):
        """Establece el modo de cliente por defecto"""
        if mode in ["normal", "optional", "default"]:
            self.set_preference("startup", "default_customer_mode", mode)
    
    def get_default_printer_id(self) -> Optional[any]:
        """Obtiene la ID de impresora por defecto (None, 'first', o int)"""
        return self.get_preference("startup", "default_printer_id")
    
    def set_default_printer_id(self, printer_id: Optional[any]):
        """Establece la ID de impresora por defecto (None, 'first', o int)"""
        self.set_preference("startup", "default_printer_id", printer_id)
    
    def get_auto_select_first_printer(self) -> bool:
        """Obtiene si auto-seleccionar primera impresora"""
        return self.get_preference("startup", "auto_select_first_printer", False)
    
    def set_auto_select_first_printer(self, enabled: bool):
        """Establece si auto-seleccionar primera impresora"""
        self.set_preference("startup", "auto_select_first_printer", enabled)
    
    def get_default_generate_mode(self) -> str:
        """Obtiene el modo de generación por defecto al iniciar ('pdf' o 'note')"""
        return self.get_preference("startup", "default_generate_mode", "pdf")
    
    def set_default_generate_mode(self, mode: str):
        """Establece el modo de generación por defecto al iniciar ('pdf' o 'note')"""
        if mode in ["pdf", "note"]:
            self.set_preference("startup", "default_generate_mode", mode)
    
    # Métodos específicos para appearance
    def get_theme(self) -> str:
        """Obtiene el tema configurado"""
        return self.get_preference("appearance", "theme", "auto")
    
    def set_theme(self, theme: str):
        """Establece el tema"""
        if theme in ["dark", "light", "auto"]:
            self.set_preference("appearance", "theme", theme)
    
    def get_window_maximized(self) -> bool:
        """Obtiene si la ventana debe iniciar maximizada"""
        return self.get_preference("appearance", "window_maximized", True)
    
    def set_window_maximized(self, maximized: bool):
        """Establece si la ventana debe iniciar maximizada"""
        self.set_preference("appearance", "window_maximized", maximized)
    
    # Métodos específicos para advance
    def get_advance_default_enabled(self) -> bool:
        """Obtiene si el anticipo debe estar habilitado por defecto"""
        return self.get_preference("advance", "default_enabled", False)
    
    def set_advance_default_enabled(self, enabled: bool):
        """Establece si el anticipo debe estar habilitado por defecto"""
        self.set_preference("advance", "default_enabled", enabled)
    
    def get_advance_default_percentage(self) -> int:
        """Obtiene el porcentaje de anticipo por defecto"""
        return self.get_preference("advance", "default_percentage", 50)
    
    def set_advance_default_percentage(self, percentage: int):
        """Establece el porcentaje de anticipo por defecto"""
        percentage = int(percentage)  # Asegurar que sea entero
        if 1 <= percentage <= 100:
            self.set_preference("advance", "default_percentage", percentage)
    
    def get_advance_auto_minimum(self) -> Dict[str, Any]:
        """Obtiene configuración de anticipo automático para montos mínimos (convierte si es necesario)"""
        logger.info("AppPreferences", "=== INICIO get_advance_auto_minimum ===")
        
        config = self.get_preference("advance", "auto_enable_minimum", {
            "enabled": False,
            "amount": 100000,
            "percentage": 30,
            "currency": "PYG"
        }).copy()  # Hacer copia para no modificar el original directamente
        
        logger.info("AppPreferences", f"Config leído del JSON: {config}")
        
        # Obtener moneda guardada (de la config misma) y actual
        saved_currency = config.get("currency", "PYG")
        current_currency = self.get_base_currency()
        amount = config.get("amount", 100000)
        
        logger.info("AppPreferences", f"Mínimo: saved_currency={saved_currency}, current={current_currency}, amount={amount}")
        
        # Si las monedas son diferentes, convertir
        if saved_currency != current_currency:
            logger.info("AppPreferences", f"Monedas diferentes, llamando a _convert_advance_amount_if_needed({amount}, {saved_currency})")
            converted_amount = self._convert_advance_amount_if_needed(amount, saved_currency, save_on_convert=False)
            logger.info("AppPreferences", f"Resultado de conversión: {amount} -> {converted_amount}")
            
            # Actualizar el monto convertido y la moneda SOLO en el objeto retornado
            config["amount"] = converted_amount
            config["currency"] = current_currency
            logger.info("AppPreferences", f"Config actualizado (NO guardado): {config}")
            # NO guardar aquí - se guardará cuando el presenter llame a set_ al guardar preferencias
        else:
            logger.info("AppPreferences", "Monedas iguales, NO se requiere conversión")
        
        logger.info("AppPreferences", f"=== FIN get_advance_auto_minimum -> retornando {config} ===")
        return config
    
    def set_advance_auto_minimum(self, enabled: bool, amount: float, percentage: int):
        """Establece configuración de anticipo automático para montos mínimos"""
        self.set_preference("advance", "auto_enable_minimum", {
            "enabled": enabled,
            "amount": float(amount),
            "percentage": int(percentage),
            "currency": self.get_base_currency()  # Guardar moneda actual
        })
    
    def get_advance_auto_maximum(self) -> Dict[str, Any]:
        """Obtiene configuración de anticipo automático para montos máximos (convierte si es necesario)"""
        logger.info("AppPreferences", "=== INICIO get_advance_auto_maximum ===")
        
        config = self.get_preference("advance", "auto_enable_maximum", {
            "enabled": False,
            "amount": 500000,
            "percentage": 50,
            "currency": "PYG"
        }).copy()  # Hacer copia para no modificar el original directamente
        
        logger.info("AppPreferences", f"Config leído del JSON: {config}")
        
        # Obtener moneda guardada (de la config misma) y actual
        saved_currency = config.get("currency", "PYG")
        current_currency = self.get_base_currency()
        amount = config.get("amount", 500000)
        
        logger.info("AppPreferences", f"Máximo: saved_currency={saved_currency}, current={current_currency}, amount={amount}")
        
        # Si las monedas son diferentes, convertir
        if saved_currency != current_currency:
            logger.info("AppPreferences", f"Monedas diferentes, llamando a _convert_advance_amount_if_needed({amount}, {saved_currency})")
            converted_amount = self._convert_advance_amount_if_needed(amount, saved_currency, save_on_convert=False)
            logger.info("AppPreferences", f"Resultado de conversión: {amount} -> {converted_amount}")
            
            # Actualizar el monto convertido y la moneda SOLO en el objeto retornado
            config["amount"] = converted_amount
            config["currency"] = current_currency
            logger.info("AppPreferences", f"Config actualizado (NO guardado): {config}")
            # NO guardar aquí - se guardará cuando el presenter llame a set_ al guardar preferencias
        else:
            logger.info("AppPreferences", "Monedas iguales, NO se requiere conversión")
        
        logger.info("AppPreferences", f"=== FIN get_advance_auto_maximum -> retornando {config} ===")
        return config
    
    def set_advance_auto_maximum(self, enabled: bool, amount: float, percentage: int):
        """Establece configuración de anticipo automático para montos máximos"""
        self.set_preference("advance", "auto_enable_maximum", {
            "enabled": enabled,
            "amount": float(amount),
            "percentage": int(percentage),
            "currency": self.get_base_currency()  # Guardar moneda actual
        })
    
    def get_advance_mode(self) -> int:
        """Obtiene el modo de anticipo configurado como número (0-4)"""
        return self.get_preference("advance", "mode", 0)
    
    def set_advance_mode(self, mode: int):
        """Establece el modo de anticipo usando número (0-4)"""
        try:
            mode = int(mode)  # Asegurar que sea entero
            if 0 <= mode <= 4:
                self.set_preference("advance", "mode", mode)
            else:
                print(f"⚠️ Modo de anticipo inválido: {mode}. Usando 0 (Ninguno) por defecto.")
                self.set_preference("advance", "mode", 0)
        except (ValueError, TypeError) as e:
            print(f"⚠️ Error convirtiendo modo '{mode}' a entero: {e}. Usando 0 por defecto.")
            self.set_preference("advance", "mode", 0)
    
    def get_advance_min_amount(self) -> float:
        """Obtiene el monto mínimo configurado para anticipo automático (convertido a moneda actual)"""
        auto_min = self.get_preference("advance", "auto_enable_minimum", {})
        amount = auto_min.get("amount", 100000) if isinstance(auto_min, dict) else 100000
        saved_currency = auto_min.get("currency", "PYG") if isinstance(auto_min, dict) else "PYG"
        return self._convert_advance_amount_if_needed(amount, saved_currency)
    
    def get_advance_max_amount(self) -> float:
        """Obtiene el monto máximo configurado para anticipo automático (convertido a moneda actual)"""
        auto_max = self.get_preference("advance", "auto_enable_maximum", {})
        amount = auto_max.get("amount", 500000) if isinstance(auto_max, dict) else 500000
        saved_currency = auto_max.get("currency", "PYG") if isinstance(auto_max, dict) else "PYG"
        return self._convert_advance_amount_if_needed(amount, saved_currency)
    
    # Métodos específicos para interface
    def get_show_tooltips(self) -> bool:
        """Obtiene si mostrar tooltips"""
        return self.get_preference("interface", "show_tooltips", True)
    
    def set_show_tooltips(self, enabled: bool):
        """Establece si mostrar tooltips"""
        self.set_preference("interface", "show_tooltips", enabled)
    
    def get_compact_mode(self) -> bool:
        """Obtiene si usar modo compacto"""
        return self.get_preference("interface", "compact_mode", False)
    
    def set_compact_mode(self, enabled: bool):
        """Establece si usar modo compacto"""
        self.set_preference("interface", "compact_mode", enabled)
    
    # Método para resetear a defaults
    def reset_to_defaults(self) -> bool:
        """Resetea todas las preferencias a los valores por defecto"""
        try:
            self._preferences = self._get_default_preferences()
            return self.save_preferences()
        except Exception as e:
            logger.error("AppPreferences", f"Error reseteando preferencias: {e}")
            return False

    def get_all_preferences(self) -> Dict[str, Any]:
        """Retorna todas las preferencias"""
        return self._preferences.copy()
    
    def update_preferences(self, new_preferences: Dict[str, Any]) -> bool:
        """Actualiza múltiples preferencias a la vez"""
        try:
            # Combinar con preferencias existentes
            self._preferences = self._merge_preferences(self._preferences, new_preferences)
            return True
        except Exception as e:
            logger.error("AppPreferences", f"Error actualizando preferencias: {e}")
            return False
    
    # ============================================================================
    # MÉTODOS DE MONEDA
    # ============================================================================
    
    def _convert_advance_amount_if_needed(self, amount: float, saved_currency: str, save_on_convert: bool = True) -> float:
        """
        Convierte un monto de anticipo si la moneda actual es diferente a la guardada
        
        Args:
            amount: Monto en la moneda guardada
            saved_currency: Moneda en la que está guardado el monto
            save_on_convert: Si True, guarda las preferencias después de convertir
            
        Returns:
            Monto convertido a la moneda actual
        """
        try:
            logger.info("AppPreferences", f"--- Entrando a _convert_advance_amount_if_needed(amount={amount}, saved_currency={saved_currency}, save_on_convert={save_on_convert})")
            
            # Obtener moneda actual del sistema
            current_currency = self.get_base_currency()
            logger.info("AppPreferences", f"Moneda actual del sistema: {current_currency}")
            
            # Si son iguales, no hay conversión
            if saved_currency == current_currency:
                logger.info("AppPreferences", f"Las monedas son iguales ({saved_currency}), retornando monto sin convertir: {amount}")
                return amount
            
            logger.info("AppPreferences", f"Las monedas son DIFERENTES, convirtiendo {amount} de {saved_currency} a {current_currency}")
            
            # Convertir usando el servicio de conversión
            from core.services.currency_conversion_service import CurrencyConversionService
            converter = CurrencyConversionService()
            
            logger.info("AppPreferences", f"Llamando a converter.convert_amount({amount}, {saved_currency}, {current_currency}, allow_inactive=True)")
            converted_amount = converter.convert_amount(
                amount=amount,
                from_currency=saved_currency,
                to_currency=current_currency,
                allow_inactive=True  # Permitir conversión desde moneda histórica
            )
            logger.info("AppPreferences", f"Resultado del converter: {converted_amount}")
            
            if converted_amount is not None:
                # Actualizar la moneda guardada SOLO si se va a guardar
                if save_on_convert:
                    self.set_preference("advance", "currency", current_currency)
                    logger.info("AppPreferences", f"Actualizada advance.currency a {current_currency}")
                    logger.info("AppPreferences", "save_on_convert=True, guardando preferencias...")
                    self.save_preferences()
                else:
                    logger.info("AppPreferences", "save_on_convert=False, NO se actualiza advance.currency ni se guardan preferencias")
                
                logger.info("AppPreferences", 
                    f"Anticipo convertido: {amount} {saved_currency} → {converted_amount} {current_currency}"
                )
                return converted_amount
            else:
                # Si falla la conversión, mantener el valor original
                logger.warning("AppPreferences",
                    f"No se pudo convertir anticipo de {saved_currency} a {current_currency}, retornando valor original {amount}"
                )
                return amount
                
        except Exception as e:
            logger.error("AppPreferences", f"Error convirtiendo monto de anticipo: {e}")
            return amount
    
    def get_base_currency(self) -> str:
        """Obtiene la moneda base configurada desde system_configs"""
        try:
            from infrastructure.database.connection import DatabaseConnection
            from infrastructure.database.repositories.system_config_repository import SystemConfigRepository
            from core.utils.path_helper import database_path
            
            db_conn = DatabaseConnection(str(database_path()))
            repo = SystemConfigRepository(db_conn)
            currency = repo.get_value("base_currency", "PYG")
            return currency
        except Exception as e:
            logger.error("AppPreferences", f"Error obteniendo moneda base: {e}")
            return "PYG"
    
    def set_base_currency(self, currency_code: str) -> bool:
        """
        Establece la moneda base del sistema en system_configs
        
        Args:
            currency_code: Código de la moneda (ej: "PYG", "USD", "EUR")
        
        Returns:
            bool: True si se guardó exitosamente, False en caso contrario
        """
        try:
            # Validar que la moneda existe y está activa
            from infrastructure.database.connection import DatabaseConnection
            from infrastructure.database.repositories.currency_repository import CurrencyRepository
            from infrastructure.database.repositories.system_config_repository import SystemConfigRepository
            from core.utils.path_helper import database_path
            
            # CurrencyRepository no acepta db_connection, crea su propia instancia
            currency_repo = CurrencyRepository()
            currency = currency_repo.get_by_code(currency_code)
            
            if not currency:
                logger.warning("AppPreferences", f"Moneda '{currency_code}' no encontrada")
                return False
            
            if not currency.is_active:
                logger.warning("AppPreferences", f"Moneda '{currency_code}' no está activa")
                return False
            
            # SystemConfigRepository sí requiere db_connection
            db_conn = DatabaseConnection(str(database_path()))
            config_repo = SystemConfigRepository(db_conn)
            success = config_repo.update_value("base_currency", currency_code)
            
            if success:
                # Limpiar cache de CurrencyHelper para forzar recarga
                from core.utils.currency_helper import CurrencyHelper
                CurrencyHelper.clear_cache()
                logger.info("AppPreferences", f"Moneda base actualizada a: {currency_code}")
            
            return success
            
        except Exception as e:
            from core.utils.logger import error
            error("AppPreferences", f"Error estableciendo moneda base: {e}")
            return False
    # ============= MÉTODOS PARA ACTUALIZACIONES =============
    
    def set_ignored_version(self, version: str) -> bool:
        """
        Establece una versión a ignorar en notificaciones
        
        Args:
            version: Versión a ignorar (ej: "1.1.6")
            
        Returns:
            True si se guardó correctamente
        """
        try:
            if "updates" not in self._preferences:
                self._preferences["updates"] = {}
            
            self._preferences["updates"]["ignored_version"] = version
            success = self.save_preferences()
            
            if success:
                logger.info("AppPreferences", f"Versión {version} será ignorada en actualizaciones")
            
            return success
            
        except Exception as e:
            logger.error("AppPreferences", f"Error ignorando versión: {e}")
            return False
    
    def get_ignored_version(self) -> Optional[str]:
        """
        Obtiene la versión ignorada
        
        Returns:
            Versión ignorada o None si no hay ninguna
        """
        try:
            return self._preferences.get("updates", {}).get("ignored_version")
        except Exception as e:
            logger.error("AppPreferences", f"Error obteniendo versión ignorada: {e}")
            return None
    
    def clear_ignored_version(self) -> bool:
        """
        Limpia la versión ignorada (para volver a mostrar notificaciones)
        
        Returns:
            True si se guardó correctamente
        """
        try:
            if "updates" in self._preferences:
                self._preferences["updates"]["ignored_version"] = None
                return self.save_preferences()
            return True
        except Exception as e:
            logger.error("AppPreferences", f"Error limpiando versión ignorada: {e}")
            return False
    
    def set_update_cache(self, update_info: dict) -> bool:
        """
        Guarda información de actualización en caché con timestamp
        
        Args:
            update_info: Diccionario con información de actualización
            
        Returns:
            True si se guardó correctamente
        """
        try:
            from datetime import datetime
            
            if "updates" not in self._preferences:
                self._preferences["updates"] = {}
            
            # Guardar fecha actual y resultado
            self._preferences["updates"]["last_check_date"] = datetime.now().isoformat()
            self._preferences["updates"]["cached_update_info"] = update_info
            
            return self.save_preferences()
            
        except Exception as e:
            logger.error("AppPreferences", f"Error guardando caché de actualización: {e}")
            return False
    
    def get_update_cache(self) -> tuple[Optional[str], Optional[dict]]:
        """
        Obtiene información de actualización en caché y su fecha
        
        Returns:
            Tupla (fecha_iso, update_info) o (None, None) si no hay caché
        """
        try:
            updates = self._preferences.get("updates", {})
            last_check = updates.get("last_check_date")
            cached_info = updates.get("cached_update_info")
            
            return (last_check, cached_info)
            
        except Exception as e:
            logger.error("AppPreferences", f"Error obteniendo caché de actualización: {e}")
            return (None, None)
    
    def should_check_updates(self, cache_days: int = 7) -> bool:
        """
        Verifica si debe hacer una nueva verificación de actualizaciones
        
        Args:
            cache_days: Días de validez del caché (por defecto 7)
            
        Returns:
            True si debe verificar, False si puede usar caché
        """
        try:
            from datetime import datetime, timedelta
            
            last_check, _ = self.get_update_cache()
            
            # Si no hay caché, debe verificar
            if not last_check:
                return True
            
            # Parsear fecha y comparar
            last_check_date = datetime.fromisoformat(last_check)
            days_since_check = (datetime.now() - last_check_date).days
            
            # Verificar si pasaron los días configurados
            should_check = days_since_check >= cache_days
            
            if should_check:
                logger.info("AppPreferences", f"Han pasado {days_since_check} días desde última verificación. Verificando...")
            else:
                logger.info("AppPreferences", f"Usando caché de actualizaciones ({days_since_check} días, válido por {cache_days})")
            
            return should_check
            
        except Exception as e:
            logger.error("AppPreferences", f"Error verificando caché: {e}")
            # En caso de error, mejor verificar
            return True
    
    def get_update_check_mode(self) -> str:
        """
        Obtiene el modo de verificación de actualizaciones
        
        Returns:
            "auto" o "manual"
        """
        try:
            return self._preferences.get("updates", {}).get("check_mode", "auto")
        except Exception as e:
            logger.error("AppPreferences", f"Error obteniendo modo de verificación: {e}")
            return "auto"
    
    def get_update_check_frequency(self) -> str:
        """
        Obtiene la frecuencia de verificación de actualizaciones
        
        Returns:
            "startup", "7days", "15days", o "30days"
        """
        try:
            return self._preferences.get("updates", {}).get("check_frequency", "30days")
        except Exception as e:
            logger.error("AppPreferences", f"Error obteniendo frecuencia de verificación: {e}")
            return "startup"
    
    def set_update_check_settings(self, mode: str, frequency: str) -> bool:
        """
        Establece la configuración de verificación de actualizaciones
        
        Args:
            mode: "auto" o "manual"
            frequency: "startup", "7days", "15days", o "30days"
            
        Returns:
            True si se guardó correctamente
        """
        try:
            if "updates" not in self._preferences:
                self._preferences["updates"] = {}
            
            self._preferences["updates"]["check_mode"] = mode
            self._preferences["updates"]["check_frequency"] = frequency
            
            success = self.save_preferences()
            
            if success:
                logger.info("AppPreferences", f"Configuración de actualizaciones guardada: {mode} / {frequency}")
            
            return success
            
        except Exception as e:
            logger.error("AppPreferences", f"Error guardando configuración de actualizaciones: {e}")
            return False
