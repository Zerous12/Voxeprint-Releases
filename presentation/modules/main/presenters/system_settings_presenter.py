"""
Presenter para el manejo de configuraciones del sistema
Coordina entre la vista de ajustes y los repositorios de datos
"""
import os
import subprocess
import sys
from typing import Dict, Any, Optional, List

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

from core.managers.database_manager import get_db_manager
from core.managers.quote_config_manager import QuoteConfigManager
from core.managers.currency_manager import CurrencyManager
from core.services.database_restore_service import DatabaseRestoreService, get_restore_service
from core.utils.logger import logger
from core.utils.path_helper import logs_dir
from core.utils.translation_helper import tr


class SystemSettingsPresenter(QObject):
    """Presenter para gestionar las configuraciones del sistema"""
    
    # Señales
    settings_loaded = Signal(dict)  # Emitida cuando se cargan las configuraciones
    settings_saved = Signal(bool)   # Emitida cuando se guardan las configuraciones
    error_occurred = Signal(str)    # Emitida cuando ocurre un error
    
    def __init__(self, view=None):
        super().__init__()
        self.view = view
        
        # Obtener el manager de base de datos
        self.db_manager = get_db_manager()
        self.system_config_repo = self.db_manager.configs
        self.quote_config_manager = QuoteConfigManager()
        self.printer_repository = self.db_manager.printers
        
        # Variable para trackear cambio de moneda
        self._currency_change_info = None  # Almacena (old_currency, new_currency) si hubo cambio
        # Variable para trackear cambio de idioma o región
        self._language_region_changed = False
        
        # Servicio de restauración de base de datos
        self._restore_service = get_restore_service()
        
        # Asegurar que la versión de BD esté registrada
        self._restore_service.ensure_db_version_stored()
        
        # Configurar conexiones con la vista
        if self.view:
            self.setup_view_connections()
    
    def setup_view_connections(self):
        """Configura las conexiones con la vista"""
        # Establecer referencia bidireccional
        self.view.presenter = self
        
        self.view.save_requested.connect(self.save_all_settings)
        self.view.settings_changed.connect(self.load_all_settings)
        self.view.open_log_requested.connect(self._handle_open_log)
        
        # Conectar señales del presenter a la vista
        self.settings_loaded.connect(self.view.load_settings)
        self.settings_saved.connect(self.view.show_save_confirmation)
    
    def load_all_settings(self):
        """Carga todas las configuraciones desde la base de datos y archivos"""
        try:
            settings_data = {}
            
            # Cargar configuraciones de la base de datos
            db_configs = self.load_database_settings()
            settings_data.update(db_configs)
            
            # Cargar configuraciones del archivo JSON
            json_configs = self.load_json_settings()
            settings_data.update(json_configs)
            
            # Emitir los datos cargados
            self.settings_loaded.emit(settings_data)
            
            # Cargar datos del tab Base de Datos
            self.load_database_tab_data()
            
            logger.info("SystemSettings", "Configuraciones cargadas exitosamente")
            
        except Exception as e:
            error_msg = f"Error al cargar configuraciones: {str(e)}"
            logger.error("SystemSettings", error_msg)
            self.error_occurred.emit(error_msg)
    
    def load_database_settings(self) -> Dict[str, Any]:
        """Carga configuraciones desde la base de datos"""
        settings = {}
        
        try:
            # Configuraciones de costos
            configs_to_load = [
                'electricity_rate',
                'default_profit_margin',
                'default_failure_margin',
                'tax_rate',  # Esta es la fuente única de verdad para IVA
                'electricity_peak_multiplier',
                'auto_save_interval',
                'backup_frequency'
            ]
            
            for config_key in configs_to_load:
                config_value = self.system_config_repo.get_value(config_key)
                if config_value is not None and config_value != "":
                    # Convertir a número si es necesario
                    if config_key in ['electricity_rate', 'default_profit_margin', 
                                    'default_failure_margin', 'tax_rate', 'electricity_peak_multiplier']:
                        settings[config_key] = float(config_value)
                    elif config_key in ['auto_save_interval', 'backup_frequency']:
                        settings[config_key] = int(config_value)
                    else:
                        settings[config_key] = config_value

            # Configuraciones de overhead (gastos fijos del negocio)
            overhead_keys = [
                'overhead_rent', 'overhead_water', 'overhead_internet',
                'overhead_accounting', 'overhead_salary', 'overhead_transport',
                'overhead_other', 'overhead_hours_per_day', 'overhead_days_per_month'
            ]
            for config_key in overhead_keys:
                config_value = self.system_config_repo.get_value(config_key)
                if config_value is not None and config_value != "":
                    settings[config_key] = float(config_value)

            # Modo y valor manual de impresoras activas
            _mode = self.system_config_repo.get_value('overhead_active_printers_mode', 'auto')
            settings['overhead_active_printers_mode'] = _mode
            _manual = self.system_config_repo.get_value('overhead_active_printers', '1')
            settings['overhead_active_printers'] = int(float(_manual)) if _manual else 1

            # Conteo real de impresoras activas desde la BD (siempre se incluye para el label)
            try:
                _active = self.printer_repository.find_active_printers()
                settings['overhead_active_printers_db_count'] = len(_active)
            except Exception:
                settings['overhead_active_printers_db_count'] = 0
            
            # Configuraciones de empresa
            company_configs = [
                'company_name',
                'company_address', 
                'company_city',
                'company_phone',
                'company_email',
                'company_website'
            ]
            
            for config_key in company_configs:
                config_value = self.system_config_repo.get_value(config_key)
                if config_value is not None and config_value != "":
                    settings[config_key] = str(config_value)
            
            # Configuraciones booleanas
            bool_configs = [
                ('backup_enabled', True),
                ('include_iva', True),
                ('commission_tax_shield', False)
            ]
            
            for config_key, default_value in bool_configs:
                config_value = self.system_config_repo.get_value(config_key)
                if config_value is not None and config_value != "":
                    settings[config_key] = str(config_value).lower() in ['true', '1', 'yes', 'on']
                else:
                    settings[config_key] = default_value
            
            # Configuración de moneda
            currency = self.system_config_repo.get_value('currency_symbol')
            settings['currency_symbol'] = currency if currency else 'Gs.'
            
        except Exception as e:
            logger.error("SystemSettingsPresenter", f"Error al cargar configuraciones de la base de datos: {str(e)}")
            raise
        
        return settings
    
    def load_json_settings(self) -> Dict[str, Any]:
        """Carga configuraciones desde el archivo JSON"""
        settings = {}
        
        try:
            # Extraer información de empresa del JSON
            company_info = self.quote_config_manager.get_company_info()
            
            # Mapear campos del JSON si no están en la base de datos
            json_mappings = {
                'company_name': company_info.get('name', ''),
                'company_address': company_info.get('address', ''),
                'company_city': company_info.get('city', ''),
                'company_phone': company_info.get('phone', ''),
                'company_email': company_info.get('email', ''),
                'company_website': company_info.get('website', ''),
            }
            
            # Solo usar valores del JSON si no están en la base de datos
            for key, value in json_mappings.items():
                if key not in settings or not settings[key]:
                    settings[key] = value
            
            # Título del PDF
            settings['pdf_title'] = self.quote_config_manager.get_title()
            settings['pdf_subtitle'] = self.quote_config_manager.get_subtitle()
            
            # Fuente del PDF
            settings['pdf_font_family'] = self.quote_config_manager.get_pdf_font_family()
            
            # Configuración del logo
            settings['document_settings'] = {
                'logo_path': self.quote_config_manager.get_logo_path()
            }
            
            # Comentarios del pie de página desde el JSON (como lista)
            footer_comments_list = self.quote_config_manager.get_footer_comments()
            # Convertir la lista a texto para mostrar en el widget (una línea por comentario)
            settings['footer_comments'] = '\n'.join(footer_comments_list) if footer_comments_list else ''
            
            # Configuraciones del margen de error desde el JSON
            settings['include_error_margin'] = self.quote_config_manager.get_include_error_margin()
            
            # Configuración de Post-Processing desde el JSON
            settings['include_post_processing'] = self.quote_config_manager.get_include_post_processing()

            # Configuraciones de Nota de Precios
            note_cfg = self.quote_config_manager.get_note_settings()
            settings['note_title']              = note_cfg.get('title', 'Nota de Precios')
            settings['note_primary_color']      = note_cfg.get('primary_color', '')
            settings['note_font_family']        = note_cfg.get('note_font_family', 'Lato')
            settings['note_show_tax']           = note_cfg.get('show_tax', True)
            settings['note_obs_text']            = note_cfg.get('obs_text', '')
            settings['note_display_mode']        = note_cfg.get('display_mode', 'summary')
            settings['note_summary_label']       = note_cfg.get('summary_label', 'Servicio de Impresión 3D')
            settings['note_postprocessing_mode'] = note_cfg.get('postprocessing_mode', 'separate')
            settings['note_failure_margin_mode'] = note_cfg.get('failure_margin_mode', 'separate')
            settings['note_validity_enabled']    = note_cfg.get('validity_enabled', True)
            settings['note_validity_days']       = note_cfg.get('validity_days', 30)

            # Configuraciones del PDF de Presupuesto
            pdf_cfg = self.quote_config_manager.get_pdf_settings()
            settings['pdf_primary_color'] = pdf_cfg.get('primary_color', '')
            settings['pdf_display_mode']  = pdf_cfg.get('display_mode', 'summary')
            settings['pdf_summary_label'] = pdf_cfg.get('summary_label', 'Servicio de Impresión 3D')

        except Exception as e:
            logger.error("SystemSettingsPresenter", f"Error al cargar configuraciones del JSON: {str(e)}")
            # No lanzar excepción aquí, usar valores por defecto
        
        return settings
    
    def save_all_settings(self, settings_data: Dict[str, Any]):
        """Guarda todas las configuraciones en la base de datos y archivos"""
        try:
            # Resetear info de cambio de moneda
            self._currency_change_info = None
            # Resetear flag de cambio de idioma/región
            self._language_region_changed = False
            
            # Guardar en la base de datos
            self.save_database_settings(settings_data)

            # Guardar en el archivo JSON
            self.save_json_settings(settings_data)

            # Guardar idioma y región
            self.save_language_region_settings(settings_data)

            # Solo emitir señal de éxito si todo fue bien
            self.settings_saved.emit(True)
            logger.info("SystemSettings", "Configuraciones guardadas exitosamente")
            
            # Si hubo cambio de moneda, mostrar diálogo después de guardar
            if self._currency_change_info:
                old_currency, new_currency = self._currency_change_info
                self._show_currency_change_dialog_and_restart(old_currency, new_currency)
            elif self._language_region_changed:
                self._show_language_region_dialog_and_restart()
            
        except Exception as e:
            error_msg = f"Error al guardar configuraciones: {str(e)}"
            logger.log_exception("SystemSettings", e, "guardar configuraciones")
            self.error_occurred.emit(error_msg)
            self.settings_saved.emit(False)
            
            # Mostrar diálogo de error al usuario
            if self.view:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    self.view,
                    "Error al Guardar",
                    "No se pudieron guardar las configuraciones.\n\n"
                    "Por favor, verifique los datos ingresados e intente nuevamente."
                )
    
    def save_database_settings(self, settings_data: Dict[str, Any]):
        """Guarda configuraciones en la base de datos"""
        try:
            # Configuraciones de costos (números)
            cost_configs = [
                'electricity_rate',
                'default_profit_margin', 
                'default_failure_margin',
                'tax_rate',  # Esta es la única fuente de verdad para impuestos/IVA
                'electricity_peak_multiplier'
            ]
            
            for config_key in cost_configs:
                if config_key in settings_data:
                    value = float(settings_data[config_key])
                    self.system_config_repo.set_config(config_key, str(value), 'costs')

            # Configuraciones de overhead (gastos fijos del negocio)
            overhead_configs = [
                'overhead_rent', 'overhead_water', 'overhead_internet',
                'overhead_accounting', 'overhead_salary', 'overhead_transport',
                'overhead_other', 'overhead_hours_per_day', 'overhead_days_per_month'
            ]
            for config_key in overhead_configs:
                if config_key in settings_data:
                    self.system_config_repo.set_config(
                        config_key, str(float(settings_data[config_key])), 'overhead'
                    )

            # Modo y valor manual de impresoras
            if 'overhead_active_printers_mode' in settings_data:
                self.system_config_repo.set_config(
                    'overhead_active_printers_mode',
                    str(settings_data['overhead_active_printers_mode']),
                    'overhead'
                )
            if 'overhead_active_printers' in settings_data:
                self.system_config_repo.set_config(
                    'overhead_active_printers',
                    str(int(settings_data['overhead_active_printers'])),
                    'overhead'
                )
            
            # Configuraciones de empresa (texto)
            company_configs = [
                'company_name',
                'company_address',
                'company_city', 
                'company_phone',
                'company_email',
                'company_website'
            ]
            
            for config_key in company_configs:
                if config_key in settings_data:
                    value = str(settings_data[config_key]).strip()
                    self.system_config_repo.set_config(config_key, value, 'company')
            
            # Configuraciones del sistema (enteros)
            system_int_configs = [
                'auto_save_interval',
                'backup_frequency'
            ]
            
            for config_key in system_int_configs:
                if config_key in settings_data:
                    value = int(settings_data[config_key])
                    self.system_config_repo.set_config(config_key, str(value), 'system')
            
            # Configuraciones booleanas
            bool_configs = [
                'backup_enabled',
                'include_iva',
                'commission_tax_shield'
            ]
            
            for config_key in bool_configs:
                if config_key in settings_data:
                    value = bool(settings_data[config_key])
                    self.system_config_repo.set_config(config_key, str(value), 'system')
            
            # Configuración de moneda base
            if 'base_currency' in settings_data:
                currency_changed = self.set_base_currency(settings_data['base_currency'])
                if not currency_changed:
                    raise Exception("No se pudo cambiar la moneda base. Verifique las tasas de cambio.")
            
            # footer_comments se maneja exclusivamente en el JSON (no en la base de datos)
            
        except Exception as e:
            logger.log_exception("SystemSettings", e, "guardar en base de datos")
            raise
    
    def save_json_settings(self, settings_data: Dict[str, Any]):
        """Guarda configuraciones en el archivo JSON"""
        try:
            # Actualizar información de empresa
            company_mappings = {
                'name': settings_data.get('company_name', ''),
                'address': settings_data.get('company_address', ''),
                'city': settings_data.get('company_city', ''),
                'phone': settings_data.get('company_phone', ''),
                'email': settings_data.get('company_email', ''),
                'website': settings_data.get('company_website', ''),
            }
            
            # Actualizar información de empresa
            if any(company_mappings.values()):  # Solo actualizar si hay algún valor
                self.quote_config_manager.update_company_info(**company_mappings)
            
            # IMPORTANTE: Sincronizar valores desde la BD para evitar duplicaciones
            self._sync_json_with_database()
            
            # Actualizar configuración específica de IVA si está presente
            if 'include_iva' in settings_data:
                self.quote_config_manager.update_include_iva(bool(settings_data['include_iva']))
            
            if 'tax_rate' in settings_data:
                self.quote_config_manager.update_iva_rate(float(settings_data['tax_rate']))
            
            # Actualizar configuraciones del margen de error
            if 'include_error_margin' in settings_data:
                self.quote_config_manager.update_include_error_margin(bool(settings_data['include_error_margin']))
            
            # Actualizar configuración de Post-Processing
            if 'include_post_processing' in settings_data:
                self.quote_config_manager.update_include_post_processing(bool(settings_data['include_post_processing']))
            
            # Actualizar configuración del logo (después de la sincronización)
            if 'logo_path' in settings_data:
                logo_path = settings_data.get('logo_path', '')
                self.quote_config_manager.update_logo_path(logo_path)
            
            # Actualizar fuente del PDF
            if 'pdf_font_family' in settings_data:
                self.quote_config_manager.set_pdf_font_family(settings_data['pdf_font_family'])
            
            # Actualizar título y subtítulo del PDF
            if 'pdf_title' in settings_data:
                self.quote_config_manager.set_title(settings_data['pdf_title'])
            
            if 'pdf_subtitle' in settings_data:
                self.quote_config_manager.set_subtitle(settings_data['pdf_subtitle'])
            
            # Guardar los cambios en el archivo de configuración
            if ('include_iva' in settings_data or 'tax_rate' in settings_data or 'logo_path' in settings_data or 
                'include_error_margin' in settings_data or 'include_post_processing' in settings_data or 
                'pdf_font_family' in settings_data or 'pdf_title' in settings_data or 'pdf_subtitle' in settings_data):
                self.quote_config_manager.save_config()
            
            # Actualizar comentarios de pie de página (solo en JSON)
            if 'footer_comments' in settings_data:
                footer_text = str(settings_data['footer_comments']).strip()
                if footer_text:
                    # Dividir por líneas y limpiar cada línea
                    footer_comments_list = [line.strip() for line in footer_text.split('\n') if line.strip()]
                else:
                    footer_comments_list = []
                
                # Actualizar en el JSON
                self.quote_config_manager.update_footer_comments(footer_comments_list)
            
            # Guardar configuración actualizada
            self.quote_config_manager.save_config()
            # Actualizar configuraciones del PDF de Presupuesto
            pdf_keys = ('pdf_primary_color', 'pdf_display_mode', 'pdf_summary_label')
            if any(k in settings_data for k in pdf_keys):
                pdf_section = self.quote_config_manager._config.setdefault('pdf_settings', {})
                pdf_section['primary_color'] = settings_data.get('pdf_primary_color', pdf_section.get('primary_color', ''))
                pdf_section['display_mode']  = settings_data.get('pdf_display_mode', pdf_section.get('display_mode', 'detailed'))
                pdf_section['summary_label'] = settings_data.get('pdf_summary_label', pdf_section.get('summary_label', 'Servicio de Impresión 3D'))
                self.quote_config_manager.save_config()
            # Actualizar configuraciones de Nota de Precios
            note_keys = (
                'note_title', 'note_primary_color', 'note_font_family',
                'note_show_tax', 'note_obs_text',
                'note_display_mode', 'note_summary_label', 'note_postprocessing_mode',
                'note_failure_margin_mode', 'note_validity_enabled', 'note_validity_days',
            )
            if any(k in settings_data for k in note_keys):
                note_section = self.quote_config_manager._config.setdefault('note_settings', {})
                note_section['title']            = settings_data.get('note_title', note_section.get('title', 'Nota de Precios'))
                note_section['primary_color']    = settings_data.get('note_primary_color', note_section.get('primary_color', ''))
                note_section['note_font_family'] = settings_data.get('note_font_family', note_section.get('note_font_family', 'Lato'))
                _pp_mode = settings_data.get('note_postprocessing_mode', note_section.get('postprocessing_mode', 'separate'))
                note_section['show_post_processing'] = _pp_mode == 'separate'
                _fm_mode = settings_data.get('note_failure_margin_mode', note_section.get('failure_margin_mode', 'separate'))
                note_section['failure_margin_mode']  = _fm_mode
                note_section['show_tax']         = settings_data.get('note_show_tax', note_section.get('show_tax', True))
                note_section['obs_text']         = settings_data.get('note_obs_text', note_section.get('obs_text', ''))
                note_section['display_mode']     = settings_data.get('note_display_mode', note_section.get('display_mode', 'summary'))
                note_section['summary_label']    = settings_data.get('note_summary_label', note_section.get('summary_label', 'Servicio de Impresión 3D'))
                note_section['postprocessing_mode'] = _pp_mode
                note_section['validity_enabled'] = settings_data.get('note_validity_enabled', note_section.get('validity_enabled', True))
                note_section['validity_days']    = int(settings_data.get('note_validity_days', note_section.get('validity_days', 30)))
                self.quote_config_manager.save_config()

        except Exception as e:
            logger.log_exception("SystemSettings", e, "guardar en archivo JSON")
            raise
    
    def _sync_json_with_database(self):
        """Sincroniza el JSON con los valores autoritarios de la base de datos"""
        try:
            # Obtener valores autoritarios de la BD
            tax_rate = self.system_config_repo.get_value('tax_rate', '10.0')
            include_iva = self.system_config_repo.get_value('include_iva', 'true')
            currency_symbol = self.system_config_repo.get_value('currency_symbol', 'Gs.')
            
            # Actualizar directamente la configuración interna del manager
            quote_settings = self.quote_config_manager._config.setdefault("quote_settings", {})
            quote_settings['iva_rate'] = float(tax_rate)
            quote_settings['include_iva'] = str(include_iva).lower() in ['true', '1', 'yes', 'on']
            quote_settings['currency'] = currency_symbol
            
            logger.info("SystemSettings", f"JSON sincronizado con BD: IVA={tax_rate}%, incluir_iva={include_iva}, moneda={currency_symbol}")
            
        except Exception as e:
            logger.warning("SystemSettings", f"Error al sincronizar JSON con BD: {str(e)}")
            raise
    
    def get_setting_value(self, key: str, default_value: Any = None) -> Any:
        """Obtiene un valor de configuración específico"""
        try:
            # Primero intentar de la base de datos
            db_value = self.system_config_repo.get_value(key)
            if db_value is not None and db_value != "":
                return db_value
            
            # Si no está en la base de datos, intentar del JSON
            if key.startswith('company_'):
                json_key = key.replace('company_', '')
                company_info = self.quote_config_manager.get_company_info()
                return company_info.get(json_key, default_value)
            
            # Buscar en configuraciones del documento
            if key == 'pdf_title':
                return self.quote_config_manager.get_title()
            if key == 'pdf_subtitle':
                return self.quote_config_manager.get_subtitle()
            
            return default_value
            
        except Exception as e:
            logger.error("SystemSettings", f"Error al obtener configuración {key}: {str(e)}")
            return default_value
    
    # ============================================================================
    # MÉTODOS DE MONEDA
    # ============================================================================
    
    def get_available_languages(self) -> List[Dict[str, Any]]:
        """Retorna los idiomas disponibles para mostrar en el combo"""
        from core.managers.language_manager import LanguageManager
        try:
            return LanguageManager().available_languages()
        except Exception as e:
            logger.error("SystemSettingsPresenter", f"Error obteniendo idiomas: {e}")
            return [{"code": "es", "language": "Español"}]

    def get_available_locales(self) -> List[Dict[str, Any]]:
        """Retorna los perfiles de locale disponibles para mostrar en el combo"""
        from core.managers.locale_manager import LocaleManager
        try:
            return LocaleManager().available_locales()
        except Exception as e:
            logger.error("SystemSettingsPresenter", f"Error obteniendo locales: {e}")
            return [{"code": "PY", "country": "Paraguay", "currency": "PYG"}]

    def get_locale_preview(self, locale_code: str) -> Dict[str, str]:
        """Retorna tax_id_label y date_format del locale indicado"""
        import json
        from core.utils.path_helper import app_root
        try:
            file_path = app_root() / "locales" / f"{locale_code.upper()}.json"
            if not file_path.exists():
                file_path = app_root() / "locales" / f"{locale_code}.json"
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {
                "tax_id_label": data.get("tax_id", {}).get("label", "—"),
                "date_format": data.get("formats", {}).get("date", "—"),
            }
        except Exception as e:
            logger.error("SystemSettingsPresenter", f"Error leyendo preview de locale '{locale_code}': {e}")
            return {"tax_id_label": "—", "date_format": "—"}

    def get_current_language(self) -> str:
        """Retorna el código de idioma actualmente configurado"""
        from core.managers.app_preferences_manager import AppPreferencesManager
        return AppPreferencesManager().get_preference("appearance", "language", "es")

    def get_current_locale(self) -> str:
        """Retorna el código de locale actualmente configurado"""
        from core.managers.app_preferences_manager import AppPreferencesManager
        return AppPreferencesManager().get_preference("appearance", "locale", "PY")

    def save_language_region_settings(self, settings_data: Dict[str, Any]):
        """Guarda configuraciones de idioma y región en AppPreferencesManager"""
        from core.managers.app_preferences_manager import AppPreferencesManager
        try:
            prefs = AppPreferencesManager()
            changed = False
            if "language" in settings_data:
                current_lang = prefs.get_preference("appearance", "language", "es")
                if settings_data["language"] != current_lang:
                    changed = True
                prefs.set_preference("appearance", "language", settings_data["language"])
            if "locale" in settings_data:
                current_locale = prefs.get_preference("appearance", "locale", "PY")
                if settings_data["locale"] != current_locale:
                    changed = True
                prefs.set_preference("appearance", "locale", settings_data["locale"])
            if "language" in settings_data or "locale" in settings_data:
                prefs.save_preferences()
                logger.info("SystemSettingsPresenter", "Idioma y región guardados")
            if changed:
                self._language_region_changed = True
        except Exception as e:
            logger.error("SystemSettingsPresenter", f"Error guardando idioma/región: {e}")
            raise

    def get_currency_options(self) -> list[Dict[str, str]]:
        """Obtiene lista de monedas disponibles para el ComboBox"""
        try:
            from infrastructure.database.repositories.currency_repository import CurrencyRepository
            repo = CurrencyRepository()
            currencies = repo.get_active()
            
            return [
                {
                    "text": f"{currency.name} ({currency.symbol})",
                    "code": currency.code
                }
                for currency in currencies
            ]
        except Exception as e:
            logger.error("SystemSettingsPresenter", f"Error cargando monedas: {e}")
            return [{"text": "Guaraní Paraguayo (Gs.)", "code": "PYG"}]
    
    def get_base_currency(self) -> str:
        """Obtiene la moneda base actual"""
        try:
            from core.managers.app_preferences_manager import AppPreferencesManager
            prefs_manager = AppPreferencesManager()
            return prefs_manager.get_base_currency()
        except Exception as e:
            logger.error("SystemSettingsPresenter", f"Error obteniendo moneda base: {e}")
            return "PYG"
    
    def set_base_currency(self, currency_code: str) -> bool:
        """Establece la moneda base con confirmación del usuario"""
        try:
            from core.managers.app_preferences_manager import AppPreferencesManager
            prefs_manager = AppPreferencesManager()
            
            # Obtener moneda actual
            old_currency = prefs_manager.get_base_currency()
            
            # Si no hay cambio, retornar True
            if old_currency == currency_code:
                return True
            
            # Obtener valores actuales de configuración (ANTES de cambiar nada)
            from core.managers.quote_config_manager import QuoteConfigManager
            quote_config = QuoteConfigManager()
            
            # IMPORTANTE: Usar old_currency (moneda anterior del sistema) como origen de conversión
            # NO usar quote_config.get_currency_code() porque puede estar desincronizado
            config_currency = old_currency
            
            # Obtener valor actual de tarifa eléctrica desde la BD
            electricity_rate = float(self.system_config_repo.get_value('electricity_rate', '435'))
            
            # Convertir valor de configuración
            new_electricity = quote_config.convert_config_values(
                config_currency, currency_code, electricity_rate
            )
            
            # Validar que la conversión fue exitosa
            if new_electricity is None:
                logger.error("SystemSettings", f"Error conversión moneda {config_currency} -> {currency_code}: tasa no encontrada")
                if self.view:
                    QMessageBox.critical(
                        self.view, 
                        "Error al cambiar moneda",
                        f"No se pudo cambiar la moneda a {currency_code}.\n\n"
                        f"Verifique que la tasa de cambio esté configurada correctamente en:\n"
                        f"Configuración del Sistema > Sistema > Tasas de Cambio"
                    )
                return False
            
            # Validar que no sean los valores originales (indica que falló silenciosamente)
            if new_electricity == electricity_rate:
                logger.warning(
                    "SystemSettings",
                    f"La conversión retornó valores originales. Posible fallo en tasa de cambio {config_currency} -> {currency_code}"
                )
            
            # Guardar valor convertido en la BD
            self.system_config_repo.set_config('electricity_rate', str(new_electricity), 'costs')

            # Convertir gastos fijos (overhead) monetarios
            from core.services.currency_conversion_service import CurrencyConversionService
            converter = CurrencyConversionService()
            overhead_monetary_keys = [
                'overhead_rent', 'overhead_water', 'overhead_internet',
                'overhead_accounting', 'overhead_salary', 'overhead_transport',
                'overhead_other'
            ]
            for key in overhead_monetary_keys:
                raw = self.system_config_repo.get_value(key, '0')
                try:
                    original_value = float(raw)
                except (ValueError, TypeError):
                    original_value = 0.0
                if original_value != 0.0:
                    converted = converter.convert_amount(original_value, config_currency, currency_code)
                    if converted is not None:
                        self.system_config_repo.set_config(key, str(converted), 'overhead')
                        logger.info("SystemSettings", f"Overhead '{key}' convertido: {original_value} {config_currency} -> {converted} {currency_code}")
                    else:
                        logger.warning("SystemSettings", f"No se pudo convertir overhead '{key}': tasa no encontrada")
            
            # Actualizar currency_code en quote_config.json
            quote_config.update_currency_code(currency_code)
            quote_config.save_config()
            
            logger.info("SystemSettings", f"Valores convertidos: Electricidad {electricity_rate} -> {new_electricity}")
            
            # Guardar cambio en preferences
            success = prefs_manager.set_base_currency(currency_code)
            
            if success:
                # Notificar al CurrencyManager
                currency_manager = CurrencyManager()
                currency_manager.set_current_currency(currency_code)
                
                logger.info("SystemSettings", f"Moneda base cambiada de {old_currency} a {currency_code}")
                
                # Guardar info del cambio para procesarla después del guardado completo
                self._currency_change_info = (old_currency, currency_code)
            
            return success
            
        except Exception as e:
            logger.log_exception("SystemSettings", e, "establecer moneda base")
            if self.view:
                QMessageBox.critical(
                    self.view,
                    "Error al cambiar moneda",
                    "No se pudo cambiar la moneda base.\n\n"
                    "Por favor, verifique las tasas de cambio y la configuración del sistema."
                )
            return False
    
    def _show_restart_dialog_and_restart(self, title: str, message: str):
        """Muestra un diálogo genérico de aviso y reinicia la aplicación."""
        if self.view:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self.view, title, message, QMessageBox.Ok)
        self._restart_application()

    def _show_currency_change_dialog_and_restart(self, old_currency: str, new_currency: str):
        """Muestra diálogo de cambio de moneda y reinicia la aplicación"""
        self._show_restart_dialog_and_restart(
            tr("SystemSettings.dialog_currency_change_title"),
            tr("SystemSettings.dialog_currency_change_text",
               old_currency=old_currency, new_currency=new_currency)
        )

    def _show_language_region_dialog_and_restart(self):
        """Muestra diálogo de cambio de idioma/región y reinicia la aplicación"""
        self._show_restart_dialog_and_restart(
            tr("SystemSettings.dialog_lang_region_change_title"),
            tr("SystemSettings.dialog_lang_region_change_text")
        )

    def _restart_application(self):
        """Reinicia la aplicación automáticamente"""
        try:
            import sys
            import subprocess
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QTimer
            
            logger.info("SystemSettings", "Reiniciando aplicación para aplicar cambios de moneda...")
            
            # Obtener argumentos del programa
            if getattr(sys, 'frozen', False):
                # Aplicación empaquetada
                program_path = sys.executable
                args = [program_path]
            else:
                # Aplicación en desarrollo
                program_path = sys.executable
                args = [program_path] + sys.argv
            
            # Programar el reinicio con un pequeño delay
            def do_restart():
                try:
                    # Usar subprocess.Popen para reiniciar en proceso separado
                    subprocess.Popen(args)
                    
                    # Cerrar la aplicación actual
                    app = QApplication.instance()
                    if app:
                        app.quit()
                except Exception as e:
                    logger.error("SystemSettings", f"Error al reiniciar aplicación: {e}")
            
            # Usar QTimer para delay de 500ms antes del reinicio
            QTimer.singleShot(500, do_restart)
            
        except Exception as e:
            logger.log_exception("SystemSettings", e, "intentar reiniciar aplicación")

    # ============================================================================
    # MÉTODOS DE BASE DE DATOS (Tab "Base de Datos")
    # ============================================================================
    
    def load_database_tab_data(self):
        """Carga datos completos para el tab de Base de Datos"""
        try:
            # Obtener estadísticas
            stats = self._restore_service.get_database_stats()
            
            # Construir dict para la vista
            stats_dict = {
                'db_version': stats.db_version,
                'schema_version': stats.schema_version,
                'db_size_mb': stats.db_size_mb,
                'db_path': stats.db_path,
                'created_at': stats.created_at,
                'total_records': stats.total_records,
                'record_counts': stats.record_counts,
                'total_backups': stats.total_backups,
                'last_backup_date': stats.last_backup_date,
                'backup_enabled': stats.backup_enabled,
                'backup_frequency_days': stats.backup_frequency_days,
            }
            
            # Actualizar la vista
            if self.view:
                self.view.update_database_info(stats_dict)
            
            # Cargar lista de backups
            self.refresh_backups_list()
            
            logger.info("SystemSettings", "Datos del tab Base de Datos cargados")
            
        except Exception as e:
            logger.error("SystemSettings", f"Error cargando datos de BD: {e}")
    
    def refresh_backups_list(self):
        """Actualiza la lista de backups en la vista"""
        try:
            backups = self._restore_service.get_backups_list()
            
            # Convertir BackupInfo a dicts para la vista
            backups_data = []
            for backup in backups:
                backups_data.append({
                    'filename': backup.filename,
                    'filepath': backup.filepath,
                    'date': backup.date,
                    'db_version': backup.db_version,
                    'size_mb': backup.size_mb,
                    'is_compatible': backup.is_compatible,
                    'compatibility_reason': backup.compatibility_reason,
                })
            
            if self.view:
                self.view.update_backups_table(backups_data)
                
        except Exception as e:
            logger.error("SystemSettings", f"Error refrescando lista de backups: {e}")
    
    def create_manual_backup(self):
        """Crea un backup manual con confirmación"""
        try:
            result = self._restore_service.create_versioned_backup(label='manual')
            
            if result['success']:
                logger.info("SystemSettings", f"Backup manual creado: {result['backup_path']}")
                if self.view:
                    QMessageBox.information(
                        self.view,
                        "Respaldo Creado",
                        f"Respaldo creado exitosamente.\n\n{result['message']}"
                    )
                # Refrescar la lista
                self.refresh_backups_list()
                self.load_database_tab_data()
            else:
                logger.error("SystemSettings", f"Error creando backup manual: {result['message']}")
                if self.view:
                    QMessageBox.critical(
                        self.view,
                        "Error al Crear Respaldo",
                        f"No se pudo crear el respaldo.\n\n{result['message']}"
                    )
                    
        except Exception as e:
            logger.log_exception("SystemSettings", e, "crear backup manual")
            if self.view:
                QMessageBox.critical(
                    self.view,
                    "Error",
                    f"Error inesperado al crear el respaldo: {e}"
                )
    
    def restore_backup(self, backup_path: str):
        """Restaura un backup después de validación"""
        try:
            # Validar primero
            is_compatible, reason = self._restore_service.validate_restore_compatibility(backup_path)
            
            if not is_compatible:
                if self.view:
                    QMessageBox.warning(
                        self.view,
                        "Backup Incompatible",
                        f"No se puede restaurar este respaldo.\n\n{reason}"
                    )
                return
            
            # Ejecutar restauración
            result = self._restore_service.restore_backup(backup_path)
            
            if result['success']:
                logger.info("SystemSettings", f"BD restaurada exitosamente desde backup")
                if self.view:
                    safety_msg = ""
                    if result.get('safety_backup_path'):
                        import os
                        safety_name = os.path.basename(result['safety_backup_path'])
                        safety_msg = f"\n\nRespaldo de seguridad creado: {safety_name}"
                    
                    QMessageBox.information(
                        self.view,
                        "Restauración Exitosa",
                        f"La base de datos fue restaurada exitosamente.{safety_msg}\n\n"
                        "La aplicación se reiniciará para aplicar los cambios."
                    )
                
                # Reiniciar aplicación
                self._restart_application()
            else:
                logger.error("SystemSettings", f"Error restaurando backup: {result['message']}")
                if self.view:
                    QMessageBox.critical(
                        self.view,
                        "Error en Restauración",
                        f"No se pudo restaurar la base de datos.\n\n{result['message']}"
                    )
                    
        except Exception as e:
            logger.log_exception("SystemSettings", e, "restaurar backup")
            if self.view:
                QMessageBox.critical(
                    self.view,
                    "Error",
                    f"Error inesperado durante la restauración: {e}"
                )
    
    def delete_backup(self, backup_path: str):
        """Elimina un backup"""
        try:
            result = self._restore_service.delete_backup(backup_path)
            
            if result['success']:
                logger.info("SystemSettings", f"Backup eliminado: {result['message']}")
                # Refrescar la lista
                self.refresh_backups_list()
                self.load_database_tab_data()
            else:
                if self.view:
                    QMessageBox.warning(
                        self.view,
                        "Error al Eliminar",
                        f"No se pudo eliminar el respaldo.\n\n{result['message']}"
                    )
                    
        except Exception as e:
            logger.log_exception("SystemSettings", e, "eliminar backup")
    
    def open_backup_folder(self):
        """Abre la carpeta de backups en el explorador"""
        try:
            self._restore_service.open_backup_folder()
        except Exception as e:
            logger.error("SystemSettings", f"Error abriendo carpeta de backups: {e}")

    def _handle_open_log(self):
        """Abre la carpeta de logs en el explorador de archivos"""
        try:
            folder = logs_dir()
            if sys.platform == "win32":
                os.startfile(str(folder))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
            logger.info("SystemSettings", f"Carpeta de logs abierta: {folder}")
        except Exception as e:
            logger.error("SystemSettings", f"Error abriendo carpeta de logs: {e}")
            QMessageBox.warning(
                self.view,
                "Error",
                f"No se pudo abrir la carpeta de logs:\n{str(e)}"
            )