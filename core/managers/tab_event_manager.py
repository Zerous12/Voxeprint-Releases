"""
Gestores de eventos para pestañas (QTabWidget).
"""

from PySide6.QtCore import QObject, QEvent, Qt, QTimer
from PySide6.QtWidgets import QLineEdit, QComboBox, QPushButton
from dataclasses import dataclass
from typing import Callable, Optional
from core.utils.logger import logger


@dataclass
class TabManagerConfig:
    """Configuración para el gestor de pestañas."""
    tab_name: str 
    tab_widget: object
    refresh_button: object
    tab_action_callback: Optional[Callable] = None
    refresh_callback: Optional[Callable] = None
    cooldown_time: int = 2000


class TabWidgetEventManager(QObject):
    """
    Gestiona los eventos de cambio de pestaña y doble clic en QTabWidget.
    
    Características:
    - Maneja cambios de pestaña con refresh automático (sujeto a cooldown)
    - Detecta doble clic para refrescar manual
    - Implementa cooldown para evitar spam de eventos
    - Gestiona eventos de movimiento de pestañas
    """
    
    def __init__(self, config: TabManagerConfig):
        super().__init__()
        self.config = config
        self.tab_widget = config.tab_widget
        self.refresh_button = config.refresh_button
        self.tab_action_callback = config.tab_action_callback
        self.refresh_callback = config.refresh_callback
        self.cooldown_time = config.cooldown_time

        self.previous_tab_index = -1
        self.tabwidget_is_moving = False
        self._is_destroyed = False

        self._setup_cooldown_timer()
        self._setup_tab_events()

    def _is_widget_valid(self, widget) -> bool:
        """
        Verifica si un widget sigue siendo válido (no ha sido eliminado).
        
        Args:
            widget: Widget a verificar
            
        Returns:
            True si el widget es válido, False si ha sido eliminado
        """
        try:
            if widget is None:
                return False
            # Intentar acceder a una propiedad básica para verificar validez
            _ = widget.objectName()
            return True
        except RuntimeError:
            # RuntimeError se lanza cuando el objeto C++ subyacente ha sido eliminado
            return False
        except Exception:
            # Cualquier otra excepción también indica que el widget no es válido
            return False

    def _safe_get_tab_bar(self):
        """
        Obtiene el tab bar de manera segura.
        
        Returns:
            QTabBar si es válido, None si no
        """
        if not self._is_widget_valid(self.tab_widget):
            return None
        try:
            return self.tab_widget.tabBar()
        except RuntimeError:
            return None

    def _setup_cooldown_timer(self):
        """Configura el timer de cooldown para evitar spam de eventos."""
        self.cooldown_timer = QTimer(self)
        self.cooldown_timer.setSingleShot(True)

    def _setup_tab_events(self):
        """Configura todos los event listeners de las pestañas."""
        tab_bar = self._safe_get_tab_bar()
        if not tab_bar:
            logger.warning("TabEventManager", "No se pudo configurar eventos de tab - widget no válido")
            return
            
        tab_bar.installEventFilter(self)
        
        # Conectar señales del tab bar
        tab_bar.tabMoved.connect(self._on_tab_moved)
        
        # Conectar botón de refresh si existe
        if self.refresh_button and self._is_widget_valid(self.refresh_button):
            self.refresh_button.clicked.connect(self.refresh_current_tab)
        
        # Conectar eventos del tab widget
        if self._is_widget_valid(self.tab_widget):
            self.tab_widget.currentChanged.connect(self._on_tab_changed)
            self.tab_widget.tabBarDoubleClicked.connect(self.refresh_current_tab)

    def refresh_current_tab(self):
        """
        Refresca la pestaña actual via doble click (siempre disponible).
        Implementa cooldown para evitar múltiples llamadas rápidas.
        """
        if self.cooldown_timer.isActive():
            return
            
        if self.refresh_callback:
            logger.debug("TabEventManager", "Refresh manual solicitado", accion="doble click")
            self.refresh_callback()
            
        self.cooldown_timer.start(self.cooldown_time)

    def _on_tab_changed(self, index: int):
        """
        Maneja el cambio de pestaña con refresh automático.
        Refresca cada vez que se cambia a una pestaña de inventario.
        """
        if not self.tabwidget_is_moving or index != self.previous_tab_index:            
            self._handle_tab_focus_change(index)
            
            # Solo pestañas que necesitan refresh de inventario (con cooldown para evitar spam)
            inventory_tabs = {1, 2, 3, 4}
            tab_names = {1: "Historial", 2: "Inventario", 3: "Impresoras", 4: "Clientes"}
            
            if index in inventory_tabs and self.refresh_callback and not self.cooldown_timer.isActive():
                tab_name = tab_names.get(index, f"Tab {index}")
                logger.debug("TabEventManager", "Auto-refresh aplicado", tab=tab_name)
                self.refresh_callback()
                self.cooldown_timer.start(self.cooldown_time)

    def _on_tab_moved(self, from_index: int, to_index: int):
        """Maneja el movimiento de pestañas."""
        self._handle_tab_focus_change(to_index)

    def _handle_tab_focus_change(self, index_to: int):
        """
        Maneja el cambio de foco entre pestañas.
        
        Args:
            index_to: Índice de la pestaña de destino
        """
        if index_to != self.previous_tab_index and self._is_widget_valid(self.tab_widget):
            try:
                current_tab_widget = self.tab_widget.currentWidget()
                if self.tab_action_callback and current_tab_widget:
                    self.tab_action_callback(current_tab_widget)
                self.previous_tab_index = index_to
            except RuntimeError:
                # Widget eliminado durante la operación
                logger.warning("Warning: Tab widget eliminado durante cambio de foco")

    def eventFilter(self, obj, event):
        """Filtra eventos para detectar movimiento de pestañas."""
        try:
            # Verificar que el tab widget aún es válido
            if not self._is_widget_valid(self.tab_widget):
                return super().eventFilter(obj, event)
                
            tab_bar = self._safe_get_tab_bar()
            if obj == tab_bar and tab_bar is not None:
                if event.type() == QEvent.MouseButtonPress:
                    self.tabwidget_is_moving = True
                elif event.type() == QEvent.MouseButtonRelease:
                    self.tabwidget_is_moving = False
        except RuntimeError as e:
            logger.warning("TabEventManager", f"RuntimeError en TabWidgetEventManager.eventFilter: {e}")
        except Exception as e:
            logger.warning("TabEventManager", f"Error en TabWidgetEventManager.eventFilter: {e}")

        return super().eventFilter(obj, event)

    def cleanup(self):
        """
        Limpia los recursos y desconecta señales para evitar errores de memoria.
        Debe ser llamado antes de que el objeto sea destruido.
        """
        try:
            if self._is_widget_valid(self.tab_widget):
                tab_bar = self._safe_get_tab_bar()
                if tab_bar:
                    tab_bar.removeEventFilter(self)
                
                # Desconectar señales
                self.tab_widget.currentChanged.disconnect()
                self.tab_widget.tabBarDoubleClicked.disconnect()
                
            if self.refresh_button and self._is_widget_valid(self.refresh_button):
                self.refresh_button.clicked.disconnect()
                
            if self.cooldown_timer:
                self.cooldown_timer.stop()
                
            self._is_destroyed = True
            
        except RuntimeError:
            # Los objetos ya fueron destruidos, no hay nada que limpiar
            pass
        except Exception as e:
            logger.error("TabEventManager", f"Error durante cleanup de TabWidgetEventManager: {e}")

    def __del__(self):
        """Destructor para asegurar limpieza de recursos."""
        self.cleanup()
