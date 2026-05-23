"""
Generación de PDF de Estadísticas de Presupuestos — Voxeprint 3D
Genera un PDF profesional A4 con gráficos de estadísticas
usando matplotlib (renderizado a imagen) + ReportLab (composición PDF).

Basado en el mockup tools/stats_pdf_mockup_demo.py pero con datos reales
provenientes de QuoteStatsService.
"""
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader

from core.utils.logger import logger
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from core.utils.currency_helper import CurrencyHelper


# ══════════════════════════════════════════════════════════
# CONFIGURACIÓN VISUAL
# ══════════════════════════════════════════════════════════

PAGE_W, PAGE_H = A4
MARGIN = 25 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

COLORS_HEX = {
    'primary': '#0070C0',
    'secondary': '#00B050',
    'accent': '#FF6B35',
    'warning': '#FFC000',
    'danger': '#FF4444',
    'neutral': '#808080',
    'dark_text': '#2D3436',
    'grid': '#E0E0E0',
}

CHART_PALETTE = ['#0070C0', '#00B050', '#FF6B35', '#FFC000', '#8E44AD',
                 '#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6']

RL_PRIMARY = colors.HexColor('#0070C0')
RL_SECONDARY = colors.HexColor('#00B050')
RL_ACCENT = colors.HexColor('#FF6B35')
RL_DANGER = colors.HexColor('#FF4444')
RL_TEXT = colors.HexColor('#2D3436')
RL_GRID = colors.HexColor('#DEE2E6')


def _setup_matplotlib_style():
    """Estilo matplotlib para renderizado limpio a imagen"""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Segoe UI', 'Arial', 'DejaVu Sans'],
        'font.size': 9,
        'axes.titlesize': 11,
        'axes.titleweight': 'bold',
        'axes.labelsize': 9,
        'axes.facecolor': '#FAFBFC',
        'axes.edgecolor': '#DEE2E6',
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.color': '#E0E0E0',
        'figure.facecolor': 'white',
        'figure.dpi': 180,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,
    })


# ══════════════════════════════════════════════════════════
# HELPERS DE FORMATO
# ══════════════════════════════════════════════════════════

def _fmt_currency_short(value, currency_code="PYG", pos=None):
    """Formato abreviado para ejes de gráficos (Gs. 150K, $ 1.2M)"""
    symbol = CurrencyHelper.get_symbol(currency_code)
    decimals = CurrencyHelper.get_decimals(currency_code)
    if value >= 1_000_000:
        return f"{symbol} {value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{symbol} {value/1_000:.0f}K"
    fmt = f"{{:.{decimals}f}}"
    return f"{symbol} {fmt.format(value)}"


def _fmt_currency_full(value, currency_code="PYG"):
    """Formato completo con símbolo y decimales según moneda"""
    return CurrencyHelper.format(value, currency_code)


def _chart_to_image(fig) -> ImageReader:
    """Convierte una figura matplotlib a un ImageReader para ReportLab"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.08)
    plt.close(fig)
    buf.seek(0)
    return ImageReader(buf)


# ══════════════════════════════════════════════════════════
# GENERACIÓN DE GRÁFICOS
# ══════════════════════════════════════════════════════════

def _make_chart_monthly_bars(monthly_data, currency_code="PYG"):
    """Montos cotizados por mes"""
    months = monthly_data['months']
    amounts = monthly_data['amounts']
    if not months:
        return _make_empty_chart(tr(I18N.StatsPDF.CHART_MONTHLY), tr(I18N.StatsPDF.EMPTY_NO_DATA))

    fig, ax = plt.subplots(figsize=(7, 2.8))
    x = np.arange(len(months))
    bars = ax.bar(x, amounts, color=COLORS_HEX['primary'],
                  alpha=0.85, width=0.7, edgecolor='white', linewidth=0.5)
    if len(bars) > 0:
        bars[-1].set_color(COLORS_HEX['accent'])
        bars[-1].set_alpha(1.0)
    ax.set_title(tr(I18N.StatsPDF.CHART_MONTHLY), pad=8, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels([m[:7] for m in months], rotation=45, ha='right')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: _fmt_currency_short(v, currency_code)))
    ax.set_ylabel(tr(I18N.StatsPDF.AXIS_AMOUNT), fontsize=8)
    # Anotar valores grandes
    if amounts:
        threshold = max(amounts) * 0.6
        for bar, val in zip(bars, amounts):
            if val > threshold:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(amounts)*0.02,
                        _fmt_currency_short(val, currency_code), ha='center', va='bottom', fontsize=6.5, fontweight='bold')
    fig.tight_layout()
    return _chart_to_image(fig)


def _make_chart_trend(monthly_data, currency_code="PYG"):
    """Evolución temporal + tendencia"""
    months = monthly_data['months']
    amounts = monthly_data['amounts']
    counts = monthly_data['counts']
    if len(months) < 2:
        return _make_empty_chart(tr(I18N.StatsPDF.CHART_TREND), tr(I18N.StatsPDF.EMPTY_NEED_MONTHS))

    fig, ax = plt.subplots(figsize=(7, 2.8))
    x = np.arange(len(months))
    symbol = CurrencyHelper.get_symbol(currency_code)
    ax.plot(x, amounts, color=COLORS_HEX['primary'],
            linewidth=2.2, marker='o', markersize=5,
            markerfacecolor='white', markeredgewidth=1.8, label=tr(I18N.StatsPDF.AXIS_AMOUNT), zorder=3)
    ax.fill_between(x, amounts, alpha=0.12, color=COLORS_HEX['primary'])
    z = np.polyfit(x, amounts, 1)
    p = np.poly1d(z)
    trend_label = f'+{z[0]/1000:.0f}K/mes' if z[0] >= 0 else f'{z[0]/1000:.0f}K/mes'
    ax.plot(x, p(x), '--', color=COLORS_HEX['danger'], linewidth=1.3,
            alpha=0.7, label=f'Tendencia ({trend_label})')
    ax2 = ax.twinx()
    ax2.bar(x, counts, alpha=0.18, color=COLORS_HEX['secondary'],
            width=0.5, label=tr(I18N.StatsPDF.AXIS_COUNT))
    ax2.set_ylabel(tr(I18N.StatsPDF.AXIS_COUNT), fontsize=7, color=COLORS_HEX['secondary'])
    ax2.tick_params(axis='y', labelcolor=COLORS_HEX['secondary'], labelsize=7)
    ax.set_title(tr(I18N.StatsPDF.CHART_TREND), pad=8, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels([m[:7] for m in months], rotation=45, ha='right')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: _fmt_currency_short(v, currency_code)))
    ax.set_ylabel(tr(I18N.StatsPDF.AXIS_AMOUNT), fontsize=8)
    ax.legend(loc='upper left', fontsize=7)
    ax2.legend(loc='upper right', fontsize=7)
    fig.tight_layout()
    return _chart_to_image(fig)


def _make_chart_productivity(monthly_data, currency_code="PYG"):
    """Productividad: volumen + ticket promedio"""
    months = monthly_data['months']
    amounts = monthly_data['amounts']
    counts = monthly_data['counts']
    if not months:
        return _make_empty_chart(tr(I18N.StatsPDF.CHART_PRODUCTIVITY), tr(I18N.StatsPDF.EMPTY_NO_DATA))

    fig, ax = plt.subplots(figsize=(7, 2.8))
    x = np.arange(len(months))
    avg_tickets = [a / c if c > 0 else 0 for a, c in zip(amounts, counts)]
    bars = ax.bar(x, counts, color=COLORS_HEX['primary'], alpha=0.8,
                  width=0.6, edgecolor='white', label=tr(I18N.StatsPDF.KPI_QUOTES_DESC))
    ax2 = ax.twinx()
    ax2.plot(x, avg_tickets, color=COLORS_HEX['accent'], linewidth=2.2,
             marker='D', markersize=4, markerfacecolor=COLORS_HEX['accent'],
             label=tr(I18N.StatsPDF.KPI_AVG_TICKET_DESC), zorder=3)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: _fmt_currency_short(v, currency_code)))
    ax2.set_ylabel(tr(I18N.StatsPDF.AXIS_AVG_TICKET), color=COLORS_HEX['accent'], fontsize=7)
    ax2.tick_params(axis='y', labelcolor=COLORS_HEX['accent'], labelsize=7)
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                str(count), ha='center', va='bottom', fontsize=7, fontweight='bold')
    ax.set_title(tr(I18N.StatsPDF.CHART_PRODUCTIVITY), pad=8, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels([m[:7] for m in months], rotation=45, ha='right')
    ax.set_ylabel(tr(I18N.StatsPDF.AXIS_COUNT), fontsize=8)
    ax.legend(loc='upper left', fontsize=7)
    ax2.legend(loc='upper right', fontsize=7)
    fig.tight_layout()
    return _chart_to_image(fig)


def _make_chart_distribution(quote_amounts, currency_code="PYG"):
    """Distribución de montos"""
    if not quote_amounts or len(quote_amounts) < 3:
        return _make_empty_chart(tr(I18N.StatsPDF.CHART_DISTRIBUTION), tr(I18N.StatsPDF.EMPTY_NEED_QUOTES))

    from matplotlib.patches import Patch
    fig, ax = plt.subplots(figsize=(4.5, 2.8))
    symbol = CurrencyHelper.get_symbol(currency_code)
    amounts_k = [a / 1000 for a in quote_amounts]
    n, bins, patches = ax.hist(amounts_k, bins=min(15, len(amounts_k)),
                                color=COLORS_HEX['primary'],
                                alpha=0.75, edgecolor='white', linewidth=0.8)
    for i, patch in enumerate(patches):
        if bins[i] < 200:
            patch.set_facecolor(COLORS_HEX['secondary'])
        elif bins[i] < 600:
            patch.set_facecolor(COLORS_HEX['primary'])
        else:
            patch.set_facecolor(COLORS_HEX['accent'])
    avg = np.mean(amounts_k)
    ax.axvline(avg, color=COLORS_HEX['danger'], linestyle='--', linewidth=1.5, alpha=0.8)
    ax.text(avg + max(amounts_k)*0.02, ax.get_ylim()[1] * 0.85,
            f'{tr(I18N.StatsPDF.LEGEND_AVG)}\n{avg:.0f}K',
            fontsize=7, color=COLORS_HEX['danger'], fontweight='bold')
    ax.set_title(tr(I18N.StatsPDF.CHART_DISTRIBUTION), pad=8, fontsize=11)
    ax.set_xlabel(f'{symbol} (miles)', fontsize=8)
    ax.set_ylabel(tr(I18N.StatsPDF.AXIS_COUNT), fontsize=8)
    legend_elements = [
        Patch(facecolor=COLORS_HEX['secondary'], label=tr(I18N.StatsPDF.LEGEND_LOW)),
        Patch(facecolor=COLORS_HEX['primary'], label=tr(I18N.StatsPDF.LEGEND_MEDIUM)),
        Patch(facecolor=COLORS_HEX['accent'], label=tr(I18N.StatsPDF.LEGEND_HIGH)),
    ]
    ax.legend(handles=legend_elements, fontsize=7, loc='upper right')
    fig.tight_layout()
    return _chart_to_image(fig)


def _make_chart_top_customers(top_customers, currency_code="PYG"):
    """Top clientes"""
    if not top_customers:
        return _make_empty_chart(tr(I18N.StatsPDF.CHART_TOP_CUSTOMERS), tr(I18N.StatsPDF.EMPTY_NO_CUSTOMERS))

    fig, ax = plt.subplots(figsize=(7, 2.6))
    names = [c[0][:30] for c in reversed(top_customers)]
    amounts = [c[1] for c in reversed(top_customers)]
    counts = [c[2] for c in reversed(top_customers)]
    y = np.arange(len(names))
    palette = CHART_PALETTE[:len(names)]
    bars = ax.barh(y, amounts, color=palette,
                   alpha=0.85, height=0.55, edgecolor='white')
    max_amt = max(amounts) if amounts else 1
    for bar, amt, cnt in zip(bars, amounts, counts):
        ax.text(bar.get_width() + max_amt * 0.02, bar.get_y() + bar.get_height()/2,
                f'{_fmt_currency_short(amt, currency_code)}  ({cnt} pres.)', va='center', fontsize=7)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_title(tr(I18N.StatsPDF.CHART_TOP_CUSTOMERS), pad=8, fontsize=11)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: _fmt_currency_short(v, currency_code)))
    ax.set_xlim(0, max_amt * 1.35)
    fig.tight_layout()
    return _chart_to_image(fig)


def _make_chart_top_filaments(top_filaments, currency_code="PYG"):
    """Top filamentos"""
    if not top_filaments:
        return _make_empty_chart(tr(I18N.StatsPDF.CHART_TOP_FILAMENTS), tr(I18N.StatsPDF.EMPTY_NO_FILAMENTS))

    fig, ax = plt.subplots(figsize=(7, 2.4))
    names = [f[0][:28] for f in reversed(top_filaments)]
    uses = [f[1] for f in reversed(top_filaments)]
    amounts = [f[2] for f in reversed(top_filaments)]
    y = np.arange(len(names))
    bars = ax.barh(y, amounts, color=COLORS_HEX['primary'], alpha=0.75,
                   height=0.55, edgecolor='white')
    max_amt = max(amounts) if amounts else 1
    for bar, use, amt in zip(bars, uses, amounts):
        ax.text(bar.get_width() + max_amt * 0.02, bar.get_y() + bar.get_height()/2,
                f'{_fmt_currency_short(amt, currency_code)}  |  {use} usos', va='center', fontsize=7)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=7.5)
    ax.set_title(tr(I18N.StatsPDF.CHART_TOP_FILAMENTS), pad=8, fontsize=11)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: _fmt_currency_short(v, currency_code)))
    ax.set_xlim(0, max_amt * 1.4)
    fig.tight_layout()
    return _chart_to_image(fig)


def _make_chart_weekly(weekly_data, currency_code="PYG"):
    """Cotizado semanal"""
    labels = weekly_data['labels']
    amounts = weekly_data['amounts']
    if not labels:
        return _make_empty_chart(tr(I18N.StatsPDF.CHART_WEEKLY), tr(I18N.StatsPDF.EMPTY_NO_WEEKLY))

    fig, ax = plt.subplots(figsize=(4.5, 2.5))
    x = np.arange(len(labels))
    bars = ax.bar(x, amounts, color=COLORS_HEX['secondary'],
                  alpha=0.8, width=0.6, edgecolor='white')
    if amounts:
        best = np.argmax(amounts)
        worst = np.argmin(amounts)
        bars[best].set_color(COLORS_HEX['primary'])
        bars[worst].set_color(COLORS_HEX['warning'])
        for bar, val in zip(bars, amounts):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(amounts)*0.02,
                        f'{val/1000:.0f}K', ha='center', va='bottom', fontsize=7, fontweight='bold')
        avg = np.mean(amounts)
        ax.axhline(avg, color=COLORS_HEX['danger'], linestyle='--', linewidth=1.2, alpha=0.6)
        avg_label = f'{tr(I18N.StatsPDF.LEGEND_AVG)}: {_fmt_currency_short(avg, currency_code)}'
        ax.text(len(x)-0.5, avg + max(amounts)*0.02, avg_label,
                fontsize=7, color=COLORS_HEX['danger'], ha='right')
    ax.set_title(f'{tr(I18N.StatsPDF.CHART_WEEKLY)} ({tr(I18N.StatsPDF.LEGEND_AVG)}. {len(labels)})', pad=8, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8, rotation=45, ha='right')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: _fmt_currency_short(v, currency_code)))
    fig.tight_layout()
    return _chart_to_image(fig)


def _make_chart_daily(daily_data, currency_code="PYG"):
    """Cotizado diario"""
    labels = daily_data['labels']
    amounts = daily_data['amounts']
    if not labels:
        return _make_empty_chart(tr(I18N.StatsPDF.CHART_DAILY), tr(I18N.StatsPDF.EMPTY_NO_DAILY))

    fig, ax = plt.subplots(figsize=(4.5, 2.5))
    x = np.arange(len(labels))
    clrs = [COLORS_HEX['primary'] if v > 0 else COLORS_HEX['grid'] for v in amounts]
    ax.bar(x, amounts, color=clrs, alpha=0.8, width=0.65, edgecolor='white')
    for i, val in enumerate(amounts):
        if val == 0:
            ax.text(i, max(amounts)*0.02 if amounts else 1, '—', ha='center', va='bottom',
                    fontsize=8, color=COLORS_HEX['neutral'])
    active = [v for v in amounts if v > 0]
    if active:
        avg = np.mean(active)
        ax.axhline(avg, color=COLORS_HEX['accent'], linestyle='--', linewidth=1.2, alpha=0.6)
        avg_label = f'{tr(I18N.StatsPDF.LEGEND_AVG)}: {_fmt_currency_short(avg, currency_code)}'
        ax.text(len(x)-0.5, avg + max(amounts)*0.02, avg_label,
                fontsize=7, color=COLORS_HEX['accent'], ha='right')
    ax.set_title(f'{tr(I18N.StatsPDF.CHART_DAILY)} ({tr(I18N.StatsPDF.LEGEND_AVG)}. {len(labels)} días)', pad=8, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, p: _fmt_currency_short(v, currency_code)))
    fig.tight_layout()
    return _chart_to_image(fig)


def _make_empty_chart(title, message):
    """Genera un gráfico vacío con un mensaje"""
    fig, ax = plt.subplots(figsize=(4.5, 2.5))
    ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=12,
            color=COLORS_HEX['neutral'], transform=ax.transAxes)
    ax.set_title(title, pad=8, fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    return _chart_to_image(fig)


# ══════════════════════════════════════════════════════════
# COMPOSICIÓN DEL PDF
# ══════════════════════════════════════════════════════════

class StatsPDFManager:
    """
    Genera el reporte PDF de estadísticas de presupuestos.
    
    Recibe datos estructurados del QuoteStatsService y produce un PDF A4
    de 3 páginas con gráficos y tablas.
    """

    def __init__(self):
        _setup_matplotlib_style()

    def generate(self, output_path: str, data: dict) -> str:
        """
        Genera el reporte PDF completo.
        
        Args:
            output_path: Ruta absoluta donde guardar el PDF
            data: Dict con estadísticas del QuoteStatsService.get_stats_for_range()
            
        Returns:
            Ruta del archivo PDF generado
        """
        try:
            return self._build_pdf(output_path, data)
        except Exception as e:
            logger.log_exception("StatsPDFManager", e, "generate")
            raise

    def _build_pdf(self, output_path: str, data: dict) -> str:
        """Construye el PDF completo (lógica interna)."""
        c = canvas.Canvas(output_path, pagesize=A4)
        page_num = [0]  # Mutable para closures
        currency_code = data.get("currency_code", "PYG")

        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        period_label = self._format_period_label(start_date, end_date)
        monthly = data.get('monthly', {'months': [], 'amounts': [], 'counts': []})

        # ═══════════ PÁGINA 1 ═══════════
        y = self._draw_header(c, tr(I18N.StatsPDF.REPORT_TITLE), data, currency_code)
        y = self._draw_kpi_cards(c, y, data, period_label, currency_code)
        y -= 2 * mm

        # Nota legal
        c.setFillColor(colors.HexColor('#666666'))
        c.setFont("Helvetica-Oblique", 7)
        c.drawString(MARGIN, y, tr(I18N.StatsPDF.NOTE_LEGAL))
        y -= 6 * mm

        # Gráfico: Montos mensuales
        y = self._draw_section_title(c, y, tr(I18N.StatsPDF.SECTION_ACTIVITY))
        y -= 2 * mm
        chart_h = 58 * mm
        img_monthly = _make_chart_monthly_bars(monthly, currency_code)
        y = self._draw_chart(c, img_monthly, MARGIN, y, CONTENT_W, chart_h)
        y -= 3 * mm

        # Gráfico: Evolución + tendencia
        img_trend = _make_chart_trend(monthly, currency_code)
        y = self._draw_chart(c, img_trend, MARGIN, y, CONTENT_W, chart_h)
        y -= 3 * mm

        # Gráfico: Productividad
        img_prod = _make_chart_productivity(monthly, currency_code)
        y = self._draw_chart(c, img_prod, MARGIN, y, CONTENT_W, chart_h)

        self._draw_footer(c, page_num)
        c.showPage()

        # ═══════════ PÁGINA 2 ═══════════
        y = self._draw_header(c, tr(I18N.StatsPDF.REPORT_TITLE_DETAILED), data, currency_code)
        y -= 2 * mm

        half_w = CONTENT_W * 0.48
        small_h = 52 * mm

        # Distribución + vacío (el donut de costos se omite porque no hay datos en BD)
        y = self._draw_section_title(c, y, tr(I18N.StatsPDF.CHART_DISTRIBUTION))
        y -= 2 * mm

        img_dist = _make_chart_distribution(data.get('quote_amounts', []), currency_code)
        self._draw_chart(c, img_dist, MARGIN, y, half_w, small_h)

        # Semanal al lado
        img_weekly = _make_chart_weekly(data.get('weekly', {'labels': [], 'amounts': []}), currency_code)
        self._draw_chart(c, img_weekly, MARGIN + CONTENT_W * 0.52, y, half_w, small_h)
        y -= small_h + 5 * mm

        # Diario (ancho completo)
        y = self._draw_section_title(c, y, tr(I18N.StatsPDF.CHART_DAILY))
        y -= 2 * mm
        img_daily = _make_chart_daily(data.get('daily', {'labels': [], 'amounts': []}), currency_code)
        y = self._draw_chart(c, img_daily, MARGIN, y, CONTENT_W, small_h)
        y -= 3 * mm

        # Top Clientes
        y = self._draw_section_title(c, y, tr(I18N.StatsPDF.SECTION_RANKING))
        y -= 2 * mm
        img_customers = _make_chart_top_customers(data.get('top_customers', []), currency_code)
        y = self._draw_chart(c, img_customers, MARGIN, y, CONTENT_W, 52 * mm)
        y -= 2 * mm

        # Top Filamentos
        img_filaments = _make_chart_top_filaments(data.get('top_filaments', []), currency_code)
        y = self._draw_chart(c, img_filaments, MARGIN, y, CONTENT_W, 48 * mm)

        self._draw_footer(c, page_num)
        c.showPage()

        # ═══════════ PÁGINA 3: Tabla numérica ═══════════
        y = self._draw_header(c, tr(I18N.StatsPDF.REPORT_TITLE_NUMERIC), data, currency_code)
        y -= 2 * mm
        y = self._draw_summary_table(c, y, monthly, currency_code)
        y -= 5 * mm

        # Observaciones
        c.setFillColor(RL_TEXT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN, y, tr(I18N.StatsPDF.OBSERVATIONS_TITLE) + ":")
        y -= 4 * mm
        c.setFont("Helvetica", 8)
        bullet = "• "
        notes = [
            bullet + tr(I18N.StatsPDF.NOTE_OBS1),
            bullet + tr(I18N.StatsPDF.NOTE_OBS2),
            bullet + tr(I18N.StatsPDF.NOTE_OBS3),
            bullet + tr(I18N.StatsPDF.NOTE_PERIOD, period_label=period_label),
            bullet + tr(I18N.StatsPDF.NOTE_TOTAL_QUOTES, quote_count=data.get('quote_count', 0)),
        ]
        for note in notes:
            c.drawString(MARGIN + 3 * mm, y, note)
            y -= 4 * mm

        self._draw_footer(c, page_num)
        c.save()

        logger.info("StatsPDFManager", f"PDF de estadísticas generado: {output_path}")
        return output_path

    # ══════════════════════════════════════════════════════════
    # COMPONENTES DEL PDF
    # ══════════════════════════════════════════════════════════

    def _draw_header(self, c, title, data, currency_code="PYG"):
        """Header de cada página"""
        c.setFillColor(RL_PRIMARY)
        c.rect(0, PAGE_H - 18 * mm, PAGE_W, 18 * mm, fill=1, stroke=0)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(MARGIN, PAGE_H - 12 * mm, title)

        c.setFont("Helvetica", 8)
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - 8 * mm,
                          tr(I18N.StatsPDF.LABEL_EXPRESSED_IN, currency=currency_code))
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - 12 * mm,
                          f"VoxePrint — {data.get('generated_at', datetime.now().strftime('%d/%m/%Y %H:%M'))}")

        c.setStrokeColor(RL_GRID)
        c.setLineWidth(0.5)
        c.line(MARGIN, PAGE_H - 20 * mm, PAGE_W - MARGIN, PAGE_H - 20 * mm)

        return PAGE_H - 24 * mm

    def _draw_footer(self, c, page_num):
        """Pie de página"""
        page_num[0] += 1
        c.setStrokeColor(RL_GRID)
        c.setLineWidth(0.5)
        c.line(MARGIN, 12 * mm, PAGE_W - MARGIN, 12 * mm)
        c.setFillColor(colors.HexColor('#808080'))
        c.setFont("Helvetica", 7)
        c.drawString(MARGIN, 8 * mm, tr(I18N.StatsPDF.FOOTER))
        c.drawRightString(PAGE_W - MARGIN, 8 * mm, f"{tr(I18N.StatsPDF.LABEL_PAGE)} {page_num[0]}")

    def _draw_kpi_cards(self, c, y, data, period_label, currency_code="PYG"):
        """Dibuja las tarjetas KPI"""
        total_amount = data.get('total_amount', 0)
        quote_count = data.get('quote_count', 0)
        avg_ticket = data.get('avg_ticket', 0)
        growth = data.get('growth_percent', 0)

        c.setFillColor(RL_TEXT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y, f"{tr(I18N.StatsPDF.SUMMARY_TITLE)}  —  {period_label}")
        y -= 5 * mm

        growth_text = f'+{growth:.1f}%' if growth > 0 else f'{growth:.1f}%'
        kpi_data = [
            [tr(I18N.StatsPDF.KPI_TOTAL), tr(I18N.StatsPDF.KPI_QUOTES),
             tr(I18N.StatsPDF.KPI_AVG_TICKET), tr(I18N.StatsPDF.KPI_GROWTH)],
            [_fmt_currency_full(total_amount, currency_code), str(quote_count),
             _fmt_currency_full(avg_ticket, currency_code), growth_text],
            [tr(I18N.StatsPDF.KPI_TOTAL_DESC), tr(I18N.StatsPDF.KPI_QUOTES_DESC),
             tr(I18N.StatsPDF.KPI_AVG_TICKET_DESC), tr(I18N.StatsPDF.KPI_GROWTH_DESC)],
        ]

        col_w = CONTENT_W / 4
        t = Table(kpi_data, colWidths=[col_w] * 4, rowHeights=[6 * mm, 8 * mm, 5 * mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), RL_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('TEXTCOLOR', (0, 1), (-1, 1), RL_TEXT),
            ('TEXTCOLOR', (3, 1), (3, 1), RL_SECONDARY if growth > 0 else RL_DANGER),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica'),
            ('FONTSIZE', (0, 2), (-1, 2), 6.5),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#808080')),
            ('BOX', (0, 0), (-1, -1), 0.5, RL_GRID),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, RL_GRID),
            ('BACKGROUND', (0, 1), (-1, 2), colors.white),
        ]))
        t.wrapOn(c, CONTENT_W, 100)
        t.drawOn(c, MARGIN, y - 19 * mm)

        return y - 24 * mm

    def _draw_chart(self, c, chart_img, x, y, width, height):
        """Dibuja un gráfico (imagen) en el PDF"""
        c.drawImage(chart_img, x, y - height, width=width, height=height,
                    preserveAspectRatio=True, mask='auto')
        return y - height - 3 * mm

    def _draw_section_title(self, c, y, title):
        """Título de sección"""
        c.setFillColor(RL_PRIMARY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, title)
        c.setStrokeColor(RL_PRIMARY)
        c.setLineWidth(0.8)
        c.line(MARGIN, y - 1.5 * mm, MARGIN + CONTENT_W, y - 1.5 * mm)
        return y - 5 * mm

    def _draw_summary_table(self, c, y, monthly, currency_code="PYG"):
        """Tabla resumen numérica"""
        y = self._draw_section_title(c, y, tr(I18N.StatsPDF.SECTION_DETAIL))
        y -= 2 * mm

        months = monthly.get('months', [])
        amounts = monthly.get('amounts', [])
        counts = monthly.get('counts', [])

        header = [tr(I18N.StatsPDF.TABLE_HEADER_MONTH),
                  tr(I18N.StatsPDF.TABLE_HEADER_QUOTES),
                  tr(I18N.StatsPDF.TABLE_HEADER_AMOUNT),
                  tr(I18N.StatsPDF.TABLE_HEADER_AVG_TICKET)]
        rows = [header]
        for i, month in enumerate(months):
            q_count = counts[i] if i < len(counts) else 0
            q_amount = amounts[i] if i < len(amounts) else 0
            ticket = q_amount / q_count if q_count > 0 else 0
            rows.append([month, str(q_count),
                         _fmt_currency_full(q_amount, currency_code),
                         _fmt_currency_full(ticket, currency_code)])

        total_q = sum(counts)
        total_a = sum(amounts)
        rows.append([tr(I18N.StatsPDF.KPI_TOTAL), str(total_q),
                      _fmt_currency_full(total_a, currency_code),
                      _fmt_currency_full(total_a / total_q if total_q > 0 else 0, currency_code)])

        col_widths = [CONTENT_W * 0.22, CONTENT_W * 0.2, CONTENT_W * 0.3, CONTENT_W * 0.28]
        row_h = 5 * mm
        t = Table(rows, colWidths=col_widths, rowHeights=[row_h] * len(rows))
        style_cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), RL_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F4FD')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 0.5, RL_GRID),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, RL_GRID),
        ]
        # Rayas alternas
        for i in range(2, len(rows) - 1, 2):
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F8F9FA')))
        t.setStyle(TableStyle(style_cmds))
        table_h = row_h * len(rows)
        t.wrapOn(c, CONTENT_W, table_h + 10)
        t.drawOn(c, MARGIN, y - table_h)
        return y - table_h - 5 * mm

    def _format_period_label(self, start_date: str, end_date: str) -> str:
        """Formatea el label del período para mostrar en el PDF"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            return f"{start.strftime('%d/%m/%Y')} — {end.strftime('%d/%m/%Y')}"
        except (ValueError, TypeError):
            return f"{start_date} — {end_date}"
