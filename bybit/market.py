from bybit.client import session


# =========================================================
# LAST PRICE
# =========================================================

def get_last_price(symbol):

    try:

        response = session.get_tickers(
            category="linear",
            symbol=symbol
        )

    except Exception as error:

        print(
            "\n===== PRICE REQUEST ERROR ====="
        )

        print(
            repr(error)
        )

        return None


    if response["retCode"] != 0:

        print(
            "\n===== PRICE REQUEST FAILED ====="
        )

        print(
            response
        )

        return None


    tickers = response[
        "result"
    ][
        "list"
    ]


    if not tickers:
        return None


    return float(
        tickers[0][
            "lastPrice"
        ]
    )


# =========================================================
# GET CANDLES
# =========================================================

def get_recent_klines(
    symbol,
    interval,
    limit=50
):

    try:

        response = session.get_kline(
            category="linear",
            symbol=symbol,
            interval=str(interval),
            limit=limit
        )

    except Exception as error:

        print(
            "\n===== KLINE REQUEST ERROR ====="
        )

        print(
            repr(error)
        )

        return None


    if response["retCode"] != 0:

        print(
            "\n===== KLINE REQUEST FAILED ====="
        )

        print(
            response
        )

        return None


    raw_klines = response[
        "result"
    ][
        "list"
    ]


    candles = []


    for candle in raw_klines:

        candles.append(
            {
                "start_time": int(
                    candle[0]
                ),

                "open": float(
                    candle[1]
                ),

                "high": float(
                    candle[2]
                ),

                "low": float(
                    candle[3]
                ),

                "close": float(
                    candle[4]
                ),

                "volume": float(
                    candle[5]
                )
            }
        )


    # Bybit gives newest -> oldest.
    # Change to oldest -> newest.

    candles.sort(
        key=lambda candle:
        candle["start_time"]
    )


    return candles


# =========================================================
# LATEST CLOSED CANDLE
# =========================================================

def get_latest_closed_candle(
    symbol,
    interval
):

    candles = get_recent_klines(
        symbol=symbol,
        interval=interval,
        limit=3
    )


    if candles is None:
        return None


    if len(candles) < 2:
        return None


    # Last candle = current/open candle.
    # Candle before it = latest completed candle.

    return candles[-2]