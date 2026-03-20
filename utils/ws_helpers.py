"""Minimal WebSocket helper utilities for Kraken v2 public API tests.

Provides a thin layer over websocket-client for connecting, subscribing,
and collecting messages. All logic lives here so test files stay focused
on assertions.
"""

import json
import certifi
import websocket

WS_URL = "wss://ws.kraken.com/v2"
DEFAULT_TIMEOUT = 15  # seconds; raise if the API is under heavy load

# Use the certifi CA bundle so connections work on all platforms including
# fresh macOS Python.org installs that lack a system cert store.
_SSL_OPT = {"ca_certs": certifi.where()}


def connect() -> websocket.WebSocket:
    """Open a connection to the Kraken v2 endpoint and discard the initial status message."""
    ws = websocket.create_connection(WS_URL, timeout=DEFAULT_TIMEOUT, sslopt=_SSL_OPT)
    ws.recv()  # discard {"channel": "status", "type": "update", ...}
    return ws


def subscribe(ws: websocket.WebSocket, channel: str, **params) -> None:
    """Send a subscribe request for *channel* with optional keyword parameters."""
    payload = {"method": "subscribe", "params": {"channel": channel, **params}}
    ws.send(json.dumps(payload))


def _recv(ws: websocket.WebSocket) -> dict:
    """Receive and JSON-decode one message."""
    return json.loads(ws.recv())


def collect_until(ws: websocket.WebSocket, predicate, max_messages: int = 30) -> list:
    """Read messages until *predicate(msg)* returns True or *max_messages* is reached.

    Returns the full list of messages collected, including the satisfying one.
    Raises AssertionError if no message satisfies the predicate within the limit.
    """
    collected = []
    for _ in range(max_messages):
        msg = _recv(ws)
        collected.append(msg)
        if predicate(msg):
            return collected
    raise AssertionError(
        f"Predicate not satisfied within {max_messages} messages. "
        f"Last message: {collected[-1] if collected else '<none>'}"
    )


def get_subscription_result(ws: websocket.WebSocket) -> dict:
    """Return the server's subscribe method response (success or error)."""
    msgs = collect_until(ws, lambda m: m.get("method") == "subscribe")
    for m in msgs:
        if m.get("method") == "subscribe":
            return m
    raise AssertionError("No subscribe method response found")


def get_snapshot(ws: websocket.WebSocket, channel: str) -> dict:
    """Return the first snapshot message for *channel*."""
    msgs = collect_until(
        ws,
        lambda m: m.get("channel") == channel and m.get("type") == "snapshot",
    )
    for m in msgs:
        if m.get("channel") == channel and m.get("type") == "snapshot":
            return m
    raise AssertionError(f"No snapshot received for channel '{channel}'")


def get_first_channel_message(ws: websocket.WebSocket, channel: str) -> dict:
    """Return the first message for *channel* regardless of message type.

    Used for channels (e.g. 'trade') that do not send a distinct snapshot type
    but instead immediately stream update messages.
    """
    msgs = collect_until(ws, lambda m: m.get("channel") == channel)
    for m in msgs:
        if m.get("channel") == channel:
            return m
    raise AssertionError(f"No message received for channel '{channel}'")
