"""
Presenter para el diálogo de preferencias de la aplicación
Maneja toda la lógica de carga, validación y guardado de configuraciones
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox, QApplication
from typing import Dict, Any, Optional, List

from core.managers.app_preferences_manager import AppPreferencesManager
from core.managers.database_manager import get_db_manager
from domain.enums.enums import AdvanceMode
from domain.models.printer import Printer
from core.utils.currency_helper import CurrencyHelper
from core.utils.logger import logger
from core.utils.translation_keys import I18N
from core.utils.translation_helper import tr


class AppPreferencesPresenter(QObject):
    """Presenter para gestionar las preferencias de la aplicación"""
    
    # Señales
    preferences_saved = Signal(dict)  # Emite las preferencias guardadas
    preferences_loaded = Signal(dict)  # Emite las preferencias cargadas
    
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog
        
        # Managers
        self.preferences_manager = AppPreferencesManager()
        self.db_manager = get_db_manager()
        
        # Estado
        self.current_preferences: Dict[str, Any] = {}
        self.available_printers: List[Printer] = []
        
        # Cargar datos iniciales
        if dialog is not None:  # Solo cargar si hay dialog (no en modo de prueba)
            self._load_initial_data()
    
    def _load_initial_data(self):
        """Carga los datos iniciales necesarios"""
        try:
            # Cargar preferencias actuales
            self.current_preferences = self.preferences_manager.get_all_preferences()
            
            # Cargar impresoras disponibles
            self._load_available_printers()
            
            # Emitir señal de datos cargados
            self.preferences_loaded.emit(self.current_preferences)
            
        except Exception as e:
            if self.dialog:
                QMessageBox.warning(self.dialog, "Error", f"Error cargando preferencias: {str(e)}")
    
    def _load_available_printers(self):
        """Carga la lista de impresoras disponibles"""
        try:
            # Aquí iría la lógica para cargar impresoras desde la base de datos
            # Por ahora dejamos una lista vacía
            self.available_printers = []
        except Exception as e:
            self.available_printers = []
    
    # ============================================================================
    # MÉTODOS DE MODO DE ANTICIPO
    # ============================================================================
    
    def get_advance_mode(self) -> int:
        """Obtiene el modo de anticipo como número"""
        return self.preferences_manager.get_advance_mode()
    
    def set_advance_mode(self, mode: int):
        """Establece el modo de anticipo usando número"""
        self.preferences_manager.set_advance_mode(mode)
    
    def set_advance_default_percentage(self, percentage: int):
        """Establece el porcentaje por defecto de anticipo"""
        self.preferences_manager.set_advance_default_percentage(percentage)
    
    def get_advance_default_percentage(self) -> int:
        """Obtiene el porcentaje por defecto de anticipo"""
        return self.preferences_manager.get_advance_default_percentage()
    
    def handle_advance_mode_changed(self, mode_index: int):
        """Maneja el cambio de modo de anticipo y actualiza la habilitación de campos en la vista"""
        if self.dialog is None:
            return
            
        # Determinar qué campos deben estar habilitados según el modo
        field_states = self._calculate_advance_field_states(mode_index)
        
        # Actualizar la vista con los estados calculados
        self._update_advance_fields_state(field_states)
    
    def _calculate_advance_field_states(self, mode_index: int) -> Dict[str, bool]:
        """Calcula qué campos deben estar habilitados según el modo de anticipo"""
        # Por defecto, todos los campos deshabilitados
        states = {
            "advance_default_percentage": False,
            "auto_min_amount": False,
            "auto_min_percentage": False,
            "auto_max_amount": False,
            "auto_max_percentage": False
        }
        
        # Habilitar campos según el modo seleccionado
        if mode_index in [0, 1]:  # "Manual" o "Automático al inicio" - ambos usan porcentaje por defecto
            states["advance_default_percentage"] = True
        elif mode_index == 2:  # "Activar al monto mínimo"
            states["auto_min_amount"] = True
            states["auto_min_percentage"] = True
        elif mode_index == 3:  # "Activar al monto máximo"
            states["auto_max_amount"] = True
            states["auto_max_percentage"] = True
        elif mode_index == 4:  # "Activar en montos mínimos y máximos"
            states["auto_min_amount"] = True
            states["auto_min_percentage"] = True
            states["auto_max_amount"] = True
            states["auto_max_percentage"] = True
        
        return states
    
    def _update_advance_fields_state(self, field_states: Dict[str, bool]):
        """Actualiza el estado (habilitado/deshabilitado) de los campos en la vista"""
        if self.dialog is None:
            return
            
        dialog = self.dialog
        
        # Actualizar cada campo según su estado calculado
        dialog.advance_default_percentage.setEnabled(field_states["advance_default_percentage"])
        dialog.auto_min_amount.setEnabled(field_states["auto_min_amount"])
        dialog.auto_min_percentage.setEnabled(field_states["auto_min_percentage"])
        dialog.auto_max_amount.setEnabled(field_states["auto_max_amount"])
        dialog.auto_max_percentage.setEnabled(field_states["auto_max_percentage"])
    
    # ============================================================================
    # MÉTODOS DE LÓGICA DE NEGOCIO PARA ANTICIPO
    # ============================================================================
    
    def get_default_advance_percentage_for_startup(self) -> int:
        """Obtiene el porcentaje de anticipo por defecto para modo startup"""
        # Siempre devolver el porcentaje configurado en las preferencias
        return self.preferences_manager.get_advance_default_percentage()
    
    def should_apply_advance_for_amount(self, total_amount: float) -> tuple[bool, int]:
        """
        Determina si se debe aplicar anticipo automático según el monto y las reglas configuradas
        
        Args:
            total_amount: Monto total del presupuesto
            
        Returns:
            tuple[bool, int]: (debe_aplicar_anticipo, porcentaje_a_usar)
        """
        advance_mode = self.get_advance_mode()
        
        if advance_mode == AdvanceMode.NONE.value:
            return False, 0
        elif advance_mode == AdvanceMode.AUTO_START.value:
            # En modo startup, no aplicar por monto (solo al iniciar)
            return False, 0
        elif advance_mode == AdvanceMode.MIN_AMOUNT.value:
            # CORREGIDO: Aplicar anticipo cuando el monto es MENOR al mínimo (montos bajos necesitan anticipo)
            min_amount = self.preferences_manager.get_advance_min_amount()
            if total_amount < min_amount:
                # Usar directamente el método del manager en lugar del método indirecto
                auto_min_data = self.preferences_manager.get_advance_auto_minimum()
                return True, auto_min_data.get("percentage", 30)
        elif advance_mode == AdvanceMode.MAX_AMOUNT.value:
            # MANTENER: Aplicar anticipo cuando el monto es MAYOR O IGUAL al máximo (montos muy altos)
            max_amount = self.preferences_manager.get_advance_max_amount()
            if total_amount >= max_amount:
                # Usar directamente el método del manager en lugar del método indirecto
                auto_max_data = self.preferences_manager.get_advance_auto_maximum()
                return True, auto_max_data.get("percentage", 50)
        elif advance_mode == AdvanceMode.MIN_MAX_AMOUNT.value:
            # CORREGIDO: Lógica para ambos casos
            min_amount = self.preferences_manager.get_advance_min_amount()
            max_amount = self.preferences_manager.get_advance_max_amount()
            auto_min_data = self.preferences_manager.get_advance_auto_minimum()
            auto_max_data = self.preferences_manager.get_advance_auto_maximum()
            
            # Si el monto es muy bajo (menor al mínimo), aplicar anticipo mínimo
            if total_amount < min_amount:
                return True, auto_min_data.get("percentage", 30)
            # Si el monto es muy alto (mayor o igual al máximo), aplicar anticipo máximo  
            elif total_amount >= max_amount:
                return True, auto_max_data.get("percentage", 50)
            # Si está entre mínimo y máximo, NO aplicar anticipo (rango neutro)
        
        return False, 0
    
    # ============================================================================
    # MÉTODOS AUXILIARES PARA CONFIGURACIONES
    # ============================================================================
    
    def get_advance_auto_minimum_settings(self) -> Dict[str, Any]:
        """Obtiene la configuración de anticipo automático para mínimo"""
        return self.preferences_manager.get_preference("advance", "auto_enable_minimum", {
            "enabled": False,
            "amount": 100000,
            "percentage": 30
        })
    
    def get_advance_auto_maximum_settings(self) -> Dict[str, Any]:
        """Obtiene la configuración de anticipo automático para máximo"""
        return self.preferences_manager.get_preference("advance", "auto_enable_maximum", {
            "enabled": False,
            "amount": 500000,
            "percentage": 50
        })
    
    # ============================================================================
    # MÉTODOS DE CONFIGURACIÓN DE ACTUALIZACIONES
    # ============================================================================
    
    def get_update_check_mode(self) -> str:
        """Obtiene el modo de verificación de actualizaciones
        
        Returns:
            str: "auto" para automático, "manual" para manual
        """
        return self.preferences_manager.get_update_check_mode()
    
    def get_update_check_frequency(self) -> str:
        """Obtiene la frecuencia de verificación de actualizaciones
        
        Returns:
            str: "startup", "7days", "15days", "30days"
        """
        return self.preferences_manager.get_update_check_frequency()
    
    def get_default_generate_mode(self) -> str:
        """Obtiene el modo de generación por defecto ('pdf' o 'note')"""
        return self.preferences_manager.get_default_generate_mode()
    
    # ============================================================================
    # MÉTODOS DE GUARDADO Y CARGA
    # ============================================================================
    
    def save_preferences(self, preferences_data: Dict[str, Any]) -> bool:
        """Guarda las preferencias validadas"""
        try:
            # Validar datos
            is_valid, message = self.validate_preferences(preferences_data)
            if not is_valid:
                if self.dialog:
                    QMessageBox.warning(
                        self.dialog,
                        "Datos inválidos",
                        f"No se pueden guardar las preferencias:\n{message}"
                    )
                return False
            
            # Procesar y normalizar datos
            processed_data = self._process_preferences_data(preferences_data)
            
            # Guardar cada preferencia usando los métodos específicos del manager
            self._save_processed_preferences(processed_data)
            
            # Actualizar estado interno
            self.current_preferences.update(processed_data)
            
            # Emitir señal de guardado exitoso
            self.preferences_saved.emit(processed_data)
            
            if self.dialog:
                QMessageBox.information(
                    self.dialog,
                    "Preferencias guardadas",
                    "Las preferencias se han guardado exitosamente."
                )
            
            return True
            
        except Exception as e:
            if self.dialog:
                QMessageBox.critical(
                    self.dialog,
                    "Error",
                    f"Error al guardar las preferencias:\n{str(e)}"
                )
            return False
    
    def validate_preferences(self, preferences: Dict[str, Any]) -> tuple[bool, str]:
        """Valida las preferencias antes de guardar"""
        try:
            # Validar modo de cliente
            customer_mode = preferences.get("customer_mode", "normal")
            if customer_mode not in ["normal", "optional", "default"]:
                return False, f"Modo de cliente inválido: {customer_mode}"
            
            # Validar tema
            theme = preferences.get("theme", "auto")
            if theme not in ["auto", "dark", "light"]:
                return False, f"Tema inválido: {theme}"
            
            # Validar porcentajes de anticipo (deben estar entre 1 y 100)
            advance_default = preferences.get("advance_default", {})
            if isinstance(advance_default, dict):
                percentage = advance_default.get("percentage", 50)
                if not (1 <= percentage <= 100):
                    return False, f"Porcentaje de anticipo inválido: {percentage}% (debe estar entre 1-100%)"
            
            # Validar configuración de anticipo automático mínimo
            auto_min = preferences.get("advance_auto_minimum", {})
            if isinstance(auto_min, dict):
                amount = auto_min.get("amount", 100000)
                percentage = auto_min.get("percentage", 30)
                if amount < 0:
                    return False, f"Monto mínimo inválido: {CurrencyHelper.format_with_current_currency(amount)} (debe ser positivo)"
                if not (1 <= percentage <= 100):
                    return False, f"Porcentaje mínimo inválido: {percentage}% (debe estar entre 1-100%)"
            
            # Validar configuración de anticipo automático máximo
            auto_max = preferences.get("advance_auto_maximum", {})
            if isinstance(auto_max, dict):
                amount = auto_max.get("amount", 500000)
                percentage = auto_max.get("percentage", 50)
                if amount < 0:
                    return False, f"Monto máximo inválido: {CurrencyHelper.format_with_current_currency(amount)} (debe ser positivo)"
                if not (1 <= percentage <= 100):
                    return False, f"Porcentaje máximo inválido: {percentage}% (debe estar entre 1-100%)"
            
            return True, "Preferencias válidas"
            
        except Exception as e:
            return False, f"Error en validación: {str(e)}"
    
    def _process_preferences_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y normaliza los datos de preferencias"""
        processed = {}
        
        # Procesar modo de cliente
        customer_mode = raw_data.get("customer_mode", "normal")
        processed["customer_mode"] = customer_mode
        
        # Procesar impresora por defecto
        printer_id = raw_data.get("default_printer_id")
        if printer_id == "None" or printer_id == "":
            processed["default_printer_id"] = None
        elif printer_id == "first":
            processed["default_printer_id"] = "first"
        else:
            try:
                processed["default_printer_id"] = int(printer_id)
            except (ValueError, TypeError):
                processed["default_printer_id"] = None
        
        # Procesar tema
        theme = raw_data.get("theme", "auto")
        processed["theme"] = theme
        
        # Procesar modo de anticipo
        advance_mode = raw_data.get("advance_mode", "Ninguno")
        advance_mode_index = raw_data.get("advance_mode_index", 0)
        
        # Si viene un índice, convertirlo al modo correspondiente
        if isinstance(advance_mode_index, int) and advance_mode_index != 0:
            mode_mapping = [
                "Ninguno",
                "Anticipo Automático al iniciar",
                "Activar al monto mínimo", 
                "Activar al monto máximo",
                "Activar en montos mínimos y máximos"
            ]
            if 0 <= advance_mode_index < len(mode_mapping):
                advance_mode = mode_mapping[advance_mode_index]
        
        processed["advance_mode"] = advance_mode
        processed["advance_mode_index"] = advance_mode_index
        
        # Procesar configuración básica de anticipo
        advance_config = raw_data.get("advance_payment", {})
        if isinstance(advance_config, dict):
            processed["advance_payment"] = advance_config
        else:
            processed["advance_payment"] = {}
        
        # Procesar anticipo por defecto
        advance_default = raw_data.get("advance_default", {})
        processed["advance_default_percentage"] = advance_default.get("percentage", 50)
        
        # Procesar anticipo automático mínimo
        auto_min = raw_data.get("advance_auto_minimum", {})
        processed["advance_auto_minimum"] = {
            "amount": auto_min.get("amount", 100000),
            "percentage": auto_min.get("percentage", 30)
        }
        
        # Procesar anticipo automático máximo  
        auto_max = raw_data.get("advance_auto_maximum", {})
        processed["advance_auto_maximum"] = {
            "amount": auto_max.get("amount", 500000),
            "percentage": auto_max.get("percentage", 50)
        }
        
        # Procesar configuración de actualizaciones
        processed["update_check_mode"] = raw_data.get("update_check_mode", "auto")
        processed["update_check_frequency"] = raw_data.get("update_check_frequency", "30days")
        
        # Procesar modo de generación por defecto
        processed["default_generate_mode"] = raw_data.get("default_generate_mode", "pdf")

        return processed
    
    def _save_processed_preferences(self, processed_data: Dict[str, Any]):
        """Guarda las preferencias procesadas usando los métodos específicos del manager"""
        # Modo de cliente
        if "customer_mode" in processed_data:
            self.preferences_manager.set_default_customer_mode(processed_data["customer_mode"])
        
        # Impresora por defecto
        if "default_printer_id" in processed_data:
            self.preferences_manager.set_default_printer_id(processed_data["default_printer_id"])
        
        # Tema
        if "theme" in processed_data:
            self.preferences_manager.set_theme(processed_data["theme"])
        
        # Modo de anticipo
        # Modo de anticipo - solo manejar índices numéricos
        if "advance_mode_index" in processed_data:
            # Guardar el índice en ambos campos para compatibilidad
            mode_index = processed_data["advance_mode_index"]
            self.preferences_manager.set_preference("advance", "mode_index", mode_index)
            self.preferences_manager.set_advance_mode(mode_index)  # También guardar en mode
        
        # Anticipo por defecto
        if "advance_default_percentage" in processed_data:
            self.preferences_manager.set_advance_default_percentage(processed_data["advance_default_percentage"])
        
        # Anticipo automático mínimo
        if "advance_auto_minimum" in processed_data:
            auto_min = processed_data["advance_auto_minimum"]
            self.preferences_manager.set_advance_auto_minimum(
                True,  # Siempre habilitado por el modo
                auto_min["amount"],
                auto_min["percentage"]
            )
        
        # Anticipo automático máximo
        if "advance_auto_maximum" in processed_data:
            auto_max = processed_data["advance_auto_maximum"]
            self.preferences_manager.set_advance_auto_maximum(
                True,  # Siempre habilitado por el modo
                auto_max["amount"],
                auto_max["percentage"]
            )
        
        # Guardar configuración básica de anticipo si está presente
        if "advance_payment" in processed_data:
            advance_config = processed_data["advance_payment"]
            for key, value in advance_config.items():
                self.preferences_manager.set_preference("advance", key, value)
        
        # Configuración de actualizaciones
        if "update_check_mode" in processed_data and "update_check_frequency" in processed_data:
            self.preferences_manager.set_update_check_settings(
                mode=processed_data["update_check_mode"],
                frequency=processed_data["update_check_frequency"]
            )
        
        # Modo de generación por defecto
        if "default_generate_mode" in processed_data:
            self.preferences_manager.set_default_generate_mode(processed_data["default_generate_mode"])

        # ¡CRÍTICO! Guardar las preferencias al archivo
        self.preferences_manager.save_preferences()
        
        # Aplicar cambios de tema en tiempo real si cambió
        if "theme" in processed_data:
            self._apply_theme_change(processed_data["theme"])
    
    def _apply_theme_change(self, new_theme: str):
        """Aplica cambios de tema - requiere reinicio de aplicación"""
        try:
            pass
            
        except Exception as e:
            pass

    def get_current_preferences(self) -> Dict[str, Any]:
        """Obtiene las preferencias actuales"""
        return self.current_preferences.copy()
    
    def reset_to_defaults(self) -> bool:
        """Resetea todas las preferencias a valores por defecto"""
        try:
            success = self.preferences_manager.reset_to_defaults()
            if success:
                self.current_preferences = self.preferences_manager.get_all_preferences()
                self.preferences_loaded.emit(self.current_preferences)
                return True
            else:
                return False
        except Exception as e:
            if self.dialog:
                QMessageBox.critical(self.dialog, "Error", f"Error reseteando preferencias: {str(e)}")
            return False
    
    # Métodos de UI helper para la vista
    def _load_available_printers(self):
        """Carga las impresoras disponibles desde la base de datos"""
        try:
            self.available_printers = self.db_manager.printers.find_active_printers()
        except Exception as e:
            self.available_printers = []
    
    def get_available_printers(self) -> List[Printer]:
        """Retorna las impresoras disponibles"""
        return self.available_printers
    
    def get_printer_display_options(self) -> List[Dict[str, Any]]:
        """Retorna las opciones de impresora para el ComboBox"""
        options = [
            {"text": tr(I18N.Prefs.OPTION_PRINTER_NONE), "value": None},
            {"text": tr(I18N.Prefs.OPTION_PRINTER_FIRST), "value": "first"}
        ]
        
        # Agregar impresoras específicas
        for printer in self.available_printers:
            display_text = f"{printer.name} ({printer.brand} {printer.model})"
            options.append({
                "text": display_text,
                "value": printer.id
            })
        
        return options
    
    def get_current_printer_selection(self) -> Optional[str]:
        """Obtiene la selección actual de impresora"""
        printer_id = self.preferences_manager.get_default_printer_id()
        
        if printer_id is None:
            return None
        elif printer_id == "first":
            return "first"
        else:
            return str(printer_id)
    
    def get_customer_mode_display(self) -> int:
        """Obtiene el modo de cliente actual para mostrar"""
        mode = self.preferences_manager.get_default_customer_mode()
        return {"normal": 0, "optional": 1, "default": 2}.get(mode, 0)
    
    def get_theme_display(self) -> int:
        """Obtiene el tema actual para mostrar"""
        theme = self.preferences_manager.get_theme()
        return {"auto": 0, "light": 1, "dark": 2}.get(theme, 0)
    
    def get_advance_mode_display(self) -> int:
        """Obtiene el índice del modo de anticipo para mostrar en el combobox"""
        try:
            # Obtener el modo numérico guardado
            current_mode = self.get_advance_mode()
            
            # Validar que sea un número válido
            if isinstance(current_mode, int) and 0 <= current_mode <= 4:
                return current_mode
            else:
                # Si no es válido, convertir si es cadena o usar 0 por defecto
                if isinstance(current_mode, str):
                    string_to_number = {
                        "Ninguno": 0,
                        "Activar por defecto al iniciar": 1, 
                        "Activar al monto mínimo": 2,
                        "Activar al monto máximo": 3,
                        "Activar en montos mínimos y máximos": 4
                    }
                    converted = string_to_number.get(current_mode, 0)
                    # Guardar la conversión
                    self.preferences_manager.set_advance_mode(converted)
                    self.preferences_manager.save_preferences()
                    return converted
                else:
                    return 0
        except Exception as e:
            logger.error("AppPreferencesPresenter", f"Error en get_advance_mode_display: {e}")
            logger.log_exception("AppPreferencesPresenter", e, "get_advance_mode_display")
            return 0
    
    def get_advance_default_settings(self) -> Dict[str, Any]:
        """Obtiene la configuración por defecto de anticipo"""
        return {
            "percentage": self.preferences_manager.get_advance_default_percentage()
        }
    
    def get_advance_auto_minimum_settings(self) -> Dict[str, Any]:
        """Obtiene la configuración de anticipo automático mínimo"""
        return self.preferences_manager.get_advance_auto_minimum()
    
    def get_advance_auto_maximum_settings(self) -> Dict[str, Any]:
        """Obtiene la configuración de anticipo automático máximo"""
        return self.preferences_manager.get_advance_auto_maximum()
    
    def validate_preferences(self, preferences_data: Dict[str, Any]) -> tuple[bool, str]:
        """Valida los datos de preferencias antes de guardar"""
        try:
            # Validar modo de cliente
            customer_mode = preferences_data.get("customer_mode")
            valid_modes = ["normal", "optional", "default"]
            if customer_mode and customer_mode not in valid_modes:
                return False, f"Modo de cliente inválido: {customer_mode}"
            
            # Validar impresora por defecto
            printer_id = preferences_data.get("default_printer_id")
            if printer_id is not None and printer_id != "first":
                # Verificar que la impresora exista
                try:
                    printer_id_int = int(printer_id)
                    if not any(p.id == printer_id_int for p in self.available_printers):
                        return False, f"Impresora con ID {printer_id_int} no encontrada"
                except ValueError:
                    return False, f"ID de impresora inválido: {printer_id}"
            
            # Validar tema
            theme = preferences_data.get("theme")
            valid_themes = ["light", "dark", "auto"]
            if theme and theme not in valid_themes:
                return False, f"Tema inválido: {theme}"
            
            return True, "Validación exitosa"
            
        except Exception as e:
            return False, f"Error en validación: {str(e)}"
    
    def reset_preferences(self) -> bool:
        """Resetea las preferencias a valores por defecto"""
        try:
            success = self.preferences_manager.reset_to_defaults()
            
            if success:
                # Recargar preferencias actuales
                self.current_preferences = self.preferences_manager.get_all_preferences()
                self.preferences_loaded.emit(self.current_preferences)
                
                if self.dialog:
                    QMessageBox.information(
                        self.dialog,
                        "Preferencias reseteadas",
                        "Las preferencias se han reseteado a sus valores por defecto."
                    )
                return True
            else:
                logger.error("AppPreferencesPresenter", "Error reseteando preferencias: resultado nulo")
                return False
            
        except Exception as e:
            logger.error("AppPreferencesPresenter", f"Error reseteando preferencias: {e}")
            logger.log_exception("AppPreferencesPresenter", e, "reset_preferences")
            if self.dialog:
                QMessageBox.critical(
                    self.dialog,
                    tr(I18N.Dialogs.ERROR_TITLE),
                    "Error al resetear las preferencias.\n\nRevise el archivo de log para más detalles."
                )
            return False