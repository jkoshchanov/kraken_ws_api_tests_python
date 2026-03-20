"""Tests for the Kraken v2 WebSocket 'ohlc' channel/feature."""
# OHLC stands for Open, High, Low, Close 
# It's a standard way to summarize price activity over a time interval (called a "candle").

import pytest
from utils.ws_helpers import connect, subscribe, get_subscription_result, get_snapshot

# Feature-level mark — run all ohlc tests with: pytest -m ohlc
pytestmark = pytest.mark.ohlc

SYMBOL = "BTC/USD"
INTERVAL = 1  # minute(s)


def test_TC_OHLC_01_subscription_succeeds():
    """
    TC-OHLC-01: SUCCESSFUL OHLC CHANNEL SUBSCRIPTION
    Given a valid symbol BTC/USD and interval of 1 minute
    When I subscribe to the ohlc channel
    Then the server should acknowledge the subscription as successful
    And the confirmed channel should be 'ohlc'
    """
    ws = connect()
    try:
        subscribe(ws, "ohlc", symbol=[SYMBOL], interval=INTERVAL)
        result = get_subscription_result(ws)
        assert result.get("success") is True, f"Subscription failed: {result.get('error')}"
        assert result.get("result", {}).get("channel") == "ohlc"
    finally:
        ws.close()


def test_TC_OHLC_02_snapshot_fields(ohlc_snapshot):
    """
    TC-OHLC-02: OHLC SNAPSHOT SCHEMA VALIDATION
    Given I am subscribed to the ohlc channel for BTC/USD
    When I receive the snapshot message
    Then it should contain all required OHLC fields
    """
    data = ohlc_snapshot["data"][0]

    for field in ("symbol", "open", "high", "low", "close", "vwap",
                  "volume", "trades", "interval_begin", "interval", "timestamp"):
        assert field in data, f"Missing required field '{field}' in OHLC snapshot"

    assert data["symbol"] == SYMBOL


def test_TC_OHLC_03_candle_invariants(ohlc_snapshot):
    """
    TC-OHLC-03: OHLC CANDLE INVARIANTS
    Given I am subscribed to the ohlc channel for BTC/USD
    When I receive the ohlc snapshot
    Then high should be greater than or equal to low
    And open and close should both fall within the high/low range
    And volume and trade count should be non-negative
    """
    d = ohlc_snapshot["data"][0]
    high, low = d["high"], d["low"]

    assert high >= low, f"OHLC high {high} < low {low}"
    assert low <= d["open"] <= high, (
        f"Open {d['open']} is outside the candle range [low={low}, high={high}]"
    )
    assert low <= d["close"] <= high, (
        f"Close {d['close']} is outside the candle range [low={low}, high={high}]"
    )
    assert d["volume"] >= 0, f"Volume must be non-negative, got {d['volume']}"
    assert d["trades"] >= 0, f"Trade count must be non-negative, got {d['trades']}"


@pytest.mark.negative
def test_TC_OHLC_04_invalid_interval_returns_error():
    """
    TC-OHLC-04: INVALID INTERVAL VALUE RETURNS ERROR [NEGATIVE TEST]
    Given an unsupported interval value of 999
    When I subscribe to the ohlc channel
    Then the server should reject the subscription with success: false
    And the response should contain an error message
    """
    ws = connect()
    try:
        subscribe(ws, "ohlc", symbol=[SYMBOL], interval=999)
        result = get_subscription_result(ws)
        assert result.get("success") is False, (
            f"[NEGATIVE TEST] Expected success=False for invalid interval=999 "
            f"but got success={result.get('success')}. Server should reject unsupported interval values."
        )
        assert "error" in result, (
            "[NEGATIVE TEST] Expected an 'error' field in the rejection response "
            "but none was found."
        )
    finally:
        ws.close()
