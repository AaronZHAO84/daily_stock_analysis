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
    """Split adjacent same-market symbols without blocking the worker queue.

    Keeping batches contiguous means two early tasks can never wait for a
    same-market partner that is still queued behind another market's task.
    """
    size = max(1, int(batch_size))
    batches: List[Tuple[str, List[str]]] = []
    current_market = None
    current_codes: List[str] = []
    seen = set()

    def flush() -> None:
        if current_codes:
            batches.append((current_market, list(current_codes)))

    for code in stock_codes:
        value = str(code or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        market = _market_for_code(value)
        if current_codes and (market != current_market or len(current_codes) >= size):
            flush()
            current_codes.clear()
        current_market = market
        current_codes.append(value)
    flush()
    return batches
