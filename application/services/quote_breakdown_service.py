from typing import Dict, Any, Optional
from core.managers.quote_config_manager import QuoteConfigManager
from application.dtos.quote_breakdown_dto import QuoteBreakdownResult, QuoteBreakdownLine


class QuoteBreakdownService:
    """Calculates the cost breakdown lines, tax, and total for quotes.

    Single source of truth: both compute_from_amounts() and
    compute_from_calculation() normalise their inputs and delegate to the
    private _build_lines() core, so display-mode / combination logic lives
    in exactly one place.
    """

    def __init__(self, config: Optional[QuoteConfigManager] = None):
        self.config = config or QuoteConfigManager()

    # ── Public entry-points ──────────────────────────────────────────────────────

    def compute_from_amounts(self, amounts: Dict[str, float],
                              config_overrides: Optional[Dict[str, Any]] = None) -> QuoteBreakdownResult:
        """Build a breakdown from a raw amounts dict.

        ``amounts`` keys: material, electricity, wear, failure, commission,
        post_processing, tax, total.

        ``config_overrides`` may contain any of:
          include_error_margin (bool), include_post_processing (bool),
          include_iva / show_tax (bool), iva_rate (float), cost_labels (dict),
          display_mode (str), postprocessing_mode (str),
          failure_margin_mode (str), summary_label (str).
        """
        overrides = config_overrides or {}

        include_error_margin = overrides.get("include_error_margin",
                                             self.config.get_include_error_margin())
        include_post_processing = overrides.get("include_post_processing",
                                                self.config.get_include_post_processing())
        include_iva = overrides.get("include_iva",
                                    overrides.get("show_tax",
                                                  self.config.get_include_iva()))
        iva_rate = overrides.get("iva_rate", self.config.get_iva_rate())
        cost_labels = overrides.get("cost_labels", self.config.get_cost_labels())

        # String modes take precedence; bool flags provide the fallback default.
        display_mode = overrides.get("display_mode", "detailed")
        failure_margin_mode = overrides.get(
            "failure_margin_mode",
            "in_operation" if include_error_margin else "separate",
        )
        postprocessing_mode = overrides.get(
            "postprocessing_mode",
            "in_commission" if include_post_processing else "separate",
        )
        summary_label = overrides.get("summary_label", "Servicio de Impresión 3D")

        return self._build_lines(
            material=float(amounts.get("material", 0)),
            electricity=float(amounts.get("electricity", 0)),
            wear=float(amounts.get("wear", 0)),
            failure=float(amounts.get("failure", 0)),
            commission=float(amounts.get("commission", 0)),
            post=float(amounts.get("post_processing", 0)),
            tax=float(amounts.get("tax", 0)),
            total=float(amounts.get("total", 0)),
            display_mode=display_mode,
            postprocessing_mode=postprocessing_mode,
            failure_margin_mode=failure_margin_mode,
            summary_label=summary_label,
            include_iva=include_iva,
            iva_rate=iva_rate,
            cost_labels=cost_labels,
        )

    def compute_from_calculation(self, calc_result: Dict[str, Any],
                                  note_cfg: Optional[Dict[str, Any]] = None,
                                  cost_labels: Optional[Dict[str, str]] = None) -> QuoteBreakdownResult:
        """Build a breakdown from a calculation result dict (Note caller path).

        ``calc_result`` keys: material_cost, electricity_cost, operation_cost,
        failure_margin_cost, commission_cost, post_amount, tax_amount,
        total_to_pay.
        """
        if note_cfg is None:
            note_cfg = self.config.get_note_settings()
        if cost_labels is None:
            cost_labels = self.config.get_cost_labels()

        amounts = {
            "material":        float(calc_result.get("material_cost", 0) or 0),
            "electricity":     float(calc_result.get("electricity_cost", 0) or 0),
            "wear":            float(calc_result.get("operation_cost", 0) or 0),
            "failure":         float(calc_result.get("failure_margin_cost", 0) or 0),
            "commission":      float(calc_result.get("commission_cost", 0) or 0),
            "post_processing": float(calc_result.get("post_amount", 0) or 0),
            "tax":             float(calc_result.get("tax_amount", 0) or 0),
            "total":           float(calc_result.get("total_to_pay", 0) or 0),
        }
        overrides = {
            "display_mode":        note_cfg.get("display_mode", "detailed"),
            "postprocessing_mode": note_cfg.get("postprocessing_mode", "separate"),
            "failure_margin_mode": note_cfg.get("failure_margin_mode", "separate"),
            "summary_label":       note_cfg.get("summary_label", "Servicio de Impresión 3D"),
            "show_tax":            note_cfg.get("show_tax", True),
            "iva_rate":            self.config.get_iva_rate(),
            "cost_labels":         cost_labels,
        }
        return self.compute_from_amounts(amounts, overrides)

    # ── Private core ─────────────────────────────────────────────────────────────

    def _build_lines(
        self,
        *,
        material: float,
        electricity: float,
        wear: float,
        failure: float,
        commission: float,
        post: float,
        tax: float,
        total: float,
        display_mode: str = "detailed",
        postprocessing_mode: str = "separate",
        failure_margin_mode: str = "separate",
        summary_label: str = "Servicio de Impresión 3D",
        include_iva: bool = True,
        iva_rate: float = 10.0,
        cost_labels: Optional[Dict[str, str]] = None,
    ) -> QuoteBreakdownResult:
        """Core builder: all display-mode and combination logic lives here."""
        if cost_labels is None:
            cost_labels = {}

        lines: list[QuoteBreakdownLine] = []

        if display_mode == "summary":
            # En resumen el margen/comisión se oculta dentro del precio del servicio.
            # Solo el post-procesado queda aparte cuando es un servicio externo separado.
            effective_commission = commission
            if postprocessing_mode == "in_commission":
                effective_commission += post
            summary_total = material + electricity + wear + failure + effective_commission
            lines.append(QuoteBreakdownLine(label=summary_label, amount=summary_total))

            if postprocessing_mode == "separate" and post:
                lines.append(QuoteBreakdownLine(
                    label=cost_labels.get("post_processing", "Post-Procesado"),
                    amount=post))

        else:
            effective_wear = wear
            if failure_margin_mode == "in_operation":
                effective_wear += failure

            lines.append(QuoteBreakdownLine(
                label=cost_labels.get("material", "Costo de Material"),
                amount=material))
            lines.append(QuoteBreakdownLine(
                label=cost_labels.get("electricity", "Costo de Energía"),
                amount=electricity))
            lines.append(QuoteBreakdownLine(
                label=cost_labels.get("wear", "Costo de Operación"),
                amount=effective_wear))

            if failure_margin_mode == "separate" and failure:
                lines.append(QuoteBreakdownLine(
                    label=cost_labels.get("failure", "Margen de Error"),
                    amount=failure))

            effective_commission = commission
            if postprocessing_mode == "in_commission":
                effective_commission += post
            if effective_commission:
                lines.append(QuoteBreakdownLine(
                    label=cost_labels.get("commission", "Comisión"),
                    amount=effective_commission))
            if postprocessing_mode == "separate" and post:
                lines.append(QuoteBreakdownLine(
                    label=cost_labels.get("post_processing", "Post-Procesado"),
                    amount=post))

        tax_label = ""
        if include_iva and tax:
            rate_str = f"{int(iva_rate)}" if iva_rate == int(iva_rate) else f"{iva_rate}"
            tax_label = f"IVA ({rate_str}%)"

        return QuoteBreakdownResult(
            lines=lines,
            tax_label=tax_label,
            tax_amount=tax,
            total_label="TOTAL A PAGAR",
            total_amount=total,
        )