from types import SimpleNamespace
from unittest.mock import MagicMock

from src.core.analysis_batching import group_stock_codes, split_market_batches
from src.analyzer import GeminiAnalyzer


def test_group_stock_codes_keeps_markets_separate_and_preserves_order():
    grouped = group_stock_codes(["002001", "hk09992", "MSFT", "688103", "AAPL", "hk02228"])

    assert grouped == {
        "cn": ["002001", "688103"],
        "hk": ["hk09992", "hk02228"],
        "us": ["MSFT", "AAPL"],
    }


def test_split_market_batches_never_mixes_markets():
    batches = split_market_batches(
        ["002001", "688103", "600668", "hk09992", "hk02228", "MSFT"],
        batch_size=2,
    )

    assert batches == [
        ("cn", ["002001", "688103"]),
        ("cn", ["600668"]),
        ("hk", ["hk09992", "hk02228"]),
        ("us", ["MSFT"]),
    ]


def test_split_market_batches_does_not_wait_for_interleaved_market_codes():
    batches = split_market_batches(["002001", "hk09992", "688103"], batch_size=2)

    assert batches == [
        ("cn", ["002001"]),
        ("hk", ["hk09992"]),
        ("cn", ["688103"]),
    ]


def test_batch_json_validator_accepts_a_stocks_envelope():
    analyzer = GeminiAnalyzer.__new__(GeminiAnalyzer)

    analyzer._validate_batch_json_response(
        '{"stocks":[{"code":"002001","sentiment_score":60,'
        '"trend_prediction":"震荡","operation_advice":"持有",'
        '"analysis_summary":"摘要"}]}'
    )


def test_market_batch_uses_streaming_for_provider_compatibility():
    analyzer = GeminiAnalyzer.__new__(GeminiAnalyzer)
    analyzer._get_runtime_config = MagicMock(
        return_value=SimpleNamespace(llm_temperature=0.2, report_language="zh")
    )
    analyzer._call_litellm = MagicMock(
        return_value=(
            '{"stocks":[{"code":"002001","sentiment_score":60,'
            '"trend_prediction":"震荡","operation_advice":"持有",'
            '"analysis_summary":"摘要"}]}',
            "deepseek/test",
            {},
        )
    )
    analyzer._parse_response = MagicMock(return_value=SimpleNamespace())
    analyzer._build_market_snapshot = MagicMock(return_value={})

    analyzer.analyze_market_batch([{"code": "002001", "stock_name": "新和成"}])

    assert analyzer._call_litellm.call_args.kwargs["stream"] is True
