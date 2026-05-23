"""
Gestor central de idiomas para Voxeprint

Proporciona un singleton para cargar, gestionar y permitir el cambio de idioma.
Basado en archivos JSON y compatible con packs ZIP de comunidad.
"""
import json
import os
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional, List

from core.utils.logger import logger


class LanguageManager:
    """Singleton para la carga y gestión de traducciones."""

    BUNDLED = ["es", "en", "pt"]
    FALLBACK = "es"

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._current = self.FALLBACK
        self._strings: Dict[str, str] = {}
        self._fallback_strings: Dict[str, str] = {}
        self._initialized = True

    def tr(self, key: str, **kwargs) -> str:
        """
        Traduce una clave. Fallback: idioma activo -> ES -> clave misma.
        Soporta placeholders via kwargs.
        """
        text = self._strings.get(key)
        if text is None:
            text = self._fallback_strings.get(key, key)
        if kwargs and '{' in text:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text

    def load_language(self, code: str) -> bool:
        """
        Carga un idioma desde translations/<code>.json o desde la carpeta packs.
        """
        if not code or not isinstance(code, str):
            return False

        code = code.strip()
        if not code:
            code = self.FALLBACK

        root_dir = self._get_base_dir()
        base_path = root_dir / "translations" / f"{code}.json"
        pack_dir = root_dir / "translations" / "packs"
        pack_json = pack_dir / f"{code}.json"

        resolved = None
        if base_path.exists():
            resolved = base_path
        elif pack_json.exists():
            resolved = pack_json
        else:
            # Intentar encontrar un .zip en packs que contenga el idioma
            if pack_dir.exists():
                for zip_candidate in pack_dir.iterdir():
                    if zip_candidate.suffix.lower() == ".zip":
                        try:
                            with zipfile.ZipFile(zip_candidate, 'r') as zf:
                                if f"{code}.json" in zf.namelist() or f"{code}/strings.json" in zf.namelist():
                                    # Extraer al directorio packs si no está extraído
                                    extracted_json = pack_dir / f"{code}.json"
                                    if not extracted_json.exists():
                                        zf.extractall(pack_dir)
                                    resolved = extracted_json
                                    break
                        except zipfile.BadZipFile:
                            continue

        if not resolved or not resolved.exists():
            logger.error("LanguageManager", f"No se encontró traducción para '{code}'")
            return False

        try:
            with open(resolved, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                logger.error("LanguageManager", f"Formato inválido en {resolved}")
                return False
            # Remover meta si existe
            data = {k: v for k, v in data.items() if not k.startswith("_")}
            self._strings = {k: str(v) for k, v in data.items()}
            self._current = code

            # Cargar fallback
            fallback_path = root_dir / "translations" / f"{self.FALLBACK}.json"
            if fallback_path.exists() and self.FALLBACK != code:
                with open(fallback_path, 'r', encoding='utf-8') as ff:
                    fb_data = json.load(ff)
                fb_data = {k: v for k, v in fb_data.items() if not k.startswith("_")}
                self._fallback_strings = {k: str(v) for k, v in fb_data.items()}
            else:
                self._fallback_strings = {}

            logger.info("LanguageManager", f"Idioma cargado: {code} ({len(self._strings)} claves)")
            return True
        except (json.JSONDecodeError, OSError) as e:
            logger.error("LanguageManager", f"Error cargando {resolved}: {e}")
            return False

    def available_languages(self) -> List[Dict[str, Any]]:
        """
        Lista los idiomas disponibles (bundled + packs instalados).
        """
        root_dir = self._get_base_dir()
        base_path = root_dir / "translations"
        codes = set(self.BUNDLED)

        # Buscar JSONs directos
        if base_path.exists():
            for f in base_path.iterdir():
                if f.suffix == ".json":
                    codes.add(f.stem)

        # Buscar en packs/ (jsons extraídos y zips)
        packs_base = base_path / "packs"
        if packs_base.exists():
            for f in packs_base.iterdir():
                if f.suffix == ".json":
                    codes.add(f.stem)
                elif f.suffix.lower() == ".zip":
                    try:
                        with zipfile.ZipFile(f, 'r') as zf:
                            names = zf.namelist()
                        for name in names:
                            if name.endswith(".json") and not name.startswith("_"):
                                codes.add(Path(name).stem)
                    except zipfile.BadZipFile:
                        continue

        result = []
        for code in sorted(codes):
            try:
                # Intentar obtener meta
                meta = self._get_language_meta(code)
                result.append({
                    "code": code,
                    "language": meta.get("language", code),
                    "version": meta.get("version", "1.0"),
                })
            except Exception:
                result.append({
                    "code": code,
                    "language": code,
                    "version": "1.0",
                })
        return result

    def install_pack(self, zip_path: str) -> bool:
        """Instala un pack .zip en translations/packs/. Valida estructura antes."""
        try:
            zip_path_obj = Path(zip_path)
            if not zip_path_obj.exists():
                return False
            dest_dir = self._get_base_dir() / "translations" / "packs"
            dest_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path_obj, 'r') as zf:
                zf.extractall(dest_dir)
            logger.info("LanguageManager", f"Pack instalado: {zip_path_obj.name}")
            return True
        except (zipfile.BadZipFile, OSError) as e:
            logger.error("LanguageManager", f"Error instalando pack: {e}")
            return False

    def current_language(self) -> str:
        return self._current

    # ---------- internos ----------
    def _get_base_dir(self) -> Path:
        """Devuelve el directorio raíz del proyecto (donde existe translations/)."""
        # Buscar a partir de este archivo hacia arriba hasta encontrar translations/
        current = Path(__file__).resolve().parent.parent
        while current.parent != current:
            if (current / "translations").exists():
                return current
            current = current.parent
        # Fallback a directorio actual del ejecutable/proyecto
        fallback = Path.cwd()
        return fallback

    def _get_language_meta(self, code: str) -> Dict[str, Any]:
        """Lee el bloque _meta del archivo JSON del idioma."""
        root_dir = self._get_base_dir()
        base_path = root_dir / "translations" / f"{code}.json"
        if base_path.exists():
            with open(base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("_meta", {})
        return {}