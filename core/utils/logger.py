#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de logging centralizado para Voxeprint
Maneja debug, info, warning y error con niveles configurables
"""

import logging
import os
from datetime import datetime
from enum import Enum
from typing import Optional
from pathlib import Path

# Importar el path helper existente
from core.utils.path_helper import logs_dir

class LogLevel(Enum):
    """Niveles de logging disponibles"""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"

class VoxeprintLogger:
    """
    Logger centralizado para la aplicación Voxeprint
    
    Características:
    - Múltiples niveles de logging (DEBUG, INFO, WARNING, ERROR)
    - Filtrado automático de datos sensibles
    - Logs enfocados únicamente en el funcionamiento del software
    - Configuración por módulos
    - Archivos de log rotativos
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern para garantizar una sola instancia"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar el logger (solo una vez)"""
        if not self._initialized:
            self._setup_logger()
            VoxeprintLogger._initialized = True
    
    def _setup_logger(self):
        """Configurar el sistema de logging"""
        try:
            # Usar el directorio de logs configurado en path_helper
            self.log_dir = logs_dir()
            
            # Limpiar logs antiguos (solo logs de +5 meses para conservar auditoría)
            self._cleanup_old_logs(keep_months=5)
            
            # Configurar logger principal
            self.logger = logging.getLogger("Voxeprint")
            self.logger.setLevel(logging.DEBUG)
            
            # Limpiar handlers existentes
            self.logger.handlers.clear()
            
            # Configurar formato de mensajes
            self.formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # Handler para archivo (todos los niveles) - usando path_helper con rotación mensual
            log_file = self.log_dir / f"voxeprint_{datetime.now().strftime('%Y%m')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
            
            # NO hay handler para consola - logging solo va a archivo
            # Para consola usar print() directamente cuando sea necesario
            
            # Estado interno
            self.debug_enabled = True
            self.module_levels = {}
            
            self.debug("VoxeprintLogger", f"Sistema de logging inicializado - Logs en: {self.log_dir}")
            self.debug("VoxeprintLogger", f"Archivo de log actual: voxeprint_{datetime.now().strftime('%Y%m')}.log")
            
        except Exception as e:
            print(f"ERROR: No se pudo inicializar el logger: {e}")
    
    def _cleanup_old_logs(self, keep_months: int = 5):
        """
        Limpiar logs antiguos para evitar acumulación excesiva
        CONSERVA logs para auditoría - solo elimina logs de más de 5 meses
        
        Args:
            keep_months: Número de meses de logs a conservar (por defecto 5 para auditoría)
        """
        try:
            import glob
            
            # Calcular fecha límite (hace X meses) usando datetime estándar
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            
            # Calcular año y mes límite
            target_month = current_month - keep_months
            target_year = current_year
            
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            cutoff_str = f"{target_year:04d}{target_month:02d}"
            
            # Buscar archivos de log que coincidan con el patrón
            log_pattern = str(self.log_dir / "voxeprint_*.log")
            log_files = glob.glob(log_pattern)
            
            deleted_count = 0
            for log_file in log_files:
                try:
                    # Extraer fecha del nombre del archivo
                    filename = Path(log_file).stem  # voxeprint_YYYYMM
                    if len(filename) >= 15:  # voxeprint_ + 6 dígitos
                        date_part = filename[-6:]  # YYYYMM
                        if date_part.isdigit() and len(date_part) == 6:
                            if date_part < cutoff_str:
                                Path(log_file).unlink()
                                deleted_count += 1
                except Exception:
                    continue  # Ignorar archivos con formato incorrecto
            
            if deleted_count > 0:
                print(f"Logs antiguos limpiados: {deleted_count} archivos eliminados (conservando últimos {keep_months} meses para auditoría)")
                
        except Exception as e:
            print(f"⚠️ Error limpiando logs antiguos: {e}")
    
    def set_debug_enabled(self, enabled: bool):
        """Habilitar/deshabilitar debug globalmente"""
        self.debug_enabled = enabled
        # No hay console handler, solo configuramos el nivel interno
        self.debug("VoxeprintLogger", f"Debug {'habilitado' if enabled else 'deshabilitado'}")
    
    def set_module_level(self, module_name: str, level: LogLevel):
        """Configurar nivel específico para un módulo"""
        self.module_levels[module_name] = level
        self.debug("VoxeprintLogger", f"Nivel {level.value} configurado para módulo '{module_name}'")
    
    def _should_log(self, module_name: str, level: LogLevel) -> bool:
        """Determinar si un mensaje debe ser registrado"""
        if not self.debug_enabled and level == LogLevel.DEBUG:
            return False
        
        module_level = self.module_levels.get(module_name, LogLevel.DEBUG)
        level_hierarchy = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1, 
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3
        }
        
        return level_hierarchy[level] >= level_hierarchy[module_level]
    
    def _sanitize_message(self, message: str) -> str:
        """
        Sanitizar mensaje para remover datos sensibles
        
        Filtra:
        - Montos y precios (números con símbolos de moneda)
        - Nombres propios en mayúsculas
        - Rutas de archivos completas del usuario
        - Direcciones IP y URLs externas
        """
        import re
        
        # Remover montos (ej: $123.45, €50.00, MXN 100)
        message = re.sub(r'[\$€£¥]\s*\d+(?:\.\d+)?', '[MONTO]', message)
        message = re.sub(r'\d+(?:\.\d+)?\s*(?:USD|EUR|MXN|COP|ARS)', '[MONTO]', message)
        
        # Remover rutas completas del usuario (mantener solo nombre de archivo)
        message = re.sub(r'[A-Za-z]:\\[^\\]+\\[^\\]+\\.*?([^\\]+\.[a-zA-Z0-9]+)', r'[RUTA]/\1', message)
        message = re.sub(r'/Users/[^/]+/.*?([^/]+\.[a-zA-Z0-9]+)', r'[RUTA]/\1', message)
        
        # Remover IPs (mantener localhost)
        message = re.sub(r'\b(?!127\.0\.0\.1|localhost)\d+\.\d+\.\d+\.\d+\b', '[IP]', message)
        
        return message
    
    def _log(self, level: LogLevel, module_name: str, message: str, **kwargs):
        """Método interno para realizar el logging"""
        if not self._should_log(module_name, level):
            return
        
        # Sanitizar mensaje
        clean_message = self._sanitize_message(message)
        
        # Formatear mensaje final
        log_message = f"{module_name}: {clean_message}"
        
        # Agregar kwargs si existen
        if kwargs:
            extras = []
            for key, value in kwargs.items():
                if isinstance(value, (str, int, float, bool)):
                    extras.append(f"{key}={value}")
            if extras:
                log_message += f" | {', '.join(extras)}"
        
        # Enviar al logger apropiado
        log_method = getattr(self.logger, level.value.lower())
        log_method(log_message)
    
    def debug(self, module_name: str, message: str, **kwargs):
        """Log de nivel DEBUG - información detallada para desarrollo"""
        self._log(LogLevel.DEBUG, module_name, message, **kwargs)
    
    def info(self, module_name: str, message: str, **kwargs):
        """Log de nivel INFO - información general del flujo"""
        self._log(LogLevel.INFO, module_name, message, **kwargs)
    
    def warning(self, module_name: str, message: str, **kwargs):
        """Log de nivel WARNING - situaciones que requieren atención"""
        self._log(LogLevel.WARNING, module_name, message, **kwargs)
    
    def error(self, module_name: str, message: str, **kwargs):
        """Log de nivel ERROR - errores que afectan funcionalidad"""
        self._log(LogLevel.ERROR, module_name, message, **kwargs)
    
    def log_exception(self, module_name: str, exception: Exception, context: str = ""):
        """Registrar excepciones con contexto"""
        import traceback
        
        error_msg = f"Excepción en {context}: {type(exception).__name__}: {str(exception)}"
        self.error(module_name, error_msg)
        
        # Log del traceback completo solo en debug
        if self.debug_enabled:
            stack_trace = traceback.format_exc()
            self.debug(module_name, f"Stack trace completo:\n{stack_trace}")


# Instancia global del logger
logger = VoxeprintLogger()

# Funciones de conveniencia para uso directo
def debug(module_name: str, message: str, **kwargs):
    """Log de debug - información detallada"""
    logger.debug(module_name, message, **kwargs)

def info(module_name: str, message: str, **kwargs):
    """Log de información general"""
    logger.info(module_name, message, **kwargs)

def warning(module_name: str, message: str, **kwargs):
    """Log de advertencia"""
    logger.warning(module_name, message, **kwargs)

def error(module_name: str, message: str, **kwargs):
    """Log de error"""
    logger.error(module_name, message, **kwargs)

def log_exception(module_name: str, exception: Exception, context: str = ""):
    """Registrar excepción con contexto"""
    logger.log_exception(module_name, exception, context)

def set_debug_enabled(enabled: bool):
    """Habilitar/deshabilitar debug globalmente"""
    logger.set_debug_enabled(enabled)

def set_module_level(module_name: str, level: LogLevel):
    """Configurar nivel para módulo específico"""
    logger.set_module_level(module_name, level)