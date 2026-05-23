from __future__ import annotations

from datetime import datetime, timedelta

from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QRect

from core.managers.quote_config_manager import QuoteConfigManager
from core.managers.locale_manager import LocaleManager
from core.utils.currency_helper import CurrencyHelper
from core.utils.translation_helper import tr
from core.utils.translation_keys import I18N
from config.app_config import BusinessParameters
from core.utils.logger import VoxeprintLogger
from application.dtos.quote_breakdown_dto import QuoteBreakdownResult
from application.services.quote_breakdown_service import QuoteBreakdownService

logger = VoxeprintLogger()


class QuoteNoteManager:
    """Manager encargado de construir y renderizar la Nota de Precios (QPixmap)."""

    NOTE_WIDTH = 590
    PAD = 24

    LOGO_H = 120
    TITLE_H = 30
    COMPANY_H = 22
    META_ROWS = 3
    INFO_PAD = 10

    TABLE_HDR_H = 28
    ROW_H = 26
    TAX_H = 22
    TOTAL_H = 32
    ADV_H = 22
    OBS_H = 72
    FOOTER_H = 28

    NOTE_HEIGHT = 634
    _DPR = 2

    def __init__(self):
        self.config = QuoteConfigManager()

    # ─────────────────────────────────────────────────────────────

    def generate(self, data: dict) -> QPixmap:
        note_cfg = self.config.get_note_settings()
        company = self.config.get_company_info()
        cost_labels = self.config.get_cost_labels()

        primary_hex = (note_cfg.get("primary_color") or "").strip() or \
                      self.config.get_colors().get("primary", "#0070C0")

        # Construir siempre el breakdown con la lógica específica de la nota,
        # que respeta display_mode, postprocessing_mode y failure_margin_mode.
        # (El breakdown pre-construido del PDF usa otra lógica y se ignora aquí.)
        breakdown = QuoteBreakdownService(self.config).compute_from_calculation(
            data, note_cfg, cost_labels
        )

        def fmt(v):
            return CurrencyHelper.format_with_current_currency(float(v or 0))

        rows = [(line.label, fmt(line.amount)) for line in breakdown.lines]

        # ── Datos empresa ─────────────────────────────────────────
        company_fields = []
        if company.get("phone"):
            company_fields.append((tr(I18N.QuoteNote.LABEL_PHONE), company["phone"]))
        if company.get("email"):
            company_fields.append((tr(I18N.QuoteNote.LABEL_EMAIL), company["email"]))
        if not company_fields:
            company_fields.append((tr(I18N.QuoteNote.LABEL_CONTACT), "—"))

        # ── Meta ─────────────────────────────────────────────────
        locale = LocaleManager()
        date_fmt = locale.get_date_format_strftime()
        now = datetime.now()
        meta_fields = [
            (tr(I18N.QuoteNote.META_NOTE_NUMBER), now.strftime("%d%m%y%H%M")),
            (tr(I18N.QuoteNote.META_ISSUE_DATE), now.strftime(date_fmt)),
            (tr(I18N.QuoteNote.META_VALID_UNTIL), (now + timedelta(days=30)).strftime(date_fmt)),
        ]

        # ── Anticipo ─────────────────────────────────────────────
        adv = data.get("advance_info") or {}
        advance_enabled = adv.get("enabled", False)
        advance_pct = float(adv.get("percentage", 0))
        
        # Obtener total del breakdown si está disponible
        if breakdown and isinstance(breakdown, QuoteBreakdownResult):
            total_val = breakdown.total_amount
        else:
            total_val = float(data.get("total_to_pay", 0) or 0)

        advance_amt = (total_val * advance_pct / 100) if advance_enabled else 0
        remaining_amt = total_val - advance_amt

        show_advance = advance_enabled and advance_amt > 0

        # ── Canvas ───────────────────────────────────────────────
        W = self.NOTE_WIDTH
        H = self.NOTE_HEIGHT
        DPR = self._DPR

        px = QPixmap(W * DPR, H * DPR)
        px.fill(QColor("#FFFFFF"))

        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.scale(DPR, DPR)

        primary = QColor(primary_hex)
        secondary = self._derive_secondary_color(primary)

        black = QColor("#1A1A1A")
        muted = QColor("#555555")
        alt_row = QColor("#F7F7F7")
        border = QColor("#CCCCCC")
        white = QColor("#FFFFFF")

        col_right_w = 160
        col_left_w = (W - self.PAD * 2) - col_right_w

        def r(x, y, w, h):
            return QRect(int(x), int(y), int(w), int(h))

        y = 0

        # ── Logo ────────────────────────────────────────────────
        try:
            logo_path = self.config.get_logo_path()
            if logo_path:
                logo = QPixmap(logo_path)
                if not logo.isNull():
                    scaled = logo.scaled(
                        W - self.PAD * 4,
                        self.LOGO_H - self.PAD,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    p.drawPixmap((W - scaled.width()) // 2,
                                 (self.LOGO_H - scaled.height()) // 2,
                                 scaled)
        except Exception as e:
            logger.error("QuoteNoteManager", str(e))

        y += self.LOGO_H

        # ── Título ──────────────────────────────────────────────
        p.setFont(QFont("Segoe UI", 18, QFont.Bold))
        p.setPen(black)
        p.drawText(r(self.PAD, y, W - self.PAD * 2, self.TITLE_H),
                   Qt.AlignCenter,
                   note_cfg.get("title", "Nota de Precios"))

        y += self.TITLE_H

        # ── Info empresa + meta ─────────────────────────────────
        f_lbl = QFont("Segoe UI", 9, QFont.Bold)
        f_val = QFont("Segoe UI", 9)

        left_x = self.PAD
        right_x = W - 168

        cy = y
        for lbl, val in company_fields:
            p.setFont(f_lbl)
            p.drawText(r(left_x, cy, 70, self.COMPANY_H), Qt.AlignLeft, lbl)
            p.setFont(f_val)
            p.drawText(r(left_x + 70, cy, 200, self.COMPANY_H), Qt.AlignLeft, val)
            cy += self.COMPANY_H

        my = y
        for lbl, val in meta_fields:
            p.setFont(f_lbl)
            p.drawText(r(right_x, my, 80, self.COMPANY_H), Qt.AlignLeft, lbl)
            p.setFont(f_val)
            p.drawText(r(right_x + 80, my, 120, self.COMPANY_H), Qt.AlignLeft, val)
            my += self.COMPANY_H

        y += max(len(company_fields), self.META_ROWS) * self.COMPANY_H + self.INFO_PAD

        # ── Tabla header ────────────────────────────────────────
        table_x = self.PAD
        table_w = W - self.PAD * 2

        p.fillRect(r(table_x, y, table_w, self.TABLE_HDR_H), primary)
        p.setPen(white)
        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.drawText(r(table_x + 8, y, col_left_w, self.TABLE_HDR_H),
                   Qt.AlignLeft, tr(I18N.QuoteNote.TABLE_COL_CONCEPT))
        p.drawText(r(table_x + col_left_w, y, col_right_w - 8, self.TABLE_HDR_H),
                   Qt.AlignRight, tr(I18N.QuoteNote.TABLE_COL_AMOUNT))

        y += self.TABLE_HDR_H

        # ── Filas ───────────────────────────────────────────────
        for i, (label, value) in enumerate(rows):
            bg = alt_row if i % 2 == 0 else white
            p.fillRect(r(table_x, y, table_w, self.ROW_H), bg)

            p.setFont(QFont("Segoe UI", 9))
            p.setPen(black)
            p.drawText(r(table_x + 8, y, col_left_w, self.ROW_H),
                       Qt.AlignLeft, label)

            p.setPen(muted)
            p.drawText(r(table_x + col_left_w, y, col_right_w - 8, self.ROW_H),
                       Qt.AlignRight, value)

            p.setPen(QPen(border, 0.5))
            p.drawLine(table_x, y + self.ROW_H - 1,
                       table_x + table_w, y + self.ROW_H - 1)

            y += self.ROW_H

        # ── IVA ─────────────────────────────────────────────────
        # Obtener tax del breakdown si está disponible
        if breakdown and isinstance(breakdown, QuoteBreakdownResult):
            tax_val = breakdown.tax_amount
        else:
            tax_val = float(data.get("tax_amount", 0) or 0)
        if tax_val and note_cfg.get("show_tax", True):
            iva_rate = self.config.get_iva_rate()
            tax_name = locale.get_tax_name()
            p.setFont(QFont("Segoe UI", 8))
            p.setPen(muted)
            p.drawText(r(table_x, y, table_w, self.TAX_H),
                       Qt.AlignRight,
                       tr(I18N.QuoteNote.TAX_LINE_FMT,
                          tax_name=tax_name,
                          rate=int(iva_rate),
                          amount=CurrencyHelper.format_with_current_currency(tax_val)))
            y += self.TAX_H

        # ── TOTAL ───────────────────────────────────────────────
        p.fillRect(r(table_x, y, table_w, self.TOTAL_H), secondary)
        p.setPen(QPen(primary, 1.5))
        p.drawLine(table_x, y, table_x + table_w, y)

        p.setFont(QFont("Segoe UI", 11, QFont.Bold))
        p.setPen(black)
        p.drawText(r(table_x + 8, y, col_left_w, self.TOTAL_H),
                   Qt.AlignLeft, tr(I18N.QuoteNote.LABEL_TOTAL))

        p.setFont(QFont("Segoe UI", 13, QFont.Bold))
        p.drawText(r(table_x + col_left_w, y, col_right_w - 8, self.TOTAL_H),
                   Qt.AlignRight,
                   CurrencyHelper.format_with_current_currency(total_val))

        y += self.TOTAL_H

        # ── Anticipo ────────────────────────────────────────────
        if show_advance:
            rows_adv = [
                (tr(I18N.QuoteNote.LABEL_ADVANCE_PCT_FMT, pct=int(advance_pct)), advance_amt),
                (tr(I18N.QuoteNote.LABEL_REMAINING), remaining_amt),
            ]
            for i, (lbl, val) in enumerate(rows_adv):
                bg = alt_row if i % 2 == 0 else white
                p.fillRect(r(table_x, y, table_w, self.ADV_H), bg)

                p.setPen(muted)
                p.drawText(r(table_x + 8, y, col_left_w, self.ADV_H),
                           Qt.AlignLeft, lbl)

                p.setPen(black)
                p.drawText(r(table_x + col_left_w, y, col_right_w - 8, self.ADV_H),
                           Qt.AlignRight,
                           CurrencyHelper.format_with_current_currency(val))

                y += self.ADV_H

        # ── Footer ──────────────────────────────────────────────
        y_footer = H - self.FOOTER_H

        # ── Observaciones ───────────────────────────────────────
        obs_text = (note_cfg.get("obs_text") or "").strip()
        if obs_text:
            obs_y = y_footer - self.OBS_H
            # Título
            p.setFont(QFont("Segoe UI", 8, QFont.Bold))
            p.setPen(muted)
            p.drawText(
                r(self.PAD, obs_y, W - self.PAD * 2, 16),
                Qt.AlignLeft,
                tr(I18N.QuoteNote.LABEL_OBS),
            )
            # Cuerpo
            p.setFont(QFont("Segoe UI", 7.5))
            p.drawText(
                r(self.PAD, obs_y + 16, W - self.PAD * 2, self.OBS_H - 16),
                Qt.AlignLeft | Qt.TextWordWrap,
                obs_text,
            )

        bp = BusinessParameters()

        footer_text = tr(I18N.QuoteNote.FOOTER_GENERATED_WITH)
        if bp.company_email:
            footer_text += f"  |  {bp.company_email}"

        p.fillRect(r(0, y_footer, W, self.FOOTER_H), QColor("#F0F0F0"))
        p.setPen(QPen(QColor("#CCCCCC"), 0.8))
        p.drawLine(0, y_footer, W, y_footer)

        p.setFont(QFont("Segoe UI", 8))
        p.setPen(black)

        p.drawText(r(0, y_footer, W, self.FOOTER_H),
                   Qt.AlignCenter,
                   footer_text)

        p.end()
        px.setDevicePixelRatio(DPR)

        return px

    # ─────────────────────────────────────────────────────────────

    def _build_rows(self, data, note_cfg, cost_labels):
        rows = []

        def fmt(v):
            return CurrencyHelper.format_with_current_currency(float(v or 0))

        rows.append((cost_labels.get("material"), fmt(data.get("material_cost"))))
        rows.append((cost_labels.get("electricity"), fmt(data.get("electricity_cost"))))
        rows.append((cost_labels.get("wear"), fmt(data.get("operation_cost"))))

        if data.get("failure_margin_cost"):
            rows.append((cost_labels.get("failure"), fmt(data.get("failure_margin_cost"))))

        rows.append((cost_labels.get("commission"), fmt(data.get("commission_cost"))))

        if data.get("post_amount"):
            rows.append((cost_labels.get("post_processing"), fmt(data.get("post_amount"))))

        return rows

    @staticmethod
    def _derive_secondary_color(primary: QColor) -> QColor:
        t = 0.10
        return QColor(
            int(primary.red() * t + 255 * (1 - t)),
            int(primary.green() * t + 255 * (1 - t)),
            int(primary.blue() * t + 255 * (1 - t)),
        )