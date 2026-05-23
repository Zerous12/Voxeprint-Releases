"""
Vista del panel de introducción usando el diseño UI
"""
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette
from presentation.modules.intro.designs.intro_ui import Ui_intro_panel


class IntroView(QWidget):
    """Vista del splash screen usando el diseño UI"""
    
    intro_success = Signal()  # Señal emitida cuando termina la carga
    
    def __init__(self):
        super().__init__()
        
        # Configurar ventana
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(486, 437)
        
        # Configurar UI
        self.ui = Ui_intro_panel()
        self.ui.setupUi(self)
        
        # Aplicar estilos después de configurar la UI
        self.apply_styles()
        
        # Centrar ventana
        self.center_window()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def apply_styles(self):
        """Aplica los estilos al widget después de configurar la UI"""
        # Estilo para el widget principal con imagen de fondo y fondo negro
        self.setStyleSheet(u"QWidget #intro_panel {\n"
        "background-color: #000000;\n"
        "background-image: url(:/resources/resources/images/voxeprint_logo.png);\n"
        "background-repeat: no-repeat;\n"
        "background-position: center;\n"
        "border: none;\n"
        "}\n"
        "\n"
        "QLabel {\n"
        "background-color: transparent;\n"
        "color: white;\n"
        "border: none;\n"
        "}\n"
        "")
        
        # Color del texto según tema del sistema
        palette = QApplication.palette()
        is_dark = palette.color(QPalette.ColorRole.Window).lightness() < 128
        text_color = "white" if is_dark else "#1A1A1A"
        self.ui.logo_loaded.setStyleSheet(f"color: {text_color};")

        # El progress bar mantiene su estilo por defecto (sin estilos personalizados)
        
    def update_progress(self, progress: int, message: str):
        """Actualiza el progreso y mensaje en la UI"""
        self.ui.progress_bar.setValue(progress)
        self.ui.logo_loaded.setText(message)
        QApplication.processEvents()  # Procesar eventos para actualizar UI
    
    def emit_success(self):
        """Emite la señal de éxito para cerrar el splash"""
        self.intro_success.emit()
    
    def mousePressEvent(self, event):
        """Permite arrastrar la ventana sin borde"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Maneja el arrastre de la ventana"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
