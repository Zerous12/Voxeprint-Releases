"""
Conexión y configuración de base de datos SQLite
"""
import sqlite3
import os
from typing import Optional
from contextlib import contextmanager
from core.utils.path_helper import database_path

class DatabaseConnection:
    """Maneja la conexión a la base de datos SQLite"""

    def __init__(self, db_path: str = None):
        """
        Inicializa la conexión a la base de datos
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        if db_path is None:
            db_path = database_path()
        self.db_path = str(db_path)
    
    @contextmanager
    def get_connection(self):
        """
        Context manager para obtener una conexión a la base de datos
        
        Yields:
            sqlite3.Connection: Conexión a la base de datos
        """
        conn = None
        try:
            # isolation_level=None activa autocommit mode para commits inmediatos
            conn = sqlite3.connect(self.db_path, isolation_level=None)
            conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
            conn.execute("PRAGMA foreign_keys = ON")  # Habilitar foreign keys
            conn.execute("PRAGMA synchronous = FULL")  # Forzar escritura inmediata a disco
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_script(self, script: str) -> None:
        """
        Ejecuta un script SQL
        
        Args:
            script: Script SQL a ejecutar
        """
        # executescript requiere isolation_level diferente de None
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executescript(script)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Ejecuta una consulta SELECT
        
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
            
        Returns:
            list: Resultados de la consulta
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def execute_command(self, command: str, params: tuple = ()) -> int:
        """
        Ejecuta un comando SQL (INSERT, UPDATE, DELETE)
        
        Args:
            command: Comando SQL
            params: Parámetros para el comando
            
        Returns:
            int: ID del último registro insertado o número de filas afectadas
        """
        with self.get_connection() as conn:
            cursor = conn.execute(command, params)
            # Con isolation_level=None, el commit es automático (autocommit mode)
            # pero lo hacemos explícito para mayor claridad
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
