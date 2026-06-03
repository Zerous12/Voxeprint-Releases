"""
Servicio de restauración y gestión avanzada de backups de base de datos.
Maneja restauración, validación de versiones, estadísticas y migraciones.
"""

import os
import platform
import re
import shutil
import sqlite3
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field

from config.app_config import APP_CONFIG
from core.utils.path_helper import backups_dir, database_path
from core.utils.logger import logger


@dataclass
class BackupInfo:
    """Información detallada de un archivo de backup"""
    filename: str
    filepath: str
    date: Optional[datetime.datetime] = None
    size_bytes: int = 0
    size_mb: float = 0.0
    db_version: Optional[str] = None
    is_compatible: bool = False
    compatibility_reason: str = ""
    record_counts: Dict[str, int] = field(default_factory=dict)


@dataclass
class DatabaseStats:
    """Estadísticas de la base de datos actual"""
    db_version: str = ""
    db_path: str = ""
    db_size_bytes: int = 0
    db_size_mb: float = 0.0
    schema_version: int = 0
    record_counts: Dict[str, int] = field(default_factory=dict)
    total_records: int = 0
    total_backups: int = 0
    last_backup_date: Optional[datetime.datetime] = None
    backup_enabled: bool = False
    backup_frequency_days: int = 7
    created_at: Optional[str] = None


class DatabaseRestoreService:
    """
    Servicio para restauración de backups y gestión avanzada de base de datos.
    
    Responsabilidades:
    - Crear backups con información de versión
    - Listar backups disponibles con metadatos
    - Validar compatibilidad de versión antes de restaurar
    - Restaurar backups validados
    - Obtener estadísticas de la base de datos
    - Gestionar migraciones secuenciales
    """
    
    # Patrón para backups con versión: voxeprint_backup_vX.Y_YYYYMMDD_HHMMSS.db
    BACKUP_PATTERN_VERSIONED = re.compile(
        r'^voxeprint_backup_v([\d.]+)_(\d{8})_(\d{6})\.db$'
    )
    # Patrón para backups legacy: voxeprint_backup_YYYYMMDD_HHMMSS.db
    BACKUP_PATTERN_LEGACY = re.compile(
        r'^voxeprint_backup_(\d{8})_(\d{6})\.db$'
    )
    # Patrón para backups de pre-migración
    BACKUP_PATTERN_MIGRATION = re.compile(
        r'^voxeprint_.*pre.*_(\d{8})_(\d{6})\.db$'
    )
    
    def __init__(self):
        self.backup_dir = str(backups_dir())
        self.current_db_path = str(database_path())
        self.current_version = APP_CONFIG.database.current_version
    
    # ========================================================================
    # CREACIÓN DE BACKUPS (con versión)
    # ========================================================================
    
    def create_versioned_backup(self, label: str = "") -> Dict[str, Any]:
        """
        Crea un backup con la versión de la BD en el nombre del archivo.
        
        Args:
            label: Etiqueta opcional para el backup (ej: 'pre_migration')
            
        Returns:
            dict con 'success', 'backup_path', 'message'
        """
        result = {'success': False, 'backup_path': None, 'message': ''}
        
        try:
            if not os.path.exists(self.current_db_path):
                result['message'] = 'La base de datos actual no existe'
                return result
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if label:
                filename = f"voxeprint_backup_v{self.current_version}_{label}_{timestamp}.db"
            else:
                filename = f"voxeprint_backup_v{self.current_version}_{timestamp}.db"
            
            backup_path = os.path.join(self.backup_dir, filename)
            
            # Copiar archivo de base de datos
            shutil.copy2(self.current_db_path, backup_path)
            
            if os.path.exists(backup_path):
                size_mb = os.path.getsize(backup_path) / (1024 * 1024)
                result['success'] = True
                result['backup_path'] = backup_path
                result['message'] = f'Backup creado: {filename} ({size_mb:.2f} MB)'
                logger.info("DatabaseRestore", f"Backup versionado creado: {backup_path}")
            else:
                result['message'] = 'Error: no se pudo crear el archivo de backup'
                
        except Exception as e:
            result['message'] = f'Error al crear backup: {e}'
            logger.error("DatabaseRestore", f"Error creando backup: {e}")
        
        return result
    
    # ========================================================================
    # LISTADO Y METADATOS DE BACKUPS
    # ========================================================================
    
    def get_backups_list(self) -> List[BackupInfo]:
        """
        Obtiene lista de todos los backups disponibles con metadatos completos.
        
        Returns:
            Lista de BackupInfo ordenada por fecha (más reciente primero)
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if not filename.endswith('.db'):
                continue
            
            filepath = os.path.join(self.backup_dir, filename)
            info = self._extract_backup_info(filename, filepath)
            
            if info:
                backups.append(info)
        
        # Ordenar por fecha (más reciente primero)
        backups.sort(key=lambda b: b.date or datetime.datetime.min, reverse=True)
        
        return backups
    
    def _extract_backup_info(self, filename: str, filepath: str) -> Optional[BackupInfo]:
        """Extrae información detallada de un archivo de backup"""
        try:
            info = BackupInfo(
                filename=filename,
                filepath=filepath,
                size_bytes=os.path.getsize(filepath),
            )
            info.size_mb = round(info.size_bytes / (1024 * 1024), 2)
            
            # Intentar patrón con versión
            match = self.BACKUP_PATTERN_VERSIONED.match(filename)
            if match:
                info.db_version = match.group(1)
                date_str = match.group(2)
                time_str = match.group(3)
                info.date = datetime.datetime.strptime(
                    f"{date_str}_{time_str}", '%Y%m%d_%H%M%S'
                )
            else:
                # Intentar patrón legacy
                match = self.BACKUP_PATTERN_LEGACY.match(filename)
                if match:
                    date_str = match.group(1)
                    time_str = match.group(2)
                    info.date = datetime.datetime.strptime(
                        f"{date_str}_{time_str}", '%Y%m%d_%H%M%S'
                    )
                    # Intentar detectar versión consultando la BD
                    info.db_version = self._detect_version_from_db(filepath)
                else:
                    # Intentar patrón de migración
                    match = self.BACKUP_PATTERN_MIGRATION.match(filename)
                    if match:
                        date_str = match.group(1)
                        time_str = match.group(2)
                        info.date = datetime.datetime.strptime(
                            f"{date_str}_{time_str}", '%Y%m%d_%H%M%S'
                        )
                        info.db_version = self._detect_version_from_db(filepath)
                    else:
                        # Archivo no reconocido, intentar obtener fecha del sistema de archivos
                        mod_time = os.path.getmtime(filepath)
                        info.date = datetime.datetime.fromtimestamp(mod_time)
                        info.db_version = self._detect_version_from_db(filepath)
            
            # Validar compatibilidad
            is_compatible, reason = self.validate_restore_compatibility(filepath, info.db_version)
            info.is_compatible = is_compatible
            info.compatibility_reason = reason
            
            return info
            
        except Exception as e:
            logger.warning("DatabaseRestore", f"Error extrayendo info de {filename}: {e}")
            return None
    
    def _detect_version_from_db(self, db_path: str) -> Optional[str]:
        """
        Detecta la versión de la BD consultando el archivo SQLite directamente.
        
        Busca en system_configs por 'db_version' o intenta inferir del schema.
        """
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar db_version en system_configs
            try:
                cursor.execute(
                    "SELECT config_value FROM system_configs WHERE config_key = 'db_version'"
                )
                row = cursor.fetchone()
                if row:
                    conn.close()
                    return row[0]
            except sqlite3.OperationalError:
                pass
            
            # Inferir versión por la presencia de tablas/columnas
            try:
                # Si tiene tabla currencies → v1.2+
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='currencies'"
                )
                has_currencies = cursor.fetchone() is not None
                
                if has_currencies:
                    # Verificar si tiene currency_code en printers → v1.2
                    cursor.execute("PRAGMA table_info(printers)")
                    columns = [col[1] for col in cursor.fetchall()]
                    if 'currency_code' in columns:
                        conn.close()
                        return "1.2"
                
                # Sin currencies → probablemente v1.0 o v1.1
                # Verificar triggers para distinguir
                cursor.execute(
                    "SELECT sql FROM sqlite_master WHERE type='trigger' AND name='customers_updated_at'"
                )
                trigger_row = cursor.fetchone()
                if trigger_row and trigger_row[0]:
                    trigger_sql = trigger_row[0]
                    if 'localtime' in trigger_sql.lower():
                        conn.close()
                        return "1.1"
                
                conn.close()
                return "1.0"
                
            except sqlite3.OperationalError:
                conn.close()
                return None
                
        except Exception as e:
            logger.warning("DatabaseRestore", f"Error detectando versión de {db_path}: {e}")
            return None
    
    # ========================================================================
    # VALIDACIÓN DE COMPATIBILIDAD
    # ========================================================================
    
    def validate_restore_compatibility(
        self, backup_path: str, backup_version: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Valida si un backup puede ser restaurado en la versión actual.
        
        Reglas:
        - Solo se pueden restaurar backups de la MISMA versión mayor.menor
        - Ejemplo: v1.2 puede restaurar v1.2, pero NO v1.1 ni v1.3
        
        Args:
            backup_path: Ruta al archivo de backup
            backup_version: Versión del backup (None = detectar automáticamente)
            
        Returns:
            (is_compatible, reason)
        """
        try:
            if not os.path.exists(backup_path):
                return False, "El archivo de backup no existe"
            
            # Detectar versión si no se proporcionó
            if backup_version is None:
                backup_version = self._detect_version_from_db(backup_path)
            
            if backup_version is None:
                return False, "No se pudo determinar la versión del backup"
            
            # Comparar versiones
            current = self._parse_version(self.current_version)
            backup = self._parse_version(backup_version)
            
            if current is None or backup is None:
                return False, f"Formato de versión inválido (actual: {self.current_version}, backup: {backup_version})"
            
            # Solo permitir restauración de la misma versión
            if current == backup:
                return True, f"Compatible: versión {backup_version}"
            
            # Versiones diferentes - no compatible
            if backup < current:
                return False, (
                    f"Versión inferior: el backup es v{backup_version} "
                    f"pero la BD actual es v{self.current_version}. "
                    f"Se requiere migración previa."
                )
            else:
                return False, (
                    f"Versión superior: el backup es v{backup_version} "
                    f"pero la BD actual es v{self.current_version}. "
                    f"Actualice la aplicación primero."
                )
                
        except Exception as e:
            return False, f"Error al validar compatibilidad: {e}"
    
    def _parse_version(self, version_str: str) -> Optional[Tuple[int, ...]]:
        """Parsea una cadena de versión a una tupla de enteros"""
        try:
            parts = version_str.strip().split('.')
            return tuple(int(p) for p in parts)
        except (ValueError, AttributeError):
            return None
    
    # ========================================================================
    # RESTAURACIÓN
    # ========================================================================
    
    def restore_backup(self, backup_path: str, create_safety_backup: bool = True) -> Dict[str, Any]:
        """
        Restaura un backup sobre la base de datos actual.
        
        Proceso:
        1. Validar compatibilidad de versión
        2. Crear backup de seguridad de la BD actual
        3. Cerrar conexiones activas
        4. Copiar el backup sobre la BD actual
        5. Verificar integridad
        
        Args:
            backup_path: Ruta al archivo de backup a restaurar
            create_safety_backup: Si crear un backup de seguridad antes de restaurar
            
        Returns:
            dict con 'success', 'message', 'safety_backup_path'
        """
        result = {
            'success': False,
            'message': '',
            'safety_backup_path': None
        }
        
        try:
            # 1. Validar que el archivo existe
            if not os.path.exists(backup_path):
                result['message'] = 'El archivo de backup no existe'
                return result
            
            # 2. Validar compatibilidad de versión
            is_compatible, reason = self.validate_restore_compatibility(backup_path)
            if not is_compatible:
                result['message'] = f'Backup incompatible: {reason}'
                return result
            
            # 3. Verificar integridad del backup antes de restaurar
            integrity_ok, integrity_msg = self._verify_integrity(backup_path)
            if not integrity_ok:
                result['message'] = f'El backup está corrupto: {integrity_msg}'
                return result
            
            # 4. Crear backup de seguridad de la BD actual
            if create_safety_backup:
                safety_result = self.create_versioned_backup(label='pre_restore')
                if safety_result['success']:
                    result['safety_backup_path'] = safety_result['backup_path']
                    logger.info("DatabaseRestore", 
                        f"Backup de seguridad creado: {safety_result['backup_path']}")
                else:
                    result['message'] = (
                        f"No se pudo crear backup de seguridad: {safety_result['message']}. "
                        "Restauración abortada por seguridad."
                    )
                    return result
            
            # 5. Copiar backup sobre la BD actual
            shutil.copy2(backup_path, self.current_db_path)
            
            # 6. Verificar que la restauración fue exitosa
            if os.path.exists(self.current_db_path):
                integrity_ok, integrity_msg = self._verify_integrity(self.current_db_path)
                if integrity_ok:
                    result['success'] = True
                    result['message'] = 'Base de datos restaurada exitosamente'
                    logger.info("DatabaseRestore", 
                        f"BD restaurada desde: {backup_path}")
                else:
                    # Restaurar el backup de seguridad
                    if result['safety_backup_path']:
                        shutil.copy2(result['safety_backup_path'], self.current_db_path)
                    result['message'] = (
                        f'Error de integridad post-restauración: {integrity_msg}. '
                        'Se restauró la BD anterior.'
                    )
            else:
                result['message'] = 'Error: la BD no existe después de la restauración'
                
        except Exception as e:
            result['message'] = f'Error durante la restauración: {e}'
            logger.error("DatabaseRestore", f"Error restaurando backup: {e}")
            
            # Intentar restaurar desde backup de seguridad
            if result.get('safety_backup_path') and os.path.exists(result['safety_backup_path']):
                try:
                    shutil.copy2(result['safety_backup_path'], self.current_db_path)
                    result['message'] += ' (BD anterior restaurada desde backup de seguridad)'
                except Exception:
                    result['message'] += ' (CRÍTICO: no se pudo restaurar la BD anterior)'
        
        return result
    
    def _verify_integrity(self, db_path: str) -> Tuple[bool, str]:
        """Verifica la integridad de un archivo SQLite"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 'ok':
                return True, "Integridad verificada"
            else:
                return False, f"Fallo de integridad: {result}"
                
        except Exception as e:
            return False, f"Error al verificar integridad: {e}"
    
    # ========================================================================
    # ELIMINACIÓN DE BACKUPS
    # ========================================================================
    
    def delete_backup(self, backup_path: str) -> Dict[str, Any]:
        """
        Elimina un archivo de backup.
        
        Args:
            backup_path: Ruta al archivo de backup a eliminar
            
        Returns:
            dict con 'success', 'message'
        """
        result = {'success': False, 'message': ''}
        
        try:
            if not os.path.exists(backup_path):
                result['message'] = 'El archivo de backup no existe'
                return result
            
            filename = os.path.basename(backup_path)
            os.remove(backup_path)
            
            result['success'] = True
            result['message'] = f'Backup eliminado: {filename}'
            logger.info("DatabaseRestore", f"Backup eliminado: {backup_path}")
            
        except Exception as e:
            result['message'] = f'Error al eliminar backup: {e}'
            logger.error("DatabaseRestore", f"Error eliminando backup: {e}")
        
        return result
    
    # ========================================================================
    # ESTADÍSTICAS DE LA BASE DE DATOS
    # ========================================================================
    
    def get_database_stats(self) -> DatabaseStats:
        """
        Obtiene estadísticas completas de la base de datos actual.
        
        Returns:
            DatabaseStats con toda la información relevante
        """
        stats = DatabaseStats()
        
        try:
            stats.db_version = self.current_version
            stats.db_path = self.current_db_path
            stats.schema_version = APP_CONFIG.database.schema_version
            
            # Tamaño del archivo
            if os.path.exists(self.current_db_path):
                stats.db_size_bytes = os.path.getsize(self.current_db_path)
                stats.db_size_mb = round(stats.db_size_bytes / (1024 * 1024), 2)
            
            # Contar registros por tabla
            stats.record_counts = self._count_all_records()
            stats.total_records = sum(stats.record_counts.values())
            
            # Info de backups
            backups = self.get_backups_list()
            stats.total_backups = len(backups)
            if backups:
                stats.last_backup_date = backups[0].date  # Ya están ordenados por fecha desc
            
            # Config de backups
            try:
                from core.managers.database_manager import get_db_manager
                db_manager = get_db_manager()
                stats.backup_enabled = db_manager.configs.get_bool_value('backup_enabled', False)
                stats.backup_frequency_days = db_manager.configs.get_int_value('backup_frequency', 7)
            except Exception:
                pass
            
            # Fecha de creación de la BD
            if os.path.exists(self.current_db_path):
                try:
                    conn = sqlite3.connect(self.current_db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT MIN(created_at) FROM system_configs"
                    )
                    row = cursor.fetchone()
                    if row and row[0]:
                        stats.created_at = row[0]
                    conn.close()
                except Exception:
                    pass
            
        except Exception as e:
            logger.error("DatabaseRestore", f"Error obteniendo estadísticas: {e}")
        
        return stats
    
    def _count_all_records(self) -> Dict[str, int]:
        """Cuenta registros en todas las tablas principales"""
        counts = {}
        tables = {
            'customers': 'Clientes',
            'printers': 'Impresoras',
            'filaments': 'Filamentos',
            'quotes': 'Presupuestos',
            'currencies': 'Monedas',
            'exchange_rates': 'Tasas de Cambio',
            'system_configs': 'Configuraciones'
        }
        
        try:
            conn = sqlite3.connect(self.current_db_path)
            cursor = conn.cursor()
            
            for table_name, display_name in tables.items():
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row = cursor.fetchone()
                    counts[table_name] = row[0] if row else 0
                except sqlite3.OperationalError:
                    counts[table_name] = 0
            
            conn.close()
            
        except Exception as e:
            logger.error("DatabaseRestore", f"Error contando registros: {e}")
        
        return counts
    
    def get_record_counts_for_backup(self, backup_path: str) -> Dict[str, int]:
        """Obtiene conteo de registros de un backup específico"""
        counts = {}
        tables = ['customers', 'printers', 'filaments', 'quotes']
        
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row = cursor.fetchone()
                    counts[table] = row[0] if row else 0
                except sqlite3.OperationalError:
                    counts[table] = 0
            
            conn.close()
        except Exception:
            pass
        
        return counts
    
    # ========================================================================
    # SISTEMA DE MIGRACIONES
    # ========================================================================
    
    def get_migration_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el estado de migraciones.
        
        Returns:
            dict con información de migraciones disponibles y estado actual
        """
        info = {
            'current_version': self.current_version,
            'schema_version': APP_CONFIG.database.schema_version,
            'migration_required': APP_CONFIG.database.migration_required,
            'available_migrations': [],
            'migration_history': []
        }
        
        # Registrar migraciones conocidas
        known_migrations = [
            {
                'from_version': '1.0',
                'to_version': '1.1',
                'description': 'Corrección de timestamps UTC → hora local',
                'date': '2025-11',
                'breaking': False
            },
            {
                'from_version': '1.1',
                'to_version': '1.2',
                'description': 'Sistema multi-moneda (currencies, exchange_rates)',
                'date': '2025-12',
                'breaking': True
            }
        ]
        
        info['available_migrations'] = known_migrations
        
        # Verificar qué migraciones aplican
        current = self._parse_version(self.current_version)
        if current:
            info['pending_migrations'] = [
                m for m in known_migrations
                if self._parse_version(m['from_version']) == current
            ]
        else:
            info['pending_migrations'] = []
        
        return info
    
    def can_migrate(self, from_version: str, to_version: str) -> Tuple[bool, str]:
        """
        Verifica si una migración es posible.
        
        Reglas:
        - Solo migración secuencial (salto de 1 versión menor)
        - Ejemplo: 1.1 → 1.2 ✅, pero 1.0 → 1.2 ❌
        
        Args:
            from_version: Versión de origen
            to_version: Versión de destino
            
        Returns:
            (can_migrate, reason)
        """
        from_v = self._parse_version(from_version)
        to_v = self._parse_version(to_version)
        
        if from_v is None or to_v is None:
            return False, "Formato de versión inválido"
        
        if from_v == to_v:
            return False, "Las versiones son iguales, no se requiere migración"
        
        if to_v < from_v:
            return False, f"No se puede degradar la versión de {from_version} a {to_version}"
        
        # Verificar que sea un salto secuencial
        # Para versiones con 2 componentes (1.0, 1.1, 1.2):
        if len(from_v) == 2 and len(to_v) == 2:
            if from_v[0] == to_v[0] and to_v[1] - from_v[1] == 1:
                return True, f"Migración secuencial válida: {from_version} → {to_version}"
            elif to_v[1] - from_v[1] > 1:
                return False, (
                    f"Salto de versión no permitido: {from_version} → {to_version}. "
                    f"Se requiere migrar secuencialmente "
                    f"(ej: {from_version} → {from_v[0]}.{from_v[1]+1})"
                )
        
        # Para versiones con 3 componentes (1.1.0, 1.1.1, 1.1.2):
        if len(from_v) == 3 and len(to_v) == 3:
            if from_v[0] == to_v[0] and from_v[1] == to_v[1]:
                if to_v[2] - from_v[2] == 1:
                    return True, f"Migración secuencial válida: {from_version} → {to_version}"
                elif to_v[2] - from_v[2] > 1:
                    return False, (
                        f"Salto de versión no permitido: {from_version} → {to_version}. "
                        f"Se requiere migrar secuencialmente "
                        f"(ej: {from_version} → {from_v[0]}.{from_v[1]}.{from_v[2]+1})"
                    )
            elif from_v[1] != to_v[1]:
                # Salto de minor version
                if to_v[1] - from_v[1] == 1 and to_v[2] == 0:
                    return True, f"Migración secuencial válida: {from_version} → {to_version}"
                else:
                    return False, (
                        f"Salto de versión no permitido: {from_version} → {to_version}. "
                        f"Migre primero a la versión intermedia."
                    )
        
        return False, f"No se encontró ruta de migración de {from_version} a {to_version}"
    
    def ensure_db_version_stored(self):
        """
        Asegura que la versión actual de la BD esté almacenada en system_configs.
        Se ejecuta al iniciar la aplicación.
        """
        try:
            conn = sqlite3.connect(self.current_db_path)
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute(
                "SELECT config_value FROM system_configs WHERE config_key = 'db_version'"
            )
            row = cursor.fetchone()
            
            if row is None:
                # Insertar la versión actual
                cursor.execute(
                    "INSERT INTO system_configs (config_key, config_value, config_type, description, category) "
                    "VALUES ('db_version', ?, 'string', 'Versión de la base de datos', 'system')",
                    (self.current_version,)
                )
                conn.commit()
                logger.info("DatabaseRestore", 
                    f"Versión de BD registrada: {self.current_version}")
            elif row[0] != self.current_version:
                # Actualizar la versión
                cursor.execute(
                    "UPDATE system_configs SET config_value = ? WHERE config_key = 'db_version'",
                    (self.current_version,)
                )
                conn.commit()
                logger.info("DatabaseRestore", 
                    f"Versión de BD actualizada: {row[0]} → {self.current_version}")
            
            conn.close()
            
        except Exception as e:
            logger.warning("DatabaseRestore", f"Error guardando versión de BD: {e}")
    
    # ========================================================================
    # UTILIDADES
    # ========================================================================
    
    def open_backup_folder(self):
        """Abre la carpeta de backups en el explorador de archivos"""
        try:
            import subprocess
            backup_path = self.backup_dir
            if os.path.exists(backup_path):
                system = platform.system()
                if system == "Windows":
                    subprocess.Popen(f'explorer "{backup_path}"')
                elif system == "Darwin":
                    subprocess.Popen(["open", str(backup_path)])
                else:
                    subprocess.Popen(["xdg-open", str(backup_path)])
            else:
                logger.warning("DatabaseRestore", 
                    f"Carpeta de backups no existe: {backup_path}")
        except Exception as e:
            logger.error("DatabaseRestore", f"Error abriendo carpeta de backups: {e}")
    
    def get_backup_folder_path(self) -> str:
        """Retorna la ruta de la carpeta de backups"""
        return self.backup_dir
    
    def get_database_folder_path(self) -> str:
        """Retorna la ruta de la carpeta de la base de datos"""
        return str(Path(self.current_db_path).parent)


# Instancia global del servicio
_restore_service_instance = None


def get_restore_service() -> DatabaseRestoreService:
    """Obtiene la instancia global del servicio de restauración"""
    global _restore_service_instance
    if _restore_service_instance is None:
        _restore_service_instance = DatabaseRestoreService()
    return _restore_service_instance
