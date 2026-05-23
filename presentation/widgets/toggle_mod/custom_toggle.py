from PySide6.QtCore import ( QEasingCurve, QPropertyAnimation, Property, QPoint, QRect )
from PySide6.QtWidgets import (QCheckBox)
from PySide6.QtGui import (Qt, QPainter, QColor)


class PyToggle(QCheckBox):

    def __init__(self, width=50, height=28, parent=None):
        super().__init__(parent)
        
        # Configuración de colores
        bg_color = "#777"
        inactive_bg_color = "#be4e4e"
        circle_color = "#DDD"
        active_color = "#16A085"
        animation_curve = QEasingCurve.OutBounce
        
        # Setting parameters with custom size
        self.setFixedSize(width, height)
        self.setCursor(Qt.PointingHandCursor)

        # Colors
        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color
        self._inactive_bg_color = inactive_bg_color
        
        # Calculated proportional values
        self._padding = max(2, round(height * 0.1))  # Padding redondeado a entero
        self._circle_diameter = height - (self._padding * 2)  # Círculo ajustado al padding
        self._circle_radius = self._circle_diameter / 2
        
        # Initial position (left side with padding)
        self._circle_position = self._padding
        
        # End position (right side with padding and circle diameter)
        self._end_position = width - self._circle_diameter - self._padding

        # Create animation
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(500)
        
        # Connect state changed
        self.stateChanged.connect(self.start_transition)
    
    # Property for circle position
    @Property(float)
    def circle_position(self):
        return self._circle_position
    
    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()

    def start_transition(self, value):
        self.animation.stop()  # Stop animation if running
        if value:
            # Move to end position (checked)
            self.animation.setEndValue(self._end_position)
        else:
            # Move to start position (unchecked)
            self.animation.setEndValue(self._padding)
        self.animation.start()
    
    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):
        # Set painter
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)

        # Draw background rectangle
        if not self.isChecked():
            # Inactive state
            p.setBrush(QColor(self._inactive_bg_color))
        else:
            # Active state
            p.setBrush(QColor(self._active_color))
        
        # Draw rounded background
        p.drawRoundedRect(0, 0, self.width(), self.height(), 
                         self.height() / 2, self.height() / 2)
        
        # Draw circle - using padding for consistent spacing
        p.setBrush(QColor(self._circle_color))
        p.drawEllipse(self._circle_position, self._padding, 
                     self._circle_diameter, self._circle_diameter)
        
        p.end()
    
    def set_colors(self, active_color=None, inactive_color=None, circle_color=None, bg_color=None):
        """Permite cambiar los colores del toggle después de la creación"""
        if active_color:
            self._active_color = active_color
        if inactive_color:
            self._inactive_bg_color = inactive_color
        if circle_color:
            self._circle_color = circle_color
        if bg_color:
            self._bg_color = bg_color
        self.update()
    
    def resize_toggle(self, width, height):
        """Permite redimensionar el toggle manteniendo las proporciones"""
        # Recalcular valores proporcionales con padding redondeado
        self._padding = max(2, round(height * 0.1))
        self._circle_diameter = height - (self._padding * 2)
        self._circle_radius = self._circle_diameter / 2
        self._end_position = width - self._circle_diameter - self._padding
        
        # Ajustar posición actual si está en estado checked
        if self.isChecked():
            self._circle_position = self._end_position
        else:
            self._circle_position = self._padding
            
        # Redimensionar widget
        self.setFixedSize(width, height)
        self.update()






        
        