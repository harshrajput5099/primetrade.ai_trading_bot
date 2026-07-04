# PrimeTrade.ai Trading Bot
 
A small Python application for placing **MARKET**, **LIMIT**, and **STOP_LIMIT**
(bonus) orders on the **Binance Futures Testnet (USDT-M)**, with structured
code, logging, and exception handling.
 
## Project Structure
 
```
trading_bot/
  bot/
    __init__.py
    client.py          # Binance API wrapper -- the ONLY module that hits the network
    orders.py           # Order-building + placement logic (MARKET/LIMIT/STOP_LIMIT)
    validators.py        # Input validation, custom ValidationError, OrderRequest model
    logging_config.py    # Central logging setup -> logs/app.log
  cli.py                 # Core CLI entry point (argparse)
  cli_rich.py             # Bonus: enhanced CLI UX (Typer + Rich), same core logic
  requirements.txt
  .env.example            # Copy to .env and fill in your own keys
  README.md
  logs/
    app.log             # created on first run
```
 
`cli.py` and `cli_rich.py` both call the exact same `bot/orders.py` and
`bot/validators.py` functions -- the enhanced CLI is a presentation layer,
not a second implementation.
 
## Setup
 
1. **Create a Binance Futures Testnet account and API key**
   Go to https://testnet.binancefuture.com and log in with GitHub (this
   testnet uses GitHub OAuth instead of a separate signup form). Once
   logged in, scroll to the **API Key** panel and generate an
   HMAC_SHA256 key. Copy the secret immediately -- it is shown once.
 
2. **Install Python dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
 
3. **Set your API credentials** -- either option works:
 
   **Option A: `.env` file (recommended)**
   ```bash
   cp .env.example .env
   # then edit .env and paste in your real testnet key + secret
   ```
 
   **Option B: shell environment variables**
   ```bash
   export BINANCE_API_KEY="your_testnet_api_key"
   export BINANCE_API_SECRET="your_testnet_api_secret"
   ```
   (Windows PowerShell: `$env:BINANCE_API_KEY="..."`)
 
   Credentials are read from the environment only -- never hardcoded,
   never logged, never printed.
 
## Running it
 
**Market order**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```
 
**Limit order**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
```
 
**Stop-Limit order (bonus order type)**
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT \
  --quantity 0.01 --price 64000 --stop-price 63900
```
 
Each run prints an order request summary, the raw order response, and a
success/failure message. Every request, response, and error is also
written to `logs/app.log`.
 
**Bonus: enhanced interactive CLI**
```bash
python cli_rich.py                 # fully guided prompts
python cli_rich.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01 --yes   # scriptable
```
 
## Assumptions & Design Notes
 
- **Symbol allow-list**: `validators.py` restricts symbols to a small known
  set (BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT) to catch typos before they
  become API errors, rather than accepting anything and letting Binance
  reject it.
- **Time-in-force**: LIMIT and STOP_LIMIT orders default to `GTC`
  (Good-Til-Cancelled).
- **STOP_LIMIT -> Binance "STOP"**: Binance Futures has no order type
  literally named `STOP_LIMIT`; a stop-limit order is a `STOP` order with
  both `price` and `stopPrice` set. `orders.py` handles this mapping.
- **Conditional orders route through Binance's Algo Service**: effective
  2025-12-09, Binance migrated conditional order types (including `STOP`)
  to a separate Algo Service. python-binance handles the routing
  automatically, but the response shape differs from a regular order
  (`algoId`/`algoStatus`/`triggerPrice` instead of
  `orderId`/`status`/`executedQty`/`avgPrice`), and the order has no fill
  data yet because it is a resting trigger, not an executed trade.
  `summarize_response()` and `cli_rich.py`'s response table detect and
  handle both shapes.
- **Testnet only, by construction**: `client.py` hardcodes the Futures
  Testnet base URL, so this code cannot accidentally place a real order.
- **No hardcoded secrets**: keys are read from the environment or a
  gitignored `.env` file only.
- **Network vs. API error handling**: `client.py` catches both
  `BinanceAPIException`/`BinanceRequestException` (the exchange responded
  with an error) and `requests.exceptions.RequestException` (no response
  at all -- DNS failure, timeout, connection refused), so a dead network
  connection fails with one clean message instead of an unhandled
  traceback.
- **Out of scope**: no authentication, deployment config, or database --
  this is a local CLI tool, per the assignment's scope.
 
## Logging
 
Every run appends to `logs/app.log` with timestamps, level, module name,
and message -- including the exact request sent and response received for
every order, and full tracebacks for unexpected errors. Console output
stays short (INFO and above by default); the file always captures DEBUG
and above, so nothing that happened is ever missing from the file even if
the console looked quiet.
"# primetrade.ai_trading_bot" 
