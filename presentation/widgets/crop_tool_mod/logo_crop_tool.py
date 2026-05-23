"""
Herramienta de Recorte de Logo Interactivo
Similar a WhatsApp - Permite seleccionar el área de recorte con ratio configurable
Integrado con el sistema de logging del proyecto
"""
import tempfile
from pathlib import Path
import numpy as np
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsEllipseItem, QWidget, QSlider,
    QGroupBox
)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QObject, QTimer, QEvent
from PySide6.QtGui import QPixmap, QPen, QColor, QBrush, QPainter, QImage, QTransform, QPainterPath
from PIL import Image
from core.utils.logger import logger
from presentation.widgets.crop_tool_mod.image_adjustment_pipeline import ImageAdjustmentPipeline
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


# Constantes de configuración
class CropToolConfig:
    """Configuración centralizada para la herramienta de recorte"""
    # Tamaños por defecto
    DEFAULT_TARGET_WIDTH = 720
    DEFAULT_TARGET_HEIGHT = 210
    DEFAULT_ASPECT_RATIO = DEFAULT_TARGET_WIDTH / DEFAULT_TARGET_HEIGHT  # 24:7
    
    # Tamaño inicial del selector
    INITIAL_SELECTOR_WIDTH = 884
    
    # Tamaños de ventana
    WINDOW_WIDTH = 898
    WINDOW_HEIGHT = 600
    
    # Panel derecho
    RIGHT_PANEL_WIDTH = 290
    
    # Preview
    PREVIEW_WIDTH = 288
    PREVIEW_HEIGHT = 84
    
    # Tamaños mínimos
    MIN_SELECTOR_SIZE = 50
    MIN_VIEW_WIDTH = 520
    MIN_VIEW_HEIGHT = 280
    
    # Ajustes group box
    ADJUSTMENTS_WIDTH = 288
    ADJUSTMENTS_HEIGHT = 300
    
    # Zoom
    ZOOM_MIN = 25
    ZOOM_MAX = 100
    ZOOM_DEFAULT = 50
    
    # Contraste/Brillo
    ADJUSTMENT_MIN = -100
    ADJUSTMENT_MAX = 100
    ADJUSTMENT_DEFAULT = 0


class CheckerboardScene(QGraphicsScene):
    """Escena con fondo checkerboard para visualizar transparencia"""

    def __init__(self, parent=None, tile_size=20):
        super().__init__(parent)
        self._tile_size = tile_size
        pix = QPixmap(tile_size * 2, tile_size * 2)
        pix.fill(QColor(210, 210, 210))
        p = QPainter(pix)
        p.fillRect(0, 0, tile_size, tile_size, QColor(240, 240, 240))
        p.fillRect(tile_size, tile_size, tile_size, tile_size, QColor(240, 240, 240))
        p.end()
        self._tile_brush = QBrush(pix)

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, self._tile_brush)


class ResizeHandle(QGraphicsEllipseItem):
    """Handle de esquina para redimensionar el selector"""
    
    def __init__(self, corner, selector, size=6):
        super().__init__(-size/2, -size/2, size, size)
        self.corner = corner  # 'tl', 'tr', 'bl', 'br'
        self.selector = selector
        self.size = size
        self.dragging = False
        self.drag_start_pos = None
        self.initial_selector_rect = None
        self.initial_selector_pos = None
        
        # Estilo del handle - punto pequeño blanco con borde negro
        self.setBrush(QBrush(QColor(255, 255, 255)))
        self.setPen(QPen(QColor(40, 40, 40), 1.5))
        
        # NO hacer movible - usaremos eventos de mouse manuales
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor if corner in ['tl', 'br'] else Qt.CursorShape.SizeBDiagCursor)
        
        # Asegurar que se muestre encima del selector
        self.setZValue(10)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.scenePos()
            self.initial_selector_rect = self.selector.rect()
            self.initial_selector_pos = self.selector.scenePos()
            event.accept()
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        if self.dragging:
            current_pos = event.scenePos()
            delta = current_pos - self.drag_start_pos
            
            self.selector.resize_from_handle(self.corner, delta, self.initial_selector_rect, self.initial_selector_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
            
    def hoverEnterEvent(self, event):
        # Resaltar al pasar el mouse - hacer más grande y cambiar color
        self.setScale(1.5)
        self.setBrush(QBrush(QColor(0, 120, 215)))
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        # Restaurar tamaño y color original
        self.setScale(1.0)
        self.setBrush(QBrush(QColor(255, 255, 255)))
        super().hoverLeaveEvent(event)


class CropSelector(QGraphicsRectItem, QObject):
    """Selector de recorte con aspect ratio fijo y handles redimensionables"""
    
    geometryChanged = Signal()  # Señal emitida cuando cambia posición o tamaño
    
    def __init__(self, rect, aspect_ratio=24/7):
        QGraphicsRectItem.__init__(self, rect)
        QObject.__init__(self)
        self.aspect_ratio = aspect_ratio  # 24:7 para 720x210
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        
        # Estilo del selector - línea discontinua naranja brillante
        pen = QPen(QColor(255, 165, 0), 2, Qt.PenStyle.DashLine)
        pen.setDashPattern([6, 3])  # Patrón de 6px línea, 3px espacio
        self.setPen(pen)
        
        # Sin relleno para ver mejor la imagen
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        
        self.image_bounds = None
        self._viewport_bounds = None
        self.is_resizing = False
        self._image_center = None
        self._snap_threshold = 15.0
        self._snapping = False
        
        # Crear handles en las esquinas (se agregan a la escena después)
        self.handles = {}
        self.create_handles()
        
    def create_handles(self):
        """Crea los handles en las 4 esquinas"""
        self.handles = {
            'tl': ResizeHandle('tl', self),  # top-left
            'tr': ResizeHandle('tr', self),  # top-right
            'bl': ResizeHandle('bl', self),  # bottom-left
            'br': ResizeHandle('br', self)   # bottom-right
        }
        
    def add_handles_to_scene(self, scene):
        """Agrega los handles a la escena"""
        for handle in self.handles.values():
            scene.addItem(handle)
        
    def update_handles_position(self):
        """Actualiza la posición de los handles en las esquinas usando coordenadas de escena"""
        if not self.handles:
            return
        # Obtener coordenadas de las esquinas en la escena
        rect = self.rect()
        pos = self.scenePos()
        
        self.handles['tl'].setPos(pos.x() + rect.left(), pos.y() + rect.top())
        self.handles['tr'].setPos(pos.x() + rect.right(), pos.y() + rect.top())
        self.handles['bl'].setPos(pos.x() + rect.left(), pos.y() + rect.bottom())
        self.handles['br'].setPos(pos.x() + rect.right(), pos.y() + rect.bottom())

    def set_image_center(self, center):
        self._image_center = center

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        r = self.rect()
        pen = QPen(QColor(255, 255, 255, 100), 1, Qt.PenStyle.DashLine)
        painter.save()
        painter.setPen(pen)
        for i in [1, 2]:
            x = r.left() + r.width() * i / 3.0
            painter.drawLine(QPointF(x, r.top()), QPointF(x, r.bottom()))
            y = r.top() + r.height() * i / 3.0
            painter.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
        painter.restore()

        if self._snapping and self._image_center:
            painter.save()
            snap_pen = QPen(QColor(0, 200, 255, 180), 1, Qt.PenStyle.SolidLine)
            painter.setPen(snap_pen)
            c = self.rect().center()
            ic = self.mapFromScene(self._image_center)
            painter.drawLine(QPointF(c.x(), c.y()), ic)
            painter.restore()

    def _check_snap(self):
        if self._image_center is None or self._viewport_bounds is None:
            return
        center = self.scenePos() + self.rect().center()
        dx = center.x() - self._image_center.x()
        dy = center.y() - self._image_center.y()
        self._snapping = abs(dx) < self._snap_threshold and abs(dy) < self._snap_threshold

    def resize_from_handle(self, corner, delta, initial_rect, initial_pos):
        """Redimensiona el selector basado en el arrastre del handle"""
        if self.is_resizing:
            return
            
        self.is_resizing = True
        
        # Calcular nuevo tamaño y posición basado en la esquina
        new_width = initial_rect.width()
        new_height = initial_rect.height()
        new_pos = QPointF(initial_pos)
        
        if corner == 'br':  # Bottom-right
            new_width = initial_rect.width() + delta.x()
            new_height = new_width / self.aspect_ratio
        elif corner == 'tl':  # Top-left
            new_width = initial_rect.width() - delta.x()
            new_height = new_width / self.aspect_ratio
            new_pos.setX(initial_pos.x() + delta.x())
            new_pos.setY(initial_pos.y() + delta.y())
        elif corner == 'tr':  # Top-right
            new_width = initial_rect.width() + delta.x()
            new_height = new_width / self.aspect_ratio
            new_pos.setY(initial_pos.y() + delta.y())
        elif corner == 'bl':  # Bottom-left
            new_width = initial_rect.width() - delta.x()
            new_height = new_width / self.aspect_ratio
            new_pos.setX(initial_pos.x() + delta.x())
        
        # Validar tamaño mínimo fijo en unidades de escena
        min_size = CropToolConfig.MIN_SELECTOR_SIZE
        if new_width < min_size:
            new_width = min_size
            new_height = new_width / self.aspect_ratio

        # Contener dentro de los límites del viewport
        if self._viewport_bounds and not self._viewport_bounds.isNull():
            proposed = QRectF(new_pos.x(), new_pos.y(), new_width, new_height)
            if proposed.left() < self._viewport_bounds.left():
                new_pos.setX(self._viewport_bounds.left())
                new_width = proposed.right() - self._viewport_bounds.left()
                new_height = new_width / self.aspect_ratio
            if proposed.right() > self._viewport_bounds.right():
                new_width = self._viewport_bounds.right() - new_pos.x()
                new_height = new_width / self.aspect_ratio
            if proposed.top() < self._viewport_bounds.top():
                new_pos.setY(self._viewport_bounds.top())
            if proposed.bottom() > self._viewport_bounds.bottom():
                new_height = self._viewport_bounds.bottom() - new_pos.y()
                new_width = new_height * self.aspect_ratio

            # Revalidar tamaño mínimo después de contención
            if new_width < min_size:
                new_width = min_size
                new_height = new_width / self.aspect_ratio

        # Aplicar cambios
        self.setRect(0, 0, new_width, new_height)
        self.setPos(new_pos)
        self.update_handles_position()
        
        self.is_resizing = False
        self.geometryChanged.emit()
        
    def set_image_bounds(self, bounds):
        """Define los límites de la imagen (solo para referencia, no restringe movimiento)"""
        self.image_bounds = bounds

    def set_viewport_bounds(self, rect):
        """Define los límites del viewport (área azul) para contener el selector"""
        self._viewport_bounds = rect

    def clamp_to_bounds(self):
        """Reposiciona y redimensiona el selector para que quepa dentro del viewport"""
        if not self._viewport_bounds or self._viewport_bounds.isNull():
            return
        pos = self.scenePos()
        rect = self.rect()
        new_w = rect.width()
        new_h = rect.height()
        max_w = self._viewport_bounds.width()
        max_h = self._viewport_bounds.height()
        if new_w > max_w:
            new_w = max_w
            new_h = new_w / self.aspect_ratio
        if new_h > max_h:
            new_h = max_h
            new_w = new_h * self.aspect_ratio
        clamped_x = max(self._viewport_bounds.left(), min(pos.x(), self._viewport_bounds.right() - new_w))
        clamped_y = max(self._viewport_bounds.top(), min(pos.y(), self._viewport_bounds.bottom() - new_h))
        if clamped_x != pos.x() or clamped_y != pos.y() or new_w != rect.width() or new_h != rect.height():
            self.setRect(0, 0, new_w, new_h)
            self.setPos(QPointF(clamped_x, clamped_y))
            self.update_handles_position()
            self.geometryChanged.emit()
        
    def itemChange(self, change, value):
        """Restringe el movimiento del selector dentro de los límites del viewport"""
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange:
            if self._viewport_bounds and not self._viewport_bounds.isNull():
                new_pos = QPointF(value)
                rect = self.rect()
                proposed = QRectF(new_pos.x(), new_pos.y(), rect.width(), rect.height())
                if not self._viewport_bounds.contains(proposed):
                    clamped_x = max(self._viewport_bounds.left(), min(new_pos.x(), self._viewport_bounds.right() - rect.width()))
                    clamped_y = max(self._viewport_bounds.top(), min(new_pos.y(), self._viewport_bounds.bottom() - rect.height()))
                    return QPointF(clamped_x, clamped_y)

        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            self.update_handles_position()
            self._check_snap()

        if change in (
            QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged,
            QGraphicsRectItem.GraphicsItemChange.ItemScenePositionHasChanged
        ):
            self.geometryChanged.emit()
            
        return super().itemChange(change, value)


class LogoCropDialog(QDialog):
    """Diálogo para recortar logo con preview en tiempo real"""    
    crop_completed = Signal(str)  # Emite la ruta del archivo recortado
    
    def __init__(self, image_path, parent=None, target_width=None, target_height=None, aspect_ratio=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_image = None
        self._cropped_path = None
        
        # Permitir configurar dimensiones desde fuera
        self.target_width = target_width or CropToolConfig.DEFAULT_TARGET_WIDTH
        self.target_height = target_height or CropToolConfig.DEFAULT_TARGET_HEIGHT
        self.aspect_ratio = aspect_ratio or (self.target_width / self.target_height)
        
        # Ajustes de imagen
        self.zoom_level = CropToolConfig.ZOOM_DEFAULT
        self.contrast_adjustment = CropToolConfig.ADJUSTMENT_DEFAULT
        self.brightness_adjustment = CropToolConfig.ADJUSTMENT_DEFAULT
        self.saturation_adjustment = CropToolConfig.ADJUSTMENT_DEFAULT
        self.sharpness_adjustment = CropToolConfig.ADJUSTMENT_DEFAULT
        self.rotation_adjustment = CropToolConfig.ADJUSTMENT_DEFAULT
        self.gamma_adjustment = 0  # 0 = 1.0 (neutro, consistente con otros sliders)
        self.flip_horizontal = False
        self.flip_vertical = False
        self.space_pressed = False

        self._cached_adjusted_image = None
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._debounced_refresh)
        self._quality_timer = QTimer(self)
        self._quality_timer.setSingleShot(True)
        self._quality_timer.timeout.connect(self._render_full_quality)
        self._fast_render = False
        self._last_crop_region = None

        self.setWindowTitle(tr(I18N.CropTool.WINDOW_TITLE).format(width=self.target_width, height=self.target_height))
        self.resize(CropToolConfig.WINDOW_WIDTH, CropToolConfig.WINDOW_HEIGHT)
        self.setFixedSize(CropToolConfig.WINDOW_WIDTH, CropToolConfig.WINDOW_HEIGHT)       
        
        self.setup_ui()
        self.load_image()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(5)
        
        # Contenedor principal horizontal
        main_container = QHBoxLayout()
        main_container.setSpacing(12)
        
        # Panel izquierdo: Editor de recorte
        left_panel = QVBoxLayout()
        
        # Vista gráfica para la imagen con mejor calidad de renderizado
        self.scene = CheckerboardScene()
        self.view = QGraphicsView(self.scene)
        # Activar todos los hints de calidad para mejor antialiasing
        self.view.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform |
            QPainter.RenderHint.TextAntialiasing |
            QPainter.RenderHint.LosslessImageRendering
        )
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, False)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setMinimumSize(CropToolConfig.MIN_VIEW_WIDTH, CropToolConfig.MIN_VIEW_HEIGHT)
        self.view.setStyleSheet("border: 2px solid #0078D4;")
        # Habilitar scrollbars para cuando la imagen sea más grande
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.installEventFilter(self)
        left_panel.addWidget(self.view)
        
        main_container.addLayout(left_panel, 3)
        
        # Panel derecho: Título, preview, ajustes y acciones
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(8)
        
        # Título y tip
        title = QLabel(tr(I18N.CropTool.TITLE_SELECT))
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #0078D4;")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_panel.addWidget(title)

        info = QLabel(tr(I18N.CropTool.INFO_DRAG))
        info.setStyleSheet("font-size: 11px; color: #666;")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_panel.addWidget(info)

        preview_title = QLabel(tr(I18N.CropTool.LABEL_PREVIEW_TITLE).format(width=self.target_width, height=self.target_height))
        preview_title.setStyleSheet("font-size: 12px; font-weight: bold;")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(preview_title)
        
        # Preview del recorte con fondo checkerboard
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(CropToolConfig.PREVIEW_WIDTH, CropToolConfig.PREVIEW_HEIGHT)
        self.preview_label.setStyleSheet("QLabel { border: 2px solid #4CAF50; background-color: #ffffff; border-radius: 5px; }")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setScaledContents(True)
        right_panel.addWidget(self.preview_label)
        
        # Información del preview
        preview_info = QLabel(tr(I18N.CropTool.LABEL_PREVIEW_INFO))
        preview_info.setStyleSheet("font-size: 10px; color: #888;")
        preview_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(preview_info)

        # Tamaño del recorte en tiempo real
        self.selector_size_label = QLabel(tr(I18N.CropTool.LABEL_CROP_SIZE_EMPTY))
        self.selector_size_label.setStyleSheet("font-size: 11px; color: #444;")
        self.selector_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(self.selector_size_label)
        
        # Controles de ajuste de imagen (group box limpio, sin bordes individuales)
        adjustments_group = QGroupBox(tr(I18N.CropTool.GROUP_ADJUSTMENTS))        
        adjustments_group.setFixedSize(CropToolConfig.ADJUSTMENTS_WIDTH, CropToolConfig.ADJUSTMENTS_HEIGHT)
        adjustments_layout = QVBoxLayout(adjustments_group)
        adjustments_layout.setContentsMargins(8, 10, 8, 8)
        adjustments_layout.setSpacing(6)
        
        # Zoom de la imagen
        zoom_layout = QHBoxLayout()
        zoom_text = QLabel(tr(I18N.CropTool.LABEL_ZOOM))
        zoom_text.setFixedWidth(70)
        self.zoom_view_slider = QSlider(Qt.Horizontal)
        self.zoom_view_slider.setMinimum(CropToolConfig.ZOOM_MIN)
        self.zoom_view_slider.setMaximum(CropToolConfig.ZOOM_MAX)
        self.zoom_view_slider.setValue(CropToolConfig.ZOOM_DEFAULT)
        self.zoom_view_slider.setSingleStep(5)
        self.zoom_view_slider.setPageStep(25)
        self.zoom_view_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_view_slider.setTickInterval(20)
        self.zoom_view_slider.valueChanged.connect(self.adjust_view_zoom)
        self.zoom_view_label = QLabel("50%")
        self.zoom_view_label.setFixedWidth(50)
        zoom_layout.addWidget(zoom_text)
        zoom_layout.addWidget(self.zoom_view_slider)
        zoom_layout.addWidget(self.zoom_view_label)
        adjustments_layout.addLayout(zoom_layout)
        
        # Contraste
        contrast_layout = QHBoxLayout()
        contrast_text = QLabel(tr(I18N.CropTool.LABEL_CONTRAST))
        contrast_text.setFixedWidth(70)
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setMinimum(CropToolConfig.ADJUSTMENT_MIN)
        self.contrast_slider.setMaximum(CropToolConfig.ADJUSTMENT_MAX)
        self.contrast_slider.setValue(CropToolConfig.ADJUSTMENT_DEFAULT)
        self.contrast_slider.valueChanged.connect(self.adjust_contrast)
        self.contrast_label = QLabel("0")
        self.contrast_label.setFixedWidth(40)
        contrast_layout.addWidget(contrast_text)
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_label)
        adjustments_layout.addLayout(contrast_layout)
        
        # Brillo
        brightness_layout = QHBoxLayout()
        brightness_text = QLabel(tr(I18N.CropTool.LABEL_BRIGHTNESS))
        brightness_text.setFixedWidth(70)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(CropToolConfig.ADJUSTMENT_MIN)
        self.brightness_slider.setMaximum(CropToolConfig.ADJUSTMENT_MAX)
        self.brightness_slider.setValue(CropToolConfig.ADJUSTMENT_DEFAULT)
        self.brightness_slider.valueChanged.connect(self.adjust_brightness)
        self.brightness_label = QLabel("0")
        self.brightness_label.setFixedWidth(40)
        brightness_layout.addWidget(brightness_text)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_label)
        adjustments_layout.addLayout(brightness_layout)
        
        # Saturación
        saturation_layout = QHBoxLayout()
        saturation_text = QLabel(tr(I18N.CropTool.LABEL_SATURATION))
        saturation_text.setFixedWidth(70)
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setMinimum(CropToolConfig.ADJUSTMENT_MIN)
        self.saturation_slider.setMaximum(CropToolConfig.ADJUSTMENT_MAX)
        self.saturation_slider.setValue(CropToolConfig.ADJUSTMENT_DEFAULT)
        self.saturation_slider.valueChanged.connect(self.adjust_saturation)
        self.saturation_label = QLabel("0")
        self.saturation_label.setFixedWidth(40)
        saturation_layout.addWidget(saturation_text)
        saturation_layout.addWidget(self.saturation_slider)
        saturation_layout.addWidget(self.saturation_label)
        adjustments_layout.addLayout(saturation_layout)
        
        # Nitidez
        sharpness_layout = QHBoxLayout()
        sharpness_text = QLabel(tr(I18N.CropTool.LABEL_SHARPNESS))
        sharpness_text.setFixedWidth(70)
        self.sharpness_slider = QSlider(Qt.Orientation.Horizontal)
        self.sharpness_slider.setMinimum(-50)
        self.sharpness_slider.setMaximum(50)
        self.sharpness_slider.setValue(0)
        self.sharpness_slider.valueChanged.connect(self.adjust_sharpness)
        self.sharpness_label = QLabel("0")
        self.sharpness_label.setFixedWidth(40)
        sharpness_layout.addWidget(sharpness_text)
        sharpness_layout.addWidget(self.sharpness_slider)
        sharpness_layout.addWidget(self.sharpness_label)
        adjustments_layout.addLayout(sharpness_layout)
        
        # Gamma
        gamma_layout = QHBoxLayout()
        gamma_text = QLabel(tr(I18N.CropTool.LABEL_GAMMA))
        gamma_text.setFixedWidth(70)
        self.gamma_slider = QSlider(Qt.Orientation.Horizontal)
        self.gamma_slider.setMinimum(CropToolConfig.ADJUSTMENT_MIN)
        self.gamma_slider.setMaximum(CropToolConfig.ADJUSTMENT_MAX)
        self.gamma_slider.setValue(CropToolConfig.ADJUSTMENT_DEFAULT)
        self.gamma_slider.valueChanged.connect(self.adjust_gamma)
        self.gamma_label = QLabel("1.00")
        self.gamma_label.setFixedWidth(40)
        gamma_layout.addWidget(gamma_text)
        gamma_layout.addWidget(self.gamma_slider)
        gamma_layout.addWidget(self.gamma_label)
        adjustments_layout.addLayout(gamma_layout)
        
        # Rotación
        rotation_layout = QHBoxLayout()
        rotation_text = QLabel(tr(I18N.CropTool.LABEL_ROTATION))
        rotation_text.setFixedWidth(70)
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotation_slider.setMinimum(-45)
        self.rotation_slider.setMaximum(45)
        self.rotation_slider.setValue(0)
        self.rotation_slider.valueChanged.connect(self.adjust_rotation)
        self.rotation_label = QLabel("0°")
        self.rotation_label.setFixedWidth(40)
        rotation_layout.addWidget(rotation_text)
        rotation_layout.addWidget(self.rotation_slider)
        rotation_layout.addWidget(self.rotation_label)
        adjustments_layout.addLayout(rotation_layout)
        
        # Voltear imagen
        flip_layout = QHBoxLayout()
        flip_text = QLabel(tr(I18N.CropTool.LABEL_FLIP))
        flip_text.setFixedWidth(70)
        flip_text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.flip_h_btn = QPushButton(tr(I18N.CropTool.BTN_FLIP_H))
        self.flip_h_btn.setCheckable(True)
        self.flip_h_btn.setFixedWidth(75)
        self.flip_h_btn.clicked.connect(self.toggle_flip_horizontal)
        self.flip_v_btn = QPushButton(tr(I18N.CropTool.BTN_FLIP_V))
        self.flip_v_btn.setCheckable(True)
        self.flip_v_btn.setFixedWidth(75)
        self.flip_v_btn.clicked.connect(self.toggle_flip_vertical)
        flip_layout.addWidget(flip_text)
        flip_layout.addWidget(self.flip_h_btn)
        flip_layout.addWidget(self.flip_v_btn)
        flip_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        adjustments_layout.addLayout(flip_layout)

        reset_layout = QHBoxLayout()
        reset_layout = QHBoxLayout()
        self.btn_reset = QPushButton(tr(I18N.CropTool.BTN_RESET))
        self.btn_reset.setFixedWidth(80)
        self.btn_reset.clicked.connect(self.reset_all)
        reset_layout.addStretch()
        reset_layout.addWidget(self.btn_reset)
        reset_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        adjustments_layout.addLayout(reset_layout)
        
        right_panel.addWidget(adjustments_group)

        # Espaciador para bajar los botones
        right_panel.addStretch()

        # Botones de acción en la misma columna de controles
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
                        
        self.btn_accept = QPushButton(tr(I18N.CropTool.BTN_CROP))
        self.btn_accept.setFixedSize(120, 30)
        self.btn_accept.setStyleSheet("""
            QPushButton {
                color: #e6fdff;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                background-color: #6cb86c;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #00aa00;
                border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #ffffff;
                background-color: #ffaa00;
                border: 1px solid #69cdff;
            }
        """)
        self.btn_accept.clicked.connect(self.accept_crop)
        buttons_layout.addWidget(self.btn_accept)

        self.btn_cancel = QPushButton(tr(I18N.CropTool.BTN_CANCEL))
        self.btn_cancel.setFixedSize(120, 30)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                color: #e6fdff;
                border: 1px solid #bcbcbc;
                border-radius: 5px;
                background-color: #f09292;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #be0000;
                border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                color: #ffffff;
                background-color: #ff0000;
                border: 1px solid #69cdff;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancel)

        right_panel.addLayout(buttons_layout)

        # Encapsular panel derecho para fijar ancho y top alignment
        right_container = QWidget()
        right_container.setLayout(right_panel)
        right_container.setFixedWidth(CropToolConfig.RIGHT_PANEL_WIDTH)
        main_container.addWidget(right_container, 0)

        layout.addLayout(main_container)
        
    def load_image(self):
        """Carga la imagen en la escena"""
        try:
            # Validar formato PNG
            if not self.image_path.lower().endswith('.png'):
                logger.warning("LogoCropDialog", f"Formato de imagen no válido: {self.image_path}")
                QMessageBox.warning(self, tr(I18N.CropTool.WARN_FORMAT_TITLE),
                    tr(I18N.CropTool.WARN_FORMAT_MSG))
                self.reject()
                return
            
            pixmap = QPixmap(self.image_path)
            if pixmap.isNull():
                logger.error("LogoCropDialog", f"No se pudo cargar la imagen: {self.image_path}")
                QMessageBox.critical(self, tr(I18N.Dialogs.ERROR_TITLE), tr(I18N.CropTool.ERROR_LOAD_MSG))
                self.reject()
                return
            
            logger.info("LogoCropDialog", f"Imagen cargada exitosamente: {self.image_path}")
                
            # Almacenar imagen original en modo RGBA para preservar transparencia
            self.original_image = Image.open(self.image_path).convert('RGBA')
            
            # Agregar imagen a la escena (el zoom se maneja desde la vista)
            self.pixmap_item = self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(pixmap.rect())

            # Aplicar el zoom inicial antes de dimensionar el selector
            initial_zoom = self.zoom_view_slider.value()
            self.adjust_view_zoom(initial_zoom)
            
            # Crear selector de recorte con tamaño dinámico basado en image+viewport
            viewport_width = self.view.viewport().width()
            rect_width = min(self.original_image.width * 0.8, viewport_width * 0.8)
            fit_scale = min(1.0, self.original_image.width / rect_width)
            rect_width *= fit_scale
            rect_height = rect_width / self.aspect_ratio

            self.crop_selector = CropSelector(QRectF(0, 0, rect_width, rect_height))
            self.crop_selector.setPos(0, 0)
            self.crop_selector.set_image_bounds(self.scene.sceneRect())
            self.crop_selector.set_image_center(self.scene.sceneRect().center())
            self.scene.addItem(self.crop_selector)

            self.crop_selector.add_handles_to_scene(self.scene)
            self.crop_selector.update_handles_position()

            self.crop_selector.geometryChanged.connect(self._schedule_preview)

            self._overlay_items = self._create_overlay_items()
            self.crop_selector.geometryChanged.connect(self._update_overlay)
            self._update_overlay()

            self.view.centerOn(self.scene.sceneRect().center())

            self._update_viewport_bounds()
            viewport_bounds = self._get_viewport_scene_rect()

            rw = rect_width
            rh = rect_height
            if rw > viewport_bounds.width():
                rw = viewport_bounds.width()
                rh = rw / self.aspect_ratio
            if rh > viewport_bounds.height():
                rh = viewport_bounds.height()
                rw = rh * self.aspect_ratio

            new_x = viewport_bounds.center().x() - rw / 2
            new_y = viewport_bounds.center().y() - rh / 2
            self.crop_selector.setRect(0, 0, rw, rh)
            self.crop_selector.setPos(new_x, new_y)
            self.crop_selector.update_handles_position()
            self.crop_selector.geometryChanged.emit()

            self.update_preview()
            
        except Exception as e:
            logger.log_exception("LogoCropDialog", e, "cargar la imagen")
            QMessageBox.critical(self, tr(I18N.Dialogs.ERROR_TITLE), tr(I18N.CropTool.ERROR_LOAD_GENERIC))
            self.reject()
            
    def adjust_view_zoom(self, value):
        """Ajusta el zoom de la VISTA (no del item), el selector mantiene su posición en coordenadas de imagen"""
        self.zoom_level = value
        self.zoom_view_label.setText(f"{value}%")

        scale_factor = value / 100.0

        current_center = self.view.mapToScene(self.view.viewport().rect().center())
        self.pixmap_item.setScale(1.0)
        self.view.resetTransform()
        self.view.scale(scale_factor, scale_factor)
        self.view.centerOn(current_center)
        if hasattr(self, 'crop_selector'):
            self._update_viewport_bounds()
            self.crop_selector.clamp_to_bounds()
        
    def adjust_contrast(self, value):
        """Ajusta el contraste de la imagen"""
        self.contrast_adjustment = value
        self.contrast_label.setText(f"{value:+d}" if value != 0 else "0")
        self._schedule_preview()
        
    def adjust_brightness(self, value):
        """Ajusta el brillo de la imagen"""
        self.brightness_adjustment = value
        self.brightness_label.setText(f"{value:+d}" if value != 0 else "0")
        self._schedule_preview()
        
    def adjust_saturation(self, value):
        """Ajusta la saturación de la imagen"""
        self.saturation_adjustment = value
        self.saturation_label.setText(f"{value:+d}" if value != 0 else "0")
        self._schedule_preview()
        
    def adjust_sharpness(self, value):
        """Ajusta la nitidez de la imagen"""
        self.sharpness_adjustment = value
        self.sharpness_label.setText(f"{value:+d}" if value != 0 else "0")
        self._schedule_preview()
        
    def adjust_gamma(self, value):
        """Ajusta el gamma de la imagen"""
        self.gamma_adjustment = value
        gamma_val = 1.0 + value / 100.0
        self.gamma_label.setText(f"{gamma_val:.2f}")
        self._schedule_preview()
        
    def adjust_rotation(self, value):
        """Ajusta la rotación de la imagen"""
        self.rotation_adjustment = value
        self.rotation_label.setText(f"{value:+d}°" if value != 0 else "0°")
        self._schedule_preview()
        
    def toggle_flip_horizontal(self):
        """Voltear imagen horizontalmente"""
        self.flip_horizontal = self.flip_h_btn.isChecked()
        self._schedule_preview()
        
    def toggle_flip_vertical(self):
        """Voltear imagen verticalmente"""
        self.flip_vertical = self.flip_v_btn.isChecked()
        self._schedule_preview()

    def reset_all(self):
        self.zoom_view_slider.setValue(CropToolConfig.ZOOM_DEFAULT)
        self.contrast_slider.setValue(CropToolConfig.ADJUSTMENT_DEFAULT)
        self.brightness_slider.setValue(CropToolConfig.ADJUSTMENT_DEFAULT)
        self.saturation_slider.setValue(CropToolConfig.ADJUSTMENT_DEFAULT)
        self.sharpness_slider.setValue(0)
        self.gamma_slider.setValue(CropToolConfig.ADJUSTMENT_DEFAULT)
        self.rotation_slider.setValue(0)
        self.flip_h_btn.setChecked(False)
        self.flip_v_btn.setChecked(False)
        self.flip_horizontal = False
        self.flip_vertical = False
        self._schedule_preview()

    def _render_full_quality(self):
        self._fast_render = False
        self._cached_adjusted_image = None
        self._update_main_view_image()
        self.update_preview()

    def _get_viewport_scene_rect(self):
        """Retorna el rectángulo visible del viewport en coordenadas de escena"""
        viewport_rect = self.view.viewport().rect()
        top_left = self.view.mapToScene(viewport_rect.topLeft())
        bottom_right = self.view.mapToScene(viewport_rect.bottomRight())
        return QRectF(top_left, bottom_right)

    def _create_overlay_items(self):
        brush = QBrush(QColor(0, 0, 0, 100))
        items = []
        for _ in range(4):
            item = self.scene.addRect(QRectF(), QPen(Qt.NoPen), brush)
            item.setZValue(5)
            item.setVisible(True)
            items.append(item)
        return items

    def _update_overlay(self):
        if not hasattr(self, '_overlay_items'):
            return
        selector = self.crop_selector
        sr = self.scene.sceneRect()
        sr = sr.adjusted(-1, -1, 1, 1)
        sr = sr.intersected(self._get_viewport_scene_rect())
        r = selector.sceneBoundingRect()
        items = self._overlay_items
        if len(items) >= 4:
            items[0].setRect(QRectF(sr.left(), sr.top(), sr.width(), r.top() - sr.top()))
            items[1].setRect(QRectF(sr.left(), r.bottom(), sr.width(), sr.bottom() - r.bottom()))
            items[2].setRect(QRectF(sr.left(), r.top(), r.left() - sr.left(), r.height()))
            items[3].setRect(QRectF(r.right(), r.top(), sr.right() - r.right(), r.height()))

    def _update_viewport_bounds(self):
        """Actualiza los límites del selector al área visible del viewport"""
        bounds = self._get_viewport_scene_rect()
        if hasattr(self, 'crop_selector'):
            self.crop_selector.set_viewport_bounds(bounds)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'crop_selector'):
            self._update_viewport_bounds()
            self.crop_selector.clamp_to_bounds()

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'crop_selector'):
            self._update_viewport_bounds()
            self.crop_selector.clamp_to_bounds()

    def _compute_crop_region(self):
        """Retorna (x, y, w, h) en coordenadas de imagen original, o None si no hay intersección"""
        selector_scene = self.crop_selector.sceneBoundingRect()
        selector_local = self.pixmap_item.mapFromScene(selector_scene).boundingRect()
        pixmap_local = QRectF(0, 0, self.pixmap_item.pixmap().width(), self.pixmap_item.pixmap().height())

        intersection = selector_local.intersected(pixmap_local)
        if intersection.isEmpty():
            return None

        scale_x = self.original_image.width / pixmap_local.width()
        scale_y = self.original_image.height / pixmap_local.height()

        crop_x = int(intersection.x() * scale_x)
        crop_y = int(intersection.y() * scale_y)
        crop_width = int(intersection.width() * scale_x)
        crop_height = int(intersection.height() * scale_y)

        crop_x = max(0, min(crop_x, self.original_image.width))
        crop_y = max(0, min(crop_y, self.original_image.height))
        crop_width = min(crop_width, self.original_image.width - crop_x)
        crop_height = min(crop_height, self.original_image.height - crop_y)

        return (crop_x, crop_y, crop_width, crop_height)

    def _render_final_image(self, crop_x, crop_y, crop_width, crop_height):
        """Recorta, redimensiona con letterbox y aplica ajustes. Retorna PIL Image RGBA"""
        cropped = self.original_image.crop((
            crop_x, crop_y,
            crop_x + crop_width,
            crop_y + crop_height
        ))

        fit_scale = min(self.target_width / crop_width, self.target_height / crop_height)
        new_w = max(1, int(crop_width * fit_scale))
        new_h = max(1, int(crop_height * fit_scale))

        resample = Image.Resampling.NEAREST if self._fast_render else Image.Resampling.LANCZOS
        resized = cropped.resize((new_w, new_h), resample)
        if resized.mode != 'RGBA':
            resized = resized.convert('RGBA')

        resized = ImageAdjustmentPipeline.apply(
            resized,
            contrast=self.contrast_adjustment,
            brightness=self.brightness_adjustment,
            saturation=self.saturation_adjustment,
            sharpness=self.sharpness_adjustment,
            gamma=self.gamma_adjustment,
            rotation=self.rotation_adjustment,
            flip_h=self.flip_horizontal,
            flip_v=self.flip_vertical
        )

        canvas = Image.new('RGBA', (self.target_width, self.target_height), (0, 0, 0, 0))
        offset_x = (self.target_width - new_w) // 2
        offset_y = (self.target_height - new_h) // 2
        canvas.paste(resized, (offset_x, offset_y))

        return canvas

    def _create_checkerboard(self, width, height, tile_size=8):
        """Crea un patrón checkerboard para visualizar transparencia"""
        x = np.arange(width) // tile_size
        y = np.arange(height) // tile_size
        mask = (x[np.newaxis, :] + y[:, np.newaxis]) % 2
        gray = np.full((height, width, 4), 200, dtype=np.uint8)
        gray[:, :, 3] = 255
        white = np.full((height, width, 4), 255, dtype=np.uint8)
        checker = np.where(mask[:, :, np.newaxis], white, gray)
        return Image.fromarray(checker, 'RGBA')

    def _schedule_preview(self):
        """Programa la actualización del preview con debounce de 80ms"""
        self._cached_adjusted_image = None
        self._fast_render = True
        self._preview_timer.start(80)
        self._quality_timer.start(350)

    def _debounced_refresh(self):
        """Refresca la vista principal y el preview tras el debounce (rápido)"""
        self._update_main_view_image()
        self.update_preview()

    def _get_adjusted_full_image(self):
        """Retorna la imagen completa con ajustes aplicados (sin rotación), en caché"""
        if self._cached_adjusted_image is not None:
            return self._cached_adjusted_image
        if self.original_image is None:
            return None
        self._cached_adjusted_image = ImageAdjustmentPipeline.apply(
            self.original_image.copy(),
            contrast=self.contrast_adjustment,
            brightness=self.brightness_adjustment,
            saturation=self.saturation_adjustment,
            sharpness=self.sharpness_adjustment,
            gamma=self.gamma_adjustment,
            flip_h=self.flip_horizontal,
            flip_v=self.flip_vertical,
            rotation=self.rotation_adjustment,
        )
        return self._cached_adjusted_image

    def _update_main_view_image(self):
        """Actualiza el pixmap de la vista principal con los ajustes aplicados"""
        adjusted = self._get_adjusted_full_image()
        if adjusted is None:
            return
        data = adjusted.tobytes('raw', 'RGBA')
        qimage = QImage(data, adjusted.width, adjusted.height, adjusted.width * 4, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)

    def update_preview(self):
        """Actualiza el preview del área recortada (solo la intersección con la imagen)"""
        try:
            region = self._compute_crop_region()
            if region is None:
                self.preview_label.clear()
                self.selector_size_label.setText(tr(I18N.CropTool.LABEL_CROP_SIZE_EMPTY))
                return

            crop_x, crop_y, crop_width, crop_height = region
            self.selector_size_label.setText(
                tr(I18N.CropTool.LABEL_CROP_SIZE_FMT).format(width=crop_width, height=crop_height)
            )

            if crop_width < 10 or crop_height < 10:
                self.preview_label.clear()
                return

            canvas = self._render_final_image(crop_x, crop_y, crop_width, crop_height)

            data = canvas.tobytes('raw', 'RGBA')
            qimage = QImage(
                data,
                canvas.width, canvas.height,
                canvas.width * 4,
                QImage.Format.Format_RGBA8888
            )

            preview_pixmap = QPixmap.fromImage(qimage)
            preview_scaled = preview_pixmap.scaled(
                CropToolConfig.PREVIEW_WIDTH, CropToolConfig.PREVIEW_HEIGHT,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.preview_label.setPixmap(preview_scaled)

        except Exception as e:
            logger.log_exception("LogoCropDialog", e, "actualizar preview")

    def accept_crop(self):
        """Acepta el recorte y guarda la imagen (solo la intersección)"""
        try:
            region = self._compute_crop_region()
            if region is None:
                QMessageBox.warning(self, tr(I18N.CropTool.WARN_NO_INTERSECTION_TITLE),
                    tr(I18N.CropTool.WARN_NO_INTERSECTION_MSG))
                return

            crop_x, crop_y, crop_width, crop_height = region
            final_image = self._render_final_image(crop_x, crop_y, crop_width, crop_height)

            temp_dir = tempfile.gettempdir()
            self._cropped_path = str(Path(temp_dir) / "logo_cropped_temp.png")
            final_image.save(self.cropped_path, 'PNG', optimize=True)

            logger.info("LogoCropDialog", f"Imagen recortada guardada en: {self._cropped_path}")
            self.crop_completed.emit(self._cropped_path)
            self.accept()

        except Exception as e:
            logger.log_exception("LogoCropDialog", e, "procesar el recorte")
            QMessageBox.critical(self, tr(I18N.Dialogs.ERROR_TITLE), tr(I18N.CropTool.ERROR_PROCESS_GENERIC))
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space and not self.space_pressed:
            self.space_pressed = True
            self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.view.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.accept_crop()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            if hasattr(self, 'crop_selector'):
                step = 10 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
                dx = dy = 0
                if event.key() == Qt.Key.Key_Left:
                    dx = -step
                elif event.key() == Qt.Key.Key_Right:
                    dx = step
                elif event.key() == Qt.Key.Key_Up:
                    dy = -step
                elif event.key() == Qt.Key.Key_Down:
                    dy = step
                self.crop_selector.setPos(self.crop_selector.scenePos() + QPointF(dx, dy))
                self.crop_selector.update_handles_position()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.space_pressed = False
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def eventFilter(self, obj, event):
        if obj is self.view and event.type() == QEvent.Type.Wheel:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                factor = 1.1 if event.angleDelta().y() > 0 else 0.9
                new_zoom = self.zoom_level * factor
                new_zoom = max(CropToolConfig.ZOOM_MIN, min(CropToolConfig.ZOOM_MAX, new_zoom))
                self.zoom_view_slider.setValue(int(new_zoom))
                return True
        return super().eventFilter(obj, event)

    @property
    def cropped_path(self):
        """Ruta del archivo recortado"""
        return self._cropped_path
