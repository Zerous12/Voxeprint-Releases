"""
Detección de configuración en el primer inicio de la aplicación.
Detecta el idioma y región del sistema operativo para aplicar defaults apropiados.
"""
import locale as _locale
from typing import Tuple


_SUPPORTED_LOCALES = {
    "AR", "AU", "BO", "BR", "CA", "CL", "CO",
    "ES", "HN", "MX", "NI", "PE", "PT", "PY",
    "US", "UY", "VE",
}

_DEFAULT_LOCALE_BY_LANG = {
    "es": "PY",
    "en": "US",
    "pt": "BR",
}

_SERVICE_LABELS = {
    "es": "Servicio de Impresión 3D",
    "en": "3D Printing Service",
    "pt": "Serviço de Impressão 3D",
}

_NOTE_TITLES = {
    "es": "Nota de Precios",
    "en": "Price Note",
    "pt": "Nota de Preços",
}

_QUOTE_TITLES = {
    "es": "PRESUPUESTO DE IMPRESIÓN 3D",
    "en": "3D PRINTING QUOTE",
    "pt": "ORÇAMENTO DE IMPRESSÃO 3D",
}

_DOC_TITLES = {
    "es": "PRESUPUESTO",
    "en": "QUOTE",
    "pt": "ORÇAMENTO",
}

_DOC_SUBTITLES = {
    "es": "Impresión 3D",
    "en": "3D Printing",
    "pt": "Impressão 3D",
}


def detect_system_defaults() -> Tuple[str, str, str]:
    """
    Detecta idioma y región del SO.

    Returns:
        (language, locale_code, service_label)
        language: 'es' | 'en' | 'pt'
        locale_code: código de país soportado (ej. 'PY', 'US', 'BR')
        service_label: etiqueta de servicio traducida
    """
    try:
        lang_code, _ = _locale.getdefaultlocale()
        if not lang_code or len(lang_code) < 2:
            return "es", "PY", _SERVICE_LABELS["es"]

        lang = lang_code[:2].lower()
        country = lang_code[3:5].upper() if len(lang_code) >= 5 else ""

        if lang == "pt":
            language = "pt"
        elif lang == "en":
            language = "en"
        else:
            language = "es"

        if country in _SUPPORTED_LOCALES:
            locale_code = country
        else:
            locale_code = _DEFAULT_LOCALE_BY_LANG[language]

        return language, locale_code, _SERVICE_LABELS[language]

    except Exception:
        return "es", "PY", _SERVICE_LABELS["es"]


def get_note_title(language: str) -> str:
    return _NOTE_TITLES.get(language, _NOTE_TITLES["es"])


def get_quote_title(language: str) -> str:
    return _QUOTE_TITLES.get(language, _QUOTE_TITLES["es"])


def get_doc_title(language: str) -> str:
    return _DOC_TITLES.get(language, _DOC_TITLES["es"])


def get_doc_subtitle(language: str) -> str:
    return _DOC_SUBTITLES.get(language, _DOC_SUBTITLES["es"])
