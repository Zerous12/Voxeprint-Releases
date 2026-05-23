"""
Facade principal para la aplicación Voxeprint
Este es el punto de entrada principal para todas las operaciones desde la UI
"""
from typing import Union, Optional
from datetime import datetime
from core.utils.logger import logger

from config.app_config import APP_CONFIG
from application.services.customer_service import CustomerService
from application.services.calculation_service import CalculationService
from application.dtos.customer_dtos import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerSearchDTO,
    CustomerListDTO
)
from application.dtos.quote_dtos import (
    QuoteCalculationRequestDTO,
    QuoteCalculationResponseDTO,
    QuoteCreateDTO
)
from application.dtos.base_dtos import BaseResponseDTO, ErrorResponseDTO, ListResponseDTO
from infrastructure.database.connection import DatabaseConnection
from infrastructure.database.repositories.quote_repository import QuoteRepository
from infrastructure.database.repositories.printer_repository import PrinterRepository
from infrastructure.database.repositories.filament_repository import FilamentRepository
from infrastructure.database.repositories.filament_roll_repository import FilamentRollRepository


class VoxeprintFacade:
    """
    Facade principal que coordina todos los servicios de la aplicación
    Esta clase proporciona una interfaz unificada para la UI
    """
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        Inicializa el facade con todos los servicios
        
        Args:
            db_connection: Conexión a la base de datos (opcional para testing)
        """
        if db_connection is None:
            # Para modo de testing/ejemplo sin base de datos real
            from infrastructure.database.connection import DatabaseConnection as _DB
            db_connection = _DB()
        self.db_connection = db_connection

        # Inicializar servicios
        self.customer_service = CustomerService(db_connection)
        self.calculation_service = CalculationService(db_connection)
        # TODO: Agregar otros servicios cuando estén listos
        # self.printer_service = PrinterService(db_connection)
        # self.filament_service = FilamentService(db_connection)
        # self.quote_service = QuoteService(db_connection)
        # self.system_config_service = SystemConfigService(db_connection)

        # Repos directos mientras no hay servicios específicos
        self.quote_repository = QuoteRepository(db_connection)
        self.printer_repository = PrinterRepository(db_connection)
        self.filament_repository = FilamentRepository(db_connection)
        self.filament_roll_repository = FilamentRollRepository(db_connection)
    
    # === GESTIÓN DE CLIENTES ===
    
    def create_customer(self, full_name: str, ruc_ci: str = "", email: str = "", 
                       phone_number: str = "", is_default: bool = False) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Crea un nuevo cliente
        
        Args:
            full_name: Nombre completo del cliente
            ruc_ci: RUC o cédula de identidad
            email: Email del cliente
            phone_number: Teléfono del cliente
            is_default: Si es cliente predeterminado
            
        Returns:
            Respuesta con el cliente creado o error
        """
        dto = CustomerCreateDTO(
            full_name=full_name,
            ruc_ci=ruc_ci,
            email=email,
            phone_number=phone_number,
            is_default=is_default
        )
        return self.customer_service.create_customer(dto)
    
    def update_customer(self, customer_id: int, full_name: Optional[str] = None,
                       ruc_ci: Optional[str] = None, email: Optional[str] = None,
                       phone_number: Optional[str] = None, is_default: Optional[bool] = None) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Actualiza un cliente existente
        
        Args:
            customer_id: ID del cliente
            full_name: Nuevo nombre completo (opcional)
            ruc_ci: Nuevo RUC/CI (opcional)
            email: Nuevo email (opcional)
            phone_number: Nuevo teléfono (opcional)
            is_default: Si es cliente predeterminado (opcional)
            
        Returns:
            Respuesta con el cliente actualizado o error
        """
        dto = CustomerUpdateDTO(
            id=customer_id,
            full_name=full_name,
            ruc_ci=ruc_ci,
            email=email,
            phone_number=phone_number,
            is_default=is_default
        )
        return self.customer_service.update_customer(dto)
    
    def get_customer(self, customer_id: int) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Obtiene un cliente por su ID
        
        Args:
            customer_id: ID del cliente
            
        Returns:
            Respuesta con el cliente o error
        """
        return self.customer_service.get_customer_by_id(customer_id)
    
    def search_customers(self, search_term: Optional[str] = None, 
                        is_default_only: bool = False, page: int = 1, 
                        page_size: int = 50) -> Union[CustomerListDTO, ErrorResponseDTO]:
        """
        Busca clientes según criterios
        
        Args:
            search_term: Término de búsqueda (nombre, RUC/CI, email)
            is_default_only: Solo clientes predeterminados
            page: Página de resultados
            page_size: Tamaño de página
            
        Returns:
            Lista de clientes o error
        """
        dto = CustomerSearchDTO(
            search_term=search_term,
            is_default_only=is_default_only,
            page=page,
            page_size=page_size
        )
        return self.customer_service.search_customers(dto)
    
    def delete_customer(self, customer_id: int) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Elimina un cliente
        
        Args:
            customer_id: ID del cliente a eliminar
            
        Returns:
            Respuesta de éxito o error
        """
        return self.customer_service.delete_customer(customer_id)
    
    def get_default_customer(self) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Obtiene el cliente predeterminado
        
        Returns:
            Respuesta con el cliente predeterminado o error
        """
        return self.customer_service.get_default_customer()
    
    def set_default_customer(self, customer_id: int) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Establece un cliente como predeterminado
        
        Args:
            customer_id: ID del cliente
            
        Returns:
            Respuesta de éxito o error
        """
        return self.customer_service.set_default_customer(customer_id)
    
    # === CÁLCULOS DE PRESUPUESTOS ===
    
    def calculate_quote_costs(self, printer_id: int, filament_id: int,
                            print_time_minutes: float, filament_weight_grams: float,
                            failure_margin_percent: Optional[float] = None,
                            profit_margin_percent: Optional[float] = None,
                            tax_rate_percent: Optional[float] = None,
                            commission_rate_percent: Optional[float] = None,
                            electricity_rate_per_kwh: Optional[float] = None,
                            filament_slots: Optional[list] = None) -> Union[QuoteCalculationResponseDTO, ErrorResponseDTO]:
        """
        Calcula todos los costos de un presupuesto
        
        Args:
            printer_id: ID de la impresora
            filament_id: ID del filamento
            print_time_minutes: Tiempo de impresión en minutos
            filament_weight_grams: Peso del filamento en gramos
            failure_margin_percent: Porcentaje de margen de error (opcional, usa config del sistema)
            profit_margin_percent: Porcentaje de margen de ganancia (opcional, usa config del sistema)
            tax_rate_percent: Porcentaje de impuesto (opcional, usa config del sistema)
            commission_rate_percent: Porcentaje de comisión (opcional, usa config del sistema)
            electricity_rate_per_kwh: Tarifa eléctrica por kWh (opcional, usa config del sistema)
            
        Returns:
            Costos calculados o error
        """
        # Obtener valores de configuración del sistema si no se proporcionan
        if failure_margin_percent is None:
            failure_margin_percent = self.calculation_service._get_system_config_float("default_failure_margin", 5.0)
        
        if profit_margin_percent is None:
            profit_margin_percent = self.calculation_service._get_system_config_float("default_profit_margin", 35.0)
        
        if tax_rate_percent is None:
            tax_rate_percent = self.calculation_service._get_system_config_float("tax_rate", 10.0)
        
        if commission_rate_percent is None:
            commission_rate_percent = 0.0  # Mantener 0.0 como default para comisión
        
        if electricity_rate_per_kwh is None:
            # Obtener tarifa desde BD o usar fallback de configuración
            base_rate = self.calculation_service._get_system_config_float(
                "electricity_rate", 
                APP_CONFIG.calculation.fallback_electricity_rate
            )
            # Aplicar multiplicador de hora punta guardado por el usuario (o el global de config)
            peak_multiplier = self.calculation_service._get_system_config_float(
                "electricity_peak_multiplier",
                APP_CONFIG.calculation.electricity_rate_multiplier
            )
            # Nunca puede ser menor a 1.0 (evita división/multiplicación por cero o negativa)
            if peak_multiplier < 1.0:
                peak_multiplier = 1.0
            electricity_rate_per_kwh = base_rate * peak_multiplier

        # Blindar comisión del IVA: leer preferencia del usuario
        commission_tax_shield = self.calculation_service._get_system_config_str(
            "commission_tax_shield", "False"
        ).lower() in ("true", "1", "yes", "on")

        dto = QuoteCalculationRequestDTO(
            printer_id=printer_id,
            filament_id=filament_id,
            print_time_minutes=print_time_minutes,
            filament_weight_grams=filament_weight_grams,
            failure_margin_percent=failure_margin_percent,
            profit_margin_percent=profit_margin_percent,
            tax_rate_percent=tax_rate_percent,
            commission_rate_percent=commission_rate_percent,
            electricity_rate_per_kwh=electricity_rate_per_kwh,
            commission_tax_shield=commission_tax_shield,
            filament_slots=filament_slots or [],
        )
        return self.calculation_service.calculate_quote_costs(dto)
    
    def estimate_basic_cost(self, printer_id: int, filament_id: int,
                           weight_grams: float, time_minutes: float) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Estimación rápida de costo (sin márgenes)
        
        Args:
            printer_id: ID de impresora
            filament_id: ID de filamento
            weight_grams: Peso en gramos
            time_minutes: Tiempo en minutos
            
        Returns:
            Estimación básica o error
        """
        return self.calculation_service.estimate_print_cost_simple(
            printer_id=printer_id,
            filament_id=filament_id,
            weight_grams=weight_grams,
            time_minutes=time_minutes
        )
    
    # === MÉTODOS DE UTILIDAD ===
    
    def health_check(self) -> BaseResponseDTO:
        """
        Verifica el estado de la aplicación
        
        Returns:
            Estado de la aplicación
        """
        try:
            # Verificar conexión a la base de datos
            test_query = "SELECT 1"
            self.db_connection.execute_query(test_query)
            
            return BaseResponseDTO(
                success=True,
                message="Aplicación funcionando correctamente"
            )
        except Exception as e:
            return ErrorResponseDTO(
                message=f"Error en aplicación: {str(e)}",
                error_code="HEALTH_CHECK_FAILED"
            )
    
    def get_application_info(self) -> BaseResponseDTO:
        """
        Obtiene información de la aplicación
        
        Returns:
            Información de la aplicación
        """
        return BaseResponseDTO(
            success=True,
            message="Información de la aplicación",
            data={
                "name": "Voxeprint - Calculadora 3D",
                "version": "2.0.0",
                "description": "Sistema de gestión y cálculo de costos para impresión 3D",
                "architecture": "Clean Architecture con DTOs",
                "database": "SQLite",
                "features": [
                    "Gestión de clientes",
                    "Gestión de impresoras",
                    "Gestión de filamentos",
                    "Cálculo de presupuestos",
                    "Sistema de configuración"
                ]
            }
        )

    # === GUARDADO DE PRESUPUESTOS ===
    def _generate_quote_number(self) -> str:
        now = datetime.now()
        return now.strftime("Q%Y%m%d-%H%M%S")

    def get_new_quote_number(self) -> str:
        """Número nuevo público para nombrar archivos antes de persistir."""
        return self._generate_quote_number()

    def save_quote(self, dto: QuoteCreateDTO, calc: QuoteCalculationResponseDTO, pdf_path: str, quote_number: Optional[str] = None) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Persiste un presupuesto en la base de datos con la ruta al PDF generado.
        """
        try:
            errors = dto.validate()
            if errors:
                return ErrorResponseDTO(message="; ".join(errors), error_code="VALIDATION_ERROR")

            qn = quote_number or self._generate_quote_number()
            # Preparar INSERT directo acorde al schema REAL
            hours = float(dto.print_time_minutes) / 60.0 if dto.print_time_minutes else 0.0
            
            # ✅ Obtener timestamp actual en hora local
            from datetime import datetime
            timestamp_local = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # ✅ Obtener moneda actual del sistema
            from core.utils.currency_helper import CurrencyHelper
            current_currency = CurrencyHelper.get_current_currency()
            
            # ✅ CORREGIDO: Incluir created_at, updated_at y currency_code
            columns = (
                "quote_number, customer_id, printer_id, filament_id, project_name, "
                "print_time_hours, filament_weight_grams, final_price, file_path, notes, "
                "created_at, updated_at, currency_code"
            )
            
            # Valores derivados del cálculo con valores seguros
            total_to_pay = getattr(calc, 'total_to_pay', 0.0) or 0.0

            # ✅ CORREGIDO: 13 valores para 13 columnas (incluyendo timestamps y currency_code)
            values = (
                qn,  # quote_number
                dto.customer_id or None,  # customer_id
                dto.printer_id or None,  # printer_id
                dto.filament_id or None,  # filament_id
                dto.project_name or '',  # project_name
                hours,  # print_time_hours
                dto.filament_weight_grams or 0.0,  # filament_weight_grams
                total_to_pay,  # final_price
                str(pdf_path) if pdf_path else '',  # file_path
                dto.notes or '',  # notes
                timestamp_local,  # created_at (hora local)
                timestamp_local,  # updated_at (hora local)
                current_currency,  # currency_code (moneda actual del sistema)
            )
            
            # Debug: verificar coincidencia columnas/valores
            cols_count = len(columns.split(', '))
            logger.debug("VoxeprintFacade", f"Columnas: {cols_count} - Valores: {len(values)} - Moneda: {current_currency}")
            if cols_count != len(values):
                logger.error("VoxeprintFacade", f"MISMATCH: {cols_count} columnas != {len(values)} valores")
            else:
                logger.debug("VoxeprintFacade", f"INSERT OK: {cols_count} columnas = {len(values)} valores")


            placeholders = ', '.join(['?' for _ in range(len(values))])
            command = f"INSERT INTO quotes ({columns}) VALUES ({placeholders})"
            new_id = self.db_connection.execute_command(command, values)

            # Retorno simplificado sin 'data' 
            return BaseResponseDTO(
                success=True, 
                message=f"Presupuesto guardado correctamente. ID: {new_id}, Quote: {qn}, Path: {pdf_path}"
            )
        except Exception as e:
            return ErrorResponseDTO(message=str(e), error_code="SAVE_QUOTE_FAILED")

    def get_all_quotes(self) -> Union[ListResponseDTO, ErrorResponseDTO]:
        """
        Obtiene todos los presupuestos
        
        Returns:
            Lista de presupuestos o error
        """
        try:
            quotes = self.quote_repository.find_all()
            return ListResponseDTO(
                success=True,
                message=f"Se encontraron {len(quotes)} presupuestos",
                data=quotes
            )
        except Exception as e:
            logger.log_exception("VoxeprintFacade", e, "get_all_quotes")
            return ErrorResponseDTO(message="Error al obtener presupuestos.", error_code="GET_QUOTES_FAILED")

    def get_quote_by_id(self, quote_id: int) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Obtiene un presupuesto por ID
        
        Args:
            quote_id: ID del presupuesto
            
        Returns:
            Presupuesto encontrado o error
        """
        try:
            quote = self.quote_repository.find_by_id(quote_id)
            if quote:
                return BaseResponseDTO(
                    success=True,
                    message="Presupuesto encontrado",
                    data=quote
                )
            else:
                return ErrorResponseDTO(
                    message="Presupuesto no encontrado",
                    error_code="QUOTE_NOT_FOUND"
                )
        except Exception as e:
            return ErrorResponseDTO(message=str(e), error_code="GET_QUOTE_FAILED")

    def delete_quote(self, quote_id: int) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Elimina un presupuesto por ID
        
        Args:
            quote_id: ID del presupuesto a eliminar
            
        Returns:
            Respuesta de éxito o error
        """
        try:
            # Verificar que el presupuesto existe
            quote = self.quote_repository.find_by_id(quote_id)
            if not quote:
                return ErrorResponseDTO(
                    message="Presupuesto no encontrado",
                    error_code="QUOTE_NOT_FOUND"
                )
            
            # Eliminar el presupuesto
            deleted = self.quote_repository.delete(quote_id)
            
            if deleted:
                return BaseResponseDTO(
                    success=True,
                    message=f"Presupuesto '{quote.quote_number}' eliminado exitosamente"
                )
            else:
                return ErrorResponseDTO(
                    message="No se pudo eliminar el presupuesto",
                    error_code="DELETE_FAILED"
                )
                
        except Exception as e:
            return ErrorResponseDTO(
                message=f"Error al eliminar presupuesto: {str(e)}",
                error_code="DELETE_QUOTE_FAILED"
            )

    def get_quote_stats(self, start_date: str, end_date: str) -> Union[BaseResponseDTO, ErrorResponseDTO]:
        """
        Obtiene estadísticas de presupuestos para un rango de fechas.
        
        Args:
            start_date: Fecha inicio formato 'YYYY-MM-DD'
            end_date: Fecha fin formato 'YYYY-MM-DD'
            
        Returns:
            BaseResponseDTO con dict de estadísticas en data, o ErrorResponseDTO
        """
        try:
            from application.services.quote_stats_service import QuoteStatsService
            stats_service = QuoteStatsService(self.db_connection)
            stats_data = stats_service.get_stats_for_range(start_date, end_date)
            response = BaseResponseDTO(
                success=True,
                message=f"Estadísticas generadas: {stats_data.get('quote_count', 0)} presupuestos",
            )
            response.data = stats_data
            return response
        except Exception as e:
            logger.log_exception("VoxeprintFacade", e, "get_quote_stats")
            return ErrorResponseDTO(
                message="No se pudieron obtener las estadísticas. Revise los logs para más detalles.",
                error_code="GET_STATS_FAILED"
            )

    # === GESTIÓN DE IMPRESORAS ===
    
    def get_all_printers(self):
        """
        Obtiene todas las impresoras activas (para selector)
        
        Returns:
            Lista de impresoras activas
        """
        try:
            return self.printer_repository.find_active_printers()
        except Exception as e:
            raise Exception(f"Error al obtener impresoras: {str(e)}")
    
    def get_all_printers_including_inactive(self):
        """
        Obtiene TODAS las impresoras (activas e inactivas) para el inventario
        
        Returns:
            Lista de todas las impresoras
        """
        try:
            return self.printer_repository.find_all()
        except Exception as e:
            raise Exception(f"Error al obtener todas las impresoras: {str(e)}")
    
    def get_printer_by_id(self, printer_id: int):
        """
        Obtiene una impresora por su ID
        
        Args:
            printer_id: ID de la impresora
            
        Returns:
            Impresora encontrada o None
        """
        try:
            return self.printer_repository.find_by_id(printer_id)
        except Exception as e:
            raise Exception(f"Error al obtener impresora: {str(e)}")
    
    def search_printers(self, search_term: str):
        """
        Busca impresoras ACTIVAS por término de búsqueda (para selector)
        
        Args:
            search_term: Término de búsqueda
            
        Returns:
            Lista de impresoras activas que coinciden
        """
        try:
            # Buscar solo en impresoras activas
            query = """
                SELECT * FROM printers 
                WHERE is_active = 1 
                AND (name LIKE ? OR brand LIKE ? OR model LIKE ?)
                ORDER BY name
            """
            search_pattern = f"%{search_term}%"
            rows = self.printer_repository.db_connection.execute_query(
                query, 
                (search_pattern, search_pattern, search_pattern)
            )
            
            return [self.printer_repository._row_to_entity(dict(row)) for row in rows]
        except Exception as e:
            raise Exception(f"Error al buscar impresoras: {str(e)}")
    
    def search_all_printers(self, search_term: str):
        """
        Busca TODAS las impresoras (activas e inactivas) para el inventario
        
        Args:
            search_term: Término de búsqueda
            
        Returns:
            Lista de todas las impresoras que coinciden
        """
        try:
            # Buscar en todas las impresoras, sin filtro de activas
            query = """
                SELECT * FROM printers 
                WHERE (name LIKE ? OR brand LIKE ? OR model LIKE ?)
                ORDER BY is_active DESC, name ASC
            """
            search_pattern = f"%{search_term}%"
            rows = self.printer_repository.db_connection.execute_query(
                query, 
                (search_pattern, search_pattern, search_pattern)
            )
            
            return [self.printer_repository._row_to_entity(dict(row)) for row in rows]
        except Exception as e:
            raise Exception(f"Error al buscar todas las impresoras: {str(e)}")
    
    def create_printer(self, name: str, brand: str = "", model: str = "", 
                      power_consumption_watts: float = 0.0, purchase_cost: float = 0.0,
                      maintenance_cost: float = 0.0, maintenance_interval_hours: float = 0.0,
                      useful_life_hours: float = 10000.0):
        """
        Crea una nueva impresora
        
        Args:
            name: Nombre/descripción de la impresora
            brand: Marca
            model: Modelo
            power_consumption_watts: Consumo real en watts (ej: 230W)
            purchase_cost: Costo de compra
            maintenance_cost: Costo total de mantenimiento
            maintenance_interval_hours: Horas entre mantenimientos
            useful_life_hours: Vida útil estimada en horas (7000-15000)
            
        Returns:
            Impresora creada
        """
        try:
            from domain.models.printer import Printer
            from datetime import datetime
            from core.utils.currency_helper import CurrencyHelper
            
            printer = Printer(
                name=name,
                brand=brand,
                model=model,
                power_consumption_watts=power_consumption_watts,
                purchase_cost=purchase_cost,
                maintenance_cost=maintenance_cost,
                maintenance_interval_hours=maintenance_interval_hours,
                useful_life_hours=useful_life_hours,
                is_active=True,
                currency_code=CurrencyHelper.get_current_currency(),  # Guardar moneda actual
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            return self.printer_repository.save(printer)
        except Exception as e:
            raise Exception(f"Error al crear impresora: {str(e)}")
    
    def update_printer(self, printer_id: int, name: str = None, brand: str = None, 
                      model: str = None, power_consumption_watts: float = None, 
                      purchase_cost: float = None, maintenance_cost: float = None, 
                      maintenance_interval_hours: float = None):
        """
        Actualiza una impresora existente
        
        Args:
            printer_id: ID de la impresora
            name: Nuevo nombre (opcional)
            brand: Nueva marca (opcional)
            model: Nuevo modelo (opcional)
            power_consumption_watts: Nuevo consumo en watts (opcional)
            purchase_cost: Nuevo costo de compra (opcional)
            maintenance_cost: Nuevo costo de mantenimiento (opcional)
            maintenance_interval_hours: Nuevo intervalo de mantenimiento (opcional)
            
        Returns:
            Impresora actualizada
        """
        try:
            from datetime import datetime
            
            printer = self.printer_repository.find_by_id(printer_id)
            if not printer:
                raise Exception(f"Impresora con ID {printer_id} no encontrada")
            
            # Actualizar solo los campos proporcionados
            if name is not None:
                printer.name = name
            if brand is not None:
                printer.brand = brand
            if model is not None:
                printer.model = model
            if power_consumption_watts is not None:
                printer.power_consumption_watts = power_consumption_watts
            if purchase_cost is not None:
                printer.purchase_cost = purchase_cost
            if maintenance_cost is not None:
                printer.maintenance_cost = maintenance_cost
            if maintenance_interval_hours is not None:
                printer.maintenance_interval_hours = maintenance_interval_hours
            
            printer.updated_at = datetime.now().isoformat()
            
            return self.printer_repository.save(printer)
        except Exception as e:
            raise Exception(f"Error al actualizar impresora: {str(e)}")
    
    def delete_printer(self, printer_id: int):
        """
        Elimina físicamente una impresora de la base de datos
        Manualmente actualiza las referencias antes de la eliminación por compatibilidad
        
        Args:
            printer_id: ID de la impresora a eliminar
        """
        try:
            printer = self.printer_repository.find_by_id(printer_id)
            if not printer:
                raise Exception(f"Impresora con ID {printer_id} no encontrada")
            
            # ✅ SOLUCIÓN MANUAL: Actualizar referencias antes de eliminar
            # Esto garantiza compatibilidad incluso si ON DELETE SET NULL no funciona
            self._update_printer_references_to_null(printer_id)
            
            # Ahora eliminar la impresora
            self.printer_repository.delete(printer_id)
            
        except Exception as e:
            raise Exception(f"Error al eliminar impresora: {str(e)}")
    
    def _update_printer_references_to_null(self, printer_id: int):
        """
        Actualiza todas las referencias a una impresora a NULL antes de eliminarla
        
        Args:
            printer_id: ID de la impresora
        """
        try:
            # Usar la conexión a la base de datos directamente
            from infrastructure.database.connection import DatabaseConnection
            db = DatabaseConnection()
            
            # Actualizar todas las referencias en la tabla quotes
            update_query = "UPDATE quotes SET printer_id = NULL WHERE printer_id = ?"
            affected_rows = db.execute_command(update_query, (printer_id,))
            
            if affected_rows > 0:
                logger.info("VoxeprintFacade", f"Actualizadas {affected_rows} referencias de presupuestos")
            
        except Exception as e:
            raise Exception(f"Error al actualizar referencias: {str(e)}")

    # === GESTIÓN DE FILAMENTOS ===
    
    def get_all_filaments(self):
        """
        Obtiene todos los filamentos activos para el selector
        
        Returns:
            Lista de filamentos activos
        """
        try:
            return self.filament_repository.find_active_filaments()
        except Exception as e:
            raise Exception(f"Error al obtener filamentos: {str(e)}")
    
    def get_all_filaments_including_inactive(self):
        """
        Obtiene TODOS los filamentos (activos e inactivos) para el inventario
        
        Returns:
            Lista de todos los filamentos
        """
        try:
            return self.filament_repository.get_all()
        except Exception as e:
            raise Exception(f"Error al obtener todos los filamentos: {str(e)}")
    
    def get_filament_by_id(self, filament_id: int):
        """
        Obtiene un filamento por su ID
        
        Args:
            filament_id: ID del filamento
            
        Returns:
            Filamento encontrado o None
        """
        try:
            return self.filament_repository.find_by_id(filament_id)
        except Exception as e:
            raise Exception(f"Error al obtener filamento: {str(e)}")
    
    def search_filaments(self, search_term: str):
        """
        Busca filamentos ACTIVOS por término de búsqueda (para selector)
        
        Args:
            search_term: Término de búsqueda
            
        Returns:
            Lista de filamentos activos que coinciden
        """
        try:
            # Buscar solo en filamentos activos
            query = """
                SELECT * FROM filaments 
                WHERE is_active = 1 
                AND (name LIKE ? OR brand LIKE ? OR type LIKE ? OR color LIKE ?)
                ORDER BY name
            """
            search_pattern = f"%{search_term}%"
            rows = self.filament_repository.db_connection.execute_query(
                query, 
                (search_pattern, search_pattern, search_pattern, search_pattern)
            )
            
            return [self.filament_repository._row_to_entity(dict(row)) for row in rows]
        except Exception as e:
            raise Exception(f"Error al buscar filamentos: {str(e)}")
    
    def search_all_filaments(self, search_term: str):
        """
        Busca TODOS los filamentos (activos e inactivos) para el inventario
        
        Args:
            search_term: Término de búsqueda
            
        Returns:
            Lista de todos los filamentos que coinciden
        """
        try:
            # Buscar en todos los filamentos, sin filtro de activos
            query = """
                SELECT * FROM filaments 
                WHERE (name LIKE ? OR brand LIKE ? OR type LIKE ? OR color LIKE ?)
                ORDER BY is_active DESC, name ASC
            """
            search_pattern = f"%{search_term}%"
            rows = self.filament_repository.db_connection.execute_query(
                query, 
                (search_pattern, search_pattern, search_pattern, search_pattern)
            )
            
            return [self.filament_repository._row_to_entity(dict(row)) for row in rows]
        except Exception as e:
            raise Exception(f"Error al buscar todos los filamentos: {str(e)}")
    
    def create_filament(self, name: str, filament_type: str, brand: str = "", 
                       color: str = "NATURAL", weight_grams: float = 1000.0,
                       price_per_unit: float = 0.0, quantity_rolls: int = 1,
                       current_stock_grams: float = 1000.0, notes: str = ""):
        """
        Crea un nuevo filamento
        
        Args:
            name: Nombre/descripción del filamento
            filament_type: Tipo de filamento (PLA, ABS, etc.)
            brand: Marca del filamento
            color: Color del filamento
            weight_grams: Peso del rollo en gramos
            price_per_unit: Precio por rollo
            quantity_rolls: Cantidad de rollos
            current_stock_grams: Stock actual en gramos
            notes: Notas adicionales
            
        Returns:
            Filamento creado
        """
        try:
            from domain.models.filament import Filament
            from domain.enums.enums import FilamentType, FilamentColor
            from datetime import datetime
            from core.utils.currency_helper import CurrencyHelper
            
            # Calcular precio por gramo
            price_per_gram = price_per_unit / weight_grams if weight_grams > 0 else 0.0
            
            filament = Filament(
                name=name,
                type=FilamentType(filament_type),
                brand=brand,
                color=FilamentColor(color),
                weight_grams=weight_grams,
                price_per_unit=price_per_unit,
                price_per_gram=price_per_gram,
                quantity_rolls=quantity_rolls,
                current_stock_grams=current_stock_grams,
                minimum_stock_grams=100.0,  # Valor por defecto
                is_active=True,
                notes=notes,
                currency_code=CurrencyHelper.get_current_currency(),  # Guardar moneda actual
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            return self.filament_repository.save(filament)
        except Exception as e:
            raise Exception(f"Error al crear filamento: {str(e)}")
    
    def update_filament(self, filament):
        """
        Actualiza un filamento existente
        
        Args:
            filament: Objeto filamento a actualizar
            
        Returns:
            Filamento actualizado
        """
        try:
            from datetime import datetime
            filament.updated_at = datetime.now().isoformat()
            return self.filament_repository.update(filament)
        except Exception as e:
            raise Exception(f"Error al actualizar filamento: {str(e)}")
    
    def delete_filament(self, filament_id: int):
        """
        Elimina físicamente un filamento de la base de datos
        Manualmente actualiza las referencias antes de la eliminación por compatibilidad
        
        Args:
            filament_id: ID del filamento a eliminar
        """
        try:
            filament = self.filament_repository.find_by_id(filament_id)
            if not filament:
                raise Exception(f"Filamento con ID {filament_id} no encontrado")
            
            # ✅ SOLUCIÓN MANUAL: Actualizar referencias antes de eliminar
            # Esto garantiza compatibilidad incluso si ON DELETE SET NULL no funciona
            self._update_filament_references_to_null(filament_id)
            
            # Ahora eliminar el filamento
            return self.filament_repository.delete(filament_id)
            
        except Exception as e:
            raise Exception(f"Error al eliminar filamento: {str(e)}")
    
    def _update_filament_references_to_null(self, filament_id: int):
        """
        Actualiza todas las referencias a un filamento a NULL antes de eliminarlo
        
        Args:
            filament_id: ID del filamento
        """
        try:
            # Actualizar todas las referencias en la tabla quotes
            update_query = "UPDATE quotes SET filament_id = NULL WHERE filament_id = ?"
            affected_rows = self.db_connection.execute_command(update_query, (filament_id,))
            
            if affected_rows > 0:
                logger.info("VoxeprintFacade", f"Actualizadas {affected_rows} referencias de presupuestos para filamento")
            
        except Exception as e:
            raise Exception(f"Error al actualizar referencias del filamento: {str(e)}")
    
    def add_filament_roll_with_weighted_price(self, roll_data):
        """
        Agrega un rollo de filamento usando precio promedio ponderado.
        También crea un registro en filament_rolls.
        """
        try:
            result = self.filament_repository.add_roll_with_weighted_price(roll_data)
            if result:
                # Crear registro individual del rollo
                from domain.models.filament_roll import FilamentRoll
                sku = self.filament_roll_repository.generate_next_sku(result.id)
                roll = FilamentRoll(
                    filament_id=result.id,
                    sku=sku,
                    initial_weight_grams=roll_data['weight_grams'],
                    current_weight_grams=roll_data['weight_grams'],
                    purchase_price=roll_data.get('price_roll', roll_data['weight_grams'] * roll_data.get('price_per_gram', 0)),
                    price_per_gram=roll_data.get('price_per_gram', 0),
                    notes=roll_data.get('notes', '')
                )
                roll.update_price_per_gram()
                self.filament_roll_repository.save(roll)
                # Sincronizar totales del padre
                self._sync_filament_from_rolls(result.id)
            return result
        except Exception as e:
            raise Exception(f"Error al agregar rollo: {str(e)}")

    # === GESTIÓN DE ROLLOS INDIVIDUALES ===

    def get_rolls_for_filament(self, filament_id: int, active_only: bool = True):
        """Obtiene todos los rollos de un filamento"""
        return self.filament_roll_repository.find_by_filament_id(filament_id, active_only)

    def get_roll_stock_summary(self, filament_id: int):
        """Obtiene resumen de stock desde los rollos"""
        return self.filament_roll_repository.get_stock_summary(filament_id)

    def create_filament_roll(self, filament_id: int, weight_grams: float,
                             purchase_price: float, notes: str = ""):
        """Crea un nuevo rollo individual y sincroniza el padre"""
        from domain.models.filament_roll import FilamentRoll
        sku = self.filament_roll_repository.generate_next_sku(filament_id)
        roll = FilamentRoll(
            filament_id=filament_id,
            sku=sku,
            initial_weight_grams=weight_grams,
            current_weight_grams=weight_grams,
            purchase_price=purchase_price,
            notes=notes
        )
        roll.update_price_per_gram()
        saved = self.filament_roll_repository.save(roll)
        self._sync_filament_from_rolls(filament_id)
        return saved

    def update_filament_roll(self, roll):
        """Actualiza un rollo existente y sincroniza el padre"""
        saved = self.filament_roll_repository.save(roll)
        self._sync_filament_from_rolls(roll.filament_id)
        return saved

    def delete_filament_roll(self, roll_id: int, filament_id: int):
        """Desactiva un rollo (soft delete) y sincroniza el padre"""
        self.filament_roll_repository.soft_delete(roll_id)
        self._sync_filament_from_rolls(filament_id)

    def adjust_roll_weight(self, roll_id: int, new_weight: float, filament_id: int):
        """Ajusta el peso de un rollo y sincroniza el padre"""
        self.filament_roll_repository.adjust_weight(roll_id, new_weight)
        self._sync_filament_from_rolls(filament_id)

    def _sync_filament_from_rolls(self, filament_id: int):
        """
        Sincroniza los campos agregados del filamento padre
        desde los rollos activos (fuente de verdad).
        """
        try:
            filament = self.filament_repository.find_by_id(filament_id)
            if not filament:
                return

            summary = self.filament_roll_repository.get_stock_summary(filament_id)

            filament.quantity_rolls = summary['roll_count']
            filament.current_stock_grams = summary['total_stock_grams']
            filament.price_per_gram = summary['weighted_price_per_gram']

            # Recalcular price_per_unit representativo (precio promedio por rollo)
            if summary['roll_count'] > 0:
                filament.price_per_unit = summary['total_value'] / summary['roll_count']
            else:
                filament.price_per_unit = 0

            from datetime import datetime
            filament.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.filament_repository.update(filament)

        except Exception as e:
            logger.error("VoxeprintFacade", f"Error sincronizando filamento {filament_id}: {e}")
