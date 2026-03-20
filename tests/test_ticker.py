"""Tests for the Kraken v2 WebSocket 'ticker' channel/feature."""

import pytest
from utils.ws_helpers import connect, subscribe, get_subscription_result, get_snapshot

# Feature-level mark — run all ticker tests with: pytest -m ticker
pytestmark = pytest.mark.ticker

SYMBOL = "BTC/USD"


def test_ticker_subscription_succeeds():
    """
    TC-TICKER-01: SUCCESSFUL TICKER CHANNEL SUBSCRIPTION
    Given a valid symbol BTC/USD
    When I subscribe to the ticker channel
    Then the server should acknowledge the subscription as successful
    And the confirmed channel should be 'ticker'
    """
    ws = connect()
    try:
        subscribe(ws, "ticker", symbol=[SYMBOL])
        result = get_subscription_result(ws)
        assert result.get("success") is True, f"Subscription failed: {result.get('error')}"
        assert result.get("result", {}).get("channel") == "ticker"
    finally:
        ws.close()


def test_ticker_snapshot_fields(ticker_snapshot):
    """
    TC-TICKER-02: TICKER SNAPSHOT SCHEMA VALIDATION
    Given I am subscribed to the ticker channel for BTC/USD
    When I receive the snapshot message
    Then it should contain all required fields with positive numeric values
    """
    data = ticker_snapshot["data"][0]

    for field in ("symbol", "bid", "bid_qty", "ask", "ask_qty", "last", "volume", "vwap", "low", "high", "change", "change_pct"):
        assert field in data, f"Missing required field '{field}' in ticker snapshot"

    assert data["symbol"] == SYMBOL

    for field in ("bid", "ask", "last", "volume", "vwap"):
        assert isinstance(data[field], (int, float)), f"'{field}' must be numeric"
        assert data[field] > 0, f"'{field}' must be positive, got {data[field]}"


def test_ticker_bid_less_than_ask(ticker_snapshot):
    """
    TC-TICKER-03: BID IS LESS THAN ASK
    Given I am subscribed to the ticker channel for BTC/USD
    When I receive the ticker snapshot
    Then the current bid price should be strictly less than the current ask price
    """
    data = ticker_snapshot["data"][0]
    assert data["bid"] < data["ask"], (
        f"Bid {data['bid']} is not less than ask {data['ask']}"
    )


@pytest.mark.negative
def test_ticker_invalid_symbol_format_returns_error():
    """
    TC-TICKER-04: INVALID SYMBOL FORMAT RETURNS ERROR [NEGATIVE TEST]
    Given a symbol with no separator 'BTCUSD' (missing the slash)
    When I subscribe to the ticker channel
    Then the server should reject the subscription with success: false
    And the response should contain an error message
    """
    ws = connect()
    try:
        subscribe(ws, "ticker", symbol=["BTCUSD"])
        result = get_subscription_result(ws)
        assert result.get("success") is False, (
            f"[NEGATIVE TEST] Expected success=False for malformed symbol 'BTCUSD' "
            f"but got success={result.get('success')}. Server should reject symbols missing the slash separator."
        )
        assert "error" in result, (
            "[NEGATIVE TEST] Expected an 'error' field in the rejection response "
            "but none was found."
        )
    finally:
        ws.close()
