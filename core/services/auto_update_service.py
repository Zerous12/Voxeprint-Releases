"""
Servicio de auto-actualización para Voxeprint3D
Verifica actualizaciones desde GitHub Releases
"""

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
from typing import Optional, Dict, Tuple
from pathlib import Path
from config.build_config import BUILD_CONFIG
from core.utils.logger import logger
from core.managers.app_preferences_manager import AppPreferencesManager


def detect_linux_install_type() -> str:
    """
    Detecta cómo fue instalado Voxeprint en Linux.

    Orden de prioridad:
      1. Variable de entorno APPIMAGE  → fue lanzado como AppImage
      2. `rpm -q voxeprint` exitoso    → instalado con .rpm
      3. `dpkg -s voxeprint` exitoso   → instalado con .deb
      4. gestor de paquetes disponible (rpm > dpkg)
      5. Fallback: appimage

    Returns:
        'appimage' | 'deb' | 'rpm'
    """
    # 1. AppImage: la variable de entorno la setea el runtime de AppImage
    if os.environ.get('APPIMAGE'):
        return 'appimage'

    # 2. Consultar la base de datos del gestor de paquetes (más fiable que /etc/os-release)
    try:
        result = subprocess.run(
            ['rpm', '-q', 'voxeprint'],
            capture_output=True, timeout=5
        )
        if result.returncode == 0:
            return 'rpm'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        result = subprocess.run(
            ['dpkg', '-s', 'voxeprint'],
            capture_output=True, timeout=5
        )
        if result.returncode == 0:
            return 'deb'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 3. Gestor de paquetes disponible (cubre openSUSE, Mageia, Amazon Linux, etc.)
    if shutil.which('rpm'):
        return 'rpm'
    if shutil.which('dpkg'):
        return 'deb'

    # 4. Fallback
    return 'appimage'


def get_installer_info() -> Tuple[str, str]:
    """
    Obtiene el sufijo y extensión del instalador según el sistema operativo y tipo de instalación.

    Returns:
        Tuple: (sufijo_buscado_en_assets, nombre_archivo_descarga)
    """
    system = platform.system()

    if system == "Windows":
        return ("-Setup.exe", "Voxeprint-Update-Setup.exe")
    elif system == "Darwin":  # macOS
        return (".dmg", "Voxeprint-Update.dmg")
    else:  # Linux
        install_type = detect_linux_install_type()
        if install_type == 'deb':
            return ("-amd64.deb", "Voxeprint-Update-amd64.deb")
        elif install_type == 'rpm':
            return (".x86_64.rpm", "Voxeprint-Update-x86_64.rpm")
        else:  # appimage
            return ("-x86_64.AppImage", "Voxeprint-Update-x86_64.AppImage")


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
            download_size = None

            sha256_url = None
            installer_asset_name = None
            for asset in latest_release.get('assets', []):
                if asset['name'].endswith(installer_suffix):
                    installer_asset_name = asset['name']
                    download_url = asset['browser_download_url']
                    download_size = asset.get('size', 0)
                    break

            if installer_asset_name:
                for asset in latest_release.get('assets', []):
                    if asset['name'] == installer_asset_name + '.sha256':
                        sha256_url = asset['browser_download_url']
                        break

            if not download_url:
                download_url = latest_release.get('html_url', self.download_url)
            
            # Comparar versiones
            is_newer = self._is_version_newer(latest_version, latest_build)
            
            update_info = {
                'version': latest_version,
                'build': latest_build,
                'download_url': download_url,
                'download_size': download_size,
                'release_notes': release_notes,
                'release_name': release_name,
                'is_newer': is_newer,
                'is_prerelease': is_prerelease,
                'published_at': published_at,
                'current_version': self.current_version,
                'current_build': self.current_build,
                'sha256_url': sha256_url,
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
            # Validar formato antes de parsear (evita ValueError con tags como "2.0.0-beta")
            if not re.match(r'^\d+(\.\d+)*$', new_version):
                logger.warning("AutoUpdateService", f"Formato de versión no reconocido: {new_version}")
                return False
            if not re.match(r'^\d+(\.\d+)*$', self.current_version):
                logger.warning("AutoUpdateService", f"Versión actual con formato no reconocido: {self.current_version}")
                return False

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
    
    def download_update(self, download_url: str, save_path: Optional[Path] = None,
                         expected_size: Optional[int] = None,
                         sha256_url: Optional[str] = None) -> Optional[Path]:
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

            req = urllib.request.Request(download_url, headers={
                'User-Agent': f'Voxeprint/{self.current_version}'
            })
            with urllib.request.urlopen(req, timeout=120) as response:
                # Verificar Content-Type: rechazar páginas HTML de error de GitHub
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    logger.error("AutoUpdateService",
                        f"La URL devolvió HTML en lugar del instalador (Content-Type: {content_type}). "
                        "Puede ser una página de error de GitHub.")
                    return None

                with open(save_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

            # Verificar que el archivo descargado no esté vacío
            downloaded_size = save_path.stat().st_size
            if downloaded_size == 0:
                logger.error("AutoUpdateService", "El archivo descargado está vacío.")
                save_path.unlink(missing_ok=True)
                return None

            # Verificar tamaño contra el reportado por GitHub (si se pasó)
            if expected_size and expected_size > 0 and downloaded_size < expected_size:
                logger.error(
                    "AutoUpdateService",
                    f"Descarga truncada: {downloaded_size:,} bytes recibidos, "
                    f"{expected_size:,} bytes esperados. Archivo eliminado."
                )
                save_path.unlink(missing_ok=True)
                return None

            # Verificar integridad SHA256 (si el release publica el checksum)
            if sha256_url:
                if not self._verify_sha256(save_path, sha256_url):
                    save_path.unlink(missing_ok=True)
                    return None

            logger.info("AutoUpdateService",
                f"Actualización descargada: {save_path} ({downloaded_size:,} bytes)")
            return save_path

        except Exception as e:
            logger.error("AutoUpdateService", f"Error al descargar actualización: {e}")
            return None
    
    def _verify_sha256(self, file_path: Path, sha256_url: str) -> bool:
        """
        Descarga el checksum SHA256 publicado en GitHub y lo compara contra el archivo local.

        Returns:
            True si el hash coincide, False en caso contrario.
        """
        try:
            req = urllib.request.Request(
                sha256_url,
                headers={'User-Agent': f'Voxeprint/{self.current_version}'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                sha256_content = response.read().decode('utf-8').strip()

            if not sha256_content:
                logger.error("AutoUpdateService",
                    "El archivo SHA256 publicado está vacío. "
                    "No es posible verificar la integridad del instalador.")
                return False

            parts = sha256_content.split()
            if not parts:
                logger.error("AutoUpdateService",
                    "El archivo SHA256 tiene un formato no reconocido. "
                    "No es posible verificar la integridad del instalador.")
                return False

            # El archivo puede ser solo el hash o "<hash>  <filename>"
            expected_hash = parts[0].lower()

            if len(expected_hash) != 64 or not re.match(r'^[0-9a-f]{64}$', expected_hash):
                logger.error("AutoUpdateService",
                    f"El hash SHA256 publicado no tiene el formato esperado: {expected_hash!r}")
                return False

            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    sha256.update(chunk)
            actual_hash = sha256.hexdigest().lower()

            if actual_hash != expected_hash:
                logger.error(
                    "AutoUpdateService",
                    f"Verificación SHA256 fallida.\n"
                    f"  Esperado: {expected_hash}\n"
                    f"  Obtenido: {actual_hash}\n"
                    "El archivo puede estar corrupto o fue alterado."
                )
                return False

            logger.info("AutoUpdateService", f"SHA256 verificado correctamente: {actual_hash}")
            return True

        except Exception as e:
            logger.error("AutoUpdateService", f"Error al descargar o procesar el checksum SHA256: {e}")
            # El checksum fue publicado pero no se pudo verificar → cancelar para no instalar
            # un binario potencialmente corrupto o alterado.
            return False

    def install_update(self, installer_path: Path, new_version: Optional[str] = None) -> bool:
        """
        Ejecuta el instalador de actualización (multiplataforma).

        En Linux:
          - AppImage: genera un script bash que espera a que cierre la app, reemplaza
            el binario original y lo relanza. La app debe cerrarse tras retornar True.
          - .deb: usa dpkg -i (sin D-Bus).
          - .rpm: usa rpm -U (sin D-Bus).

        Args:
            installer_path: Ruta al instalador descargado
            new_version: Versión nueva (ej: '1.2.4') para renombrar el AppImage

        Returns:
            True si el proceso de actualización fue iniciado correctamente.
            La UI debe llamar QApplication.quit() inmediatamente después.
        """
        try:
            import os
            import shutil
            import tempfile
            system = platform.system()

            logger.info("AutoUpdateService", f"Iniciando instalador de actualización: {installer_path}")

            if system == "Windows":
                if not installer_path.exists():
                    logger.error("AutoUpdateService", f"El instalador no existe: {installer_path}")
                    return False
                subprocess.Popen([str(installer_path)])

            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", str(installer_path)])

            else:  # Linux
                install_type = detect_linux_install_type()

                if install_type == 'appimage':
                    if not self._install_appimage(installer_path, new_version=new_version):
                        return False
                    # AppImage: el script bash se encarga de relanzar la app

                elif install_type == 'deb':
                    if not self._install_deb(installer_path):
                        return False
                    # Tras dpkg, relanzar la app recién instalada
                    self._relaunch_after_package_install()

                else:  # rpm
                    if not self._install_rpm(installer_path):
                        return False
                    # Tras rpm/dnf, relanzar la app recién instalada
                    self._relaunch_after_package_install()

            logger.info("AutoUpdateService",
                "Proceso de actualización iniciado. La aplicación debe cerrarse ahora.")
            return True

        except Exception as e:
            logger.error("AutoUpdateService", f"Error al iniciar instalador: {e}")
            return False

    def _relaunch_after_package_install(self) -> None:
        """
        Relanza la aplicación después de instalar un .deb o .rpm.
        Busca el ejecutable por nombre en el PATH (lo registra el paquete en /usr/bin).
        Se lanza en sesión separada para que no sea hijo del proceso que está a punto
        de cerrarse con QApplication.quit().
        """
        executable = shutil.which(BUILD_CONFIG.app.data_dir_name)  # ej: "voxeprint"
        if not executable:
            logger.warning(
                "AutoUpdateService",
                f"No se encontró '{BUILD_CONFIG.app.data_dir_name}' en el PATH. "
                "Abre la aplicación manualmente para completar la actualización."
            )
            return
        try:
            subprocess.Popen([executable], start_new_session=True)
            logger.info("AutoUpdateService", f"Relanzando aplicación: {executable}")
        except Exception as e:
            logger.error("AutoUpdateService", f"Error al relanzar la aplicación: {e}")

    def _install_appimage(self, new_appimage: Path, new_version: Optional[str] = None) -> bool:
        """
        Reemplaza el AppImage actual mediante un script bash externo.
        El script espera a que cierre el proceso actual, reemplaza el binario y lo relanza.
        La app debe llamar QApplication.quit() tras este método.

        Returns:
            True si el script de actualización fue lanzado correctamente, False en caso contrario.
        """
        import os
        import stat

        original_appimage = os.environ.get('APPIMAGE', '')
        if not original_appimage:
            logger.error(
                "AutoUpdateService",
                "Variable APPIMAGE no encontrada. No es posible reemplazar el binario automáticamente. "
                f"El nuevo AppImage está disponible en: {new_appimage}. "
                "Ejecútalo manualmente para completar la actualización."
            )
            os.chmod(new_appimage, 0o755)
            return False

        # Verificar que el archivo descargado existe y no está vacío
        if not new_appimage.exists() or new_appimage.stat().st_size == 0:
            logger.error("AutoUpdateService",
                f"El AppImage descargado no existe o está vacío: {new_appimage}")
            return False

        # Hacer el nuevo AppImage ejecutable antes del reemplazo
        os.chmod(new_appimage, 0o755)

        current_pid = os.getpid()

        # Obtener directorio de logs para que el script pueda escribir diagnóstico
        try:
            from core.utils.path_helper import PathHelper
            log_dir = str(PathHelper.logs_dir())
        except Exception:
            log_dir = '/tmp'
        update_log = os.path.join(log_dir, 'appimage_update.log')

        import tempfile as _tempfile
        fd, script_path = _tempfile.mkstemp(prefix='voxeprint_update_', suffix='.sh')
        os.close(fd)
        script_file = Path(script_path)

        # Las rutas se pasan como variables de entorno para evitar inyección de comandos.
        # El script escribe cada paso en update_log para diagnóstico.
        script_content = """#!/bin/bash
# Script de actualización de Voxeprint - generado automáticamente
NEW_APPIMAGE="$VOXEPRINT_NEW_APPIMAGE"
ORIGINAL_APPIMAGE="$VOXEPRINT_ORIGINAL_APPIMAGE"
PID="$VOXEPRINT_PID"
LOG="$VOXEPRINT_UPDATE_LOG"
NEW_VERSION="$VOXEPRINT_NEW_VERSION"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [AppImage-Update] $1" >> "$LOG"
}

log "Script iniciado. PID a esperar: $PID"
log "Nuevo AppImage: $NEW_APPIMAGE"
log "AppImage original: $ORIGINAL_APPIMAGE"

# Verificar que el nuevo AppImage existe
if [ ! -f "$NEW_APPIMAGE" ]; then
    log "ERROR: El nuevo AppImage no existe en $NEW_APPIMAGE"
    exit 1
fi

# Esperar a que cierre la instancia actual
log "Esperando cierre del proceso $PID..."
while kill -0 "$PID" 2>/dev/null; do
    sleep 1
done
log "Proceso $PID terminado. Iniciando reemplazo."

# Reemplazar el AppImage copiando primero a un archivo temporal en el mismo directorio
DEST_DIR="$(dirname "$ORIGINAL_APPIMAGE")"
TMP_TARGET="$DEST_DIR/.voxeprint_update_tmp.AppImage"

cp "$NEW_APPIMAGE" "$TMP_TARGET"
if [ $? -ne 0 ]; then
    log "ERROR: cp falló al copiar $NEW_APPIMAGE -> $TMP_TARGET"
    exit 1
fi
log "Copia temporal exitosa: $TMP_TARGET"

mv -f "$TMP_TARGET" "$ORIGINAL_APPIMAGE"
if [ $? -ne 0 ]; then
    log "ERROR: mv falló al mover $TMP_TARGET -> $ORIGINAL_APPIMAGE"
    rm -f "$TMP_TARGET"
    exit 1
fi
log "Reemplazo exitoso: $ORIGINAL_APPIMAGE"

chmod +x "$ORIGINAL_APPIMAGE"
rm -f "$NEW_APPIMAGE"

# Renombrar el archivo para reflejar la nueva versión
# Reemplaza el primer bloque de dígitos separados por puntos en el nombre del archivo
FILENAME="$(basename "$ORIGINAL_APPIMAGE")"
RENAMED_FILENAME="$(echo "$FILENAME" | sed -E "s/[0-9]+\\.[0-9]+\\.[0-9]+(\\.[0-9]+)?/$NEW_VERSION/")"
RENAMED_APPIMAGE="$DEST_DIR/$RENAMED_FILENAME"

if [ "$RENAMED_FILENAME" != "$FILENAME" ] && [ -n "$NEW_VERSION" ]; then
    mv -f "$ORIGINAL_APPIMAGE" "$RENAMED_APPIMAGE"
    if [ $? -eq 0 ]; then
        log "Renombrado: $FILENAME -> $RENAMED_FILENAME"
        ORIGINAL_APPIMAGE="$RENAMED_APPIMAGE"
    else
        log "WARN: No se pudo renombrar, se usará el nombre original"
        ORIGINAL_APPIMAGE="$ORIGINAL_APPIMAGE"
    fi
else
    log "Renombrado omitido (sin cambio de nombre o versión no disponible)"
fi

log "Relanzando: $ORIGINAL_APPIMAGE"
APPIMAGE_EXTRACT_AND_RUN=1 "$ORIGINAL_APPIMAGE" &
log "Relanzamiento iniciado con PID $!"

# Autoeliminarse
rm -f "$0"
"""

        script_file.write_text(script_content)
        script_file.chmod(script_file.stat().st_mode | stat.S_IEXEC)

        subprocess.Popen(
            [str(script_file)],
            start_new_session=True,
            env={
                **os.environ,
                'VOXEPRINT_NEW_APPIMAGE': str(new_appimage),
                'VOXEPRINT_ORIGINAL_APPIMAGE': original_appimage,
                'VOXEPRINT_PID': str(current_pid),
                'VOXEPRINT_UPDATE_LOG': update_log,
                'VOXEPRINT_NEW_VERSION': new_version or '',  # versión nueva para renombrar el archivo
            }
        )
        logger.info("AutoUpdateService",
            f"Script de actualización AppImage lanzado. "
            f"Reemplazará {original_appimage} al cerrarse la app. "
            f"Log del script: {update_log}")
        return True

    def _get_privilege_escalator(self) -> Optional[str]:
        """
        Devuelve el escalador de privilegios disponible en el sistema.
        Prioridad: pkexec (diálogo gráfico) > sudo (terminal).
        Retorna None si no hay ninguno.
        """
        import shutil
        for tool in ('pkexec', 'sudo'):
            if shutil.which(tool):
                return tool
        return None

    def _install_deb(self, deb_path: Path) -> bool:
        """
        Instala el .deb usando dpkg -i con pkexec o sudo para elevar privilegios.

        Se usa dpkg en lugar de apt/apt-get para evitar que pkexec intente comunicarse
        con aptdaemon vía D-Bus, lo que causa el error
        "org.freedesktop.DBus.Error.NoReply" en Ubuntu/Mint con entornos GUI.
        dpkg es suficiente para paquetes autocontenidos (PyInstaller).

        Returns:
            True si la instalación fue exitosa, False en caso contrario.
        """
        escalator = self._get_privilege_escalator()
        if not escalator:
            logger.error(
                "AutoUpdateService",
                f"No se encontró pkexec ni sudo. Instala manualmente con:\n"
                f"  sudo dpkg -i {deb_path}"
            )
            return False

        # dpkg -i no usa D-Bus ni aptdaemon, evita el error de aptkit en Linux Mint/Ubuntu.
        # subprocess.run() (bloqueante) mantiene la app viva mientras pkexec muestra
        # el diálogo de autenticación.
        cmd = [escalator, 'dpkg', '-i', str(deb_path)]
        logger.info("AutoUpdateService", f"Ejecutando: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            logger.error("AutoUpdateService",
                f"Instalación .deb falló con código {result.returncode}. "
                f"Intenta manualmente: sudo dpkg -i {deb_path}")
            return False
        return True

    def _install_rpm(self, rpm_path: Path) -> bool:
        """
        Instala el .rpm usando dnf (preferred, maneja dependencias) o rpm -U como fallback.
        Usa pkexec o sudo para elevar privilegios.

        Returns:
            True si el proceso de instalación fue iniciado, False en caso contrario.
        """
        import shutil

        escalator = self._get_privilege_escalator()
        if not escalator:
            logger.error(
                "AutoUpdateService",
                f"No se encontró pkexec ni sudo. Instala manualmente con:\n"
                f"  sudo dnf install -y {rpm_path}"
            )
            return False

        # Usar rpm -U directamente (equivalente a dpkg -i para .rpm).
        # Evita que dnf/zypper intenten comunicarse con PackageKit vía D-Bus,
        # lo que causaría el mismo error de "NoReply" que aptdaemon en sistemas Debian.
        # Para paquetes autocontenidos (PyInstaller) rpm -U es suficiente.
        # subprocess.run() (bloqueante) mantiene la app viva mientras pkexec
        # muestra el diálogo de autenticación.
        rpm_path_str = str(rpm_path)
        if shutil.which('rpm'):
            cmd = [escalator, 'rpm', '-U', rpm_path_str]
        elif shutil.which('dnf'):  # Fallback si rpm no está disponible
            cmd = [escalator, 'dnf', 'install', '-y', rpm_path_str]
        elif shutil.which('zypper'):  # openSUSE fallback
            cmd = [escalator, 'zypper', '--non-interactive', 'install', rpm_path_str]
        else:
            logger.error("AutoUpdateService",
                f"No se encontró rpm, dnf ni zypper. Instala manualmente: sudo rpm -U {rpm_path_str}")
            return False
        logger.info("AutoUpdateService", f"Ejecutando: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            logger.error("AutoUpdateService",
                f"Instalación .rpm falló con código {result.returncode}. "
                f"Intenta manualmente: sudo {cmd[1]} install -y {rpm_path_str}")
            return False
        return True


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
