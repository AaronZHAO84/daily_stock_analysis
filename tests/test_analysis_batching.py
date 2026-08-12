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
