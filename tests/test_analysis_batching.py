from src.core.analysis_batching import group_stock_codes, split_market_batches


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
