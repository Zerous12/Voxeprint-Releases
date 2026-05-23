"""
Presenter para el panel de introducción/splash screen
"""
from PySide6.QtCore import QObject, QTimer, QThread, Signal
from core.utils.logger import info, error, debug
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N


class LoadingWorker(QThread):
    """Worker thread para cargar la aplicación - ejecuta inicialización real"""
    
    progress_changed = Signal(int, str)  # progreso, mensaje
    loading_finished = Signal(bool)  # True si éxito, False si hubo error
    loading_error = Signal(str)  # mensaje de error
    
    def __init__(self):
        super().__init__()
        self._error_message = None
    
    def run(self):
        """Ejecuta la inicialización real de la aplicación"""
        try:
            # Paso 1: Crear estructura de directorios
            self.progress_changed.emit(5, tr(I18N.Intro.SETUP_DIRS))
            self._setup_directories()
            
            # Paso 2: Verificar/crear base de datos
            self.progress_changed.emit(15, tr(I18N.Intro.VERIFY_DB))
            self._setup_database()
            
            # Paso 3: Ejecutar migraciones si es necesario
            self.progress_changed.emit(30, tr(I18N.Intro.CHECK_MIGRATIONS))
            self._check_migrations()
            
            # Paso 4: Cargar configuraciones
            self.progress_changed.emit(50, tr(I18N.Intro.LOAD_CONFIG))
            self._load_configurations()
            
            # Paso 5: Inicializar servicios
            self.progress_changed.emit(70, tr(I18N.Intro.INIT_SERVICES))
            self._initialize_services()
            
            # Paso 6: Preparar interfaz
            self.progress_changed.emit(90, tr(I18N.Intro.PREPARE_UI))
            self._prepare_interface()
            
            # Listo
            self.progress_changed.emit(100, tr(I18N.Intro.READY))
            self.loading_finished.emit(True)
            
        except Exception as e:
            error("LoadingWorker", f"Error durante la inicialización: {str(e)}")
            self._error_message = str(e)
            self.progress_changed.emit(100, f"Error: {str(e)}")
            self.loading_error.emit(str(e))
            self.loading_finished.emit(False)
    
    def _setup_directories(self):
        """Crea la estructura de directorios necesaria"""
        try:
            from core.utils.path_helper import (
                database_path, pdfs_dir, logs_dir, 
                backups_dir, logos_dir, config_dir
            )
            # Cada función crea su directorio con mkdir(parents=True, exist_ok=True)
            database_path()
            pdfs_dir()
            logs_dir()
            backups_dir()
            logos_dir()
            config_dir()
            debug("LoadingWorker", "Directorios verificados/creados correctamente")
        except Exception as e:
            error("LoadingWorker", f"Error creando directorios: {e}")
            raise
    
    def _setup_database(self):
        """Verifica e inicializa la base de datos"""
        try:
            from infrastructure.database.initializer import setup_database
            setup_database()
            debug("LoadingWorker", "Base de datos verificada/inicializada")
        except Exception as e:
            error("LoadingWorker", f"Error inicializando base de datos: {e}")
            raise
    
    def _check_migrations(self):
        """Verifica y ejecuta migraciones pendientes"""
        try:
            from infrastructure.database.migrations.migrate_v1_0_to_v1_1 import run_migration_if_needed
            run_migration_if_needed()
            debug("LoadingWorker", "Migraciones verificadas")
        except ImportError:
            debug("LoadingWorker", "No hay migraciones pendientes")
        except Exception as e:
            error("LoadingWorker", f"Error en migraciones: {e}")
            # No lanzar excepción - migraciones fallidas no deben bloquear el inicio
    
    def _load_configurations(self):
        """Carga las configuraciones del sistema"""
        try:
            from core.managers.database_manager import get_db_manager
            db_manager = get_db_manager()
            debug("LoadingWorker", "Configuraciones cargadas desde base de datos")
        except Exception as e:
            error("LoadingWorker", f"Error cargando configuraciones: {e}")
            raise
    
    def _initialize_services(self):
        """Pre-inicializa los servicios principales"""
        try:
            from application.facades.voxeprint_facade import VoxeprintFacade
            # Solo verificar que se puede crear - la instancia real la crea MainPresenter
            debug("LoadingWorker", "Servicios verificados")
        except Exception as e:
            error("LoadingWorker", f"Error inicializando servicios: {e}")
            raise
    
    def _prepare_interface(self):
        """Prepara recursos para la interfaz"""
        try:
            from core.managers.quote_pdf_manager import QuotePDFManager
            # Precargar fuentes disponibles
            QuotePDFManager.get_available_fonts()
            debug("LoadingWorker", "Recursos de interfaz preparados")
        except Exception as e:
            error("LoadingWorker", f"Error preparando interfaz: {e}")
            # No crítico, continuar


class IntroPresenter(QObject):
    """Presenter para manejar la lógica del splash screen - Punto de entrada MVP"""
    
    intro_finished = Signal()  # Señal cuando termina la intro completamente
    
    def __init__(self):
        super().__init__()
        self.view = None
        self.worker = None
        self._loading_success = False
        
        # Crear la vista
        self.create_view()
        
        # Configurar conexiones
        self.setup_connections()
    
    def create_view(self):
        """Crea la vista del splash screen"""
        # Importar aquí para evitar import circular
        from presentation.modules.intro.views.intro_view import IntroView
        self.view = IntroView()
        
        # Conectar señales de la vista
        self.view.intro_success.connect(self.on_intro_complete)
    
    def setup_connections(self):
        """Configura las conexiones entre el worker y la vista"""
        self.worker = LoadingWorker()
        self.worker.progress_changed.connect(self.update_progress)
        self.worker.loading_finished.connect(self.on_loading_finished)
        self.worker.loading_error.connect(self._on_loading_error)
    
    def show(self):
        """Muestra la vista del splash screen"""
        if self.view:
            self.view.show()
            # Iniciar carga automáticamente
            QTimer.singleShot(300, self.start_loading)
    
    def start_loading(self):
        """Inicia el proceso de carga"""
        if self.worker:
            self.worker.start()
    
    def update_progress(self, progress: int, message: str):
        """Actualiza el progreso en la vista"""
        if self.view:
            self.view.update_progress(progress, message)
    
    def on_loading_finished(self, success: bool):
        """Se ejecuta cuando termina la carga"""
        self._loading_success = success

        if success:
            if self.view:
                self.view.update_progress(100, tr(I18N.Intro.READY))
            # Pausa breve para mostrar completado
            QTimer.singleShot(800, self.finish_loading)
        else:
            # Error en carga: cerrar splash primero, luego mostrar error
            QTimer.singleShot(500, self._handle_loading_failure)

    def _handle_loading_failure(self):
        """Cierra el splash y muestra el error crítico sin que el loading tape el diálogo"""
        from PySide6.QtWidgets import QMessageBox, QApplication
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl, Qt
        from core.utils.path_helper import logs_dir

        if self.view:
            self.view.close()
            self.view = None

        log_dir = logs_dir()

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(tr(I18N.Intro.ERROR_TITLE))
        msg.setText(tr(I18N.Intro.ERROR_TEXT))
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        btn_logs  = msg.addButton("Ver Logs",  QMessageBox.ButtonRole.ActionRole)
        btn_close = msg.addButton(tr(I18N.Dialogs.CLOSE),    QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(btn_close)

        msg.exec()

        if msg.clickedButton() == btn_logs:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_dir)))

        QApplication.instance().quit()
    
    def _on_loading_error(self, error_message: str):
        """Maneja errores durante la carga"""
        error("IntroPresenter", f"Error durante la carga: {error_message}")
        if self.view:
            self.view.update_progress(100, f"Error: {error_message}")
    
    def finish_loading(self):
        """Finaliza el proceso de carga"""
        if self.view:
            self.view.emit_success()  # Hace que la vista emita su señal
    
    def on_intro_complete(self):
        """Se ejecuta cuando la vista emite intro_success"""
        info("IntroPresenter", "Splash screen completado - Lanzando aplicación")
        self.intro_finished.emit()
        
    def close(self):
        """Cierra el presenter y su vista"""
        if self.worker:
            if self.worker.isRunning():
                self.worker.quit()
                self.worker.wait(3000)
            # Desconectar señales explícitamente antes de liberar para evitar crash de GC
            try:
                self.worker.progress_changed.disconnect()
                self.worker.loading_finished.disconnect()
                self.worker.loading_error.disconnect()
            except RuntimeError:
                pass
            self.worker.deleteLater()
            self.worker = None
        if self.view:
            self.view.close()
            self.view = None
