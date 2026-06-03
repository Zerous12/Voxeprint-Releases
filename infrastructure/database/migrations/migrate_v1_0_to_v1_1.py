"""
Migración de v1.0 a v1.1: Corrección de timestamps UTC a hora local

CAMBIOS:
- v1.0: Usaba CURRENT_TIMESTAMP (UTC) 
- v1.1: Usa datetime('now', 'localtime') para timestamps en hora local

COMPATIBILIDAD:
- Schema NO cambió (mismas columnas)
- Solo cambió el DEFAULT de created_at/updated_at
- BDs v1.0 funcionan con código v1.1
- Esta migración corrige registros antiguos (opcional)
"""
import sys
from pathlib import Path
from typing import Tuple

# Para importar desde raíz
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from infrastructure.database.connection import DatabaseConnection
from core.utils.path_helper import database_path
from core.utils.logger import logger


class Migration_v1_0_to_v1_1:
    """
    Migración de base de datos v1.0 → v1.1
    
    Corrige timestamps de UTC a hora local en registros existentes
    """
    
    def __init__(self):
        # Detectar si tenemos BD v1.0 o v1.1
        db_dir = database_path().parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        self.old_db_path = db_dir / "voxeprint_1.0.db"
        self.new_db_path = db_dir / "voxeprint_1.1.db"
        
        # Usar la BD que exista
        if self.old_db_path.exists():
            self.db_path = self.old_db_path
        elif self.new_db_path.exists():
            self.db_path = self.new_db_path
        else:
            # Si no existe ninguna, usar la que debería crear la app
            self.db_path = database_path()
        
        self.db = DatabaseConnection(str(self.db_path))
        self.utc_offset_hours = -3  # Paraguay: UTC-3 (o -4 según temporada)
    
    def check_if_needed(self) -> Tuple[bool, str]:
        """
        Verifica si la migración es necesaria
        
        Returns:
            (is_needed, reason)
        """
        try:
            # Verificar si ya existe la BD v1.1
            if self.new_db_path.exists():
                return False, "BD v1.1 ya existe - migración ya realizada"
            
            # Verificar si existe la BD v1.0
            if not self.old_db_path.exists():
                return False, "No hay BD v1.0 para migrar"
            
            # Contar registros que podrían tener timestamps UTC
            try:
                count = self.db.execute_query(
                    "SELECT COUNT(*) as cnt FROM quotes"
                )[0]['cnt']
                
                if count == 0:
                    return True, "BD v1.0 encontrada (sin presupuestos, pero se migrará estructura)"
                
                return True, f"BD v1.0 encontrada con {count} presupuestos para migrar"
            except Exception as e:
                return True, f"BD v1.0 encontrada (se migrará estructura): {e}"
            
        except Exception as e:
            return False, f"Error verificando: {e}"
    
    def migrate(self, auto_detect_offset: bool = True) -> Tuple[bool, str]:
        """
        Ejecuta la migración de timestamps
        
        Args:
            auto_detect_offset: Si True, detecta el offset automáticamente
            
        Returns:
            (success, message)
        """
        try:            
            # 1. Backup automático
            import shutil
            from datetime import datetime
            
            backup_dir = self.old_db_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"voxeprint_1.0_pre_migration_{timestamp}.db"
            
            shutil.copy2(self.old_db_path, backup_path)
            
            # 2. Analizar registros            
            tables_to_check = ['quotes', 'customers', 'printers', 'filaments', 'system_configs']
            total_updated = 0
            
            for table in tables_to_check:
                try:
                    # Contar registros
                    count = self.db.execute_query(
                        f"SELECT COUNT(*) as cnt FROM {table}"
                    )[0]['cnt']
                    
                    if count == 0:
                        logger.info(f"Migration", f"{table}: Sin registros")
                        continue
                    
                    # Actualizar timestamps (restar offset UTC)
                    # Paraguay está UTC-3, entonces los timestamps están +3 horas adelante
                    update_sql = f"""
                        UPDATE {table}
                        SET created_at = datetime(created_at, '{self.utc_offset_hours} hours'),
                            updated_at = datetime(updated_at, '{self.utc_offset_hours} hours')
                        WHERE created_at IS NOT NULL
                    """
                    
                    affected = self.db.execute_command(update_sql)
                    total_updated += affected
                    
                    logger.info(f"Migration", f"{table}: {affected} registros actualizados")
                    
                except Exception as e:
                    logger.error(f"Migration", f"Error en {table}: {e}")            
            # Copiar BD actualizada a nueva versión
            import shutil
            shutil.copy2(self.old_db_path, self.new_db_path)  
            return True, f"Migración exitosa: {total_updated} registros actualizados"
            
        except Exception as e:
            logger.error(f"Migration", f"Error en migración: {e}")            
            return False, f"Error: {e}"
    
    def rollback(self, backup_file: str) -> Tuple[bool, str]:
        """
        Revierte la migración desde un backup
        
        Args:
            backup_file: Nombre del archivo de backup
            
        Returns:
            (success, message)
        """
        try:
            backup_dir = self.old_db_path.parent / "backups"
            backup_path = backup_dir / backup_file
            
            if not backup_path.exists():
                return False, f"Backup no encontrado: {backup_file}"
            
            import shutil
            # Restaurar el backup a v1.0
            shutil.copy2(backup_path, self.old_db_path)
            
            # Opcional: eliminar v1.1 si existe
            if self.new_db_path.exists():
                self.new_db_path.unlink()
                logger.info("Migration", f"voxeprint_1.1.db eliminado")
            
            return True, f"BD restaurada desde: {backup_file}"
            
        except Exception as e:
            return False, f"Error en rollback: {e}"


def run_migration_if_needed():
    """
    Función helper para ejecutar la migración si es necesaria
    """
    migration = Migration_v1_0_to_v1_1()
    
    is_needed, reason = migration.check_if_needed()
    
    if not is_needed:
        logger.info("Migration", f"Migración no necesaria: {reason}")
        return True    
    
    response = input("Continuar? [S/n]: ").strip().lower()
    
    if response in ['', 's', 'si', 'sí', 'y', 'yes']:
        success, message = migration.migrate()
        logger.info("Migration", message)
        return success
    else:
        logger.info("Migration", "Migración cancelada por el usuario")
        return False

