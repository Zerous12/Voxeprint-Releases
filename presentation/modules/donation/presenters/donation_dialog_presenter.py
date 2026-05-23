"""
Presenter para el diálogo de donaciones
"""
import webbrowser
from PySide6.QtWidgets import QMessageBox

from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from presentation.modules.donation.views.donation_dialog_view import DonationDialogView


class DonationDialogPresenter:
    """Maneja la lógica del diálogo de donaciones"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.view = None
        
        # Cargar URLs desde el archivo de configuración
        self.urls = self._load_donation_urls()
        self.config_available = self._check_config_available()

    def _check_config_available(self) -> bool:
        """Verifica si donation_config.py está disponible."""
        try:
            from config.donation_config import DonationConfig  # noqa: F401
            return True
        except ImportError:
            return False
    
    def _load_donation_urls(self):
        """Carga las URLs de donación desde el archivo de configuración"""
        try:
            from config.donation_config import DonationConfig
            return DonationConfig.get_urls()
        except ImportError:
            logger.warning("DonationPresenter", "Archivo donation_config.py no encontrado. Usando URLs por defecto.")
            return {
                'nowpayments': 'https://nowpayments.io/'
            }
        except Exception as e:
            logger.error("DonationPresenter", f"Error cargando configuración de donaciones: {e}")
            return {
                'nowpayments': 'https://nowpayments.io/'
            }
    
    def run(self):
        """Ejecuta el diálogo de donaciones"""
        try:
            # Crear vista
            self.view = DonationDialogView(self.parent)
            
            # Conectar señales
            self.view.crypto_clicked.connect(self._handle_crypto)
            self.view.bank_transfer_clicked.connect(self._handle_bank_transfer)
            self.view.ach_transfer_clicked.connect(self._handle_ach_transfer)
            
            # Mostrar diálogo
            return self.view.exec()
            
        except Exception as e:
            logger.error("DonationPresenter", f"Error mostrando diálogo de donaciones: {e}")
            logger.log_exception("DonationPresenter", e, "run")
            return None
    
    def _handle_crypto(self):
        """Abre NOWPayments para donaciones en cripto"""
        try:
            webbrowser.open(self.urls['nowpayments'])
            # Abrir directamente sin mensaje de confirmación
        except Exception as e:
            logger.error("DonationPresenter", f"Error abriendo URL de cripto: {str(e)}", url=self.urls.get('nowpayments'))
            logger.log_exception("DonationPresenter", e, "_handle_crypto")
            self._show_error_message("No se pudo abrir el sistema de donaciones en criptomonedas.")
    
    def _handle_bank_transfer(self):
        """Muestra el diálogo de transferencias bancarias"""
        if not self.config_available:
            QMessageBox.information(
                self.view,
                tr(I18N.Donation.BANK_NOT_AVAILABLE_TITLE),
                tr(I18N.Donation.BANK_NOT_AVAILABLE)
            )
            return
        try:
            from presentation.modules.donation.views.bank_transfer_dialog_view import BankTransferDialogView
            bank_dialog = BankTransferDialogView(self.view)
            bank_dialog.exec()
        except Exception as e:
            logger.error("DonationPresenter", f"Error mostrando diálogo bancario: {str(e)}")
            logger.log_exception("DonationPresenter", e, "_handle_bank_transfer")
            self._show_error_message("No se pudo mostrar la información de transferencias bancarias.")

    def _handle_ach_transfer(self):
        """Muestra el diálogo de transferencias ACH/Zelle para USA"""
        if not self.config_available:
            QMessageBox.information(
                self.view,
                tr(I18N.Donation.ACH_NOT_AVAILABLE_TITLE),
                tr(I18N.Donation.ACH_NOT_AVAILABLE)
            )
            return
        try:
            from presentation.modules.donation.views.ach_transfer_dialog_view import AchTransferDialogView
            ach_dialog = AchTransferDialogView(self.view)
            ach_dialog.exec()
        except Exception as e:
            logger.error("DonationPresenter", f"Error mostrando diálogo ACH: {str(e)}")
            logger.log_exception("DonationPresenter", e, "_handle_ach_transfer")
            self._show_error_message("No se pudo mostrar la información de transferencias ACH.")
    
    def _show_thanks_message(self, platform):
        """Muestra mensaje de agradecimiento"""
        if self.view:
            QMessageBox.information(
                self.view,
                "¡Gracias! 💚",
                f"Se ha abierto {platform} en tu navegador.\n\n"
                "¡Gracias por considerar apoyar Voxeprint!"
            )
    
    def _show_error_message(self, error_msg):
        """Muestra mensaje de error"""
        if self.view:
            QMessageBox.critical(
                self.view,
                "Error",
                error_msg
            )
