"""
Generación de PDF de Presupuestos (Quote) usando reportlab.
Estilo profesional basado en OrdenTrabajoPDF.
"""
import os
from typing import Dict, Any
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from num2words import num2words
from core.utils.path_helper import pdfs_dir
from core.managers.quote_config_manager import QuoteConfigManager
from core.utils.currency_helper import CurrencyHelper
from core.utils.logger import logger
from core.managers.locale_manager import LocaleManager
from core.managers.language_manager import LanguageManager
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from application.dtos.quote_breakdown_dto import QuoteBreakdownResult


class QuotePDFManager:
    """Crea un PDF profesional con el desglose del presupuesto usando el estilo de OrdenTrabajoPDF."""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.config = QuoteConfigManager()
        self.width, self.height = A4
        self.page_number = 1
        
        # Registrar fuentes del sistema (multiplataforma)
        self._register_system_fonts()
        
        # Configuración desde JSON
        margins = self.config.get_margins()

        self.margen_x = margins.get('x', 30)  # 30 como fallback si no está en JSON
        self.top_margin_offset = margins.get('top_offset', 65)
        self.spacing_between_sections = margins.get('spacing_sections', 15)
        self.spacing_between_tables = margins.get('spacing_tables', 20)
        self.spacing_before_section_title = margins.get('spacing_before_title', 10)
        
        # Configuración de estilo
        colors_config = self.config.get_colors()
        self.styles_config = {
            "fonts": self.config.get_font_config(),
            "colors": {
                "primary": colors.HexColor(colors_config.get("primary", "#0070C0")),
                "accent": colors.HexColor(colors_config.get("accent", "#808080")),
                "text": colors.HexColor(colors_config.get("text", "#000000")),
                "table_header_bg": colors.HexColor(colors_config.get("table_header_bg", "#0070C0")),
                "table_header_text": colors.HexColor(colors_config.get("table_header_text", "#FFFFFF"))
            }
        }

    def _register_system_fonts(self):
        """
        Registra fuentes desde el sistema operativo (multiplataforma).
        No redistribuye fuentes, solo las usa si están disponibles en el sistema.
        
        Soporta:
        - Windows: C:\\Windows\\Fonts
        - Linux: /usr/share/fonts
        - macOS: /System/Library/Fonts, /Library/Fonts
        """
        import platform
        
        system = platform.system()
        self.registered_fonts = []
        
        # Configuración de fuentes por sistema operativo
        if system == 'Windows':
            self._register_windows_fonts()
        elif system == 'Darwin':  # macOS
            self._register_macos_fonts()
        elif system == 'Linux':
            self._register_linux_fonts()
        else:
            logger.warning("QuotePDFManager", f"Sistema {system} no soportado, usando Helvetica")
            self.current_font = 'Helvetica'
            return
        
        # Configurar fuente actual
        preferred_font = self.config.get_pdf_font_family()
        
        if preferred_font and preferred_font in self.registered_fonts:
            self.current_font = preferred_font
            logger.info("QuotePDFManager", f"Usando fuente: {self.current_font}")
        elif self.registered_fonts:
            self.current_font = self.registered_fonts[0]
            logger.info("QuotePDFManager", f"Usando fuente por defecto: {self.current_font}")
        else:
            self.current_font = 'Helvetica'
            logger.warning("QuotePDFManager", "No se encontraron fuentes del sistema, usando Helvetica")
    
    def _register_windows_fonts(self):
        """Registra fuentes de Windows desde C:\\Windows\\Fonts"""
        fonts_dir = r'C:\Windows\Fonts'
        
        # Mapeo de fuentes de Windows con sus archivos
        windows_fonts = {
            'Arial': {
                'regular': 'arial.ttf',
                'bold': 'arialbd.ttf',
                'italic': 'ariali.ttf',
                'bolditalic': 'arialbi.ttf'
            },
            'Calibri': {
                'regular': 'calibri.ttf',
                'bold': 'calibrib.ttf',
                'italic': 'calibrii.ttf',
                'bolditalic': 'calibriz.ttf'
            },
            'Segoe UI': {
                'regular': 'segoeui.ttf',
                'bold': 'segoeuib.ttf',
                'italic': 'segoeuii.ttf',
                'bolditalic': 'segoeuiz.ttf'
            },
            'Tahoma': {
                'regular': 'tahoma.ttf',
                'bold': 'tahomabd.ttf',
                'italic': 'tahoma.ttf',
                'bolditalic': 'tahomabd.ttf'
            }
        }
        
        self._register_font_family(fonts_dir, windows_fonts)
    
    def _register_macos_fonts(self):
        """Registra fuentes de macOS desde /System/Library/Fonts y /Library/Fonts"""
        # Intentar primero /System/Library/Fonts
        system_fonts_dir = '/System/Library/Fonts'
        library_fonts_dir = '/Library/Fonts'
        
        # Mapeo de fuentes de macOS
        macos_fonts = {
            'Helvetica': {
                'regular': 'Helvetica.ttc',
                'bold': 'Helvetica.ttc',
                'italic': 'Helvetica.ttc',
                'bolditalic': 'Helvetica.ttc'
            },
            'Arial': {
                'regular': 'Arial.ttf',
                'bold': 'Arial Bold.ttf',
                'italic': 'Arial Italic.ttf',
                'bolditalic': 'Arial Bold Italic.ttf'
            },
            'San Francisco': {
                'regular': 'SF-Pro-Display-Regular.otf',
                'bold': 'SF-Pro-Display-Bold.otf',
                'italic': 'SF-Pro-Display-RegularItalic.otf',
                'bolditalic': 'SF-Pro-Display-BoldItalic.otf'
            }
        }
        
        # Intentar ambos directorios
        for fonts_dir in [system_fonts_dir, library_fonts_dir]:
            if os.path.exists(fonts_dir):
                self._register_font_family(fonts_dir, macos_fonts)
                if self.registered_fonts:
                    break
    
    def _register_linux_fonts(self):
        """Registra fuentes de Linux desde /usr/share/fonts"""
        # Directorios comunes de fuentes en Linux
        fonts_dirs = [
            '/usr/share/fonts/truetype/liberation',
            '/usr/share/fonts/truetype/dejavu',
            '/usr/share/fonts/truetype/noto',
            '/usr/share/fonts/truetype'
        ]
        
        # Mapeo de fuentes de Linux (equivalentes a Windows)
        linux_fonts = {
            'Liberation Sans': {
                'regular': 'LiberationSans-Regular.ttf',
                'bold': 'LiberationSans-Bold.ttf',
                'italic': 'LiberationSans-Italic.ttf',
                'bolditalic': 'LiberationSans-BoldItalic.ttf'
            },
            'DejaVu Sans': {
                'regular': 'DejaVuSans.ttf',
                'bold': 'DejaVuSans-Bold.ttf',
                'italic': 'DejaVuSans-Oblique.ttf',
                'bolditalic': 'DejaVuSans-BoldOblique.ttf'
            },
            'Noto Sans': {
                'regular': 'NotoSans-Regular.ttf',
                'bold': 'NotoSans-Bold.ttf',
                'italic': 'NotoSans-Italic.ttf',
                'bolditalic': 'NotoSans-BoldItalic.ttf'
            }
        }
        
        # Intentar cada directorio hasta encontrar fuentes
        for fonts_dir in fonts_dirs:
            if os.path.exists(fonts_dir):
                self._register_font_family(fonts_dir, linux_fonts)
                if self.registered_fonts:
                    break
    
    def _register_font_family(self, fonts_dir, font_mapping):
        """
        Método auxiliar para registrar familias de fuentes desde un directorio.
        
        Args:
            fonts_dir: Directorio donde buscar las fuentes
            font_mapping: Diccionario con el mapeo de fuentes y sus variantes
        """
        for font_name, variants in font_mapping.items():
            try:
                regular_path = os.path.join(fonts_dir, variants['regular'])
                
                # Verificar que el archivo regular existe
                if not os.path.exists(regular_path):
                    continue
                
                # Registrar variante regular
                pdfmetrics.registerFont(TTFont(font_name, regular_path))
                
                # Registrar variante Bold
                bold_path = os.path.join(fonts_dir, variants['bold'])
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont(f'{font_name}-Bold', bold_path))
                
                # Registrar variante Italic (Oblique en ReportLab)
                italic_path = os.path.join(fonts_dir, variants['italic'])
                if os.path.exists(italic_path):
                    pdfmetrics.registerFont(TTFont(f'{font_name}-Oblique', italic_path))
                
                # Registrar variante Bold+Italic
                bi_path = os.path.join(fonts_dir, variants['bolditalic'])
                if os.path.exists(bi_path):
                    pdfmetrics.registerFont(TTFont(f'{font_name}-BoldOblique', bi_path))
                
                self.registered_fonts.append(font_name)
                logger.debug("QuotePDFManager", f"Fuente registrada: {font_name}")
                
            except Exception as e:
                logger.error("QuotePDFManager", f"No se pudo registrar {font_name}: {str(e)}")
    
    @staticmethod
    def get_available_fonts():
        """
        Obtiene lista de fuentes disponibles según el sistema operativo.
        Útil para poblar UI sin necesidad de instanciar QuotePDFManager.
        
        Returns:
            list: Lista de nombres de fuentes disponibles en el sistema
        """
        import platform
        
        system = platform.system()
        
        if system == 'Windows':
            return ['Arial', 'Calibri', 'Segoe UI', 'Tahoma']
        elif system == 'Darwin':  # macOS
            return ['Helvetica', 'Arial', 'San Francisco']
        elif system == 'Linux':
            return ['Liberation Sans', 'DejaVu Sans', 'Noto Sans']
        else:
            return ['Helvetica']

    def _format_printer_display(self, data: Dict[str, Any]) -> str:
        """
        Formatea la información de la impresora para mostrar como 'marca + modelo'
        en lugar de solo el nombre interno.
        """
        ctx = data.get("context", {})
        
        # Intentar obtener brand y model desde printer_info si está disponible
        printer_info = data.get("printer_info", {})
        if not printer_info:
            # Si no hay printer_info en data, buscar en other contexts
            # (esto puede pasar si se llama desde diferentes lugares)
            printer_info = {}
        
        brand = printer_info.get("brand", "").strip()
        model = printer_info.get("model", "").strip()
        printer_name = printer_info.get("name", ctx.get("printer_name", "")).strip()
        
        # Construir el display: priorizar "marca + modelo"
        if brand and model:
            return f"{brand} {model}"
        elif brand:
            return f"{brand} (modelo sin especificar)"
        elif model:
            return f"(marca sin especificar) {model}"
        elif printer_name:
            return printer_name
        else:
            return "N/A"

    def ensure_docs_dir(self) -> str:
        """
        Devuelve la ruta a Documentos/Voxeprint3D/PDF,
        creándola si no existe.
        """
        return str(pdfs_dir())

    def _draw_footer(self, c):
        """Pie de página estilo Nota de Precios.

        Banda gris (#F0F0F0) con línea superior (#CCCCCC) que ocupa todo
        el ancho de la página. Distribución de contenido:
          · Izquierda  → "Generado con Voxeprint"
          · Derecha    → teléfono  |  email  (desde BusinessParameters)
          · Encima del footer, centrado → solo el número de página (ej. "1")
        """
        from config.app_config import BusinessParameters

        FOOTER_H = 20          # altura de la banda en puntos
        FOOTER_Y = 0           # arranca en el borde inferior de la página
        TEXT_Y   = FOOTER_H / 2 - 3   # centrado vertical del texto dentro del footer

        # ── Número de página encima del footer, centrado ──────────────────────
        c.setFont(self.current_font, 8)
        c.setFillColor(self.styles_config["colors"]["accent"])
        c.drawCentredString(self.width / 2, FOOTER_H + 4, str(self.page_number))

        # ── Fondo gris ────────────────────────────────────────────────────────
        c.setFillColor(colors.HexColor("#F0F0F0"))
        c.rect(0, FOOTER_Y, self.width, FOOTER_H, fill=1, stroke=0)

        # ── Línea separadora superior ─────────────────────────────────────────
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.setLineWidth(0.8)
        c.line(0, FOOTER_H, self.width, FOOTER_H)
        c.setLineWidth(1)

        # ── Textos dentro del footer ──────────────────────────────────────────
        c.setFont(self.current_font, 7)
        c.setFillColor(colors.HexColor("#1A1A1A"))

        footer_text = tr(I18N.QuoteNote.FOOTER_GENERATED_WITH)
        try:
            _bp = BusinessParameters()
            if _bp.company_email:
                footer_text += f"  |  {_bp.company_email}"
        except Exception:
            pass

        c.drawCentredString(self.width / 2, TEXT_Y, footer_text)

        # ── Restaurar estado del canvas ───────────────────────────────────────
        c.setFillColor(self.styles_config["colors"]["text"])
        c.setStrokeColor(self.styles_config["colors"]["text"])
        c.setLineWidth(1)

    def _draw_horizontal_line(self, c, y, color=None, thickness=1, x_start=None, x_end=None):
        """Dibuja una línea horizontal"""
        if color is None:
            color = self.styles_config["colors"]["accent"]
        x_start = x_start if x_start is not None else self.margen_x
        x_end = x_end if x_end is not None else self.width - self.margen_x
        c.setStrokeColor(color)
        c.setLineWidth(thickness)
        c.line(x_start, y, x_end, y)
        c.setStrokeColor(self.styles_config["colors"]["text"])
        c.setLineWidth(1)

    def _draw_header(self, c, data: Dict[str, Any]):
        """Dibuja logo y datos de cabecera estilo OrdenTrabajoPDF"""
        company_info = self.config.get_company_info()
        logo_path = self.config.get_logo_path()
        
        # Logo más pequeño y a la izquierda para dar espacio al título
        logo_w, logo_h = 228, 66
        logo_top = self.height - 25
        title_top = self.height - 55

        # Logo con manejo robusto de errores
        if self.page_number == 1:
            try:
                logo_path = self.config.get_logo_path()
                
                # Si get_logo_path() retorna None, usar texto directamente
                if logo_path is None:
                    logger.info("QuotePDFManager", "Sin logo disponible - dibujando texto de empresa")
                    self._draw_company_text_fallback(c, company_info, logo_top, logo_h, logo_w)
                else:
                    # Intentar dibujar el logo
                    try:
                        logger.debug("QuotePDFManager", f"Intentando dibujar logo desde: {logo_path}")
                        c.drawImage(logo_path, self.margen_x, logo_top - logo_h, logo_w, logo_h,
                                   preserveAspectRatio=True, mask='auto')
                        logger.debug("QuotePDFManager", "Logo dibujado exitosamente")
                    except Exception as logo_error:
                        logger.error("QuotePDFManager", f"Error al dibujar logo: {logo_error}")
                        logger.info("QuotePDFManager", "Fallback: dibujando texto de empresa")
                        self._draw_company_text_fallback(c, company_info, logo_top, logo_h, logo_w)
                        
            except Exception as general_error:
                logger.error("QuotePDFManager", f"Error general en manejo de logo: {general_error}")
                logger.info("QuotePDFManager", "Fallback de emergencia: dibujando texto de empresa")
                self._draw_company_text_fallback(c, company_info, logo_top, logo_h, logo_w)

        # Título principal (configurable)
        font_header = self.styles_config["fonts"]["header"]
        c.setFont(font_header[0], font_header[1])
        title_x = self.width/2 + 10
        title_text = self.config.get_title()
        c.drawString(title_x, title_top, title_text)
        
        # Subtítulo (configurable) con letra más pequeña
        c.setFont(f"{self.current_font}", 12)
        subtitle_text = self.config.get_subtitle()
        c.drawString(title_x, title_top - 20, subtitle_text)
        
        # Información en paralelo (izquierda y derecha)
        font_body = self.styles_config["fonts"]["body"]
        c.setFont(font_body[0], font_body[1])
        
        left_x = self.margen_x
        right_x = self.width/2 + 10
        label_offset = 0
        field_offset_right = 100
        field_offset_left = field_offset_right - 20
        y_base = title_top - 50  # Ajustar para el nuevo título
        y_step = 15

        def kv(key, val, x, y, offset_label_x=0, offset_field_x=52):
            label_x = x + offset_label_x
            field_x = x + offset_field_x
            c.setFont(f"{self.current_font}-Bold", font_body[1])
            c.drawString(label_x, y, f"{key}:")
            c.setFont(font_body[0], font_body[1])
            c.drawString(field_x, y, str(val))
            # Línea solo para la zona derecha
            if x > self.width/2:
                self._draw_horizontal_line(c, y - 2, x_start=405, x_end=550, thickness=1)

        ctx = data.get("context", {})
        meta = data.get("meta", {})
        
        # Fila 1 (City y Quote # en la misma fila)
        kv(tr(I18N.QuotePDF.LABEL_QUOTE_NUMBER), meta.get("quote_number", "N/A"), right_x, y_base - y_step, label_offset, field_offset_right)
        # Fila 2  
        kv(tr(I18N.QuotePDF.LABEL_CITY), company_info.get("city", "N/A"), left_x, y_base - y_step, label_offset, field_offset_left)
        kv(tr(I18N.QuotePDF.LABEL_DATE), datetime.now().strftime(LocaleManager().get_date_format_strftime()), right_x, y_base - 2*y_step, label_offset, field_offset_right)
        # Fila 3
        kv(tr(I18N.QuotePDF.LABEL_ADDRESS), company_info.get("address", "N/A"), left_x, y_base - 2*y_step, label_offset, field_offset_left)
        # Fila 4
        kv(tr(I18N.QuotePDF.LABEL_PHONE), company_info.get("phone", "N/A"), left_x, y_base - 3*y_step, label_offset, field_offset_left)
        # Fila 5 (Email — solo si no está vacío)
        company_email = company_info.get("email", "").strip()
        if company_email:
            kv(tr(I18N.QuotePDF.LABEL_EMAIL), company_email, left_x, y_base - 4*y_step, label_offset, field_offset_left)
            return y_base - 4*y_step - 30


        return y_base - 3*y_step - 30

    def _draw_costs_table(self, c, start_y, data: Dict[str, Any]):
        """Dibuja la tabla de costos sin subtotales (IVA y total van abajo separados).
        
        Ahora solo renderiza el resultado del QuoteBreakdownService.
        """
        
        def money_no_currency(v):
            """Formato sin moneda para la tabla - respeta decimales según configuración de moneda"""
            try:
                amount = float(v) if v is not None else 0
                formatted = CurrencyHelper.format_with_current_currency(amount)
                import re
                no_symbol = re.sub(r'^[^\d\-]+', '', formatted).strip()
                return no_symbol
            except Exception:
                return "0"

        y = start_y
        y -= self.spacing_before_section_title
        
        # Título de la sección
        font_section = self.styles_config["fonts"]["section_title"]
        c.setFont(font_section[0], font_section[1])
        c.drawString(self.margen_x, y, tr(I18N.QuotePDF.SECTION_COSTS))
        y -= self.spacing_between_sections

        # Preparar datos de la tabla
        table_data = [
            [tr(I18N.QuoteNote.TABLE_COL_CONCEPT), tr(I18N.QuoteNote.TABLE_COL_AMOUNT)],  # Header
        ]

        # Obtener breakdown del servicio (si está disponible)
        breakdown = data.get("breakdown")

        if breakdown and isinstance(breakdown, QuoteBreakdownResult) and breakdown.lines:
            # El breakdown ya viene con el modo de visualización correcto aplicado.
            for line in breakdown.lines:
                table_data.append([line.label, money_no_currency(line.amount)])
        else:
            # Fallback: comportamiento legacy (mantener backward compatibility)
            amounts = data.get("amounts", {})
            cost_labels = self.config.get_cost_labels()
            include_error_margin = self.config.get_include_error_margin()
            include_post_processing = self.config.get_include_post_processing()
            failure_amount = amounts.get("failure", 0)
            wear_amount = amounts.get("wear", 0)
            commission_amount = amounts.get("commission", 0)
            post_processing_amount = amounts.get("post_processing", 0)
            
            base_costs = [
                ("material", cost_labels.get("material", "Costo de Material")),
                ("electricity", cost_labels.get("electricity", "Costo de Energía")),
            ]
            
            if include_error_margin and failure_amount > 0:
                combined_wear = wear_amount + failure_amount
                base_costs.append(("wear_combined", cost_labels.get("wear", "Costo de Operación")))
                for key, label in base_costs[:-1]:
                    value = amounts.get(key, 0)
                    table_data.append([label, money_no_currency(value)])
                table_data.append([cost_labels.get("wear", "Costo de Operación"), money_no_currency(combined_wear)])
            else:
                base_costs.extend([
                    ("wear", cost_labels.get("wear", "Costo de Operación")),
                    ("failure", cost_labels.get("failure", "Margen de Error"))
                ])
                for key, label in base_costs:
                    value = amounts.get(key, 0)
                    if key == "failure" and value == 0:
                        continue
                    table_data.append([label, money_no_currency(value)])
            
            combined_commission = commission_amount
            if include_post_processing and post_processing_amount > 0:
                combined_commission += post_processing_amount
            if combined_commission > 0:
                table_data.append([cost_labels.get("commission", "Comisión"), money_no_currency(combined_commission)])
            if not include_post_processing and post_processing_amount > 0:
                table_data.append([cost_labels.get("post_processing", "Post-Procesado"), money_no_currency(post_processing_amount)])

        # Calcular ancho total disponible para la tabla (hasta el margen derecho)
        total_table_width = self.width - 2*self.margen_x  # 595 - (45*2) = 505 puntos
        
        # Ajustar anchos de columnas para que llegue hasta el margen derecho
        monto_width = 120  # Un poco más ancho para números
        concepto_width = total_table_width - monto_width  # El resto para concepto
        col_widths = [concepto_width, monto_width]
        
        table = Table(table_data, colWidths=col_widths)
        
        table_style = TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), self.styles_config["colors"]["table_header_bg"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), self.styles_config["colors"]["table_header_text"]),
            ("FONTNAME", (0, 0), (-1, 0), f"{self.current_font}-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),  # Centrar solo "Monto" en header
            
            # Body
            ("FONTNAME", (0, 1), (-1, -1), self.current_font),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),  # Números a la derecha
            
            # Bordes
            ("BOX", (0, 0), (-1, -1), 1, self.styles_config["colors"]["text"]),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, self.styles_config["colors"]["accent"]),
        ])
        
        table.setStyle(table_style)
        
        # Calcular posición y dibujar
        table_width, table_height = table.wrap(self.width - 2*self.margen_x, y)
        table.drawOn(c, self.margen_x, y - table_height)
        
        return y - table_height - 10

    def _draw_company_text_fallback(self, c, company_info, logo_top, logo_h, logo_w):
        """Dibuja texto de la empresa cuando no hay logo disponible"""
        try:
            # Dibujar rectángulo con borde
            c.setStrokeColor(self.styles_config["colors"]["accent"])
            c.setLineWidth(1)
            c.rect(self.margen_x, logo_top - logo_h, logo_w, logo_h)
            
            # Texto centrado en lugar del logo
            c.setFont(*self.styles_config["fonts"]["header"])
            c.setFillColor(self.styles_config["colors"]["text"])
            company_name = company_info.get("name", "VOXEPRINT")
            
            # Centrar el texto tanto horizontal como verticalmente
            text_x = self.margen_x + logo_w/2
            text_y = logo_top - logo_h/2
            c.drawCentredString(text_x, text_y, company_name)
            
            # Restaurar color por defecto
            c.setFillColor(self.styles_config["colors"]["text"])
            c.setStrokeColor(self.styles_config["colors"]["text"])
            c.setLineWidth(1)
            
        except Exception as e:
            logger.error("QuotePDFManager", f"Error al dibujar texto de empresa: {e}")
            # Fallback mínimo: solo el rectángulo
            try:
                c.rect(self.margen_x, logo_top - logo_h, logo_w, logo_h)
            except:
                pass  # Si hasta esto falla, al menos no crashea

    def _draw_customer_section(self, c, start_y, customer_info: dict):
        """Dibuja la sección de información del cliente"""
        y = start_y
        y -= self.spacing_before_section_title
        
        # Título de la sección
        font_section = self.styles_config["fonts"]["section_title"]
        c.setFont(font_section[0], font_section[1])
        c.drawString(self.margen_x, y, tr(I18N.QuotePDF.SECTION_CUSTOMER))
        y -= self.spacing_between_sections

        # Preparar datos de la tabla del cliente
        table_data = [
            [tr(I18N.QuotePDF.TABLE_COL_FIELD), tr(I18N.QuotePDF.TABLE_COL_INFO)],  # Header
            [tr(I18N.QuotePDF.LABEL_FULL_NAME), customer_info.get('full_name', 'No disponible')],
            [LocaleManager().get_tax_id_label(), customer_info.get('ruc_ci', 'No disponible')],
            [tr(I18N.QuotePDF.LABEL_PHONE), customer_info.get('phone_number', 'No disponible')],
            [tr(I18N.QuotePDF.LABEL_EMAIL), customer_info.get('email', 'No disponible')]
        ]

        # Calcular ancho total disponible para la tabla
        total_table_width = self.width - 2*self.margen_x
        
        # Ajustar anchos de columnas: campo más estrecho, información más ancha
        campo_width = 120
        info_width = total_table_width - campo_width
        col_widths = [campo_width, info_width]
        
        table = Table(table_data, colWidths=col_widths)
        
        table_style = TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), self.styles_config["colors"]["table_header_bg"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), self.styles_config["colors"]["table_header_text"]),
            ("FONTNAME", (0, 0), (-1, 0), f"{self.current_font}-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),  # Alinear "Campo" a la izquierda en header
            ("ALIGN", (1, 0), (1, 0), "CENTER"),  # Centrar "Información" en header
            
            # Body
            ("FONTNAME", (0, 1), (-1, -1), self.current_font),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),   # Campo a la izquierda
            ("ALIGN", (1, 1), (1, -1), "LEFT"),   # Información a la izquierda
            
            # Bordes
            ("BOX", (0, 0), (-1, -1), 1, self.styles_config["colors"]["text"]),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, self.styles_config["colors"]["accent"]),
        ])
        
        table.setStyle(table_style)
        
        # Calcular posición y dibujar
        table_width, table_height = table.wrap(self.width - 2*self.margen_x, y)
        table.drawOn(c, self.margen_x, y - table_height)
        
        return y - table_height - self.spacing_between_tables

    def _draw_quantity_details(self, c, start_y, amounts, quantity_info):
        """Dibuja información discreta de cantidad y costo unitario cuando hay más de 1 lote"""
        quantity = quantity_info.get('quantity', 1)
        
        # Solo mostrar si hay más de 1 lote
        if quantity <= 1:
            return start_y
        
        total = amounts.get('total', 0)
        cost_per_batch = total / quantity if quantity > 0 else 0
        
        def money_with_currency(v):
            """Formato con moneda actual"""
            try:
                amount = float(v) if v is not None else 0
                return CurrencyHelper.format_with_current_currency(amount)
            except Exception:
                return CurrencyHelper.format_with_current_currency(0)
        
        y = start_y
        y -= 1  # Espacio mínimo antes del bloque
        
        # Información discreta en una sola línea con cursiva
        c.setFont(f"{self.current_font}-Oblique", 9)  # Fuente cursiva y más pequeña
        c.setFillColor(self.styles_config["colors"]["accent"])
        
        # Texto combinado en una línea: Cantidad + Costo unitario
        info_text = tr(I18N.QuotePDF.QUANTITY_DETAIL_FMT, quantity=quantity, cost=money_with_currency(cost_per_batch))
        c.drawString(self.margen_x, y, info_text)
        
        # Restaurar color de texto normal
        c.setFillColor(self.styles_config["colors"]["text"])
        
        return y - 8  # Espacio mínimo después

    def _draw_totals_block(self, c, start_y, amounts, breakdown=None):
        """Dibuja totales exactamente como en document_manager.py.
        
        Ahora puede usar breakdown del servicio en lugar de amounts.
        """
        # Recargar configuración para asegurar valores actualizados
        self.config.reload_config()
        
        def money_with_currency(v):
            """Formato con moneda actual para totales finales"""
            try:
                amount = float(v) if v is not None else 0
                return CurrencyHelper.format_with_current_currency(amount)
            except Exception:
                return CurrencyHelper.format_with_current_currency(0)

        # Obtener tax y total del breakdown si está disponible
        if breakdown and isinstance(breakdown, QuoteBreakdownResult):
            iva = breakdown.tax_amount
            total = breakdown.total_amount
        else:
            iva = amounts.get('tax', 0)
            total = amounts.get('total', 0)
        
        # Total en letras - usa num2words(to='currency') con el idioma activo de la app.
        # Si la combinación idioma+moneda no está soportada, intenta con 'es' como fallback.
        # Si tampoco funciona, omite la línea (total_en_letras = None).
        #
        # Sufijos legales por moneda para documentos comerciales:
        #   MXN → "M.N."  (Moneda Nacional, uso oficial en México)
        #   Resto → código ISO de 3 letras (evita ambigüedad con el símbolo $)
        _LEGAL_SUFFIX = {'MXN': 'M.N.'}
        # Conector que usa num2words para separar entero de centavos según idioma
        _LANG_CONNECTOR = {
            'es': ' con ', 'en': ' and ', 'pt': ' e ',
            'pt_BR': ' e ', 'pt_PT': ' e ', 'de': ' und ',
            'fr': ' et ', 'it': ' e ',
        }

        def _total_a_letras(amount, lang, currency):
            if currency == 'PYG':
                total_entero = int(round(amount))
                texto = num2words(total_entero, lang=lang)
                moneda = 'guaraníes' if total_entero != 1 else 'guaraní'
                return texto.capitalize() + f" {moneda}"

            # Monedas con decimales: formato "Palabras con XX/100 SUFIJO"
            config = CurrencyHelper._get_currency_config(currency)
            decimals = config.get('decimals', 2)
            suffix = _LEGAL_SUFFIX.get(currency, currency)

            full_text = num2words(amount, lang=lang, to='currency', currency=currency)
            if decimals > 0:
                connector = _LANG_CONNECTOR.get(lang, ' con ')
                factor = 10 ** decimals
                entero = int(amount)
                fraccion = round((amount - entero) * factor)
                if connector in full_text:
                    integer_words = full_text.split(connector, 1)[0]
                    return f"{integer_words.capitalize()} {connector.strip()} {fraccion:02d}/100 {suffix}"
            return full_text.capitalize()

        try:
            current_currency = CurrencyHelper.get_current_currency()
            idioma = LanguageManager().current_language()

            # Para locales con idioma propio (BR→pt_BR, PT→pt_PT), usar su num2words nativo
            _LOCALE_LANG_OVERRIDE = {'BR': 'pt_BR', 'PT': 'pt_PT'}
            current_locale = LocaleManager().current_locale()
            preferred_lang = _LOCALE_LANG_OVERRIDE.get(current_locale, idioma)

            try:
                total_en_letras = _total_a_letras(total, preferred_lang, current_currency)
            except Exception:
                try:
                    total_en_letras = _total_a_letras(total, 'es', current_currency)
                except Exception:
                    total_en_letras = None
        except Exception:
            total_en_letras = None  # Moneda no soportada en ningún idioma → omitir línea
        
        # Calcular posición Y para la línea del total (misma línea para ambos elementos)
        total_line_y = start_y - 20
        
        # TOTAL IVA (solo si está habilitado en configuración) - línea superior
        if self.config.get_include_iva():
            iva_rate = self.config.get_iva_rate()
            # Formatear IVA rate como entero si no tiene decimales significativos
            iva_rate_formatted = f"{int(iva_rate)}" if iva_rate.is_integer() else f"{iva_rate:.1f}"
            c.setFont(self.current_font, 9)
            c.drawRightString(self.width - self.margen_x, total_line_y + 15,
                             tr(I18N.QuotePDF.TOTAL_IVA_FMT, rate=iva_rate_formatted, amount=money_with_currency(iva)))
        
        # TOTAL en negrita (lado derecho) - línea principal
        c.setFont(f"{self.current_font}-Bold", 10)
        c.drawRightString(self.width - self.margen_x, total_line_y,
                         tr(I18N.QuotePDF.LABEL_TOTAL_FMT, amount=money_with_currency(total)))
        
        # Total en letras (línea inferior) - se omite si el idioma no está soportado por num2words
        if total_en_letras is not None:
            total_en_letras_y = total_line_y - 15  # Una línea más abajo
            label = tr(I18N.QuotePDF.LABEL_TOTAL_IN_WORDS)
            font_body = self.styles_config["fonts"]["body"]
            
            c.setFont(f"{self.current_font}-Bold", font_body[1])
            c.drawString(self.margen_x, total_en_letras_y, label)
            c.setFont(self.current_font, font_body[1])
            
            # Posición del texto en letras después del label
            label_width = c.stringWidth(label)
            total_en_letras_x = self.margen_x + label_width + 10
            c.drawString(total_en_letras_x, total_en_letras_y, total_en_letras)
        
        # Calcular el retorno dinámico basado en si se mostró IVA o no
        if self.config.get_include_iva():
            return start_y - 60  # Ajustado para la nueva disposición
        else:
            return start_y - 40  # Menos espacio cuando no hay IVA

    def _draw_advance_section(self, c, start_y, amounts, advance_data):
        """Dibuja la sección de plan de pagos cuando el anticipo está habilitado"""
        if not advance_data or not advance_data.get('enabled', False):
            return start_y
        
        percentage = advance_data.get('percentage', 30)
        total = amounts.get('total', 0)
        advance_amount = (total * percentage) / 100
        remaining_amount = total - advance_amount
        
        def money_with_currency(v):
            """Formato con moneda actual"""
            try:
                amount = float(v) if v is not None else 0
                return CurrencyHelper.format_with_current_currency(amount)
            except Exception:
                return CurrencyHelper.format_with_current_currency(0)
        
        # Espacio antes de la sección (mínimo para estar muy cerca del total)
        section_start_y = start_y + 5
        
        # Título de la sección
        c.setFont(f"{self.current_font}-Bold", 10)
        c.setFillColor(self.styles_config["colors"]["text"])
        c.drawString(self.margen_x, section_start_y - 12, tr(I18N.QuotePDF.SECTION_PAYMENT_PLAN))
        
        # Línea separadora superior
        self._draw_horizontal_line(c, section_start_y - 16, color=self.styles_config["colors"]["primary"], thickness=1)
        
        # Información del anticipo
        c.setFont(f"{self.current_font}-Bold", 9)
        c.setFillColor(self.styles_config["colors"]["text"])
        
        # Anticipo
        c.drawString(self.margen_x, section_start_y - 28, tr(I18N.QuoteNote.LABEL_ADVANCE_PCT_FMT, pct=percentage))
        right_x = self.width - self.margen_x
        c.drawRightString(right_x, section_start_y - 28, money_with_currency(advance_amount))
        
        # Descripción del anticipo (en fuente normal y más pequeña)
        c.setFont(self.current_font, 8)
        c.setFillColor(self.styles_config["colors"]["accent"])
        c.drawString(self.margen_x + 15, section_start_y - 38, tr(I18N.QuotePDF.ADVANCE_START_DESC))
        
        # Saldo pendiente
        c.setFont(f"{self.current_font}-Bold", 9)
        c.setFillColor(self.styles_config["colors"]["text"])
        c.drawString(self.margen_x, section_start_y - 52, tr(I18N.QuotePDF.LABEL_BALANCE))
        c.drawRightString(right_x, section_start_y - 52, money_with_currency(remaining_amount))
        
        # Descripción del saldo (en fuente normal y más pequeña)
        c.setFont(self.current_font, 8)
        c.setFillColor(self.styles_config["colors"]["accent"])
        c.drawString(self.margen_x + 15, section_start_y - 62, tr(I18N.QuotePDF.BALANCE_DELIVERY_DESC))
        
        # Línea separadora inferior
        bottom_line_y = section_start_y - 72
        self._draw_horizontal_line(c, bottom_line_y, color=self.styles_config["colors"]["primary"], thickness=1)
        
        # ✅ IMPORTANTE: Restablecer color de texto para secciones siguientes
        c.setFillColor(self.styles_config["colors"]["text"])
        
        return bottom_line_y - 15  # Espacio después de la sección (reducido)

    def _draw_footer_comments(self, c, start_y):
        """Dibuja comentarios del pie de página"""
        comments = self.config.get_footer_comments()
        if not comments:
            return start_y
        
        padding_top = 16
        line_height = 10
        padding_bottom = 10
        block_h = padding_top + len(comments) * line_height + padding_bottom
        
        # Verificar si hay espacio
        if start_y - block_h < 80:
            self._draw_footer(c)
            c.showPage()
            self.page_number += 1
            start_y = self.height - self.top_margin_offset
        
        c.setStrokeColor(self.styles_config["colors"]["text"])
        c.rect(self.margen_x, start_y - block_h, self.width - 2*self.margen_x, block_h)
        
        c.setFont(f"{self.current_font}-Bold", 8)
        c.drawString(self.margen_x + 5, start_y - 10, tr(I18N.QuotePDF.SECTION_CONDITIONS))
        
        font_comments = self.styles_config["fonts"]["comments"]
        c.setFont(font_comments[0], font_comments[1])
        for i, txt in enumerate(comments):
            c.drawString(self.margen_x + 5, start_y - (25 + i*10), f"• {txt}")
        
        return start_y - block_h - 20

    def generate(self, output_path: str, data: Dict[str, Any]) -> str:
        """
        Genera el PDF con los datos del presupuesto.
        data requiere, al menos:
          - context: {printer_name, filament_name, project_name?}
          - amounts: dict con keys: material, electricity, wear, failure, subtotal_with_margin, commission, tax, total
          - meta: dict opcional {quote_number, created_at}
        """
        try:
            # Recargar configuración para asegurar valores actualizados
            self.config.reload_config()

            # Aplicar color primario del PDF si está configurado
            pdf_cfg = self.config.get_pdf_settings()
            _override_color = (pdf_cfg.get("primary_color") or "").strip()
            if _override_color:
                from reportlab.lib.colors import HexColor as _HexColor
                _c = _HexColor(_override_color)
                self.styles_config["colors"]["primary"] = _c
                self.styles_config["colors"]["table_header_bg"] = _c

            c = canvas.Canvas(output_path, pagesize=A4)
            
            # Header
            y = self._draw_header(c, data)
            
            # Sección de cliente (solo si hay información del cliente)
            customer_info = data.get('customer_info')
            if customer_info:
                y = self._draw_customer_section(c, y, customer_info)
            
            # Tabla de costos (sin totales)
            y = self._draw_costs_table(c, y, data)
            
            # Obtener amounts para usar en las siguientes secciones
            amounts = data.get("amounts", {})
            
            # Sección de detalles por cantidad (solo si quantity > 1)
            quantity_info = data.get('quantity_info')
            if quantity_info:
                y = self._draw_quantity_details(c, y, amounts, quantity_info)
            
            # Totales exactamente como document_manager
            breakdown = data.get("breakdown")
            y = self._draw_totals_block(c, y, amounts, breakdown)
            
            # Sección de anticipo (si está habilitado)
            advance_data = data.get('advance_info')
            if advance_data:
                y = self._draw_advance_section(c, y, amounts, advance_data)
            
            # Comentarios del pie
            y = self._draw_footer_comments(c, y)
            
            # Pie de página
            self._draw_footer(c)
            
            c.save()
            return output_path
            
        except Exception as e:
            logger.log_exception("QuotePDFManager", e, "generate")
            # Generar PDF de error simple
            return self._generate_error_pdf(output_path)

    def _truncate_text_to_fit(self, c, text, available_width):
        """Trunca el texto para que quepa en el ancho disponible, agregando '...' al final"""
        if c.stringWidth(text) <= available_width:
            return text
        
        # Reducir texto carácter por carácter hasta que quepa con "..."
        ellipsis = "..."
        ellipsis_width = c.stringWidth(ellipsis)
        
        for i in range(len(text) - 1, 0, -1):
            truncated = text[:i] + ellipsis
            if c.stringWidth(truncated) <= available_width:
                return truncated
        
        # Si ni siquiera "..." cabe, retornar string vacío
        return "" if ellipsis_width > available_width else ellipsis

    def _generate_error_pdf(self, output_path: str) -> str:
        """Genera un PDF de error si falla la generación principal"""
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Mensaje de error centrado
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.red)
        c.drawCentredString(width / 2, height / 2, "ERROR AL GENERAR PRESUPUESTO")
        
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, height / 2 - 30, "No se pudieron procesar los datos del presupuesto.")
        c.drawCentredString(width / 2, height / 2 - 50, "Por favor, contacte al soporte técnico.")
        
        c.save()
        return output_path