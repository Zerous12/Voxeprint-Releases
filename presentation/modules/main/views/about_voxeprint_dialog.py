"""
Diálogo "Acerca de Voxeprint" con efecto de créditos animados optimizado
Integrado con UI de Qt Designer
Utiliza buffer QPixmap 2x para scroll ultra-suave y alta calidad
"""

import os
import webbrowser
from PySide6.QtWidgets import QDialog, QWidget, QApplication, QToolTip
from PySide6.QtCore import Qt, Signal, QTimer, QUrl, QPoint, QTimeLine, QElapsedTimer, QSize
from PySide6.QtGui import QFont, QPainter, QLinearGradient, QColor, QCursor, QClipboard, QDesktopServices, QIcon

from config.build_config import BUILD_CONFIG
from core.utils.logger import logger
from core.managers.theme_manager import PaletteManager
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from presentation.common.icon_utils import IconUtils
from presentation.modules.main.designs.about_ui import Ui_Dialog_About


class AboutVoxeprintDialog(QDialog):
    """
    Diálogo "Acerca de Voxeprint" con créditos animados estilo AIMP
    Utiliza UI generada por Qt Designer
    Optimizado con buffer QPixmap 2x para máxima calidad y suavidad
    """
    
    # Señales
    github_profile_requested = Signal()
    license_requested = Signal()
    changelog_requested = Signal()
    check_updates_requested = Signal()  # Nueva señal para buscar actualizaciones
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurar UI generada
        self.ui = Ui_Dialog_About()
        self.ui.setupUi(self)
        
        # Configurar ventana
        self.setWindowTitle(tr(I18N.About.DIALOG_TITLE))
        self.setModal(True)
        
        # Widget de créditos animados
        self.credits_widget = None
        
        # Información de contacto
        self.author_email = "zerous12@example.com"  # Se actualizará con build_config
        
        # Detectar tema actual
        self.theme_manager = PaletteManager()
        self.is_dark_mode = self.theme_manager.is_dark_mode
        
        # Timer para desbloqueador del botón después de cooldown
        self._unblock_timer = QTimer()
        self._unblock_timer.setSingleShot(False)
        self._unblock_timer.timeout.connect(self._update_blocked_countdown)
        self._blocked_remaining_seconds = 0
        
        self._setup_ui_functionality()
        self._load_build_info()
        self._connect_signals()
    
    def _setup_ui_functionality(self):
        """Configura la funcionalidad de los widgets de UI"""

        # Sobrescribir textos del retranslateUi con el sistema de traducción propio
        self.ui.label_autor.setText(tr(I18N.About.LABEL_AUTOR))
        self.ui.label_contact.setText(tr(I18N.About.LABEL_CONTACT))
        self.ui.label_license.setText(tr(I18N.About.LABEL_LICENSE))
        self.ui.label_worklog.setText(tr(I18N.About.LABEL_WORKLOG))
        self.ui.btn_close_about.setText(tr(I18N.About.BTN_CLOSE))
        self.ui.btn_search_updates.setText(tr(I18N.About.BTN_SEARCH_UPDATES))

        # Configurar el frame_credits con el color correcto
        self.ui.frame_credits.setStyleSheet("#frame_credits { background-color: #5a5a5a; border: none; }")
        
        # ===== CONFIGURAR ÍCONO DEL BOTÓN SEARCH UPDATES =====
        # Recolorear según el tema
        icon_path = ":/resources/resources/icons/sys_refresh_alt_fat.svg"
        if self.is_dark_mode:
            # En tema oscuro, cargar directamente (SVG ya es blanco)
            search_icon = QIcon()
            search_icon.addFile(icon_path, QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        else:
            # En tema claro, recolorear a negro para que sea visible
            try:
                search_icon = IconUtils.recolor_icon_svg(icon_path, "#000000")
            except Exception:
                # Fallback: cargar icono sin recolorear
                search_icon = QIcon()
                search_icon.addFile(icon_path, QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        
        self.ui.btn_search_updates.setIcon(search_icon)
        
        # ===== CONFIGURAR WIDGET DE CRÉDITOS =====
        # Aplicar la funcionalidad de scroll directamente al scroll_widget existente
        if self.ui.scroll_widget:
            # Configurar para que use el fondo del frame padre
            self.ui.scroll_widget.setAutoFillBackground(False)
            
            # Agregar las propiedades y métodos de scroll al widget existente
            self._setup_scrolling_functionality(self.ui.scroll_widget)
            
            # El scroll_widget ahora ES el credits_widget
            self.credits_widget = self.ui.scroll_widget
        
        # ===== CONFIGURAR LABELS CLICKEABLES =====
        
        # Label de email clickeable (copia al portapapeles)
        self._make_label_clickeable(
            self.ui.label_autor_mail,
            tooltip=tr(I18N.About.TOOLTIP_COPY_EMAIL),
            click_handler=self._copy_email_to_clipboard
        )
        
        # Labels de navegación clickeables
        self._make_label_clickeable(
            self.ui.label_license,
            tooltip=tr(I18N.About.TOOLTIP_LICENSE),
            click_handler=self.license_requested.emit
        )
        
        self._make_label_clickeable(
            self.ui.label_worklog,
            tooltip=tr(I18N.About.TOOLTIP_CHANGELOG),
            click_handler=self.changelog_requested.emit
        )
        
        # ===== CONFIGURAR BOTONES =====
        # Solo configurar btn_close_about, btn_github mantiene su tamaño del UI
        self.ui.btn_close_about.setFixedHeight(30)
        self.ui.btn_close_about.setFixedWidth(105)
       
    
    def _setup_scrolling_functionality(self, widget):
        """Configura la funcionalidad de scroll usando buffer QPixmap (método AIMP)"""
        
        # Propiedades de scroll
        widget.credits_content = []
        widget.scroll_speed = 25.0  # píxeles por segundo
        widget.is_scrolling = True
        widget.offset_y = 0.0  # Desplazamiento actual en el buffer
        widget.total_content_height = 0.0
        widget.buffer = None  # QPixmap buffer (se crea después)
        widget.bg_color = QColor("#5a5a5a")  # Color de fondo del frame
        widget.timer = QElapsedTimer()
        widget.timer.start()

        # Timer para animación con precisión
        widget.animation_timer = QTimer()
        widget.animation_timer.setTimerType(Qt.TimerType.PreciseTimer)
        widget.animation_timer.timeout.connect(lambda: self._update_scroll_buffer(widget))
        widget.animation_timer.start(16)  # 60 FPS
        
        # Reemplazar paintEvent para usar buffer
        widget.paintEvent = lambda event: self._paint_scroll_buffer(widget, event)
        
        # Configurar para que use el fondo del padre
        widget.setAutoFillBackground(False)
    
    def _update_scroll_buffer(self, widget):
        """Actualiza el offset del buffer (método ultra-suave)"""
        if not widget.is_scrolling:
            return

        # Calcular delta time
        elapsed_ms = widget.timer.restart()
        delta = (elapsed_ms / 1000.0) * widget.scroll_speed
        widget.offset_y += delta

        # Reiniciar cuando llegue al final (considerar escala del buffer)
        if hasattr(widget, 'buffer') and widget.buffer and hasattr(widget, 'scale_factor'):
            buffer_logical_height = widget.buffer.height() / widget.scale_factor
            if widget.offset_y >= buffer_logical_height - widget.height():
                widget.offset_y = 0.0

        widget.update()
    
    def _build_credit_buffer(self, widget):
        """Construye el buffer QPixmap con todo el contenido (UNA SOLA VEZ) en alta resolución"""
        # Calcular altura total del buffer
        total_height = int(widget.total_content_height) + widget.height() * 2
        width = widget.width()
        
        # Factor de escalado para alta calidad (2x = Retina quality)
        scale_factor = 2.0
        widget.scale_factor = scale_factor
        
        # Crear pixmap buffer en alta resolución con el color de fondo correcto
        from PySide6.QtGui import QPixmap
        widget.buffer = QPixmap(int(width * scale_factor), int(total_height * scale_factor))
        widget.buffer.fill(widget.bg_color)
        
        # Pintar TODO el contenido en el buffer con alta calidad
        painter = QPainter(widget.buffer)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Empezar desde abajo del widget (escalado)
        y_pos = float(widget.height()) * scale_factor
        
        for item in widget.credits_content:
            if item["type"] == "space":
                y_pos += item["height"] * scale_factor
                continue
            
            # Configurar fuente (escalada)
            font = QFont()
            font.setPointSize(int(item["size"] * scale_factor))
            font.setBold(item.get("bold", False))
            painter.setFont(font)
            
            # Obtener métricas para descenders
            from PySide6.QtGui import QFontMetrics
            metrics = QFontMetrics(font)
            text_height = float(metrics.height())
            text_descent = float(metrics.descent())
            
            # Color
            color = QColor(item.get("color", "#B36E6E"))
            painter.setPen(color)
            
            # Dibujar texto con altura correcta (escalado)
            from PySide6.QtCore import QRectF
            draw_height = text_height + text_descent + 4.0
            painter.drawText(QRectF(10.0 * scale_factor, y_pos, float(width - 20) * scale_factor, draw_height),
                           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, 
                           item["text"])
            
            y_pos += self._get_item_height(item) * scale_factor
        
        painter.end()
    
    def _paint_scroll_buffer(self, widget, event):
        """Dibuja el buffer con desplazamiento (ULTRA RÁPIDO) en alta calidad"""
        # Construir buffer si no existe
        if not hasattr(widget, 'buffer') or widget.buffer is None:
            self._build_credit_buffer(widget)
        
        painter = QPainter(widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Calcular rectángulo fuente (qué parte del buffer dibujar) - escalado
        from PySide6.QtCore import QRect
        scale = widget.scale_factor
        src_rect = QRect(0, int(widget.offset_y * scale), 
                        int(widget.width() * scale), 
                        int(widget.height() * scale))
        
        # Dibujar la porción del buffer en el widget (escala de vuelta al tamaño normal)
        painter.drawPixmap(widget.rect(), widget.buffer, src_rect)
        
        # Aplicar gradientes de fade directamente con el color de fondo
        from PySide6.QtCore import QPoint
        
        # Fade superior: color de fondo (oculta) → transparente (muestra texto)
        gradient_top = QLinearGradient(QPoint(0, 0), QPoint(0, 50))
        gradient_top.setColorAt(0, widget.bg_color)                    # Opaco arriba
        gradient_top.setColorAt(1, QColor(widget.bg_color.red(), 
                                          widget.bg_color.green(), 
                                          widget.bg_color.blue(), 0))  # Transparente abajo
        painter.fillRect(QRect(0, 0, widget.width(), 50), gradient_top)
        
        # Fade inferior: transparente (muestra texto) → color de fondo (oculta)
        # Extendemos 1 píxel extra para cubrir completamente el borde
        gradient_bottom = QLinearGradient(QPoint(0, widget.height() - 50), QPoint(0, widget.height() + 1))
        gradient_bottom.setColorAt(0, QColor(widget.bg_color.red(), 
                                              widget.bg_color.green(), 
                                              widget.bg_color.blue(), 0))  # Transparente arriba
        gradient_bottom.setColorAt(1, widget.bg_color)                     # Opaco abajo
        painter.fillRect(QRect(0, widget.height() - 50, widget.width(), 51), gradient_bottom)
    
    def _get_item_height(self, item):
        """Calcula la altura de un elemento de crédito - retorna float para precisión sub-pixel"""
        if item["type"] == "space":
            return float(item["height"])
        elif item["type"] in ["title", "subtitle", "section", "text", "credit"]:
            return float(item["size"] + 6)  # Tamaño de fuente + espaciado reducido
        return 15.0
    
    def _make_label_clickeable(self, label, tooltip: str, click_handler):
        """Hace que un QLabel sea clickeable con estilo visual (misma lógica que main_window.py)"""
        try:
            # Establecer cursor de mano
            label.setCursor(QCursor(Qt.PointingHandCursor))
            
            # Actualizar tooltip
            label.setToolTip(tooltip)
            
            # Aplicar estilo para indicar que es clickeable (mismo color que main_window)
            original_style = label.styleSheet()
            clickable_style = """
                QLabel:hover {
                    color: #e2e200;
                }
            """
            label.setStyleSheet(f"{original_style}\n{clickable_style}")
            
            # Asignar manejador de click - DESPUÉS de soltar el click
            def mouse_release_event(event):
                if event.button() == Qt.LeftButton:
                    click_handler()
            
            label.mouseReleaseEvent = mouse_release_event
            
        except Exception as e:
            logger.error("AboutDialog", f"Error haciendo label clickeable: {e}")
    
    def _load_build_info(self):
        """Carga información de build desde build_config"""
        try:
            from config.build_config import get_formatted_version_build, get_full_version, BUILD_CONFIG, TeamParameters
            
            # Crear instancia del equipo
            team = TeamParameters()
            
            # Actualizar información de versión y build
            version_text = get_formatted_version_build()
            self.ui.label_version_build.setText(version_text)
            
            # Actualizar información de bit y fecha
            platform_info = f"{BUILD_CONFIG.build.architecture}-bit ({BUILD_CONFIG.app.release_date})"
            self.ui.label_bit_date.setText(platform_info)
            
            # Actualizar información de autor
            self.ui.label_autor_name.setText(BUILD_CONFIG.app.author)
            self.author_email = BUILD_CONFIG.app.contact_email
            self.ui.label_autor_mail.setText(self.author_email)
            
            # Configurar información para créditos animados
            if self.credits_widget:
                about_info = {
                    "name": tr(I18N.App.TITLE),
                    "version": get_full_version(),
                    "author": BUILD_CONFIG.app.author,
                    "build_id": BUILD_CONFIG.get_build_identifier(),  # Usar método correcto
                    "platform": f"{BUILD_CONFIG.build.target_platform} {BUILD_CONFIG.build.architecture}",
                    "copyright": BUILD_CONFIG.app.copyright,
                    # Agregar información del equipo
                    "developers": team.developers,
                    "designers": team.designers,
                    "testers": team.testers,
                    "features": team.features,
                    "technologies": team.technologies,
                    "acknowledgments": team.acknowledgments
                }
                self._setup_credits_content(self.credits_widget, about_info)
                
        except ImportError as e:
            logger.warning("AboutDialog", f"No se pudo cargar build_config: {e}")
            # Valores por defecto
            self.ui.label_version_build.setText("v1.0, build dev")
            self.ui.label_bit_date.setText("64-bit (06.10.2025)")
            self.ui.label_autor_name.setText("Zerous12")
            self.ui.label_autor_mail.setText("zerous12@example.com")
            
            # Configurar créditos con valores por defecto
            if self.credits_widget:
                about_info = {
                    "name": "Voxeprint", 
                    "version": "1.0",
                    "author": "Zerous12",
                    "build_id": "dev",
                    "platform": "Windows x64",
                    "copyright": "© 2025 Voxeprint Studio",
                    "developers": ("• Richard Mequert",),
                    "designers": ("• Richard Mequert",),
                    "testers": ("• Paolo Olmedo",),
                    "features": ("• Calculadora profesional",),
                    "technologies": ("Python • PySide6",),
                    "acknowledgments": ("Comunidad OpenSource",)
                }
                self._setup_credits_content(self.credits_widget, about_info)
        except Exception as e:
            logger.error("AboutDialog", f"Error cargando build info: {e}")
            # Valores por defecto en caso de cualquier otro error
            self.ui.label_version_build.setText("v1.0, build dev")
            self.ui.label_bit_date.setText("64-bit (06.10.2025)")
            self.ui.label_autor_name.setText("Richard Mequert")
            self.author_email = "Zerous_12@hotmail.com"
            self.ui.label_autor_mail.setText(self.author_email)
    
    def _connect_signals(self):
        """Conecta las señales de botones y eventos"""
        
        # Botón cerrar
        self.ui.btn_close_about.clicked.connect(self.accept)
        
        # Botón GitHub
        self.ui.btn_github.clicked.connect(self._open_github)
        
        # Botón buscar actualizaciones
        self.ui.btn_search_updates.clicked.connect(self._on_search_updates)
    
    def _copy_email_to_clipboard(self):
        """Copia el email del autor al portapapeles con feedback visual"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.author_email)
            
        # Mostrar tooltip de confirmación usando mapToGlobal con el centro
        rect = self.ui.label_autor_mail.rect()
        global_pos = self.ui.label_autor_mail.mapToGlobal(rect.center())
        QToolTip.showText(
            global_pos, 
            tr(I18N.About.MSG_EMAIL_COPIED),
            self.ui.label_autor_mail
        )
        logger.info("AboutDialog", f"Email copiado al portapapeles: {self.author_email}")

    def _open_github(self):
        """Abre el perfil de GitHub y emite señal para el presenter"""
        try:
            # Emitir señal para que el presenter maneje la apertura
            self.github_profile_requested.emit()
        except Exception as e:
            logger.error("AboutDialog", f"Error emitiendo señal de GitHub: {e}")
    
    def mousePressEvent(self, event):
        """Maneja clicks en el diálogo - Los créditos manejan sus propios clicks"""
        # No interferir con el scroll - cada widget maneja sus propios eventos
        super().mousePressEvent(event)
    
    def closeEvent(self, event):
        """Maneja el cierre del diálogo - Detener timers activos"""
        try:
            # Detener timer de desbloqueo si está activo
            if self._unblock_timer.isActive():
                self._unblock_timer.stop()
                logger.info("AboutDialog", "Timer de desbloqueo detenido al cerrar diálogo")
            
            # Llamar al método padre para cerrar normalmente
            super().closeEvent(event)
            
        except Exception as e:
            logger.error("AboutDialog", f"Error al cerrar diálogo: {e}")
            super().closeEvent(event)
    
    def set_about_info(self, about_info: dict):
        """Establece información personalizada para mostrar"""
        if self.credits_widget and hasattr(self.credits_widget, 'credits_content'):
            self._setup_credits_content(self.credits_widget, about_info)
    
    def _setup_credits_content(self, widget, about_info: dict):
        """Configura el contenido de los créditos en el widget"""
        
        widget.credits_content = [
            # Comenzar directamente con el equipo
            # Desarrollador(es)
            {"type": "section", "text": "Developer", "size": 12, "bold": True, "color": "#4A9EFF"},
            {"type": "space", "height": 8},  # Espacio después del título
        ]
        
        # Agregar desarrolladores dinámicamente desde build_config
        for dev in about_info.get("developers", ["Richard Mequert"]):
            widget.credits_content.append({"type": "credit", "text": dev, "size": 10, "bold": False, "color": "#FFFFFF"})
        
        widget.credits_content.extend([
            {"type": "space", "height": 25},
            
            # Diseño
            {"type": "section", "text": "Design", "size": 12, "bold": True, "color": "#FF9E4A"},
            {"type": "space", "height": 8},  # Espacio después del título
        ])
        
        # Agregar diseñadores dinámicamente desde build_config
        for designer in about_info.get("designers", ["Richard Mequert"]):
            widget.credits_content.append({"type": "credit", "text": designer, "size": 10, "bold": False, "color": "#FFFFFF"})
        
        widget.credits_content.extend([
            {"type": "space", "height": 25},
            
            # Testers
            {"type": "section", "text": "Testers", "size": 12, "bold": True, "color": "#4AFFFF"},
            {"type": "space", "height": 8},  # Espacio después del título
        ])
        
        # Agregar testers dinámicamente desde build_config
        for tester in about_info.get("testers", ["Paolo Olmedo"]):
            widget.credits_content.append({"type": "credit", "text": tester, "size": 10, "bold": False, "color": "#FFFFFF"})
        
        widget.credits_content.extend([
            {"type": "space", "height": 25},
            
            # Características principales
            {"type": "section", "text": "Features", "size": 12, "bold": True, "color": "#4AFF9E"},
            {"type": "space", "height": 8},  # Espacio después del título
        ])
        
        # Agregar características dinámicamente desde build_config
        for feature in about_info.get("features", ["• Calculadora profesional"]):
            widget.credits_content.append({"type": "credit", "text": feature, "size": 9, "bold": False, "color": "#E0E0E0"})
        
        widget.credits_content.extend([
            {"type": "space", "height": 25},
            
            # Tecnologías
            {"type": "section", "text": "Technologies", "size": 12, "bold": True, "color": "#FF9E4A"},
            {"type": "space", "height": 8},  # Espacio después del título
        ])
        
        # Agregar tecnologías dinámicamente desde build_config
        for tech in about_info.get("technologies", ["Python • PySide6"]):
            widget.credits_content.append({"type": "credit", "text": tech, "size": 9, "bold": False, "color": "#E0E0E0"})
        
        widget.credits_content.extend([
            {"type": "space", "height": 25},
            
            # Licencia
            {"type": "section", "text": "License", "size": 12, "bold": True, "color": "#FFD700"},
            {"type": "space", "height": 8},  # Espacio después del título
            {"type": "credit", "text": BUILD_CONFIG.app.license, "size": 9, "bold": True, "color": "#FFFFFF"},
            {"type": "credit", "text": BUILD_CONFIG.app.license_short, "size": 8, "bold": False, "color": "#CCCCCC"},
            {"type": "space", "height": 25},
            
            # Mensaje del Equipo
            {"type": "section", "text": "Team Message", "size": 12, "bold": True, "color": "#4AFF4A"},
            {"type": "space", "height": 8},  # Espacio después del título
            {"type": "credit", "text": "• Built by one developer with passion for every maker.", "size": 9, "bold": False, "color": "#FFFFFF"},
            {"type": "credit", "text": "• Every donation, no matter how small, keeps this project alive.", "size": 9, "bold": False, "color": "#FFFFFF"},
            {"type": "space", "height": 25},
            
            # Final
            {"type": "title", "text": "Thank you for using Voxeprint!", "size": 14, "bold": True, "color": "#4AFF4A"},
            {"type": "space", "height": 8},  # Espacio después del título
            {"type": "subtitle", "text": "Your 3D printing companion", "size": 9, "bold": False, "color": "#CCCCCC"},
            {"type": "space", "height": 30},
        ])
        
        # Calcular altura total de contenido
        widget.total_content_height = sum(self._get_item_height(item) for item in widget.credits_content)
        widget.current_y = widget.height()
        widget.current_y = widget.height()    
    def _on_search_updates(self):
        """Maneja el click en el botón de buscar actualizaciones"""
        try:
            # Emitir señal para que el presenter maneje la búsqueda
            self.check_updates_requested.emit()
        except Exception as e:
            logger.error("AboutDialog", f"Error emitiendo señal de buscar actualizaciones: {e}")
    
    def set_checking_state(self, is_checking: bool):
        """
        Controla el estado del botón de búsqueda durante la verificación
        
        Args:
            is_checking: True para deshabilitar (verificando), False para habilitar
        """
        try:
            self.ui.btn_search_updates.setEnabled(not is_checking)
            
            if is_checking:
                self.ui.btn_search_updates.setText(tr(I18N.About.BTN_CHECKING))
                logger.info("AboutDialog", "Botón deshabilitado durante verificación")
            else:
                # Solo habilitar si no hay un bloqueo activo
                if self._blocked_remaining_seconds <= 0:
                    self.ui.btn_search_updates.setText(tr(I18N.About.BTN_SEARCH_UPDATES))
                    logger.info("AboutDialog", "Botón habilitado después de verificación")
                
        except Exception as e:
            logger.error("AboutDialog", f"Error cambiando estado del botón: {e}")
    
    def set_blocked_state(self, seconds: int):
        """
        Bloquea el botón temporalmente cuando hay cooldown activo
        
        Args:
            seconds: Segundos que permanecerá bloqueado
        """
        try:
            self._blocked_remaining_seconds = seconds
            self.ui.btn_search_updates.setEnabled(False)
            self.ui.btn_search_updates.setText(tr(I18N.About.BTN_WAIT, seconds=seconds))
            
            # Iniciar timer de cuenta regresiva (actualizar cada segundo)
            self._unblock_timer.start(1000)
            
            logger.info("AboutDialog", f"Botón bloqueado por {seconds} segundos (cooldown)")
            
        except Exception as e:
            logger.error("AboutDialog", f"Error bloqueando botón: {e}")
    
    def _update_blocked_countdown(self):
        """Actualiza el contador de bloqueo y desbloquea cuando llega a 0"""
        try:
            self._blocked_remaining_seconds -= 1
            
            if self._blocked_remaining_seconds <= 0:
                # Desbloquear botón
                self._unblock_timer.stop()
                self.ui.btn_search_updates.setEnabled(True)
                self.ui.btn_search_updates.setText(tr(I18N.About.BTN_SEARCH_UPDATES))
                logger.info("AboutDialog", "Botón desbloqueado después de cooldown")
            else:
                # Actualizar contador
                self.ui.btn_search_updates.setText(tr(I18N.About.BTN_WAIT, seconds=self._blocked_remaining_seconds))
                
        except Exception as e:
            logger.error("AboutDialog", f"Error actualizando countdown: {e}")
            self._unblock_timer.stop()
    
    def set_update_available(self, update_info: dict):
        """
        Actualiza el botón de búsqueda para indicar que hay actualización disponible
        
        Args:
            update_info: Información de la actualización disponible
        """
        try:
            # Asegurar que el botón esté habilitado
            self.ui.btn_search_updates.setEnabled(True)
            
            # Cambiar texto e ícono del botón
            self.ui.btn_search_updates.setText(tr(I18N.About.BTN_UPDATE_AVAILABLE))
            
            # Usar ícono de alerta con recoloreo según tema
            icon_path = ":/resources/resources/icons/sys_alert_square_rounded.svg"
            if self.is_dark_mode:
                # En tema oscuro, cargar directamente (SVG ya es blanco)
                alert_icon = QIcon()
                alert_icon.addFile(icon_path, QSize(), QIcon.Mode.Normal, QIcon.State.Off)
            else:
                # En tema claro, recolorear a negro para que sea visible
                try:
                    alert_icon = IconUtils.recolor_icon_svg(icon_path, "#000000")
                except Exception:
                    # Fallback: cargar icono sin recolorear
                    alert_icon = QIcon()
                    alert_icon.addFile(icon_path, QSize(), QIcon.Mode.Normal, QIcon.State.Off)
            
            self.ui.btn_search_updates.setIcon(alert_icon)
            
            logger.info("AboutDialog", f"Botón actualizado para mostrar actualización disponible: v{update_info.get('version', 'N/A')}")
            
        except Exception as e:
            logger.error("AboutDialog", f"Error actualizando botón de actualización: {e}")
