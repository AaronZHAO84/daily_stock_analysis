"""Planning helpers for market-isolated LLM analysis batches."""

from collections import OrderedDict
from typing import Dict, Iterable, List, Tuple


def _market_for_code(code: str) -> str:
    value = str(code or "").strip()
    lowered = value.lower()
    if lowered.startswith(("hk", "sh.hk", "sz.hk")) or value.endswith(".HK"):
        return "hk"
    if value.isdigit() and len(value) in (5, 6):
        return "cn"
    return "us"


def group_stock_codes(stock_codes: Iterable[str]) -> Dict[str, List[str]]:
    """Group symbols into CN, HK, and US buckets without changing input order."""
    grouped: "OrderedDict[str, List[str]]" = OrderedDict(
        (market, []) for market in ("cn", "hk", "us")
    )
    seen = set()
    for code in stock_codes:
        value = str(code or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        grouped[_market_for_code(value)].append(value)
    return {market: codes for market, codes in grouped.items() if codes}


def split_market_batches(
    stock_codes: Iterable[str], batch_size: int = 3
) -> List[Tuple[str, List[str]]]:
    """Split symbols into same-market batches, preserving market and symbol order."""
    size = max(1, int(batch_size))
    batches: List[Tuple[str, List[str]]] = []
    for market, codes in group_stock_codes(stock_codes).items():
        for start in range(0, len(codes), size):
            batches.append((market, codes[start : start + size]))
    return batches
