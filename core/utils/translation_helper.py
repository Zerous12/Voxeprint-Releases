"""
Helper global de traducción para vistas y presentadores.

Uso:
    from core.utils.translation_helper import tr
    from core.utils.translation_keys import I18N

    self.view.lbl_status.setText(tr(I18N.StatusBar.LOADING))
    self.view.btn_save.setText(tr(I18N.Buttons.SAVE))
"""
from core.managers.language_manager import LanguageManager


def tr(key: str, **kwargs) -> str:
    """
    Traduce una clave usando el LanguageManager.

    Args:
        key: Clave de traducción (ej. "Buttons.save").
        **kwargs: Placeholders opcionales para interpolación.
    """
    return LanguageManager().tr(key, **kwargs)