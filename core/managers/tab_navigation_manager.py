"""
Gestor de navegación por teclado para elementos de UI.

Este módulo maneja la navegación personalizada por teclado entre widgets,
definiendo órdenes de tabulación y comportamientos especiales.
"""

from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QLineEdit, QComboBox, QPushButton
from typing import List, Any
from core.utils.logger import logger


class TabNavigationManager(QObject):
    """
    Gestiona la navegación por teclado entre widgets en una interfaz.
    
    Características:
    - Define orden de tabulación personalizado
    - Maneja navegación con Enter/Return
    - Soporte especial para QComboBox
    - Estilos visuales para indicar foco
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.widgets: List[Any] = []

    def set_tab_order(self, *widgets):
        """
        Establece el orden de tabulación para los widgets.
        
        Args:
            *widgets: Secuencia de widgets en orden de tabulación
        """
        # Configurar orden de tabulación nativo de Qt
        for i in range(len(widgets) - 1):
            self.parent.setTabOrder(widgets[i], widgets[i + 1])
            
        self.widgets = list(widgets)
        self._setup_keyboard_navigation()

    def _setup_keyboard_navigation(self):
        """Configura la navegación por teclado para todos los widgets."""
        for widget in self.widgets:
            if isinstance(widget, (QLineEdit, QPushButton, QComboBox)):
                widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Maneja eventos de teclado y foco para navegación personalizada."""
        try:
            # Verificar que el objeto sigue siendo válido
            if not self._is_widget_valid(obj):
                return super().eventFilter(obj, event)
                
            # Manejo de estilos de foco para QComboBox
            if isinstance(obj, QComboBox):
                self._handle_combobox_focus_styling(obj, event)

            # Manejo de tecla Enter/Return
            if event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter):
                return self._handle_return_key_press(obj)
                
        except RuntimeError as e:
            logger.error("TabNavigationManager", f"RuntimeError en TabNavigationManager.eventFilter: {e}")
        except Exception as e:
            logger.error("TabNavigationManager", f"Error en TabNavigationManager.eventFilter: {e}")
            
        return super().eventFilter(obj, event)

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

    def _handle_combobox_focus_styling(self, combobox: QComboBox, event):
        """Aplica estilos visuales cuando un QComboBox recibe o pierde el foco."""
        if event.type() == QEvent.FocusIn:
            combobox.setStyleSheet("QComboBox { border: 1px solid #ffaa00; }")
        elif event.type() == QEvent.FocusOut:
            combobox.setStyleSheet("QComboBox { border: 1px solid #21252b; }")

    def _handle_return_key_press(self, widget) -> bool:
        """
        Maneja la pulsación de Enter/Return en diferentes tipos de widgets.
        
        Args:
            widget: Widget que recibió la pulsación de tecla
            
        Returns:
            True si el evento fue manejado, False en caso contrario
        """
        if isinstance(widget, QComboBox):
            return self._handle_combobox_return(widget)
        elif isinstance(widget, QPushButton):
            widget.click()
            return True
        else:
            self._navigate_to_next_widget(widget)
            return True

    def _handle_combobox_return(self, combobox: QComboBox) -> bool:
        """Maneja Enter/Return específicamente para QComboBox."""
        if combobox.view().isVisible():
            # Lista desplegable visible: seleccionar elemento actual
            combobox.setCurrentIndex(combobox.currentIndex())
            self._navigate_to_next_widget(combobox)
        else:
            # Lista no visible: abrir dropdown
            combobox.showPopup()
        return True

    def _navigate_to_next_widget(self, current_widget):
        """Navega al siguiente widget en el orden de tabulación."""
        if current_widget in self.widgets:
            current_index = self.widgets.index(current_widget)
            next_index = (current_index + 1) % len(self.widgets)
            next_widget = self.widgets[next_index]
            
            # Verificar que el siguiente widget es válido antes de darle foco
            if self._is_widget_valid(next_widget):
                try:
                    next_widget.setFocus()
                except RuntimeError:
                    logger.warning("TabNavigationManager", "No se pudo enfocar widget - ya fue eliminado")

    def cleanup(self):
        """
        Limpia los recursos y remove event filters para evitar errores de memoria.
        """
        try:
            for widget in self.widgets:
                if self._is_widget_valid(widget):
                    widget.removeEventFilter(self)
            self.widgets.clear()
        except RuntimeError:
            # Los objetos ya fueron destruidos
            pass
        except Exception as e:
            logger.error("TabNavigationManager", f"Error durante cleanup de TabNavigationManager: {e}")

    def __del__(self):
        """Destructor para asegurar limpieza de recursos."""
        self.cleanup()
