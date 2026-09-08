# Tradingbot

Python trading bot for executing TradingView webhook signals on Bybit.

## Features

* Long / short execution
* Static stops
* Percentage trailing stops
* ATR trailing stops
* Partial take profits
* Intrabar or candle-close exits
* Automatic quantity-step handling
* Duplicate signal protection
* Position synchronization
* Persistent state
* Restart recovery

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/Tradingbot.git
cd Tradingbot

python -m venv .venv
pip install -r requirements.txt
```

Create a `.env` file:

```env
BYBIT_API_KEY_DEMO=your_api_key
BYBIT_API_SECRET_DEMO=your_api_secret
USE_DEMO=True
WEBHOOK_SECRET=your_webhook_secret
```

Run:

```bash
python app.py
```

## Webhook

TradingView alerts should send JSON to:

```text
/webhook
```

Example payload:

```json
{
  "payload_version": 1,
  "secret": "your_webhook_secret",
  "strategy": "Strategy Name",
  "symbol": "BYBIT:BTCUSDT.P",
  "direction": "LONG",
  "entry_price": 76000,
  "stoploss": 75000,
  "stoploss_intra_closed": true,
  "positionsize": 0.01,
  "first_target_ONOFF": true,
  "first_target": 77000,
  "first_target_close_perc": 50,
  "first_target_intra_closed": true,
  "exit_options": "Percentage",
  "stop_static_trail": true,
  "trail_distance": 0.5,
  "trail_intra_closed": true,
  "current_atr": 150,
  "timeframe": "1",
  "bar_time": 1788353628310,
  "signal_id": "BYBIT:BTCUSDT.P_LONG_1788353628310"
}
```

## Exit Modes

### Percentage

```text
LONG  = highest_price × (1 - trail_distance / 100)
SHORT = lowest_price  × (1 + trail_distance / 100)
```

### ATR

`trail_distance` is used as the ATR length.

```text
LONG  = highest_price - ATR
SHORT = lowest_price + ATR
```

ATR uses RMA smoothing.

Trailing stops only move in the profitable direction.

## State

Runtime state is stored in:

```text
state/bot_state.json
```

The bot restores open trade state after a restart and resynchronizes with the exchange position.

## Tests

```bash
python test_price.py
python test_order.py
python test_webhook.py
```

## Deployment

For 24/7 use, run the bot on a VPS and manage the process with something like `systemd`.

## Security

Do not commit:

```text
.env
.venv/
state/
API keys
webhook secrets
```
