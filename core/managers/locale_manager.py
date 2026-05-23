"""
Gestor central de localización (locale) para Voxeprint

Carga perfiles de país desde locales/ y provee valores formateados
y adaptados a la región seleccionada (Tax ID, formato de fecha, moneda).
"""
import json
from pathlib import Path
from typing import Dict, Any, List

from core.utils.logger import logger


class LocaleManager:
    """Singleton para la carga y gestión de perfiles de localización."""

    DEFAULT = "PY"
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._current = self.DEFAULT
        self._data: Dict[str, Any] = {}
        self._initialized = True

        # Carga automática del default
        self.load_locale(self.DEFAULT)

    # ---------- Acceso rápido a valores del locale ----------

    def get_tax_id_label(self) -> str:
        return self._get_path("tax_id", "label", default="RUC/CI")

    def get_tax_id_placeholder(self) -> str:
        return self._get_path("tax_id", "placeholder", default="Ej: 12345678-9")

    def get_date_format(self) -> str:
        return self._get_path("formats", "date", default="dd/MM/yyyy")

    def get_date_format_strftime(self) -> str:
        """Convierte el formato Qt (dd/MM/yyyy) al formato Python strftime."""
        qt_fmt = self.get_date_format()
        return (qt_fmt
                .replace("yyyy", "%Y")
                .replace("yy", "%y")
                .replace("MM", "%m")
                .replace("dd", "%d"))

    def get_default_tax_rate(self) -> float:
        return self._get_path("business_terms", "tax_rate_default", default=10.0)

    def get_tax_name(self) -> str:
        return self._get_path("business_terms", "tax_name", default="IVA")

    def get_currency(self) -> str:
        return self._get_path("_meta", "currency", default="PYG")

    # ---------- Gestión de locale ----------

    def available_locales(self) -> List[Dict[str, Any]]:
        """Lista los perfiles de localización disponibles en locales/."""
        root_dir = self._get_base_dir()
        locales_dir = root_dir / "locales"
        results = []
        if not locales_dir.exists():
            return results

        for f in sorted(locales_dir.iterdir()):
            if f.suffix == ".json":
                try:
                    with open(f, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                    # Compatibilidad: _meta anidado (AR, PY…) o campos en raíz (BR, AU…)
                    meta = data.get("_meta") or {}
                    code = f.stem
                    country = meta.get("country") or data.get("country", code)
                    flag_icon = meta.get("flag_icon") or data.get("flag_icon", "sys_cif_" + code.lower())
                    currency = meta.get("currency") or data.get("currency", "")
                    results.append({
                        "code": code,
                        "country": country,
                        "flag_icon": flag_icon,
                        "currency": currency,
                    })
                except (json.JSONDecodeError, OSError):
                    continue
        return results

    def load_locale(self, code: str) -> bool:
        """Carga un perfil de locale desde locales/<code>.json."""
        if not code or not isinstance(code, str):
            return False

        code = code.strip().upper()
        if not code:
            code = self.DEFAULT

        root_dir = self._get_base_dir()
        file_path = root_dir / "locales" / f"{code}.json"
        fallback_path = root_dir / "locales" / f"{self.DEFAULT}.json"

        def read_json(p: Path) -> dict:
            if not p.exists():
                return {}
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)

        data = read_json(file_path)
        if not data and file_path != fallback_path:
            data = read_json(fallback_path)

        if not data:
            logger.error("LocaleManager", f"No se pudo cargar ningsun locale (ni fallback {self.DEFAULT})")
            return False

        self._data = data
        self._current = code
        logger.info("LocaleManager", f"Locale activo: {code}")
        return True

    def current_locale(self) -> str:
        return self._current

    # ---------- internos ----------

    def _get_base_dir(self) -> Path:
        current = Path(__file__).resolve().parent.parent
        while current.parent != current:
            if (current / "locales").exists():
                return current
            current = current.parent
        return Path.cwd()

    def _get_path(self, *keys: str, default=None):
        """Navega recursivamente por el diccionario del locale usando las claves dadas."""
        data = self._data
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, default)
            else:
                return default
        return data if data is not None else default