"""
Gestor de configuración para documentos PDF
"""
import json, sys, os
from typing import Dict, Any, List, Tuple
from pathlib import Path
from core.utils.path_helper import config_dir, build_resource_path
from core.utils.logger import logger
from core.utils.first_run_detector import (
    detect_system_defaults, get_note_title, get_quote_title,
    get_doc_title, get_doc_subtitle,
)

class QuoteConfigManager:
    """Maneja la configuración para la generación de PDFs de presupuestos"""
    
    def __init__(self, config_path: str = None):
        self.ensure_config_json()
        if config_path is None:
            # SIEMPRE usar configuración en Documentos del usuario
            config_path = config_dir() / "quote_config.json"
        self.config_path = str(config_path)
        self._config = self._load_config()
    
    @staticmethod
    def ensure_config_json():
        """Crea la carpeta y el archivo de configuración si no existen"""
        config_path = config_dir() / "quote_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        if not config_path.exists():
            # Detectar idioma del sistema para personalizar el JSON inicial
            language, _, service_label = detect_system_defaults()
            note_title  = get_note_title(language)
            quote_title = get_quote_title(language)
            doc_title   = get_doc_title(language)
            doc_subtitle = get_doc_subtitle(language)

            default_config = {
                "company_info": {
                    "name": "Company Name",
                    "address": "Address",
                    "city": "City",
                    "phone": "+1-555-1234",
                    "email": "CompanyEmail@example.com",
                    "website": "www.CompanyWebsite.com"
                },
                "document_settings": {
                    "logo_path": "",  # Vacío por defecto - usará logo_default
                    "logo_default": "resources/images/logo_for_PDF_company.png",
                    "pdf_font_family": "Arial",
                    "title": doc_title,
                    "subtitle": doc_subtitle,
                    "font_config": {
                        "header": ["Helvetica-Bold", 18],
                        "section_title": ["Helvetica-Bold", 10],
                        "body": ["Helvetica", 9],
                        "comments": ["Helvetica", 7]
                    },
                    "colors": {
                        "primary": "#0070C0",
                        "accent": "#808080",
                        "text": "#000000",
                        "table_header_bg": "#0070C0",
                        "table_header_text": "#FFFFFF"
                    },
                    "margins": {
                        "x": 45,
                        "top_offset": 65,
                        "spacing_sections": 15,
                        "spacing_tables": 20,
                        "spacing_before_title": 10
                    }
                },
                "quote_settings": {
                    "title": quote_title,
                    "currency": "Gs.",
                    "currency_code": "PYG",
                    "include_iva": True,
                    "iva_rate": 10.0,
                    "include_error_margin": False,
                    "include_post_processing": False,
                    "footer_comments": [
                        "Los precios pueden variar según las especificaciones finales del proyecto.",
                        "El tiempo de entrega se estima según la complejidad y disponibilidad de materiales.",
                        "Este presupuesto tiene validez de 30 días desde la fecha de emisión.",
                        "El cliente debe inspeccionar las piezas dentro de las 48 horas posteriores a la entrega.",
                        "Se requiere aprobación previa para modificaciones de diseño durante la producción.",
                        "Los archivos 3D proporcionados deben cumplir con las especificaciones técnicas requeridas.",
                        "No se aceptan devoluciones de piezas fabricadas bajo especificaciones del cliente.",
                        "Los colores pueden variar ligeramente respecto a las muestras digitales.",
                        "La empresa no se responsabiliza por defectos de diseño en archivos 3D proporcionados por el cliente."
                    ],
                    "cost_labels": {
                        "material": "Costo de Material",
                        "electricity": "Costo de Energía",
                        "wear": "Costo de Operación",
                        "failure": "Margen de Error",
                        "subtotal": "Subtotal Base",
                        "commission": "Comisión",
                        "post_processing": "Post-Procesado",
                        "subtotal_with_margin": "Subtotal con Márgenes",
                        "tax": "I.V.A (10%)",
                        "total": "TOTAL A PAGAR"
                    }
                },
                "note_settings": {
                    "title": note_title,
                    "primary_color": "",
                    "display_mode": "summary",
                    "summary_label": service_label,
                    "show_material": True,
                    "show_electricity": True,
                    "show_wear": True,
                    "show_failure_margin": True,
                    "show_commission": True,
                    "show_post_processing": True,
                    "show_tax": True
                },
                "pdf_settings": {
                    "primary_color": "",
                    "display_mode": "summary",
                    "summary_label": service_label
                }
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)

    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("QuoteConfigManager", f"⚠️ Archivo de configuración no encontrado: {self.config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error("QuoteConfigManager", f"⚠️ Error al leer configuración JSON: {e}")
            return self._get_default_config()
    
    def reload_config(self) -> None:
        """Recarga la configuración desde el archivo JSON"""
        self._config = self._load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto si no se puede cargar el archivo"""
        return {
            "company_info": {
                "name": "VoxePrint",
                "address": "Dirección no configurada",
                "city": "Ciudad no configurada",
                "phone": "Teléfono no configurado"
            },
            "document_settings": {
                "logo_default": "resources/images/logo_for_PDF_company.png",
                "font_config": {
                    "header": ["Helvetica-Bold", 18],
                    "body": ["Helvetica", 9]
                },
                "colors": {"primary": "#0070C0"},
                "margins": {
                    "x": 60,
                    "top_offset": 65,
                    "spacing_sections": 15,
                    "spacing_tables": 20,
                    "spacing_before_title": 10
                }
            },
            "quote_settings": {
                "title": "PRESUPUESTO DE IMPRESIÓN 3D",
                "currency": "Gs.",
                "include_iva": True,
                "iva_rate": 10.0,
                "include_error_margin": False,
                "include_post_processing": False
            }
        }
    
    def get_company_info(self) -> Dict[str, str]:
        """Obtiene la información de la empresa"""
        return self._config.get("company_info", {})
    
    def get_document_settings(self) -> Dict[str, Any]:
        """Obtiene configuraciones del documento"""
        return self._config.get("document_settings", {})
    
    def get_quote_settings(self) -> Dict[str, Any]:
        """Obtiene configuraciones específicas de presupuestos"""
        return self._config.get("quote_settings", {})
    
    def get_logo_path(self) -> str:
        """
        Obtiene la ruta del logo con manejo robusto de errores.
        Retorna None si debe usar texto en lugar de logo.
        
        Orden de fallback:
        1. Logo personalizado (logo_path) si existe
        2. Logo por defecto (logo_default) si existe  
        3. None (usar texto de empresa)
        """
        doc_settings = self.get_document_settings()
        logo_path = doc_settings.get("logo_path", "")
        logo_default_rel = doc_settings.get("logo_default", "resources/images/logo_for_PDF_company.png")
        
        # Intentar obtener ruta absoluta del logo por defecto
        try:
            logo_default_abs = build_resource_path(logo_default_rel)
        except Exception as e:
            logger.error("QuoteConfigManager", f"⚠️ Error al construir ruta del logo por defecto: {e}")
            logo_default_abs = None
        
        # PASO 1: Intentar logo personalizado si está configurado
        if logo_path and logo_path.strip() != "":
            try:
                # Si la ruta es relativa, convertirla a absoluta
                if not os.path.isabs(logo_path):
                    from core.utils.path_helper import logos_dir
                    logo_path_abs = str(logos_dir() / os.path.basename(logo_path))
                else:
                    logo_path_abs = logo_path
                
                # Verificar que sea un archivo (no carpeta) y que exista
                if os.path.isfile(logo_path_abs):
                    logger.info("QuoteConfigManager", f"Usando logo personalizado: {logo_path_abs}")
                    return logo_path_abs
                else:
                    logger.warning("QuoteConfigManager", f"Logo personalizado no es un archivo válido: {logo_path_abs}")
            except Exception as e:
                logger.error("QuoteConfigManager", f"Error al procesar logo personalizado: {e}")
        
        # PASO 2: Intentar logo por defecto como fallback
        if logo_default_abs:
            try:
                if os.path.isfile(logo_default_abs):
                    logger.info("QuoteConfigManager", f"Usando logo por defecto: {logo_default_abs}")
                    return logo_default_abs
                else:
                    logger.warning("QuoteConfigManager", f"Logo por defecto no existe: {logo_default_abs}")
            except Exception as e:
                logger.error("QuoteConfigManager", f"Error al verificar logo por defecto: {e}")
        
        # PASO 3: Fallback final - usar texto
        logger.warning("QuoteConfigManager", "No se encontró ningún logo válido, se usará texto de empresa")
        return None
    
    def get_font_config(self) -> Dict[str, List]:
        """Obtiene configuración de fuentes"""
        return self.get_document_settings().get("font_config", {})
    
    def get_pdf_font_family(self) -> str:
        """Obtiene la familia de fuente preferida para PDFs"""
        return self.get_document_settings().get("pdf_font_family", "Lato")
    
    def set_pdf_font_family(self, font_family: str):
        """Establece la familia de fuente para PDFs"""
        if "document_settings" not in self._config:
            self._config["document_settings"] = {}
        self._config["document_settings"]["pdf_font_family"] = font_family
        self.save_config()
    
    def set_title(self, title: str):
        """Establece el título del documento"""
        if "document_settings" not in self._config:
            self._config["document_settings"] = {}
        self._config["document_settings"]["title"] = title
        self.save_config()
    
    def set_subtitle(self, subtitle: str):
        """Establece el subtítulo del documento"""
        if "document_settings" not in self._config:
            self._config["document_settings"] = {}
        self._config["document_settings"]["subtitle"] = subtitle
        self.save_config()
    
    def get_colors(self) -> Dict[str, str]:
        """Obtiene configuración de colores"""
        return self.get_document_settings().get("colors", {})
    
    def get_margins(self) -> Dict[str, int]:
        """Obtiene configuración de márgenes"""
        return self.get_document_settings().get("margins", {})
    
    def get_cost_labels(self) -> Dict[str, str]:
        """Obtiene las etiquetas para los costos"""
        return self.get_quote_settings().get("cost_labels", {})
    
    def get_footer_comments(self) -> List[str]:
        """Obtiene los comentarios del pie de página"""
        return self.get_quote_settings().get("footer_comments", [])
    
    def get_currency(self) -> str:
        """Obtiene el símbolo de moneda"""
        return self.get_quote_settings().get("currency", "Gs.")
    
    def get_title(self) -> str:
        """Obtiene el título del documento"""
        return self.get_document_settings().get("title", "PRESUPUESTO")
    
    def get_subtitle(self) -> str:
        """Obtiene el subtítulo del documento"""
        return self.get_document_settings().get("subtitle", "Impresión 3D")
    
    def get_include_iva(self) -> bool:
        """Obtiene si se debe incluir IVA en el documento"""
        return self.get_quote_settings().get("include_iva", True)
    
    def get_iva_rate(self) -> float:
        """Obtiene la tasa de IVA"""
        return self.get_quote_settings().get("iva_rate", 10.0)
    
    def get_include_error_margin(self) -> bool:
        """Obtiene si se debe incluir margen de error"""
        return self.get_quote_settings().get("include_error_margin", False)
    
    def get_include_post_processing(self) -> bool:
        """Obtiene si se debe incluir post-procesado en comisión"""
        return self.get_quote_settings().get("include_post_processing", False)

    def get_pdf_settings(self) -> Dict[str, Any]:
        """Obtiene configuraciones específicas del PDF de Presupuesto.
        Usa defaults si la sección no existe en el JSON (backwards compat)."""
        defaults = {
            "primary_color": "",
            "display_mode": "summary",
            "summary_label": "Servicio de Impresión 3D",
        }
        stored = self._config.get("pdf_settings", {})
        return {**defaults, **stored}

    def get_note_settings(self) -> Dict[str, Any]:
        """Obtiene configuraciones específicas de Notas de Precios.
        Usa defaults si la sección no existe en el JSON (backwards compat)."""
        defaults = {
            "title": "Nota de Precios",
            "primary_color": "",
            "note_font_family": "Lato",
            "display_mode": "summary",
            "summary_label": "Servicio de Impresión 3D",
            "postprocessing_mode": "separate",
            "failure_margin_mode": "separate",
            "validity_enabled": True,
            "validity_days": 30,
            "show_material": True,
            "show_electricity": True,
            "show_wear": True,
            "show_failure_margin": True,
            "show_commission": True,
            "show_post_processing": True,
            "show_tax": True,
            "obs_text": (
                "Esta nota de precios es informativa y no tiene validez legal ni fiscal. "
                "Los precios pueden variar según las especificaciones finales del proyecto."
            ),
        }
        stored = self._config.get("note_settings", {})
        return {**defaults, **stored}
    
    def save_config(self) -> bool:
        """Guarda la configuración actual al archivo"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error("QuoteConfigManager", f"Error al guardar configuración: {e}")
            return False
    
    def update_company_info(self, **kwargs) -> None:
        """Actualiza información de la empresa"""
        company = self._config.setdefault("company_info", {})
        company.update(kwargs)
    
    def update_logo_path(self, new_path: str) -> None:
        """Actualiza la ruta del logo"""
        doc_settings = self._config.setdefault("document_settings", {})
        doc_settings["logo_path"] = new_path
    
    def update_footer_comments(self, comments_list: List[str]) -> None:
        """Actualiza los comentarios del pie de página"""
        quote_settings = self._config.setdefault("quote_settings", {})
        quote_settings["footer_comments"] = comments_list
    
    def update_include_iva(self, include_iva: bool) -> None:
        """Actualiza si se debe incluir IVA en el documento"""
        quote_settings = self._config.setdefault("quote_settings", {})
        quote_settings["include_iva"] = include_iva
    
    def update_iva_rate(self, iva_rate: float) -> None:
        """Actualiza la tasa de IVA"""
        quote_settings = self._config.setdefault("quote_settings", {})
        quote_settings["iva_rate"] = iva_rate
    
    def update_include_error_margin(self, include_error_margin: bool) -> None:
        """Actualiza si se debe incluir margen de error"""
        quote_settings = self._config.setdefault("quote_settings", {})
        quote_settings["include_error_margin"] = include_error_margin

    def update_include_post_processing(self, include_post_processing: bool) -> None:
        """Actualiza si se debe incluir post-procesado en comisión"""
        quote_settings = self._config.setdefault("quote_settings", {})
        quote_settings["include_post_processing"] = include_post_processing
    def convert_config_values(self, from_currency: str, to_currency: str, electricity_rate: float):
        """
        Convierte la tarifa eléctrica entre monedas
        
        Args:
            from_currency: Código de moneda origen (PYG, USD, etc.)
            to_currency: Código de moneda destino
            electricity_rate: Tarifa eléctrica actual
            
        Returns:
            electricity_rate convertida, o None si falla la conversión
        """
        try:
            from core.services.currency_conversion_service import CurrencyConversionService
            from core.utils.logger import VoxeprintLogger
            
            logger = VoxeprintLogger()
            converter = CurrencyConversionService()
            
            # Convertir tarifa eléctrica
            new_electricity = converter.convert_amount(electricity_rate, from_currency, to_currency)
            
            if new_electricity is None:
                logger.error(
                    "QuoteConfig",
                    f"Error - No se pudo convertir tarifa eléctrica de {from_currency} a {to_currency}. "
                    f"Verifique que exista la tasa de cambio en la base de datos."
                )
                return electricity_rate
            
            logger.info(
                "QuoteConfig",
                f"Conversión exitosa - Electricidad {electricity_rate} {from_currency} -> "
                f"{new_electricity} {to_currency}"
            )
            
            return new_electricity
            
        except Exception as e:
            from core.utils.logger import VoxeprintLogger
            logger = VoxeprintLogger()
            logger.log_exception("QuoteConfig", e, "convertir valores de configuración")
            return electricity_rate
    
    def update_currency_code(self, currency_code: str) -> None:
        """Áctualiza el código de moneda en la configuración"""
        quote_settings = self._config.setdefault("quote_settings", {})
        quote_settings["currency_code"] = currency_code
    
    def get_currency_code(self) -> str:
        """Obtiene el código de moneda actual"""
        return self.get_quote_settings().get("currency_code", "PYG")