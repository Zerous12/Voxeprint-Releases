"""
Utilidades para manipulación de íconos
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter, QColor, QPixmap
from PySide6.QtSvg import QSvgRenderer


class IconUtils:
    """Utilidades para recolorear íconos según el tema"""
    
    @staticmethod
    def recolor_icon_png(png_path: str, target_color: QColor) -> QIcon:
        """
        Recolorea un ícono PNG al color especificado
        
        Args:
            png_path: Ruta al archivo PNG
            target_color: Color objetivo
            
        Returns:
            QIcon recoloreado
        """
        pixmap = QPixmap(png_path)
        if pixmap.isNull():
            raise FileNotFoundError(f"No se pudo cargar la imagen: {png_path}")

        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(colored_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), target_color)
        painter.end()

        return QIcon(colored_pixmap)
    
    @staticmethod
    def recolor_icon_svg(svg_path: str, color: str) -> QIcon:
        """
        Recolorea un ícono SVG al color especificado
        
        Args:
            svg_path: Ruta al archivo SVG
            color: Color en formato string (ej: "#000000")
            
        Returns:
            QIcon recoloreado
        """
        renderer = QSvgRenderer(svg_path)
        if not renderer.isValid():
            raise ValueError(f"El archivo SVG no es válido o no se pudo cargar: {svg_path}")

        base_pixmap = QPixmap(renderer.defaultSize())
        base_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(base_pixmap)
        renderer.render(painter)
        painter.end()

        colored_pixmap = QPixmap(base_pixmap.size())
        colored_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(colored_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.drawPixmap(0, 0, base_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), QColor(color))
        painter.end()
        return QIcon(colored_pixmap)
