"""
Widget de Cartelera Animada para Eventos de Donaciones

Muestra mensajes rotativos con animación vertical tipo cartelera
promoviendo donaciones para apoyar el proyecto Voxeprint.
"""
from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import (
    QTimer, QPropertyAnimation, QEasingCurve, 
    QSequentialAnimationGroup, Property, Qt
)
from PySide6.QtGui import QFont
from typing import List, Dict, Optional


class DonationEventLabel(QLabel):
    """Label animado que muestra mensajes rotativos sobre donaciones"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuración visual básica
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(120, 22)
        self.setMaximumHeight(22)
        
        # Estado interno
        self._messages: List[Dict] = []
        self._current_index: int = 0
        self._animation_group: Optional[QSequentialAnimationGroup] = None
        self._rotation_timer: Optional[QTimer] = None
        
        # Efecto de opacidad para animaciones
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(1.0)
        
        # Configurar fuente
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.setFont(font)
        
        # Hacer el texto no seleccionable
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    
    def set_donation_messages(self):
        """
        Configura los mensajes motivadores para donaciones
        """
        self._messages.clear()
        
        # Mensajes positivos y motivadores sobre donaciones
        self._messages = [
            {
                'text': '¡Voxeprint es gratuito!',
                'color': '#4CAF50'
            },
            {
                'text': '¿Te gusta? ¡Apóyanos!',
                'color': '#FF9800'
            },
            {
                'text': 'Tu donación nos ayuda',
                'color': '#2196F3'
            },
            {
                'text': '¡Gracias por usarnos!',
                'color': "#C355A2"
            },
            {
                'text': 'Hecho con amor en PY',
                'color': "#CD325B"
            },
            {
                'text': '¡Software libre y abierto!',
                'color': '#4CAF50'
            },
            {
                'text': 'Cada donación cuenta',
                'color': '#FF5722'
            },
            {
                'text': '¡Ayúdanos a crecer!',
                'color': '#FFC107'
            }
        ]
        
        # Reiniciar animación con nuevos mensajes
        self._current_index = 0
        self.start_rotation()
    
    def start_rotation(self):
        """Inicia la rotación automática de mensajes"""
        if not self._messages:
            return
        
        # Mostrar el primer mensaje inmediatamente
        self._show_message(0)
        
        # Configurar timer para rotación (cambiar cada 4 segundos)
        if self._rotation_timer:
            self._rotation_timer.stop()
        
        self._rotation_timer = QTimer(self)
        self._rotation_timer.timeout.connect(self._rotate_message)
        self._rotation_timer.start(4000)  # 4 segundos por mensaje
    
    def stop_rotation(self):
        """Detiene la rotación de mensajes"""
        if self._rotation_timer:
            self._rotation_timer.stop()
        
        if self._animation_group:
            self._animation_group.stop()
    
    def _rotate_message(self):
        """Rota al siguiente mensaje con animación"""
        if not self._messages:
            return
        
        # Pasar al siguiente mensaje
        self._current_index = (self._current_index + 1) % len(self._messages)
        
        # Animar transición
        self._animate_transition()
    
    def _animate_transition(self):
        """Animación de transición entre mensajes (fade out -> cambio -> fade in)"""
        if self._animation_group:
            self._animation_group.stop()
        
        self._animation_group = QSequentialAnimationGroup(self)
        
        # 1. Fade out (500ms)
        fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_out.setDuration(500)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # 2. Cambiar mensaje cuando esté invisible
        fade_out.finished.connect(lambda: self._show_message(self._current_index))
        
        # 3. Fade in (500ms)
        fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_in.setDuration(500)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self._animation_group.addAnimation(fade_out)
        self._animation_group.addAnimation(fade_in)
        self._animation_group.start()
    
    def _show_message(self, index: int):
        """Muestra un mensaje específico"""
        if not self._messages or index >= len(self._messages):
            return
        
        msg = self._messages[index]
        self.setText(msg['text'])
        
        # Aplicar estilo solo con color de texto (sin fondo)
        self.setStyleSheet(f"""
            QLabel {{
                color: {msg['color']};
                background-color: transparent;
                padding: 2px 8px;
                font-weight: bold;
            }}
        """)
    
    def get_opacity(self):
        """Getter para la propiedad opacity (necesario para animación)"""
        return self._opacity_effect.opacity()
    
    def set_opacity(self, value):
        """Setter para la propiedad opacity (necesario para animación)"""
        self._opacity_effect.setOpacity(value)
    
    # Propiedad para animaciones
    opacity = Property(float, get_opacity, set_opacity)
