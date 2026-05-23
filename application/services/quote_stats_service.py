from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import OrderedDict
from infrastructure.database.connection import DatabaseConnection
from infrastructure.database.repositories.quote_repository import QuoteRepository
from core.utils.logger import logger
from core.utils.currency_helper import CurrencyHelper
from core.services.currency_conversion_service import CurrencyConversionService


class QuoteStatsService:
    """Servicio para obtener estadísticas de presupuestos en un rango de fechas"""

    def __init__(self, db_connection: DatabaseConnection):
        self.quote_repository = QuoteRepository(db_connection)
        self.currency_conversion = CurrencyConversionService()

    def get_stats_for_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        end_date_full = f"{end_date} 23:59:59"
        start_date_full = f"{start_date} 00:00:00"

        try:
            base_currency = CurrencyHelper.get_current_currency()

            summary_rows = self.quote_repository.get_summary_stats(start_date_full, end_date_full)
            monthly_rows = self.quote_repository.get_monthly_stats(start_date_full, end_date_full)
            weekly_rows = self.quote_repository.get_weekly_stats(start_date_full, end_date_full)
            daily_rows = self.quote_repository.get_daily_stats(start_date_full, end_date_full)
            customer_rows = self.quote_repository.get_top_customers(start_date_full, end_date_full)
            filament_rows = self.quote_repository.get_top_filaments(start_date_full, end_date_full)
            all_amount_rows = self.quote_repository.get_all_amounts_in_range(start_date_full, end_date_full)

            summary = self._aggregate_summary(summary_rows, base_currency)

            monthly_merged = self._merge_time_series(monthly_rows, base_currency, 'month')
            weekly_merged = self._merge_time_series(weekly_rows, base_currency, 'week')
            daily_merged = self._merge_time_series(daily_rows, base_currency, 'day')

            growth_percent = self._calculate_monthly_growth(monthly_merged)

            stats_data = {
                'start_date': start_date,
                'end_date': end_date,
                'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'currency_code': base_currency,
                'total_amount': float(summary.get('total_amount', 0)),
                'quote_count': int(summary.get('quote_count', 0)),
                'avg_ticket': float(summary.get('avg_ticket', 0)),
                'max_amount': float(summary.get('max_amount', 0)),
                'min_amount': float(summary.get('min_amount', 0)),
                'growth_percent': growth_percent,
                'monthly': self._format_monthly(monthly_merged),
                'weekly': self._format_weekly(weekly_merged),
                'daily': self._format_daily(daily_merged, end_date),
                'top_customers': self._merge_customer_ranking(customer_rows, base_currency),
                'top_filaments': self._merge_filament_ranking(filament_rows, base_currency),
                'quote_amounts': self._convert_amount_list(all_amount_rows, base_currency),
            }

            logger.info("QuoteStatsService",
                         f"Estadísticas generadas: {stats_data['quote_count']} presupuestos, "
                         f"rango {start_date} a {end_date}, moneda {base_currency}")

            return stats_data

        except Exception as e:
            logger.log_exception("QuoteStatsService", e, "get_stats_for_range")
            raise

    def _convert_amount(self, amount: float, from_currency: str, to_currency: str) -> float:
        if not amount or from_currency == to_currency:
            return amount
        converted = self.currency_conversion.convert_amount(amount, from_currency, to_currency)
        return converted if converted is not None else amount

    def _merge_time_series(self, rows: List[Dict[str, Any]], base_currency: str, period_key: str) -> List[Dict[str, Any]]:
        merged = OrderedDict()
        for row in rows:
            period = row[period_key]
            if period not in merged:
                merged[period] = {k: v for k, v in row.items() if k not in ('currency_code', period_key)}
                merged[period][period_key] = period
                merged[period]['total_amount'] = 0.0
                merged[period]['quote_count'] = 0

            currency = row.get('currency_code', 'PYG')
            amount = self._convert_amount(float(row.get('total_amount', 0)), currency, base_currency)
            merged[period]['total_amount'] += amount
            merged[period]['quote_count'] += int(row.get('quote_count', 0))

        return list(merged.values())

    def _aggregate_summary(self, rows: List[Dict[str, Any]], base_currency: str) -> Dict[str, Any]:
        result = {
            'total_amount': 0.0,
            'quote_count': 0,
            'avg_ticket': 0.0,
            'max_amount': 0.0,
            'min_amount': float('inf'),
        }

        for row in rows:
            currency = row.get('currency_code', 'PYG')
            result['quote_count'] += int(row.get('quote_count', 0))

            total = self._convert_amount(float(row.get('total_amount', 0)), currency, base_currency)
            result['total_amount'] += total

            max_amt = self._convert_amount(float(row.get('max_amount', 0)), currency, base_currency)
            result['max_amount'] = max(result['max_amount'], max_amt)

            min_amt = self._convert_amount(float(row.get('min_amount', 0)), currency, base_currency)
            if min_amt > 0:
                result['min_amount'] = min(result['min_amount'], min_amt)

        if result['quote_count'] > 0:
            result['avg_ticket'] = result['total_amount'] / result['quote_count']
        if result['min_amount'] == float('inf'):
            result['min_amount'] = 0.0

        return result

    def _merge_customer_ranking(self, rows: List[Dict[str, Any]], base_currency: str, limit: int = 7) -> List[tuple]:
        entities = OrderedDict()
        for row in rows:
            cid = row.get('customer_id')
            if cid is None:
                cid = f"__unknown_{len(entities)}"
            if cid not in entities:
                entities[cid] = {
                    'name': row.get('customer_name', ''),
                    'total_amount': 0.0,
                    'quote_count': 0,
                }

            currency = row.get('currency_code', 'PYG')
            amount = self._convert_amount(float(row.get('total_amount', 0)), currency, base_currency)
            entities[cid]['total_amount'] += amount
            entities[cid]['quote_count'] += int(row.get('quote_count', 0))

        sorted_entities = sorted(entities.values(), key=lambda x: x['total_amount'], reverse=True)
        return [(e['name'], e['total_amount'], e['quote_count']) for e in sorted_entities[:limit]]

    def _merge_filament_ranking(self, rows: List[Dict[str, Any]], base_currency: str, limit: int = 6) -> List[tuple]:
        entities = OrderedDict()
        for row in rows:
            fid = row.get('filament_id')
            if fid is None:
                fid = f"__unknown_{len(entities)}"
            if fid not in entities:
                entities[fid] = {
                    'name': row.get('filament_name', ''),
                    'total_amount': 0.0,
                    'usage_count': 0,
                }

            currency = row.get('currency_code', 'PYG')
            amount = self._convert_amount(float(row.get('total_amount', 0)), currency, base_currency)
            entities[fid]['total_amount'] += amount
            entities[fid]['usage_count'] += int(row.get('usage_count', 0))

        sorted_entities = sorted(entities.values(), key=lambda x: x['total_amount'], reverse=True)
        return [(e['name'], e['usage_count'], e['total_amount']) for e in sorted_entities[:limit]]

    def _convert_amount_list(self, rows: List[Dict[str, Any]], base_currency: str) -> List[float]:
        result = []
        for row in rows:
            amt = float(row.get('final_price', 0))
            currency = row.get('currency_code', 'PYG')
            result.append(self._convert_amount(amt, currency, base_currency))
        return result

    def _calculate_monthly_growth(self, monthly: List[Dict[str, Any]]) -> float:
        if len(monthly) < 2:
            return 0.0
        current = float(monthly[-1].get('total_amount', 0))
        previous = float(monthly[-2].get('total_amount', 0))
        if previous > 0:
            return ((current - previous) / previous) * 100
        return 0.0

    def _format_monthly(self, monthly: List[Dict[str, Any]]) -> Dict[str, Any]:
        months = []
        amounts = []
        counts = []
        for row in monthly:
            try:
                dt = datetime.strptime(row['month'], '%Y-%m')
                months.append(dt.strftime('%b %Y'))
            except (ValueError, KeyError):
                months.append(str(row.get('month', '?')))
            amounts.append(float(row.get('total_amount', 0)))
            counts.append(int(row.get('quote_count', 0)))
        return {'months': months, 'amounts': amounts, 'counts': counts}

    def _format_weekly(self, weekly: List[Dict[str, Any]]) -> Dict[str, Any]:
        data = weekly[-8:] if len(weekly) > 8 else weekly
        labels = []
        amounts = []
        for i, row in enumerate(data):
            week_start = row.get('week_start', '')
            if week_start:
                try:
                    dt = datetime.strptime(week_start, '%Y-%m-%d')
                    labels.append(dt.strftime('%d/%m'))
                except ValueError:
                    labels.append(f'Sem {i+1}')
            else:
                labels.append(f'Sem {i+1}')
            amounts.append(float(row.get('total_amount', 0)))
        return {'labels': labels, 'amounts': amounts}

    def _format_daily(self, daily: List[Dict[str, Any]], end_date: str) -> Dict[str, Any]:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            end_dt = datetime.now()

        start_dt = end_dt - timedelta(days=13)

        day_map = {}
        for row in daily:
            day_map[row['day']] = float(row.get('total_amount', 0))

        labels = []
        amounts = []
        current = start_dt
        while current <= end_dt:
            day_key = current.strftime('%Y-%m-%d')
            labels.append(current.strftime('%d/%m'))
            amounts.append(day_map.get(day_key, 0))
            current += timedelta(days=1)

        return {'labels': labels, 'amounts': amounts}
