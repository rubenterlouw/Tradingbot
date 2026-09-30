from bybit.client import session

from bybit.instruments import (
    normalize_quantity
)


# =========================================================
# MARKET ORDER
# =========================================================

def place_market_order(
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
                "Invalid quantity "
                "for instrument"
            )
        }


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