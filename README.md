# kraken_ws_api_tests_python
WebSocket API tests for Kraken public market data feeds

## Overview

This project is a regression test suite written from scratch to validate the Kraken WebSocket v2 public API.
It covers 4 channels — Book, Ticker, OHLC and Trade — using pytest and the websocket-client libary.
No Kraken account is needed as all tested channels are publicly accessible without authentication.

The tests are designed to act as a regression suite, meaning they capture the current expected behavior
of the API so that any future changes or refactoring can be quickly validated.

## What I used

- **Python 3.12** — main language
- **pytest** — test framework
- **websocket-client** — to connect and communicate with the Kraken WS API
- **certifi** — SSL certificate handling (needed on some platforms like macOS)
- **pytest-html** — to generate HTML test reports
- **Docker** — to containerize and run the tests in a clean environment
- **GitHub Actions** — for CI/CD, automatically runs tests on every push to main

## How to run

### With Docker (recommended)

```bash
docker build -t kraken_ws_api_tests_python .
docker run --rm kraken_ws_api_tests_python
```

### To get an HTML report from Docker

```bash
mkdir -p reports
docker run --rm -v $(pwd)/reports:/app/reports kraken_ws_api_tests_python \
  -v --tb=short --html=reports/report.html --self-contained-html
```

### Locally (without Docker)

```bash
pip install -r requirements.txt
pytest -v --tb=short
```

### To generate HTML report localy

```bash
pytest -v --tb=short --html=report.html --self-contained-html
```

Open `report.html` in your browser to view results.

### To run tests by feature (channel)

Each channel has a feature-level mark applied to the entire test file:

```bash
pytest -m book -v           # run all Book channel tests
pytest -m ticker -v         # run all Ticker channel tests
pytest -m ohlc -v           # run all OHLC channel tests
pytest -m trade -v          # run all Trade channel tests
```

### To run negative tests across all channels

```bash
pytest -m negative -v       # run all negative test cases across all channels
```

### To combine marks

```bash
pytest -m "book or ticker" -v          # run book and ticker tests together
pytest -m "book and negative" -v       # run only book's negative test
```

## Project structure

```
.
├── .github/workflows/      # CI/CD pipeline (GitHub Actions)
├── utils/
│   └── ws_helpers.py       # WebSocket connect/subscribe/collect utilities
├── tests/
│   ├── test_book.py        # Book channel tests
│   ├── test_ticker.py      # Ticker channel tests
│   ├── test_ohlc.py        # OHLC channel tests (coming soon)
│   └── test_trade.py       # Trade channel tests (coming soon)
├── conftest.py             # Shared pytest fixtures
├── Dockerfile
├── pytest.ini              # Marks registration
├── requirements.txt
└── README.md
```

## Notes

- Each test opens its own WebSocket connection for full isolation
- BTC/USD was chosen as the test symbol due to its high liquidity and consistent activity
- AI assistance was used for approximately 30% of this project (WebSocket lifecycle,
  pytest fixture structure, Dockerfile, and GitHub Actions YAML syntax)
- All test case design, scenario selection and assertions were written independantly
