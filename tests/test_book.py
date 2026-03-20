"""Tests for the Kraken v2 WebSocket 'book' (order book) channel."""

import pytest
from utils.ws_helpers import connect, subscribe, get_subscription_result, get_snapshot

SYMBOL = "BTC/USD"
DEPTH = 10


@pytest.mark.book_01
def test_book_subscription_succeeds():
    """
    TC-BOOK-01: SUCCESSFUL BOOK CHANNEL SUBSCRIPTION
    Given a valid symbol BTC/USD and depth of 10
    When I subscribe to the book channel
    Then the server should acknowledge the subscription as successful
    And the confirmed channel should be 'book'
    """
    ws = connect()
    try:
        subscribe(ws, "book", symbol=[SYMBOL], depth=DEPTH)
        result = get_subscription_result(ws)
        assert result.get("success") is True, f"Subscription failed: {result.get('error')}"
        assert result.get("result", {}).get("channel") == "book"
    finally:
        ws.close()


@pytest.mark.book_02
def test_book_snapshot_fields(book_snapshot):
    """
    TC-BOOK-02: BOOK SNAPSHOT SCHEMA VALIDATION
    Given I am subscribed to the book channel for BTC/USD
    When I receive the snapshot message
    Then it should contain the fields: symbol, bids, asks, checksum, timestamp
    And each bid and ask entry should have a numeric price and qty
    """
    data = book_snapshot["data"][0]

    for field in ("symbol", "bids", "asks", "checksum", "timestamp"):
        assert field in data, f"Missing required field '{field}' in book snapshot"

    assert data["symbol"] == SYMBOL

    for side in ("bids", "asks"):
        assert len(data[side]) > 0, f"'{side}' list must not be empty"
        for level in data[side]:
            for field in ("price", "qty"):
                assert field in level, f"Missing '{field}' in {side} price level"
            assert isinstance(level["price"], (int, float)), f"{side} price must be numeric"
            assert isinstance(level["qty"], (int, float)), f"{side} qty must be numeric"


@pytest.mark.book_03
def test_book_not_crossed(book_snapshot):
    """
    TC-BOOK-03: ORDER BOOK NOT CROSSED
    Given I am subscribed to the book channel for BTC/USD
    When I receive the order book snapshot
    Then the best bid price should be strictly less than the best ask price
    """
    data = book_snapshot["data"][0]
    best_bid = max(level["price"] for level in data["bids"])
    best_ask = min(level["price"] for level in data["asks"])
    assert best_bid < best_ask, (
        f"Order book is crossed: best_bid={best_bid} >= best_ask={best_ask}"
    )


@pytest.mark.book_04
def test_book_positive_values(book_snapshot):
    """
    TC-BOOK-04: POSITIVE PRICES AND QUANTITIES
    Given I am subscribed to the book channel for BTC/USD
    When I receive the order book snapshot
    Then every price and quantity on both sides should be strictly positive
    """
    data = book_snapshot["data"][0]
    for side in ("bids", "asks"):
        for level in data[side]:
            assert level["price"] > 0, f"Non-positive price in {side}: {level['price']}"
            assert level["qty"] > 0, f"Non-positive qty in {side}: {level['qty']}"


@pytest.mark.book_05
@pytest.mark.negative
def test_book_invalid_symbol_returns_error():
    """
    TC-BOOK-05: INVALID SYMBOL RETURNS ERROR [NEGATIVE TEST]
    Given a non-existent symbol 'BANANA/USD'
    When I subscribe to the book channel
    Then the server should reject the subscription with success: false
    And the response should contain an error message
    And the error message should reference the invalid symbol
    """
    ws = connect()
    try:
        subscribe(ws, "book", symbol=["BANANA/USD"])
        result = get_subscription_result(ws)
        assert result.get("success") is True, ( 
            # this assertion is intentionally checking for success=True to demonstrate the negative test case, 
            # setting line 100 to False boolean will pass the test.
            f"[NEGATIVE TEST] Expected success=False for non-existent symbol 'BANANA/USD' "
            f"but got success={result.get('success')}. Server should reject unsupported symbols."
        )
        assert "error" in result, (
            "[NEGATIVE TEST] Expected an 'error' field in the rejection response "
            "but none was found."
        )
        assert "BANANA/USD" in result.get("error", ""), (
            f"[NEGATIVE TEST] Expected error message to reference 'BANANA/USD' "
            f"but got: '{result.get('error')}'"
        )
    finally:
        ws.close()
