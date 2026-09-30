from bybit.client import session


def get_position_size(
    symbol,
    direction
):

    """
    Get the actual open position size
    from Bybit.

    Returns None if the API request fails.

    Returns 0.0 if the request succeeds
    but no matching position exists.
    """

    symbol = (
        symbol
        .replace("BYBIT:", "")
        .replace(".P", "")
    )


    try:

        response = session.get_positions(
            category="linear",
            symbol=symbol
        )


    except Exception as error:

        print(
            "\n===== POSITION REQUEST ERROR ====="
        )

        print(
            repr(error)
        )

        return None


    if response["retCode"] != 0:

        print(
            "\n===== GET POSITION FAILED ====="
        )

        print(
            response
        )

        return None


    positions = response[
        "result"
    ][
        "list"
    ]


    for position in positions:

        position_size = float(
            position["size"]
        )


        if position_size <= 0:
            continue


        position_side = (
            position["side"]
        )


        if (
            direction == "LONG"
            and
            position_side == "Buy"
        ):

            return position_size


        if (
            direction == "SHORT"
            and
            position_side == "Sell"
        ):

            return position_size


    return 0.0