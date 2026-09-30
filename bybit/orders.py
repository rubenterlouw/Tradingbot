from bybit.client import session

from bybit.instruments import (
    normalize_quantity
)


# =========================================================
# PTS SETTINGS
# =========================================================

PTS_LEVERAGE = 10


# =========================================================
# SET LEVERAGE
# =========================================================

def set_symbol_leverage(
    symbol,
    leverage=PTS_LEVERAGE
):

    leverage_string = str(
        leverage
    )


    try:

        response = session.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=leverage_string,
            sellLeverage=leverage_string
        )


        print(
            "\n===== LEVERAGE RESPONSE ====="
        )

        print(
            response
        )


        if response["retCode"] == 0:

            print(
                f"Leverage set to "
                f"{leverage}x "
                f"for {symbol}"
            )

            return True


        return False


    except Exception as error:

        error_text = str(
            error
        )


        # Bybit can return an error when the requested
        # leverage is already set. That should not stop
        # us from opening the trade.
        if (
            "leverage not modified"
            in error_text.lower()
        ):

            print(
                f"\n===== LEVERAGE ALREADY "
                f"{leverage}X ====="
            )

            return True


        print(
            "\n===== SET LEVERAGE ERROR ====="
        )

        print(
            repr(error)
        )

        return False


# =========================================================
# MARKET ORDER
# =========================================================

def place_market_order(
    symbol,
    side,
    qty
):

    # -----------------------------------------------------
    # FORCE PTS LEVERAGE BEFORE OPENING POSITION
    # -----------------------------------------------------

    leverage_ready = (
        set_symbol_leverage(
            symbol=symbol,
            leverage=PTS_LEVERAGE
        )
    )


    if not leverage_ready:

        return {
            "success": False,
            "error": (
                "Could not set leverage "
                f"for {symbol}"
            )
        }


    # -----------------------------------------------------
    # NORMALIZE QUANTITY
    # -----------------------------------------------------

    normalized_qty = (
        normalize_quantity(
            symbol,
            qty
        )
    )


    if normalized_qty is None:

        return {
            "success": False,
            "error": (
                "Invalid quantity "
                "for instrument"
            )
        }


    # -----------------------------------------------------
    # PLACE ORDER
    # -----------------------------------------------------

    try:

        response = session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=normalized_qty
        )

    except Exception as error:

        print(
            "\n===== MARKET ORDER ERROR ====="
        )

        print(
            repr(error)
        )

        return {
            "success": False,
            "error": str(error)
        }


    print(
        "\n===== OPEN ORDER RESPONSE ====="
    )

    print(
        response
    )


    if response["retCode"] == 0:

        return {
            "success": True,
            "order_id": response[
                "result"
            ][
                "orderId"
            ]
        }


    return {
        "success": False,
        "error": response
    }


# =========================================================
# PARTIAL CLOSE
# =========================================================

def close_partial_position(
    symbol,
    side,
    qty
):

    normalized_qty = (
        normalize_quantity(
            symbol,
            qty
        )
    )


    if normalized_qty is None:

        return {
            "success": False,
            "error": (
                "Invalid partial "
                "close quantity"
            )
        }


    try:

        response = session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=normalized_qty,
            reduceOnly=True
        )

    except Exception as error:

        print(
            "\n===== PARTIAL CLOSE ERROR ====="
        )

        print(
            repr(error)
        )

        return {
            "success": False,
            "error": str(error)
        }


    print(
        "\n===== PARTIAL CLOSE RESPONSE ====="
    )

    print(
        response
    )


    if response["retCode"] == 0:

        return {
            "success": True,
            "order_id": response[
                "result"
            ][
                "orderId"
            ]
        }


    return {
        "success": False,
        "error": response
    }


# =========================================================
# FULL CLOSE
# =========================================================

def close_position(
    symbol,
    side,
    qty
):

    normalized_qty = (
        normalize_quantity(
            symbol,
            qty
        )
    )


    if normalized_qty is None:

        return {
            "success": False,
            "error": (
                "Invalid full "
                "close quantity"
            )
        }


    try:

        response = session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=normalized_qty,
            reduceOnly=True
        )

    except Exception as error:

        print(
            "\n===== FULL CLOSE ERROR ====="
        )

        print(
            repr(error)
        )

        return {
            "success": False,
            "error": str(error)
        }


    print(
        "\n===== FULL CLOSE RESPONSE ====="
    )

    print(
        response
    )


    if response["retCode"] == 0:

        return {
            "success": True,
            "order_id": response[
                "result"
            ][
                "orderId"
            ]
        }


    return {
        "success": False,
        "error": response
    }