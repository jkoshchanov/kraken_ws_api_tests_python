"""Tests for the Kraken v2 WebSocket 'trade' channel/feature.

Note: the trade channel does not send a distinct snapshot message; it immediately
streams update messages with recent trades after subscription.
"""

import pytest
from utils.ws_helpers import connect, subscribe, get_subscription_result, get_first_channel_message

# Feature-level mark — run all trade tests with: pytest -m trade
pytestmark = pytest.mark.trade

SYMBOL = "BTC/USD"
VALID_SIDES = {"buy", "sell"}


def test_TC_TRADE_01_subscription_succeeds():
    """
    TC-TRADE-01: SUCCESSFUL TRADE CHANNEL SUBSCRIPTION
    Given a valid symbol BTC/USD
    When I subscribe to the trade channel
    Then the server should acknowledge the subscription as successful
    And the confirmed channel should be 'trade'
    """
    ws = connect()
    try:
        subscribe(ws, "trade", symbol=[SYMBOL])
        result = get_subscription_result(ws)
        assert result.get("success") is True, f"Subscription failed: {result.get('error')}"
        assert result.get("result", {}).get("channel") == "trade"
    finally:
        ws.close()


def test_TC_TRADE_02_message_fields(trade_snapshot):
    """
    TC-TRADE-02: TRADE MESSAGE SCHEMA VALIDATION
    Given I am subscribed to the trade channel for BTC/USD
    When I receive the first trade message
    Then it should contain at least one trade
    And each trade should have all required fields
    """
    trades = trade_snapshot["data"]
    assert len(trades) > 0, "Trade message must contain at least one recent trade"

    for i, trade in enumerate(trades):
        for field in ("symbol", "side", "price", "qty", "ord_type", "trade_id", "timestamp"):
            assert field in trade, f"Trade[{i}] missing required field '{field}'"
        assert trade["symbol"] == SYMBOL


def test_TC_TRADE_03_values_valid(trade_snapshot):
    """
    TC-TRADE-03: TRADE VALUES VALIDATION
    Given I am subscribed to the trade channel for BTC/USD
    When I receive the first trade message
    Then every trade side should be 'buy' or 'sell'
    And every price and quantity should be strictly positive
    """
    for i, trade in enumerate(trade_snapshot["data"]):
        assert trade["side"] in VALID_SIDES, (
            f"Trade[{i}] has invalid side '{trade['side']}'; expected one of {VALID_SIDES}"
        )
        assert trade["price"] > 0, f"Trade[{i}] non-positive price: {trade['price']}"
        assert trade["qty"] > 0, f"Trade[{i}] non-positive qty: {trade['qty']}"


@pytest.mark.negative
def test_TC_TRADE_04_wrong_symbol_type_returns_error():
    """
    TC-TRADE-04: WRONG SYMBOL TYPE RETURNS ERROR [NEGATIVE TEST]
    Given a symbol passed as a string instead of a list 'BTC/USD'
    When I subscribe to the trade channel
    Then the server should reject the subscription with success: false
    And the response should contain an error message
    """
    ws = connect()
    try:
        subscribe(ws, "trade", symbol="BTC/USD")
        result = get_subscription_result(ws)
        assert result.get("success") is False, (
            f"[NEGATIVE TEST] Expected success=False when symbol is passed as a string "
            f"but got success={result.get('success')}. Server should reject incorrect symbol type."
        )
        assert "error" in result, (
            "[NEGATIVE TEST] Expected an 'error' field in the rejection response "
            "but none was found."
        )
    finally:
        ws.close()
