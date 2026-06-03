"""
Servicio de auto-actualización para Voxeprint3D
Verifica actualizaciones desde GitHub Releases
"""

import json
import platform
import subprocess
import sys
import urllib.request
import urllib.error
from typing import Optional, Dict, Tuple
from pathlib import Path
from config.build_config import BUILD_CONFIG
from core.utils.logger import logger
from core.managers.app_preferences_manager import AppPreferencesManager


def get_installer_info() -> Tuple[str, str]:
    """
    Obtiene el sufijo y extensión del instalador según el sistema operativo.
    
    Returns:
        Tuple: (sufijo_buscado_en_assets, nombre_archivo_descarga)
    """
    system = platform.system()
    
    if system == "Windows":
        return ("-Setup.exe", "Voxeprint-Update-Setup.exe")
    elif system == "Darwin":  # macOS
        return (".dmg", "Voxeprint-Update.dmg")
    else:  # Linux
        return (".AppImage", "Voxeprint-Update.AppImage")


class AutoUpdateService:
    """Servicio para verificar y notificar actualizaciones disponibles"""
    
    def __init__(self):
        self.current_version = BUILD_CONFIG.app.version
        self.current_build = BUILD_CONFIG.app.build_number
        self.update_url = BUILD_CONFIG.release.update_server
        self.download_url = BUILD_CONFIG.release.download_url
        self._preferences = AppPreferencesManager()
        
    def check_for_updates(self, use_cache: bool = True) -> Optional[Dict]:
        """
        Verifica si hay actualizaciones disponibles en GitHub Releases
        
        Args:
            use_cache: Si True, usa caché (automático). Si False, fuerza verificación (manual)
        
        Returns:
            Dict con información de actualización o None si no hay updates
            {
                'version': '1.2.0',
                'build': 120,
                'download_url': 'https://...',
                'release_notes': 'Changelog...',
                'is_newer': True,
                'from_cache': False
            }
        """
        # --- VERIFICAR CACHÉ ---
        if use_cache and not self._preferences.should_check_updates(cache_days=7):
            # Hay caché válido, verificar si la versión local cambió
            last_check, cached_info = self._preferences.get_update_cache()
            
            if cached_info:
                # Validar que la versión local no haya cambiado desde que se guardó el caché
                cached_app_version = cached_info.get('current_version')
                cached_app_build = cached_info.get('current_build')
                
                if cached_app_version == self.current_version and cached_app_build == self.current_build:
                    # La versión local es la misma, usar caché
                    logger.info("AutoUpdateService", f"Usando información de caché (última verificación: {last_check})")
                    cached_info['from_cache'] = True
                    return cached_info
                else:
                    # La versión local cambió (usuario actualizó), invalidar caché y verificar de nuevo
                    logger.info(
                        "AutoUpdateService", 
                        f"Versión local cambió ({cached_app_version} -> {self.current_version}), "
                        f"invalidando caché y verificando actualizaciones..."
                    )
        
        # --- HACER VERIFICACIÓN REAL ---
        try:
            logger.info("AutoUpdateService", f"Verificando actualizaciones desde {self.update_url}")
            
            # Hacer request a GitHub API
            request = urllib.request.Request(
                self.update_url,
                headers={'User-Agent': f'Voxeprint/{self.current_version}'}
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if not data:
                logger.warning("AutoUpdateService", "No se encontraron releases en GitHub")
                return None

            # Buscar el último release estable (saltar prereleases si hay estables)
            latest_release = None
            for release in data:
                if not release.get('prerelease', False):
                    latest_release = release
                    break
            if not latest_release:
                latest_release = data[0]
                logger.info("AutoUpdateService", "Solo hay prereleases disponibles, usando la más reciente")
            
            # Extraer información
            latest_version = latest_release.get('tag_name', '').lstrip('v')
            release_name = latest_release.get('name', '')
            release_notes = latest_release.get('body', 'No hay notas de la versión.')
            is_prerelease = latest_release.get('prerelease', False)
            published_at = latest_release.get('published_at', '')
            
            # Extraer build number del release name (si existe)
            # Ejemplo: "v1.2.0 (Build 120)"
            latest_build = self._extract_build_number(release_name)
            
            # Buscar el instalador en los assets según el sistema operativo
            installer_suffix, _ = get_installer_info()
            download_url = None
            
            for asset in latest_release.get('assets', []):
                if asset['name'].endswith(installer_suffix):
                    download_url = asset['browser_download_url']
                    break
            
            if not download_url:
                download_url = latest_release.get('html_url', self.download_url)
            
            # Comparar versiones
            is_newer = self._is_version_newer(latest_version, latest_build)
            
            update_info = {
                'version': latest_version,
                'build': latest_build,
                'download_url': download_url,
                'release_notes': release_notes,
                'release_name': release_name,
                'is_newer': is_newer,
                'is_prerelease': is_prerelease,
                'published_at': published_at,
                'current_version': self.current_version,
                'current_build': self.current_build,
                'from_cache': False
            }
            
            if is_newer:
                logger.info("AutoUpdateService", f"Nueva versión disponible: v{latest_version} (Build {latest_build})")
            else:
                logger.info("AutoUpdateService", f"✓ Estás usando la última versión: v{self.current_version}")
            
            # Guardar en caché
            self._preferences.set_update_cache(update_info)
            
            return update_info
            
        except urllib.error.HTTPError as e:
            if e.code == 403:
                logger.error("AutoUpdateService",
                    "Límite de GitHub API alcanzado (60 requests/hora). "
                    "Los updates se reintentarán automáticamente más tarde.")
            elif e.code == 404:
                logger.error("AutoUpdateService",
                    "URL de releases no encontrada. Verifica la configuración del repositorio.")
            else:
                logger.error("AutoUpdateService", f"Error HTTP {e.code} al verificar actualizaciones: {e}")
            return None
        except urllib.error.URLError as e:
            logger.error("AutoUpdateService", f"Error de conexión al verificar actualizaciones: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error("AutoUpdateService", f"Error al decodificar respuesta de GitHub: {e}")
            return None
        except Exception as e:
            logger.error("AutoUpdateService", f"Error inesperado al verificar actualizaciones: {e}")
            return None
    
    def _extract_build_number(self, release_name: str) -> Optional[int]:
        """Extrae el build number del nombre del release"""
        import re
        match = re.search(r'Build\s+(\d+)', release_name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def _is_version_newer(self, new_version: str, new_build: Optional[int] = None) -> bool:
        """
        Compara versiones para determinar si la nueva es más reciente
        
        Args:
            new_version: Versión nueva (ej: "1.2.0")
            new_build: Build number nuevo (opcional)
        
        Returns:
            True si la nueva versión es más reciente
        """
        try:
            # Convertir versiones a tuplas de enteros
            current_parts = tuple(map(int, self.current_version.split('.')))
            new_parts = tuple(map(int, new_version.split('.')))
            
            # Comparar versiones
            if new_parts > current_parts:
                return True
            elif new_parts == current_parts and new_build:
                # Si las versiones son iguales, comparar build numbers
                return new_build > self.current_build
            
            return False
            
        except (ValueError, AttributeError) as e:
            logger.warning("AutoUpdateService", f"Error al comparar versiones: {e}")
            return False
    
    def download_update(self, download_url: str, save_path: Optional[Path] = None) -> Optional[Path]:
        """
        Descarga el instalador de actualización
        
        Args:
            download_url: URL del instalador
            save_path: Ruta donde guardar (opcional)
        
        Returns:
            Path del archivo descargado o None si falló
        """
        try:
            if not save_path:
                import tempfile
                _, installer_name = get_installer_info()
                save_path = Path(tempfile.gettempdir()) / installer_name
            
            logger.info("AutoUpdateService", f"Descargando actualización desde {download_url}")
            logger.info("AutoUpdateService", f"Guardando en {save_path}")
            
            # Descargar archivo con timeout (urlretrieve no soporta timeout)
            req = urllib.request.Request(download_url, headers={
                'User-Agent': f'Voxeprint/{self.current_version}'
            })
            with urllib.request.urlopen(req, timeout=120) as response:
                with open(save_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
            
            logger.info("AutoUpdateService", f"Actualización descargada: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error("AutoUpdateService", f"Error al descargar actualización: {e}")
            return None
    
    def install_update(self, installer_path: Path) -> bool:
        """
        Ejecuta el instalador de actualización (multiplataforma)
        
        Args:
            installer_path: Ruta al instalador descargado
        
        Returns:
            True si se inició el instalador
        """
        try:
            system = platform.system()
            
            logger.info("AutoUpdateService", f"🚀 Iniciando instalador de actualización: {installer_path}")
            
            if system == "Windows":
                # Windows: ejecutar .exe directamente
                subprocess.Popen([str(installer_path)])
                
            elif system == "Darwin":  # macOS
                # macOS: montar .dmg y abrir
                subprocess.Popen(["open", str(installer_path)])
                
            else:  # Linux
                # Linux: hacer ejecutable el AppImage y ejecutar
                import os
                os.chmod(installer_path, 0o755)
                subprocess.Popen([str(installer_path)])
            
            logger.info("AutoUpdateService", "👋 Cerrando aplicación para actualizar...")
            
            # Nota: La aplicación debe cerrarse después de esto
            # Para hacerlo, puedes usar QApplication.quit() desde la UI
            
            return True
            
        except Exception as e:
            logger.error("AutoUpdateService", f"Error al iniciar instalador: {e}")
            return False


# Instancia global del servicio
UPDATE_SERVICE = AutoUpdateService()


def check_for_updates() -> Optional[Dict]:
    """Función de conveniencia para verificar actualizaciones"""
    return UPDATE_SERVICE.check_for_updates()


def get_update_info() -> Dict:
    """Obtiene información de actualización y versión actual"""
    return {
        'current_version': UPDATE_SERVICE.current_version,
        'current_build': UPDATE_SERVICE.current_build,
        'update_url': UPDATE_SERVICE.update_url,
        'download_url': UPDATE_SERVICE.download_url
    }
