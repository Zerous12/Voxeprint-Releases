"""
Servicio para cálculos de presupuestos de impresión 3D
"""
from typing import Optional, Union
from datetime import datetime

from config.app_config import APP_CONFIG
from .base_service import BaseService
from application.dtos.quote_dtos import (
    QuoteCalculationRequestDTO,
    QuoteCalculationResponseDTO
)
from application.dtos.base_dtos import BaseResponseDTO, ErrorResponseDTO
from infrastructure.database.repositories.printer_repository import PrinterRepository
from infrastructure.database.repositories.filament_repository import FilamentRepository
from infrastructure.database.repositories.system_config_repository import SystemConfigRepository
from infrastructure.database.connection import DatabaseConnection


class CalculationService(BaseService):
    """Servicio para cálculos de costos de impresión 3D"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el servicio de cálculos
        
        Args:
            db_connection: Conexión a la base de datos
        """
        super().__init__(db_connection)
        self.printer_repository = PrinterRepository(db_connection)
        self.filament_repository = FilamentRepository(db_connection)
        self.config_repository = SystemConfigRepository(db_connection)
    
    def calculate_quote_costs(self, dto: QuoteCalculationRequestDTO) -> Union[QuoteCalculationResponseDTO, ErrorResponseDTO]:
        """
        Calcula todos los costos de un presupuesto
        
        Args:
            dto: Datos para el cálculo
            
        Returns:
            Costos calculados o error
        """
        # Validar DTO
        validation_error = self.validate_dto(dto)
        if validation_error:
            return validation_error
        
        try:
            # Obtener datos de impresora
            printer = self.printer_repository.find_by_id(dto.printer_id)
            if not printer:
                return self.create_error_response(
                    message="Impresora no encontrada",
                    error_code="PRINTER_NOT_FOUND"
                )
            
            if not printer.is_active:
                return self.create_error_response(
                    message="La impresora seleccionada no está activa",
                    error_code="PRINTER_INACTIVE"
                )
            
            # Obtener datos de filamento
            filament = self.filament_repository.find_by_id(dto.filament_id)
            if not filament:
                return self.create_error_response(
                    message="Filamento no encontrado",
                    error_code="FILAMENT_NOT_FOUND"
                )
            
            if not filament.is_active:
                return self.create_error_response(
                    message="El filamento seleccionado no está activo",
                    error_code="FILAMENT_INACTIVE"
                )
            
            # ✅ FASE 5: Convertir impresora y filamento a moneda del sistema si es necesario
            from core.utils.currency_helper import CurrencyHelper
            from core.services.currency_conversion_service import CurrencyConversionService
            from domain.models.printer import Printer
            from domain.models.filament import Filament
            
            current_currency = CurrencyHelper.get_current_currency()
            conversion_service = CurrencyConversionService(self.db_connection)
            
            # Verificar si necesitan conversión
            printer_currency = getattr(printer, 'currency_code', 'PYG')
            filament_currency = getattr(filament, 'currency_code', 'PYG')
            
            # Convertir impresora si es necesario
            if printer_currency != current_currency:
                converted_purchase = conversion_service.convert_amount(
                    printer.purchase_cost, printer_currency, current_currency
                )
                converted_maintenance = conversion_service.convert_amount(
                    printer.maintenance_cost, printer_currency, current_currency
                )
                
                if converted_purchase is None or converted_maintenance is None:
                    return ErrorResponseDTO(
                        success=False,
                        message=f"No se pudo convertir costos de impresora de {printer_currency} a {current_currency}. Verifique las tasas de cambio.",
                        error_code="CONVERSION_ERROR"
                    )
                
                printer = Printer(
                        id=printer.id,
                        name=printer.name,
                        brand=printer.brand,
                        model=printer.model,
                        power_consumption_watts=printer.power_consumption_watts,
                        purchase_cost=converted_purchase,
                        maintenance_cost=converted_maintenance,
                        maintenance_interval_hours=printer.maintenance_interval_hours,
                        useful_life_hours=printer.useful_life_hours,
                        is_active=printer.is_active,
                        currency_code=current_currency,
                        created_at=printer.created_at,
                        updated_at=printer.updated_at
                    )
            
            # Convertir filamento si es necesario
            if filament_currency != current_currency:
                converted_price_unit = conversion_service.convert_amount(
                    filament.price_per_unit, filament_currency, current_currency
                )
                converted_price_gram = conversion_service.convert_amount(
                    filament.price_per_gram, filament_currency, current_currency
                )
                
                if converted_price_unit is None or converted_price_gram is None:
                    return ErrorResponseDTO(
                        success=False,
                        message=f"No se pudo convertir precios de filamento de {filament_currency} a {current_currency}. Verifique las tasas de cambio.",
                        error_code="CONVERSION_ERROR"
                    )
                
                filament = Filament(
                        id=filament.id,
                        name=filament.name,
                        type=filament.type,
                        brand=filament.brand,
                        color=filament.color,
                        weight_grams=filament.weight_grams,
                        price_per_unit=converted_price_unit,
                        price_per_gram=converted_price_gram,
                        quantity_rolls=filament.quantity_rolls,
                        current_stock_grams=filament.current_stock_grams,
                        minimum_stock_grams=filament.minimum_stock_grams,
                        is_active=filament.is_active,
                        notes=filament.notes,
                        currency_code=current_currency,
                        created_at=filament.created_at,
                        updated_at=filament.updated_at
                    )
            
            # Obtener tarifa eléctrica (del DTO o de configuración)
            # NOTA: El multiplicador 1.6 se aplica para cubrir costos operativos adicionales
            electricity_rate = dto.electricity_rate_per_kwh
            if electricity_rate is None:
                # Obtener tarifa base y aplicar multiplicador
                base_rate = self._get_system_config_float(
                    "electricity_rate_per_kwh", 
                    APP_CONFIG.calculation.default_electricity_rate
                )
                electricity_rate = base_rate * APP_CONFIG.calculation.electricity_rate_multiplier
            
            # Calcular costos base
            # ── MULTICOLOR: calcular costo por slot y sumar ──────────────────────
            if dto.filament_slots:
                material_cost = 0.0
                for slot in dto.filament_slots:
                    if slot.filament_id <= 0 or slot.weight_grams <= 0:
                        continue
                    slot_fil = self.filament_repository.find_by_id(slot.filament_id)
                    if not slot_fil:
                        continue
                    # Conversión de moneda para el filamento del slot si es necesario
                    slot_currency = getattr(slot_fil, 'currency_code', 'PYG')
                    if slot_currency != current_currency:
                        conv_pgram = conversion_service.convert_amount(
                            slot_fil.price_per_gram, slot_currency, current_currency
                        )
                        conv_punit = conversion_service.convert_amount(
                            slot_fil.price_per_unit, slot_currency, current_currency
                        )
                        if conv_pgram is not None:
                            from domain.models.filament import Filament as _FilamentModel
                            slot_fil = _FilamentModel(
                                id=slot_fil.id, name=slot_fil.name, type=slot_fil.type,
                                brand=slot_fil.brand, color=slot_fil.color,
                                weight_grams=slot_fil.weight_grams,
                                price_per_unit=conv_punit or slot_fil.price_per_unit,
                                price_per_gram=conv_pgram,
                                quantity_rolls=slot_fil.quantity_rolls,
                                current_stock_grams=slot_fil.current_stock_grams,
                                minimum_stock_grams=slot_fil.minimum_stock_grams,
                                is_active=slot_fil.is_active, notes=slot_fil.notes,
                                currency_code=current_currency,
                                created_at=slot_fil.created_at, updated_at=slot_fil.updated_at
                            )
                    slot_cost = self._calculate_material_cost(slot_fil, slot.weight_grams)
                    slot.price_per_gram = slot_fil.price_per_gram
                    slot.slot_cost = slot_cost
                    material_cost += slot_cost
            else:
                # ── MONOCOLOR legacy ─────────────────────────────────────────────
                material_cost = self._calculate_material_cost(filament, dto.filament_weight_grams)
            # ────────────────────────────────────────────────────────────────────
            electricity_cost = self._calculate_electricity_cost(
                printer, dto.print_time_minutes, electricity_rate
            )
            operation_cost = self._calculate_operation_cost(
                printer, dto.print_time_minutes
            ) + self._calculate_overhead_cost(dto.print_time_minutes)
            
            # Calcular subtotales
            subtotal_base_costs = material_cost + electricity_cost + operation_cost
            failure_margin_cost = subtotal_base_costs * (dto.failure_margin_percent / 100)
            subtotal_with_margin = subtotal_base_costs + failure_margin_cost

            # Comisión: si no se proporciona comisión, usar margen de ganancia como comisión (estilo Excel)
            commission_rate = dto.commission_rate_percent if dto.commission_rate_percent and dto.commission_rate_percent > 0 else dto.profit_margin_percent

            # Blindar comisión del IVA: multiplicar la comisión por (1 + tax/100)
            # para que, tras el impuesto, quede íntegra la ganancia esperada
            if getattr(dto, 'commission_tax_shield', False) and dto.tax_rate_percent and dto.tax_rate_percent > 0:
                commission_rate = commission_rate * (1 + dto.tax_rate_percent / 100)

            commission_cost = subtotal_with_margin * (commission_rate / 100)
            subtotal_before_profit = subtotal_with_margin + commission_cost

            # Ganancia adicional: solo si se proporcionó comisión distinta de cero y además hay margen de ganancia separado
            # En modo Excel, cuando comisión = margen de ganancia, no se suma una ganancia adicional
            profit_amount = 0.0
            if dto.commission_rate_percent and dto.commission_rate_percent > 0 and dto.profit_margin_percent and dto.profit_margin_percent > 0:
                profit_amount = subtotal_before_profit * (dto.profit_margin_percent / 100)

            subtotal_before_tax = subtotal_before_profit + profit_amount

            # IVA incluido (estilo Excel): no se suma al total, solo se muestra el monto incluido
            # Fórmula: IVA_incluido = Total - (Total / (1 + iva))
            tax_amount = subtotal_before_tax - (subtotal_before_tax / (1 + (dto.tax_rate_percent / 100))) if dto.tax_rate_percent and dto.tax_rate_percent > 0 else 0.0
            total_to_pay = subtotal_before_tax
            
            # Crear respuesta
            response = QuoteCalculationResponseDTO(
                material_cost=round(material_cost, 2),
                electricity_cost=round(electricity_cost, 2),
                operation_cost=round(operation_cost, 2),  # Ahora contiene el costo de operación completo
                subtotal_base_costs=round(subtotal_base_costs, 2),
                failure_margin_cost=round(failure_margin_cost, 2),
                subtotal_with_margin=round(subtotal_with_margin, 2),
                commission_cost=round(commission_cost, 2),
                subtotal_before_profit=round(subtotal_before_profit, 2),
                profit_amount=round(profit_amount, 2),
                subtotal_before_tax=round(subtotal_before_tax, 2),
                tax_amount=round(tax_amount, 2),
                total_to_pay=round(total_to_pay, 2),
                calculation_timestamp=datetime.now().isoformat(),
                printer_info={
                    "id": printer.id,
                    "name": printer.name,
                    "brand": printer.brand,
                    "model": printer.model,
                    "power_consumption_watts": printer.power_consumption_watts,
                    "operation_cost_per_hour": printer.operation_cost_per_hour,
                    "service_cost_per_hour": printer.service_cost_per_hour,
                    "total_cost_per_hour": printer.total_cost_per_hour
                },
                filament_info={
                    "id": filament.id,
                    "name": filament.name,
                    "type": filament.type.value if hasattr(filament.type, 'value') else str(filament.type),
                    "brand": filament.brand,
                    "color": filament.color.value if hasattr(filament.color, 'value') else str(filament.color),
                    "price_per_gram": filament.price_per_gram
                },
                calculation_details={
                    "print_time_hours": dto.print_time_minutes / 60,
                    "filament_weight_kg": dto.filament_weight_grams / 1000,
                    "electricity_rate_per_kwh": electricity_rate,
                    "failure_margin_percent": dto.failure_margin_percent,
                    "profit_margin_percent": dto.profit_margin_percent,
                    "tax_rate_percent": dto.tax_rate_percent,
                    "commission_rate_percent": dto.commission_rate_percent,
                    "overhead_cost_per_hour": self._get_overhead_per_hour(),
                    "overhead_monthly_total": self._get_overhead_monthly_total(),
                    "is_multicolor": bool(dto.filament_slots),
                    "slot_breakdown": [
                        {
                            "slot_index": s.slot_index,
                            "filament_id": s.filament_id,
                            "weight_grams": s.weight_grams,
                            "price_per_gram": s.price_per_gram,
                            "slot_cost": s.slot_cost,
                        }
                        for s in dto.filament_slots
                    ] if dto.filament_slots else [],
                }
            )
            
            return response
            
        except Exception as e:
            return self.handle_repository_error(e, "calcular costos de presupuesto")
    
    def _calculate_overhead_cost(self, print_time_minutes: float) -> float:
        """
        Calcula el overhead del negocio proporcional al tiempo de impresión.

        Fórmula: (suma_gastos_fijos_mensuales / (horas_dia × dias_mes × impresoras_activas)) × horas_impresión

        Si no hay gastos configurados (todos en 0), retorna 0.0 sin impacto.
        """
        total_monthly = self._get_overhead_monthly_total()
        if total_monthly <= 0:
            return 0.0

        hours_day      = self._get_system_config_float("overhead_hours_per_day",  12.0)
        days_month     = self._get_system_config_float("overhead_days_per_month", 30.0)
        active_printers = self._get_active_printers_count()
        monthly_hours  = hours_day * days_month * max(1, active_printers)
        if monthly_hours <= 0:
            return 0.0

        overhead_per_hour = total_monthly / monthly_hours
        return overhead_per_hour * (print_time_minutes / 60.0)

    def _get_active_printers_count(self) -> int:
        """
        Devuelve el número de impresoras activas para distribuir el overhead.

        Modo 'auto': consulta directamente la BD (impresoras con is_active=1).
        Modo 'manual': usa el valor configurado en system_configs.
        """
        mode = self.config_repository.get_value("overhead_active_printers_mode", "auto")
        if mode == "manual":
            return max(1, int(self._get_system_config_float("overhead_active_printers", 1.0)))
        try:
            active = self.printer_repository.find_active_printers()
            return max(1, len(active))
        except Exception:
            return 1

    def _get_overhead_monthly_total(self) -> float:
        """Suma todos los gastos fijos mensuales configurados."""
        keys = [
            "overhead_rent", "overhead_water", "overhead_internet",
            "overhead_accounting", "overhead_salary",
            "overhead_transport", "overhead_other"
        ]
        return sum(self._get_system_config_float(k, 0.0) for k in keys)

    def _get_overhead_per_hour(self) -> float:
        """Devuelve el overhead por hora calculado (para trazabilidad en calculation_details)."""
        total = self._get_overhead_monthly_total()
        if total <= 0:
            return 0.0
        hours_day      = self._get_system_config_float("overhead_hours_per_day",  12.0)
        days_month     = self._get_system_config_float("overhead_days_per_month", 30.0)
        active_printers = self._get_active_printers_count()
        monthly_hours  = hours_day * days_month * max(1, active_printers)
        return round(total / monthly_hours, 4) if monthly_hours > 0 else 0.0

    def _calculate_material_cost(self, filament, weight_grams: float) -> float:
        """
        Calcula el costo del material
        
        Formula: peso_gramos * precio_por_gramo
        
        Args:
            filament: Entidad filamento
            weight_grams: Peso en gramos
            
        Returns:
            Costo del material
        """
        if filament.price_per_gram <= 0:
            # Si no hay precio por gramo, calcular desde precio por unidad
            if filament.weight_grams > 0 and filament.price_per_unit > 0:
                price_per_gram = filament.price_per_unit / filament.weight_grams
            else:
                price_per_gram = 0.0
        else:
            price_per_gram = filament.price_per_gram
        
        return weight_grams * price_per_gram
    
    def _calculate_electricity_cost(self, printer, print_time_minutes: float, rate_per_kwh: float) -> float:
        """
        Calcula el costo de electricidad usando la fórmula física correcta.
        
        NOTA: La tarifa rate_per_kwh que recibe ya viene multiplicada por 1.6 
        (desde calculate_quote_costs) para cubrir costos operativos adicionales.
        
        Fórmula: (Watts × Horas ÷ 1000) × Tarifa_kWh_con_multiplicador
        
        Ejemplo USD con multiplicador 1.6:
            Tarifa base: 0.12 USD/kWh × 1.6 = 0.192 USD/kWh aplicada
            285W × 2.833h = 807.4 Wh
            807.4 Wh ÷ 1000 = 0.8074 kWh
            0.8074 kWh × 0.192 USD/kWh = $0.155
        
        Ejemplo PYG con multiplicador 1.6:
            Tarifa base: 435 Gs/kWh × 1.6 = 696 Gs/kWh aplicada
            285W × 2.833h = 807.4 Wh
            0.8074 kWh × 696 Gs/kWh = 562 Gs
        
        Args:
            printer: Entidad impresora
            print_time_minutes: Tiempo de impresión en minutos
            rate_per_kwh: Tarifa por kWh con multiplicador incluido
            
        Returns:
            Costo de electricidad en la moneda configurada
        """
        if printer.power_consumption_watts <= 0 or rate_per_kwh <= 0:
            return 0.0
        
        # Convertir minutos a horas
        print_time_hours = print_time_minutes / 60.0
        
        # Calcular kWh consumidos
        watts = float(printer.power_consumption_watts)
        kwh_consumed = (watts * print_time_hours) / 1000.0
        
        # Calcular costo
        cost = kwh_consumed * rate_per_kwh
        
        return cost  # Retornar valor sin redondear (formato se aplica en presentación)
    
    def _calculate_operation_cost(self, printer, print_time_minutes: float) -> float:
        """
        Calcula el costo de operación (desgaste + mantenimiento) para mostrar al cliente
        
        Args:
            printer: Objeto Printer
            print_time_minutes: Tiempo de impresión en minutos
            
        Returns:
            float: Costo de operación en Gs
        """
        try:
            # Usar el método del modelo que calcula desgaste + mantenimiento
            return printer.calculate_operation_cost(print_time_minutes)
        except Exception as e:
            print(f"Error calculando costo de operación: {e}")
            return 0.0
        
        return 0.0

    def _get_system_config_str(self, key: str, default_value: str) -> str:
        """Obtiene un valor de configuración como string."""
        try:
            config = self.config_repository.find_by_key(key)
            if config and config.config_value:
                return str(config.config_value)
        except Exception:
            pass
        return default_value
    
    def _get_system_config_float(self, key: str, default_value: float) -> float:
        """
        Obtiene un valor de configuración como float
        
        Args:
            key: Clave de configuración
            default_value: Valor por defecto
            
        Returns:
            Valor de configuración o valor por defecto
        """
        try:
            config = self.config_repository.find_by_key(key)
            if config and config.config_value:
                return float(config.config_value)
        except (ValueError, TypeError):
            pass
        
        return default_value
    
    def estimate_print_cost_simple(self, printer_id: int, filament_id: int, 
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
        try:
            # Validaciones básicas
            if printer_id <= 0 or filament_id <= 0 or weight_grams <= 0 or time_minutes <= 0:
                return self.create_error_response(
                    message="Parámetros inválidos para estimación",
                    error_code="INVALID_PARAMETERS"
                )
            
            # Obtener datos
            printer = self.printer_repository.find_by_id(printer_id)
            filament = self.filament_repository.find_by_id(filament_id)
            
            if not printer or not filament:
                return self.create_error_response(
                    message="Impresora o filamento no encontrado",
                    error_code="RESOURCES_NOT_FOUND"
                )
            
            # Cálculos básicos
            # Obtener tarifa base y aplicar multiplicador desde configuración global
            base_rate = self._get_system_config_float(
                "electricity_rate",
                APP_CONFIG.calculation.fallback_electricity_rate
            )
            electricity_rate = base_rate * APP_CONFIG.calculation.electricity_rate_multiplier
            
            material_cost = self._calculate_material_cost(filament, weight_grams)
            electricity_cost = self._calculate_electricity_cost(printer, time_minutes, electricity_rate)
            operation_cost = self._calculate_operation_cost(printer, time_minutes)
            
            basic_total = material_cost + electricity_cost + operation_cost
            
            return self.create_success_response(
                message="Estimación calculada",
                data={
                    "material_cost": round(material_cost, 2),
                    "electricity_cost": round(electricity_cost, 2),
                    "operation_cost": round(operation_cost, 2),
                    "basic_total": round(basic_total, 2),
                    "printer_name": printer.name,
                    "filament_name": filament.name,
                    "calculation_time": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return self.handle_repository_error(e, "estimar costo básico")
