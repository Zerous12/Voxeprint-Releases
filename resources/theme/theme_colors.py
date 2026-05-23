"""
Enumeraciones y constantes de colores para la aplicación
Recursos de tema - define los colores base del sistema de temas
"""
from enum import Enum
from PySide6.QtGui import QPalette, QColor


class ThemeMode(Enum):
    """Modos de tema disponibles"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Sigue configuración del sistema


class ColorRole(Enum):
    """Roles de colores en la paleta de la aplicación"""
    WINDOW = "window"
    WINDOW_TEXT = "windowText"
    BASE = "base"
    ALTERNATE_BASE = "alternateBase"
    TEXT = "text"
    BUTTON = "button"
    BUTTON_TEXT = "buttonText"
    BRIGHT_TEXT = "brightText"
    HIGHLIGHT = "highlight"
    HIGHLIGHTED_TEXT = "highlightedText"
    TOOLTIP_BASE = "toolTipBase"
    TOOLTIP_TEXT = "toolTipText"
    ACCENT = "accent"
    PLACEHOLDER_TEXT = "placeholderText"


class ThemeColors:
    """Constantes de colores para los temas de la aplicación"""
    
    # Paleta tema oscuro
    DARK_THEME = {
        ColorRole.WINDOW: "#1e1e1e",
        ColorRole.WINDOW_TEXT: "#FFFFFF",
        ColorRole.BASE: "#2d2d2d",        
        ColorRole.TEXT: "#FFFFFF",
        ColorRole.BUTTON: "#3C3C3C",
        ColorRole.BUTTON_TEXT: "#FFFFFF",
        ColorRole.BRIGHT_TEXT: "#FF0000",
        ColorRole.ALTERNATE_BASE: "#005799",
        ColorRole.HIGHLIGHT: "#42A5F5",
        ColorRole.HIGHLIGHTED_TEXT: "#FFFFFF",
        ColorRole.TOOLTIP_BASE: "#3C3C3C",
        ColorRole.TOOLTIP_TEXT: "#F2F2F2",
        ColorRole.ACCENT: "#41b8fa",
        ColorRole.PLACEHOLDER_TEXT: "#BABABA",
    }
    
    # Colores disabled para tema oscuro
    DARK_THEME_DISABLED = {
        ColorRole.WINDOW_TEXT: "#969696",
        ColorRole.TEXT: "#969696",
        ColorRole.BASE: "#262626",
        ColorRole.BUTTON: "#555555",
        ColorRole.BUTTON_TEXT: "#A0A0A0",
        ColorRole.HIGHLIGHT: "#5A5A5A",
        ColorRole.HIGHLIGHTED_TEXT: "#B0B0B0",
        ColorRole.PLACEHOLDER_TEXT: "#7d7d7c"
    }
    
    # Paleta tema claro
    LIGHT_THEME = {
        ColorRole.WINDOW: "#FFFFFF",
        ColorRole.WINDOW_TEXT: "#000000",
        ColorRole.BASE: "#F5F5F5",        
        ColorRole.TEXT: "#000000",
        ColorRole.BUTTON: "#E0E0E0",
        ColorRole.BUTTON_TEXT: "#000000",
        ColorRole.BRIGHT_TEXT: "#FF0000",
        ColorRole.ALTERNATE_BASE: "#E0E0E0",
        ColorRole.HIGHLIGHT: "#42A5F5",
        ColorRole.HIGHLIGHTED_TEXT: "#FFFFFF",
        ColorRole.TOOLTIP_BASE: "#FFFFF0",
        ColorRole.TOOLTIP_TEXT: "#000000",
        ColorRole.ACCENT: "#41b8fa",
        ColorRole.PLACEHOLDER_TEXT: "#BABABA",
    }
    
    # Colores disabled para tema claro
    LIGHT_THEME_DISABLED = {
        ColorRole.WINDOW_TEXT: "#5f5f5f",
        ColorRole.TEXT: "#5f5f5f",
        ColorRole.BASE: "#D0D0D0",
        ColorRole.BUTTON: "#E0E0E0",
        ColorRole.BUTTON_TEXT: "#A0A0A0",
        ColorRole.HIGHLIGHT: "#5A5A5A",
        ColorRole.HIGHLIGHTED_TEXT: "#B0B0B0",
        ColorRole.PLACEHOLDER_TEXT: "#7A7A7A"
    }
    
    # Mapeo a QPalette.ColorRole
    QT_COLOR_ROLE_MAPPING = {
        ColorRole.WINDOW: QPalette.ColorRole.Window,
        ColorRole.WINDOW_TEXT: QPalette.ColorRole.WindowText,
        ColorRole.BASE: QPalette.ColorRole.Base,
        ColorRole.ALTERNATE_BASE: QPalette.ColorRole.AlternateBase,
        ColorRole.TEXT: QPalette.ColorRole.Text,
        ColorRole.BUTTON: QPalette.ColorRole.Button,
        ColorRole.BUTTON_TEXT: QPalette.ColorRole.ButtonText,
        ColorRole.BRIGHT_TEXT: QPalette.ColorRole.BrightText,
        ColorRole.HIGHLIGHT: QPalette.ColorRole.Highlight,
        ColorRole.HIGHLIGHTED_TEXT: QPalette.ColorRole.HighlightedText,
        ColorRole.TOOLTIP_BASE: QPalette.ColorRole.ToolTipBase,
        ColorRole.TOOLTIP_TEXT: QPalette.ColorRole.ToolTipText,
        ColorRole.PLACEHOLDER_TEXT: QPalette.ColorRole.PlaceholderText,
    }
