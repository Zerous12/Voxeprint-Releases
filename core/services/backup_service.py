"""
Servicio de respaldos automáticos independiente
Maneja la lógica de respaldos sin depender de Qt
"""

import os
import datetime
from typing import Optional
from core.managers.database_manager import get_db_manager
from core.utils.path_helper import backups_dir


class BackupService:
    """Servicio para gestionar respaldos automáticos de la base de datos"""
    
    def __init__(self):
        self.backup_dir = str(backups_dir())
        self._ensure_backup_directory()
    
    def _ensure_backup_directory(self):
        """Asegura que el directorio de respaldos existe"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)
    
    def is_backup_enabled(self) -> bool:
        """Verifica si los respaldos automáticos están habilitados"""
        try:
            db_manager = get_db_manager()
            return db_manager.configs.get_bool_value('backup_enabled', False)
        except Exception:
            return False
    
    def get_backup_frequency_days(self) -> int:
        """Obtiene la frecuencia de respaldos en días"""
        try:
            db_manager = get_db_manager()
            return db_manager.configs.get_int_value('backup_frequency', 7)
        except Exception:
            return 7
    
    def needs_backup(self) -> bool:
        """Determina si es necesario crear un respaldo"""
        try:
            if not self.is_backup_enabled():
                return False
            
            frequency_days = self.get_backup_frequency_days()
            
            # Buscar archivos de respaldo
            backup_files = self._get_backup_files()
            
            if not backup_files:
                return True  # No hay respaldos, crear uno
            
            # Encontrar el respaldo más reciente
            latest_backup = max(backup_files)
            
            # Extraer fecha del nombre del archivo
            last_backup_date = self._extract_date_from_filename(latest_backup)
            
            if last_backup_date is None:
                return True  # No se puede determinar fecha, crear respaldo por seguridad
            
            # Calcular días desde el último respaldo
            days_since_backup = (datetime.date.today() - last_backup_date).days
            
            return days_since_backup >= frequency_days
            
        except Exception:
            return True  # En caso de error, crear respaldo por seguridad
    
    def _get_backup_files(self) -> list:
        """Obtiene la lista de archivos de respaldo"""
        if not os.path.exists(self.backup_dir):
            return []
        
        return [f for f in os.listdir(self.backup_dir) 
                if f.startswith('voxeprint_backup_') and f.endswith('.db')]
    
    def _extract_date_from_filename(self, filename: str) -> Optional[datetime.date]:
        """Extrae la fecha de un nombre de archivo de respaldo"""
        try:
            # Formato versionado: voxeprint_backup_vX.Y_YYYYMMDD_HHMMSS.db
            # Formato versionado con label: voxeprint_backup_vX.Y_label_YYYYMMDD_HHMMSS.db
            # Formato legacy: voxeprint_backup_YYYYMMDD_HHMMSS.db
            import re
            
            # Intentar patrón versionado
            match = re.search(r'(\d{8})_(\d{6})\.db$', filename)
            if match:
                date_str = match.group(1)
                return datetime.datetime.strptime(date_str, '%Y%m%d').date()
            
            # Fallback: formato original
            date_part = filename.replace('voxeprint_backup_', '').replace('.db', '')
            date_str = date_part.split('_')[0]  # Solo la parte de fecha YYYYMMDD
            return datetime.datetime.strptime(date_str, '%Y%m%d').date()
        except (ValueError, IndexError):
            return None
    
    def create_backup(self) -> Optional[str]:
        """Crea un respaldo de la base de datos (con versión en el nombre)"""
        try:
            from core.services.database_restore_service import get_restore_service
            restore_service = get_restore_service()
            result = restore_service.create_versioned_backup(label='auto')
            if result['success']:
                return result['backup_path']
            
            # Fallback al método original si el nuevo servicio falla
            db_manager = get_db_manager()
            backup_path = db_manager.backup_database()
            return backup_path
        except Exception as e:
            print(f"Error al crear respaldo: {e}")
            return None
    
    def cleanup_old_backups(self, max_backups: int = 8) -> int:
        """Limpia respaldos antiguos manteniendo solo los más recientes"""
        try:
            backup_files = self._get_backup_files()
            
            if len(backup_files) <= max_backups:
                return 0  # No hay demasiados respaldos
            
            # Ordenar por fecha (más reciente primero)
            backup_files.sort(reverse=True)
            
            # Eliminar respaldos antiguos
            files_to_delete = backup_files[max_backups:]
            deleted_count = 0
            
            for file_to_delete in files_to_delete:
                file_path = os.path.join(self.backup_dir, file_to_delete)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"No se pudo eliminar respaldo antiguo {file_to_delete}: {e}")
            
            return deleted_count
            
        except Exception as e:
            print(f"Error en limpieza de respaldos: {e}")
            return 0
    
    def perform_automatic_backup(self) -> dict:
        """Ejecuta un respaldo automático completo con limpieza"""
        result = {
            'success': False,
            'backup_path': None,
            'message': '',
            'cleaned_files': 0
        }
        
        try:
            # Limpiar respaldos antiguos siempre (independientemente de si se crea nuevo backup)
            cleaned_files = self.cleanup_old_backups()
            result['cleaned_files'] = cleaned_files
            
            # Verificar si se necesita respaldo
            if not self.needs_backup():
                result['message'] = 'No se necesita respaldo en este momento'
                if cleaned_files > 0:
                    result['message'] += f'. {cleaned_files} respaldos antiguos eliminados'
                result['success'] = True
                return result
            
            # Crear respaldo
            backup_path = self.create_backup()
            
            if backup_path and os.path.exists(backup_path):
                result['success'] = True
                result['backup_path'] = backup_path
                
                # Verificar tamaño
                size_mb = os.path.getsize(backup_path) / (1024 * 1024)
                
                result['message'] = f'Respaldo creado exitosamente ({size_mb:.2f} MB)'
                if cleaned_files > 0:
                    result['message'] += f'. {cleaned_files} respaldos antiguos eliminados'
            else:
                result['message'] = 'Error: no se pudo crear el archivo de respaldo'
                
        except Exception as e:
            result['message'] = f'Error durante respaldo automático: {e}'
        
        return result
    
    def get_backup_status(self) -> dict:
        """Obtiene el estado actual del sistema de respaldos"""
        backup_files = self._get_backup_files()
        
        status = {
            'enabled': self.is_backup_enabled(),
            'frequency_days': self.get_backup_frequency_days(),
            'total_backups': len(backup_files),
            'needs_backup': False,
            'last_backup_date': None,
            'days_since_last': None
        }
        
        if backup_files:
            latest_backup = max(backup_files)
            status['last_backup_date'] = self._extract_date_from_filename(latest_backup)
            
            if status['last_backup_date']:
                status['days_since_last'] = (datetime.date.today() - status['last_backup_date']).days
        
        status['needs_backup'] = self.needs_backup()
        
        return status


# Instancia global del servicio
_backup_service_instance = None


def get_backup_service() -> BackupService:
    """Obtiene la instancia global del servicio de respaldos"""
    global _backup_service_instance
    if _backup_service_instance is None:
        _backup_service_instance = BackupService()
    return _backup_service_instance
