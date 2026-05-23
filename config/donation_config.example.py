"""
Plantilla de configuración de donaciones para Voxeprint.

INSTRUCCIONES:
1. Copia este archivo como `donation_config.py` en la misma carpeta.
2. Completa los valores con tus datos reales.
3. `donation_config.py` está en .gitignore — nunca se sube al repositorio.

Si este archivo NO existe, la sección de donaciones bancarias y ACH quedará
deshabilitada automáticamente en la aplicación. Solo la opción de cripto
(NOWPayments) seguirá disponible con la URL por defecto.
"""


class DonationConfig:
    """Configuración de plataformas de donación"""

    # =========================================================================
    # DONACIONES EN CRIPTOMONEDAS — NOWPayments
    # =========================================================================
    # 1. Crea una cuenta en https://nowpayments.io/
    # 2. Ve a https://nowpayments.io/donation-tools y crea tu enlace
    # 3. Pega el enlace aquí:
    NOWPAYMENTS_URL = "https://nowpayments.io/donation/TU_ENLACE_AQUI"

    NOWPAYMENTS_API_KEY = None  # Opcional

    ACCEPTED_CRYPTOS = ["BTC", "ETH", "USDT", "USDC", "BNB"]
    RECEIVE_CURRENCY = "USDT"
    RECEIVE_NETWORK = "TRC20"

    # =========================================================================
    # ACH / WIRE TRANSFERS (EE.UU.)
    # =========================================================================
    ACH_ENABLED = True

    ACH_ACCOUNT_HOLDER = "Tu Nombre Completo"
    ACH_BANK_NAME = "Nombre del Banco"
    ACH_ROUTING_NUMBER = "000000000"   # 9 dígitos
    ACH_ACCOUNT_NUMBER = "0000000000"
    ACH_ACCOUNT_TYPE = "Checking"      # Checking / Savings

    # =========================================================================
    # TRANSFERENCIAS BANCARIAS LOCALES
    # =========================================================================
    BANK_TRANSFERS_ENABLED = True

    ACCOUNT_HOLDER_NAME = "Tu Nombre Completo"
    ACCOUNT_HOLDER_CI = "0.000.000"

    # Banco local (SIPAP)
    LOCAL_BANK_NAME = "Bank Name"
    LOCAL_BANK_ALIAS = "00000000"
    LOCAL_BANK_ACCOUNT_NUMBER = "000000000"
    LOCAL_BANK_CURRENCY = "PYG"
    LOCAL_BANK_ENTITY = "Bank legal entity name"

    # =========================================================================
    # Métodos de utilidad (no modificar)
    # =========================================================================
    @classmethod
    def get_urls(cls):
        return {'nowpayments': cls.NOWPAYMENTS_URL or 'https://nowpayments.io/'}

    @classmethod
    def is_configured(cls):
        return bool(cls.NOWPAYMENTS_URL or cls.BANK_TRANSFERS_ENABLED)

    @classmethod
    def get_crypto_info(cls):
        return {
            'enabled': bool(cls.NOWPAYMENTS_URL),
            'url': cls.NOWPAYMENTS_URL,
            'accepted_cryptos': cls.ACCEPTED_CRYPTOS,
            'receive_currency': cls.RECEIVE_CURRENCY,
            'receive_network': cls.RECEIVE_NETWORK,
        }

    @classmethod
    def get_ach_info(cls):
        return {
            'ach_enabled': cls.ACH_ENABLED,
            'ach': {
                'holder':         cls.ACH_ACCOUNT_HOLDER,
                'bank':           cls.ACH_BANK_NAME,
                'routing_number': cls.ACH_ROUTING_NUMBER,
                'account_number': cls.ACH_ACCOUNT_NUMBER,
                'account_type':   cls.ACH_ACCOUNT_TYPE,
            },
        }

    @classmethod
    def get_bank_info(cls):
        return {
            'enabled': cls.BANK_TRANSFERS_ENABLED,
            'holder_name': cls.ACCOUNT_HOLDER_NAME,
            'holder_ci': cls.ACCOUNT_HOLDER_CI,
            'banks': [
                {
                    'name': cls.LOCAL_BANK_NAME,
                    'alias': cls.LOCAL_BANK_ALIAS,
                    'account_number': cls.LOCAL_BANK_ACCOUNT_NUMBER,
                    'currency': cls.LOCAL_BANK_CURRENCY,
                    'entity': cls.LOCAL_BANK_ENTITY,
                }
            ],
        }
