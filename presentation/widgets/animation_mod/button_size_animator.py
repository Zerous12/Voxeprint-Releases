"""
ButtonSizeAnimator - Sistema de animaciones con logging centralizado
Incluye manejo profesional de logs y monitoreo de estados
Versión con efecto OutExpo (desaceleración exponencial dramática) y delay anti-spam
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QObject, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QSize, Signal, QTimer
from PySide6.QtGui import QEnterEvent
from typing import Optional

# Sistema de logging centralizado
from core.utils.logger import debug, info, warning, error, log_exception


class ButtonSizeAnimator(QObject):
    """
    Animador que maneja transiciones suaves de tamaño entre dos botones
    Versión mejorada con debug avanzado
    """
    
    # Señales para monitoreo
    animation_started = Signal(str)  # tipo de animación: "hover" o "normal"
    animation_finished = Signal(str)
    frame_updated = Signal(int, int)  # primary_width, secondary_width
    
    def __init__(self, 
                 primary_button: QPushButton,
                 secondary_button: QPushButton,
                 primary_normal_width: int = 90,
                 primary_hover_width: int = 25,
                 secondary_normal_width: int = 25,
                 secondary_hover_width: int = 90,
                 animation_duration: int = 200,
                 easing_curve: QEasingCurve.Type = QEasingCurve.Type.OutCubic):
        
        super().__init__()
        
        # Nombre del módulo para logging
        self.module_name = "ButtonSizeAnimator"
        
        try:
            # Validación de parámetros
            if not isinstance(primary_button, QPushButton) or not isinstance(secondary_button, QPushButton):
                raise ValueError("Los botones deben ser instancias de QPushButton")
            
            # Propiedades
            self.primary_button = primary_button
            self.secondary_button = secondary_button
            self.primary_normal_width = primary_normal_width
            self.primary_hover_width = primary_hover_width
            self.secondary_normal_width = secondary_normal_width
            self.secondary_hover_width = secondary_hover_width
            self.animation_duration = animation_duration
            self.easing_curve = easing_curve
            
            # Textos para los estados (valores por defecto apropiados)
            self.primary_normal_text = self.primary_button.text()  # Texto estándar para botón de búsqueda
            self.primary_hover_text = ""  # Sin texto en hover (solo el icono si lo hay)
            self.secondary_normal_text = self.secondary_button.text()  # Texto estándar para botón de limpieza
            self.secondary_hover_text = "Limpiar"  # Texto cuando se expande
            
            # Estado interno
            self._is_hovering = False
            self._animation_running = False
            self._close_timer = None  # Timer para delay de cierre
            
            # Configurar animaciones
            self._setup_animations()
            
            # Instalar event filter
            self._install_event_filter()
            
            # Configurar tamaños iniciales
            self._set_initial_sizes()
            
        except Exception as e:
            log_exception(self.module_name, e, "constructor ButtonSizeAnimator")
    
    def _setup_animations(self):
        """Configurar las animaciones de tamaño con efecto OutExpo"""
        try:
            # Usar OutExpo para desaceleración exponencial dramática y rápida
            easing_curve = QEasingCurve.Type.OutExpo
            
            # === ANIMACIONES DE TAMAÑO ===
            # Animación del botón primario (animar tanto min como max size)
            self.primary_animation = QPropertyAnimation(self.primary_button, b"maximumSize")
            self.primary_animation.setDuration(500)  # Duración similar al toggle
            self.primary_animation.setEasingCurve(easing_curve)
            
            # Animación adicional para el minimumSize del primary
            self.primary_min_animation = QPropertyAnimation(self.primary_button, b"minimumSize")
            self.primary_min_animation.setDuration(500)
            self.primary_min_animation.setEasingCurve(easing_curve)
            
            # Animación del botón secundario
            self.secondary_animation = QPropertyAnimation(self.secondary_button, b"maximumSize")
            self.secondary_animation.setDuration(500)
            self.secondary_animation.setEasingCurve(easing_curve)
            
            # Animación adicional para el minimumSize del secondary
            self.secondary_min_animation = QPropertyAnimation(self.secondary_button, b"minimumSize")
            self.secondary_min_animation.setDuration(500)
            self.secondary_min_animation.setEasingCurve(easing_curve)
            
            # Grupo paralelo para sincronizar TODAS las animaciones de tamaño
            # Parent explícito para que Qt gestione el ciclo de vida y evitar crashes
            self.animation_group = QParallelAnimationGroup(self.primary_button)
            self.animation_group.addAnimation(self.primary_animation)
            self.animation_group.addAnimation(self.primary_min_animation)
            self.animation_group.addAnimation(self.secondary_animation)
            self.animation_group.addAnimation(self.secondary_min_animation)
            
            # Conectar señales para debugging
            self.animation_group.stateChanged.connect(self._on_animation_state_changed)
            self.animation_group.finished.connect(self._on_animation_finished)
            
            # Conectar valueChanged para monitoreo frame por frame
            self.primary_animation.valueChanged.connect(self._on_primary_value_changed)
            self.secondary_animation.valueChanged.connect(self._on_secondary_value_changed)
                
        except Exception as e:
            error(self.module_name, f"Error configurando animaciones: {str(e)}")
            log_exception(self.module_name, e, "_setup_animations")
    
    def _set_initial_sizes(self):
        """Establecer tamaños iniciales de los botones"""
        try:
            # Obtener altura actual
            height = max(self.primary_button.height(), 24)  # Mínimo 24px
            
            # Configurar botón primario
            primary_size = QSize(self.primary_normal_width, height)
            self.primary_button.setMinimumSize(primary_size)
            self.primary_button.setMaximumSize(primary_size)
            
            # Configurar botón secundario
            secondary_size = QSize(self.secondary_normal_width, height)
            self.secondary_button.setMinimumSize(secondary_size)
            self.secondary_button.setMaximumSize(secondary_size)
                
        except Exception as e:
            error(self.module_name, f"Error estableciendo tamaños iniciales: {str(e)}")
            log_exception(self.module_name, e, "_set_initial_sizes")
    
    def _install_event_filter(self):
        """Instalar filtro de eventos para detectar hover en ambos botones"""
        try:
            # Instalar en AMBOS botones para detectar hover
            self.primary_button.installEventFilter(self)
            self.secondary_button.installEventFilter(self)
                
        except Exception as e:
            error(self.module_name, f"Error instalando event filter: {str(e)}")
            log_exception(self.module_name, e, "_install_event_filter")
    
    def eventFilter(self, obj, event):
        """Filtrar eventos de mouse para detectar hover en ambos botones con delay anti-spam"""
        try:
            # Detectar Enter en el secondary button (expandir secondary INMEDIATAMENTE)
            if obj == self.secondary_button and event.type() == event.Type.Enter:
                # Cancelar cualquier timer de cierre pendiente
                self._cancel_close_timer()
                
                if not self._is_hovering:
                    self._is_hovering = True
                    self._animate_to_hover()
                    
            # Detectar Leave en secondary button (DELAY antes de cerrar)
            elif obj == self.secondary_button and event.type() == event.Type.Leave:
                if self._is_hovering:
                    # Iniciar timer de 500ms antes de cerrar
                    self._start_close_timer()
                    
            # Detectar Enter en primary button (cancelar cierre O cerrar inmediatamente)
            elif obj == self.primary_button and event.type() == event.Type.Enter:
                if self._is_hovering:
                    # Cancelar el timer y cerrar INMEDIATAMENTE
                    self._cancel_close_timer()
                    self._is_hovering = False
                    self._animate_to_normal()
            
            return super().eventFilter(obj, event)
            
        except Exception as e:
            error(self.module_name, f"Error en eventFilter: {str(e)}")
            log_exception(self.module_name, e, "eventFilter")
            return False
    
    def _start_close_timer(self):
        """Iniciar timer de delay antes de cerrar (500ms)"""
        try:
            # Cancelar timer anterior si existe
            self._cancel_close_timer()
            
            # Crear nuevo timer de 500ms (medio segundo) con parent para que Qt gestione su vida
            self._close_timer = QTimer(self.primary_button)
            self._close_timer.setSingleShot(True)
            self._close_timer.timeout.connect(self._delayed_close)
            self._close_timer.start(500)  # 500ms de delay
            
        except Exception as e:
            error(self.module_name, f"Error iniciando close timer: {str(e)}")
            log_exception(self.module_name, e, "_start_close_timer")
    
    def _cancel_close_timer(self):
        """Cancelar el timer de cierre si existe"""
        try:
            if self._close_timer is not None:
                self._close_timer.stop()
                self._close_timer.deleteLater()
                self._close_timer = None
                
        except Exception as e:
            error(self.module_name, f"Error cancelando close timer: {str(e)}")
            log_exception(self.module_name, e, "_cancel_close_timer")
    
    def _delayed_close(self):
        """Ejecutar cierre después del delay (solo si NO se movió a primary)"""
        try:
            if self._is_hovering:
                self._is_hovering = False
                self._animate_to_normal()
            
            # Limpiar timer
            self._close_timer = None
            
        except Exception as e:
            error(self.module_name, f"Error en delayed close: {str(e)}")
            log_exception(self.module_name, e, "_delayed_close")
    
    def _animate_to_hover(self):
        """Animar al estado hover con efecto bounce"""
        try:
            # Validar que las animaciones existen
            if not hasattr(self, 'primary_animation') or not hasattr(self, 'secondary_animation'):
                error(self.module_name, "Las animaciones no están inicializadas")
                return
            
            # Detener cualquier animación en curso
            if self._animation_running and hasattr(self, 'animation_group'):
                self.animation_group.stop()
                self._animation_running = False
            
            height = max(self.primary_button.height(), 24)
            
            # CONFIGURAR ANIMACIÓN PRIMARY (buscar): DE GRANDE A PEQUEÑO
            primary_normal_size = QSize(self.primary_normal_width, height)
            primary_hover_size = QSize(self.primary_hover_width, height)
            
            self.primary_animation.setStartValue(primary_normal_size)      # Max: 90px
            self.primary_animation.setEndValue(primary_hover_size)         # Max: 25px
            self.primary_min_animation.setStartValue(primary_normal_size)  # Min: 90px
            self.primary_min_animation.setEndValue(primary_hover_size)     # Min: 25px
            
            # CONFIGURAR ANIMACIÓN SECONDARY (cleaner): DE PEQUEÑO A GRANDE
            secondary_normal_size = QSize(self.secondary_normal_width, height)
            secondary_hover_size = QSize(self.secondary_hover_width, height)
            
            self.secondary_animation.setStartValue(secondary_normal_size)      # Max: 25px
            self.secondary_animation.setEndValue(secondary_hover_size)         # Max: 90px
            self.secondary_min_animation.setStartValue(secondary_normal_size)  # Min: 25px
            self.secondary_min_animation.setEndValue(secondary_hover_size)     # Min: 90px
            
            # CAMBIAR TEXTOS INMEDIATAMENTE AL INICIAR LA ANIMACIÓN
            self._update_button_texts_for_hover()
            
            # Iniciar animación
            self._animation_running = True
            self.animation_group.start()
            self.animation_started.emit("hover")
            
        except Exception as e:
            error(self.module_name, f"Error en _animate_to_hover: {str(e)}")
            log_exception(self.module_name, e, "_animate_to_hover")
    
    def _animate_to_normal(self):
        """Animar al estado normal con efecto bounce"""
        try:
            # Validar que las animaciones existen
            if not hasattr(self, 'primary_animation') or not hasattr(self, 'secondary_animation'):
                error(self.module_name, "Las animaciones no están inicializadas")
                return
            
            # Detener cualquier animación en curso
            if self._animation_running and hasattr(self, 'animation_group'):
                self.animation_group.stop()
                self._animation_running = False
            
            height = max(self.primary_button.height(), 24)
            
            # CONFIGURAR ANIMACIÓN PRIMARY (buscar): DE PEQUEÑO A GRANDE (inverso)
            primary_hover_size = QSize(self.primary_hover_width, height)
            primary_normal_size = QSize(self.primary_normal_width, height)
            
            self.primary_animation.setStartValue(primary_hover_size)       # Max: 25px
            self.primary_animation.setEndValue(primary_normal_size)        # Max: 90px
            self.primary_min_animation.setStartValue(primary_hover_size)   # Min: 25px
            self.primary_min_animation.setEndValue(primary_normal_size)    # Min: 90px
            
            # CONFIGURAR ANIMACIÓN SECONDARY (cleaner): DE GRANDE A PEQUEÑO (inverso)
            secondary_hover_size = QSize(self.secondary_hover_width, height)
            secondary_normal_size = QSize(self.secondary_normal_width, height)
            
            self.secondary_animation.setStartValue(secondary_hover_size)       # Max: 90px
            self.secondary_animation.setEndValue(secondary_normal_size)        # Max: 25px
            self.secondary_min_animation.setStartValue(secondary_hover_size)   # Min: 90px
            self.secondary_min_animation.setEndValue(secondary_normal_size)    # Min: 25px
            
            # RESTAURAR TEXTOS INMEDIATAMENTE AL INICIAR LA ANIMACIÓN
            self._update_button_texts_for_normal()
            
            # Iniciar animación
            self._animation_running = True
            self.animation_group.start()
            self.animation_started.emit("normal")
            
        except Exception as e:
            error(self.module_name, f"Error en _animate_to_normal: {str(e)}")
            log_exception(self.module_name, e, "_animate_to_normal")
    
    def _on_animation_state_changed(self, new_state, old_state):
        """Callback cuando cambia el estado de la animación"""
        pass
    
    def _on_animation_finished(self):
        """Callback cuando termina la animación"""
        self._animation_running = False
        
        # Asegurar que los tamaños finales están correctos
        height = max(self.primary_button.height(), 24)
        
        if self._is_hovering:
            # Estado hover: primary pequeño, secondary grande
            primary_size = QSize(self.primary_hover_width, height)
            secondary_size = QSize(self.secondary_hover_width, height)
        else:
            # Estado normal: primary grande, secondary pequeño
            primary_size = QSize(self.primary_normal_width, height)
            secondary_size = QSize(self.secondary_normal_width, height)
        
        # Establecer tamaños finales explícitamente
        self.primary_button.setMinimumSize(primary_size)
        self.primary_button.setMaximumSize(primary_size)
        self.secondary_button.setMinimumSize(secondary_size)
        self.secondary_button.setMaximumSize(secondary_size)
        
        self.animation_finished.emit("hover" if self._is_hovering else "normal")
    
    def _on_primary_value_changed(self, value):
        """Callback cuando cambia el valor del botón primario"""
        if isinstance(value, QSize):
            secondary_width = self.secondary_button.width()
            self.frame_updated.emit(value.width(), secondary_width)
    
    def _on_secondary_value_changed(self, value):
        """Callback cuando cambia el valor del botón secundario"""
        if isinstance(value, QSize):
            primary_width = self.primary_button.width()
            self.frame_updated.emit(primary_width, value.width())
    
    def cleanup(self):
        """Limpiar recursos incluyendo timer"""
        try:
            # Cancelar timer de cierre si existe
            self._cancel_close_timer()
            
            # Detener animaciones de forma segura
            if hasattr(self, 'animation_group'):
                try:
                    self.animation_group.stop()
                except RuntimeError:
                    pass  # Ya fue eliminado por Qt
            
            # Remover event filter de AMBOS botones
            if hasattr(self, 'primary_button'):
                try:
                    self.primary_button.removeEventFilter(self)
                except RuntimeError:
                    pass  # Ya fue eliminado por Qt
                    
            if hasattr(self, 'secondary_button'):
                try:
                    self.secondary_button.removeEventFilter(self)
                except RuntimeError:
                    pass  # Ya fue eliminado por Qt
            
            # Limpiar referencias a animaciones
            for attr in ['primary_animation', 'primary_min_animation', 
                        'secondary_animation', 'secondary_min_animation',
                        'animation_group']:
                if hasattr(self, attr):
                    delattr(self, attr)
            
        except Exception as e:
            error(self.module_name, f"Error en cleanup: {str(e)}")
            log_exception(self.module_name, e, "cleanup")
    
    def enable_debug(self, enabled: bool = True):
        """Habilitar/deshabilitar debug - DEPRECATED: usar logger.set_debug_enabled()"""
        warning(self.module_name, "enable_debug() está deprecado, usar logger.set_debug_enabled()")
        from core.utils.logger import set_debug_enabled
        set_debug_enabled(enabled)
    
    def reset_if_stuck(self):
        """Método público para que los presenters resetten el estado si detectan problemas"""
        warning(self.module_name, "Reset manual solicitado desde presenter")
        self.force_reset_to_normal()
    
    def is_animating(self) -> bool:
        """Verificar si está animando"""
        return self._animation_running
    
    def _update_button_texts_for_hover(self):
        """Actualizar textos de botones para estado hover"""
        try:
            # Primary button: quitar texto, mantener solo icono
            self.primary_button.setText(self.primary_hover_text)
            
            # Secondary button: mostrar "Limpiar"
            self.secondary_button.setText(self.secondary_hover_text)
                
        except Exception as e:
            error(self.module_name, f"Error cambiando textos hover: {str(e)}")
            log_exception(self.module_name, e, "_update_button_texts_for_hover")
    
    def _update_button_texts_for_normal(self):
        """Restaurar textos de botones para estado normal"""
        try:
            # Primary button: restaurar texto original
            self.primary_button.setText(self.primary_normal_text)
            
            # Secondary button: restaurar texto original
            self.secondary_button.setText(self.secondary_normal_text)
                
        except Exception as e:
            error(self.module_name, f"Error restaurando textos: {str(e)}")
            log_exception(self.module_name, e, "_update_button_texts_for_normal")
    
    def set_text_configuration(self, 
                             primary_normal_text: str = None,
                             primary_hover_text: str = "",
                             secondary_normal_text: str = None,
                             secondary_hover_text: str = "Limpiar"):
        """Configurar textos personalizados para los botones"""
        if primary_normal_text is not None:
            self.primary_normal_text = primary_normal_text
        if primary_hover_text is not None:
            self.primary_hover_text = primary_hover_text
        if secondary_normal_text is not None:
            self.secondary_normal_text = secondary_normal_text
        if secondary_hover_text is not None:
            self.secondary_hover_text = secondary_hover_text
    
    def force_hover_state(self):
        """Forzar estado hover (para testing)"""
        self._is_hovering = True
        self._animate_to_hover()
    
    def force_normal_state(self):
        """Forzar estado normal (para testing)"""
        self._is_hovering = False
        self._animate_to_normal()
    
    def force_reset_to_normal(self):
        """Forzar reset completo al estado normal sin animación"""
        try:
            # Detener cualquier animación
            if hasattr(self, 'animation_group') and self._animation_running:
                self.animation_group.stop()
            
            # Resetear estado interno
            self._is_hovering = False
            self._animation_running = False
            
            # Establecer tamaños normales directamente
            height = max(self.primary_button.height(), 24)
            primary_size = QSize(self.primary_normal_width, height)
            secondary_size = QSize(self.secondary_normal_width, height)
            
            self.primary_button.setMinimumSize(primary_size)
            self.primary_button.setMaximumSize(primary_size)
            self.secondary_button.setMinimumSize(secondary_size)
            self.secondary_button.setMaximumSize(secondary_size)
            
            # Restaurar textos normales
            self._update_button_texts_for_normal()
                
        except Exception as e:
            error(self.module_name, f"Error en force_reset_to_normal: {str(e)}")
            log_exception(self.module_name, e, "force_reset_to_normal")