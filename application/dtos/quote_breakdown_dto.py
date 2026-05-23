from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class QuoteBreakdownLine:
    label: str
    amount: float


@dataclass
class QuoteBreakdownResult:
    lines: List[QuoteBreakdownLine] = field(default_factory=list)
    tax_label: str = ""
    tax_amount: float = 0.0
    total_label: str = ""
    total_amount: float = 0.0