"""Project-level pytest fixtures shared across all test modules.

Note: AI assistance was used to understand how to structure pytest fixtures
for WebSocket subscriptions — specifically the connect/subscribe/close lifecycle
and how to pass live data into test functions via fixtures. Test case design
and assertions were written independently.
"""

import pytest
from utils.ws_helpers import connect, subscribe, get_snapshot, get_first_channel_message

SYMBOL = "BTC/USD"
BOOK_DEPTH = 10
OHLC_INTERVAL = 1  # minutes


@pytest.fixture
def book_snapshot():
    """First snapshot data entry for the 'book' channel (BTC/USD, depth=10)."""
    ws = connect()
    try:
        subscribe(ws, "book", symbol=[SYMBOL], depth=BOOK_DEPTH)
        return get_snapshot(ws, "book")
    finally:
        ws.close()


@pytest.fixture
def ticker_snapshot():
    """First snapshot data entry for the 'ticker' channel (BTC/USD)."""
    ws = connect()
    try:
        subscribe(ws, "ticker", symbol=[SYMBOL])
        return get_snapshot(ws, "ticker")
    finally:
        ws.close()


@pytest.fixture
def ohlc_snapshot():
    """First snapshot data entry for the 'ohlc' channel (BTC/USD, 1-minute interval)."""
    ws = connect()
    try:
        subscribe(ws, "ohlc", symbol=[SYMBOL], interval=OHLC_INTERVAL)
        return get_snapshot(ws, "ohlc")
    finally:
        ws.close()


@pytest.fixture
def trade_snapshot():
    """First trade channel message for BTC/USD.

    The Kraken v2 trade channel does not send a distinct snapshot type;
    it immediately streams update messages with recent trades.
    """
    ws = connect()
    try:
        subscribe(ws, "trade", symbol=[SYMBOL])
        return get_first_channel_message(ws, "trade")
    finally:
        ws.close()
