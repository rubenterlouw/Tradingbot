import requests
import time


WEBHOOK_URL = "http://127.0.0.1:5000/webhook"


# =========================================================
# TEST SETTINGS
# =========================================================

symbol = "BYBIT:BTCUSDT.P"

direction = "LONG"

entry_price = 76762.0

stoploss = 75000.0

position_size = 0.001


# ---------------------------------------------------------
# FIRST TARGET
# ---------------------------------------------------------

first_target_enabled = True

first_target = 77000.0

first_target_close_perc = 50


# ---------------------------------------------------------
# PERCENTAGE TRAIL
# ---------------------------------------------------------

exit_options = "Percentage"

stop_static_trail = True

# 0.10 = 0.10%
trail_distance = 0.50


# ---------------------------------------------------------
# TRIGGER MODES
# ---------------------------------------------------------

# True = live/intrabar
# False = candle close

stoploss_intra_closed = True

first_target_intra_closed = True

trail_intra_closed = True


# ---------------------------------------------------------
# ATR
# ---------------------------------------------------------

# Not used by Percentage mode,
# but included because your payload now supports it.

current_atr = 100.0


# ---------------------------------------------------------
# TIMEFRAME
# ---------------------------------------------------------

timeframe = "1"


# =========================================================
# UNIQUE SIGNAL ID
# =========================================================

current_time_ms = int(
    time.time() * 1000
)

signal_id = (
    f"{symbol}_"
    f"{direction}_"
    f"{current_time_ms}"
)


# =========================================================
# PAYLOAD
# =========================================================

payload = {

    "payload_version": 1,

    "secret": "mySuperSecretPassword",

    "strategy": "PTS FSW 3.0",

    "symbol": symbol,

    "direction": direction,

    "entry_price": entry_price,

    "stoploss": stoploss,

    "stoploss_intra_closed":
        stoploss_intra_closed,

    "positionsize": position_size,

    "first_target_ONOFF":
        first_target_enabled,

    "first_target": first_target,

    "first_target_close_perc":
        first_target_close_perc,

    "first_target_intra_closed":
        first_target_intra_closed,

    "exit_options":
        exit_options,

    "stop_static_trail":
        stop_static_trail,

    "trail_distance":
        trail_distance,

    "trail_intra_closed":
        trail_intra_closed,

    "current_atr":
        current_atr,

    "timeframe":
        timeframe,

    "bar_time":
        current_time_ms,

    "signal_id":
        signal_id
}


# =========================================================
# SEND TEST
# =========================================================

print(
    "\n===== SENDING TEST WEBHOOK ====="
)

print(
    f"Signal ID: {signal_id}"
)

print(
    f"Direction: {direction}"
)

print(
    f"Symbol: {symbol}"
)

print(
    f"Position size: {position_size}"
)

print(
    f"Exit method: {exit_options}"
)

print(
    f"Trailing: {stop_static_trail}"
)

print(
    f"Trail distance: {trail_distance}%"
)


try:

    response = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=10
    )


    print(
        "\n===== WEBHOOK RESPONSE ====="
    )

    print(
        f"Status code: "
        f"{response.status_code}"
    )


    try:

        print(
            response.json()
        )

    except Exception:

        print(
            response.text
        )


except requests.exceptions.ConnectionError:

    print(
        "\n===== CONNECTION FAILED ====="
    )

    print(
        "Make sure app.py is running first."
    )


except Exception as error:

    print(
        "\n===== TEST ERROR ====="
    )

    print(
        repr(error)
    )