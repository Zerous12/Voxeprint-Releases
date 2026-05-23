from PySide6.QtCore import QTimer, QUrl, Signal, QObject, QUrlQuery
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
import sys, os
from pathlib import Path
from presentation.widgets.animation_mod.rotating_circle import WaitingCircle

class PdfViewerLoader(QObject):
    pdf_loaded = Signal()
    pdf_load_failed = Signal(str)
    pdf_print_requested = Signal()
    pdf_download_requested = Signal(object)

    def __init__(self, container_widget):
        super().__init__()        
        self.container = container_widget
        self.current_theme = "auto"  # auto, light, dark        
        # Crear el QWebEngineView
        self.webview = QWebEngineView()
        self.webview.setZoomFactor(1)
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.webview.page().settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)

        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)

        self.webview.page().printRequested.connect(lambda: self.pdf_print_requested.emit())
        self.webview.page().profile().downloadRequested.connect(self._handle_download_request)

        # Crear un layout si no existe
        if self.container.layout() is None:
            layout = QVBoxLayout(self.container)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            layout = self.container.layout()

        layout.addWidget(self.webview)
        # Mostrar el indicador de carga solo en el container  
        self.loading_indicator = WaitingCircle(parent=self.container)
        self.loading_indicator.hide()
        self.loading_indicator.superposition(True)
        self.loading_indicator.start()
        self.webview.loadFinished.connect(self._on_load_finished)

        self._pdf_loaded_ok = False
        self.pdf_viewer_path = self._resolve_viewer_path()

    def load_pdf(self, pdf_path: str):
        try:
            viewer_url = QUrl.fromLocalFile(str(self.pdf_viewer_path))
            pdf_url = QUrl.fromLocalFile(str(Path(pdf_path)))
            query = QUrlQuery()
            query.addQueryItem("file", pdf_url.toString(QUrl.FullyEncoded))
            query.addQueryItem("page", "1")
            viewer_url.setQuery(query)
            self.webview.load(viewer_url)
            # Force repaint inicial más temprano para evitar granulado
            QTimer.singleShot(50, self._force_repaint)
            # Y otro después para asegurar renderizado completo
            QTimer.singleShot(150, self._force_repaint)
        except Exception as e:
            self.load_error_viewer()
        finally:
            QTimer.singleShot(110, self.loading_indicator.stop)
 
    def load_error_viewer(self, error_msg=None):        
        html = """
        <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#b22222;font-family:sans-serif;'>
            <h2>❌ Error 404</h2>
            <p>Archivo PDF no encontrado.</p>
            <p>{error}</p>
        </div>
        """.format(error=error_msg or "Error desconocido.")
        self.webview.setHtml(html)

    def _on_load_finished(self, ok):        
        self._pdf_loaded_ok = bool(ok)
        if ok:
            # Force repaint después de que el PDF se cargue para evitar granulado
            QTimer.singleShot(80, self._force_repaint)
            # 🎯 Emitir señal - el tema se aplicará desde PDFViewer via señal
            self.pdf_loaded.emit()
        else:
            self.pdf_load_failed.emit("El loader no pudo cargar el PDF.")

    def _handle_download_request(self, download):
        """
        Maneja la solicitud de descarga del navegador.
        Emite la señal y acepta/rechaza según el resultado.
        """
        # Guardar referencia al objeto download
        self._pending_download = download
        
        # Emitir señal - el receptor debe indicar si permitir la descarga
        self.pdf_download_requested.emit(download)
    
    def accept_pending_download(self):
        """Acepta la descarga pendiente"""
        if hasattr(self, '_pending_download') and self._pending_download:
            self._pending_download.accept()
            self._pending_download = None
    
    def cancel_pending_download(self):
        """Cancela la descarga pendiente"""
        if hasattr(self, '_pending_download') and self._pending_download:
            self._pending_download.cancel()
            self._pending_download = None
    
    def _resolve_viewer_path(self) -> Path:
        """
        Devuelve Path absoluto a .../infrastructure/integrations/pdf_viewer_mod/web/viewer.html
        Funciona igual en dev y en binario (Nuitka standalone).
        """
        if getattr(sys, "frozen", False):
            base = Path(sys.executable).parent  # carpeta app.dist
            # la estructura se preserva por include-data-dir
            return base / "infrastructure" / "integrations" / "pdf_viewer_mod" / "web" / "viewer.html"
        else:
            # Este archivo vive en presentation/widgets/animation_mod/...
            here = Path(__file__).resolve()
            project_root = here.parents[4]  # ajusta niveles según tu layout real
            return project_root / "infrastructure" / "integrations" / "pdf_viewer_mod" / "web" / "viewer.html"

    def _force_repaint(self):
        """
        Fuerza el re-renderizado moviendo la ventana completa
        Más efectivo que cambiar el tamaño del widget para WebEngine
        """
        if self.webview:
            # Buscar la ventana padre que contiene el WebView
            parent_window = self.webview.window()
            
            if parent_window:
                current_pos = parent_window.pos()
                parent_window.move(current_pos.x() + 1, current_pos.y())
                
                QTimer.singleShot(10, lambda: parent_window.move(current_pos.x(), current_pos.y()))
            else:
                # Fallback: método original si no encuentra ventana padre
                self.webview.resize(self.webview.width()+1, self.webview.height())
                self.webview.resize(self.webview.width()-1, self.webview.height())
            

    def get_webview(self):
        return self.webview

    def force_repaint_public(self):
        """Método público para forzar repaint desde afuera"""
        self._force_repaint()

    def clean_cache(self):
        """
        Limpia la caché del visor PDF.
        """
        if self.webview:
            self.webview.page().profile().clearHttpCache()
            self.webview.page().profile().clearAllVisitedLinks()          

    def simulate_pdfjs_download(self):
        """
        Simula un click en el botón de descarga de PDF.js si el PDF está cargado correctamente.
        El callback recibe el resultado JS.
        """
        if not self._pdf_loaded_ok:           
            return
        js_code = """
            (function() {
                let downloadButton = document.querySelector('#download');
                if (downloadButton) {
                    downloadButton.click();
                    return 'Descarga iniciada.';
                } else {
                    return 'Botón de descarga no encontrado.';
                }
            })();
        """
        
        def handle_download_result(result):
            if result and "iniciada" in result:
                # Emitir la señal personalizada para que el presenter maneje la descarga
                self.pdf_download_requested.emit(None)
        
        self.webview.page().runJavaScript(js_code, handle_download_result)

    def simulate_pdfjs_print(self):
        """
        Simula un click en el botón de impresión de PDF.js si el PDF está cargado correctamente.
        """
        if not self._pdf_loaded_ok:           
            return
        js_code = """
            (function() {
                let printButton = document.querySelector('#print');
                if (printButton) {
                    printButton.click();
                    return 'Impresión iniciada.';
                } else {
                    return 'Botón de impresión no encontrado.';
                }
            })();
        """
        
        def handle_print_result(result):
            if result and "iniciada" in result:
                self.pdf_print_requested.emit()
        
        self.webview.page().runJavaScript(js_code, handle_print_result)

    def set_theme(self, theme_mode="auto"):
        """
        Cambia el tema del visor PDF usando nuestra modificación en viewer.js
        que permite temas personalizados.
        
        Args:
            theme_mode: 'auto', 'light', 'dark'
        """
        if not self._pdf_loaded_ok:
            # Guardar tema para aplicar después de cargar
            self.current_theme = theme_mode
            return
        
        # JavaScript simplificado que usa nuestra modificación en viewer.js
        theme_js = f"""
        (function() {{
            // Establecer el tema personalizado en window que nuestro viewer.js modificado detectará
            window.CUSTOM_PDF_THEME = '{theme_mode}';
            
            // Forzar la aplicación inmediata si PDFViewerApplication está disponible
            if (window.PDFViewerApplication && window.PDFViewerApplication._applyCssTheme) {{
                let themeValue;
                switch('{theme_mode}') {{
                    case 'dark':
                        themeValue = 2;
                        break;
                    case 'light': 
                        themeValue = 1;
                        break;
                    case 'auto':
                    default:
                        themeValue = 0;
                        break;
                }}
                
                window.PDFViewerApplication._applyCssTheme(themeValue);
                return `Tema aplicado: {theme_mode}`;
            }}
            
            return `Tema programado: {theme_mode}`;
        }})();
        """
        
        self.webview.page().runJavaScript(theme_js)
        self.current_theme = theme_mode

    def get_current_theme(self):
        """Retorna el tema actual del visor PDF"""
        return self.current_theme