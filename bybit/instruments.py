from decimal import Decimal, ROUND_DOWN

from bybit.client import session


# =========================================================
# GET QUANTITY RULES FOR SYMBOL
# =========================================================

def get_quantity_rules(symbol):

    try:

        response = session.get_instruments_info(
            category="linear",
            symbol=symbol
        )

    except Exception as error:

        print(
            "\n===== INSTRUMENT INFO ERROR ====="
        )

        print(
            repr(error)
        )

        return None


    if response["retCode"] != 0:

        print(
            "\n===== INSTRUMENT INFO FAILED ====="
        )

        print(
            response
        )

        return None


    instruments = response[
        "result"
    ][
        "list"
    ]


    if not instruments:

        print(
            f"\n===== SYMBOL NOT FOUND: "
            f"{symbol} ====="
        )

        return None


    instrument = instruments[0]

    lot_size = instrument[
        "lotSizeFilter"
    ]


    return {

        "qty_step": lot_size[
            "qtyStep"
        ],

        "min_qty": lot_size[
            "minOrderQty"
        ],

        "max_market_qty": lot_size.get(
            "maxMktOrderQty"
        )
    }


# =========================================================
# NORMALIZE QUANTITY
# =========================================================

def normalize_quantity(
    symbol,
    qty
):

    rules = get_quantity_rules(
        symbol
    )


    if rules is None:
        return None


    qty_decimal = Decimal(
        str(qty)
    )

    step = Decimal(
        str(
            rules["qty_step"]
        )
    )

    min_qty = Decimal(
        str(
            rules["min_qty"]
        )
    )


    if step <= 0:

        print(
            "\n===== INVALID QTY STEP ====="
        )

        return None


    # -----------------------------------------------------
    # ROUND DOWN TO VALID STEP
    # -----------------------------------------------------

    steps = (
        qty_decimal /
        step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )


    normalized_qty = (
        steps *
        step
    )


    # -----------------------------------------------------
    # CHECK MINIMUM SIZE
    # -----------------------------------------------------

    if normalized_qty < min_qty:

        print(
            "\n===== QUANTITY BELOW MINIMUM ====="
        )

        print(
            f"Symbol: {symbol}"
        )

        print(
            f"Requested: {qty}"
        )

        print(
            f"Normalized: "
            f"{normalized_qty}"
        )

        print(
            f"Minimum: {min_qty}"
        )

        return None


    # -----------------------------------------------------
    # RETURN AS STRING
    # -----------------------------------------------------

    normalized_string = format(
        normalized_qty,
        "f"
    )


    return normalized_string