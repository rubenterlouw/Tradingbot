import json
import os
from dataclasses import asdict

from models.trade import Trade


STATE_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "state"
)

STATE_FILE = os.path.join(
    STATE_FOLDER,
    "bot_state.json"
)


def ensure_state_folder():

    os.makedirs(
        STATE_FOLDER,
        exist_ok=True
    )


def trade_to_dict(trade):

    if trade is None:
        return None

    return asdict(trade)


def trade_from_dict(data):

    if data is None:
        return None

    trade = Trade(
        symbol=data["symbol"],
        direction=data["direction"],

        entry_price=data["entry_price"],
        stop_loss=data["stop_loss"],
        position_size=data["position_size"],

        first_target_enabled=data[
            "first_target_enabled"
        ],

        first_target=data[
            "first_target"
        ],

        first_target_close_perc=data[
            "first_target_close_perc"
        ],

        exit_option=data[
            "exit_option"
        ],

        stop_static_trail=data[
            "stop_static_trail"
        ],

        trail_distance=data[
            "trail_distance"
        ],

        current_atr=data.get(
            "current_atr"
        ),

        timeframe=data[
            "timeframe"
        ],

        signal_id=data[
            "signal_id"
        ],

        bar_time=data[
            "bar_time"
        ],

        stoploss_intra_closed=data.get(
            "stoploss_intra_closed",
            True
        ),

        first_target_intra_closed=data.get(
            "first_target_intra_closed",
            True
        ),

        trail_intra_closed=data.get(
            "trail_intra_closed",
            True
        )
    )

    # -------------------------------------------------
    # RESTORE DYNAMIC STATE
    # -------------------------------------------------

    trade.current_stop = data.get(
        "current_stop",
        trade.stop_loss
    )

    trade.highest_price = data.get(
        "highest_price",
        trade.entry_price
    )

    trade.lowest_price = data.get(
        "lowest_price",
        trade.entry_price
    )

    trade.remaining_position = data.get(
        "remaining_position",
        trade.position_size
    )

    trade.first_target_hit = data.get(
        "first_target_hit",
        False
    )

    trade.status = data.get(
        "status",
        "OPEN"
    )

    trade.atr_value = data.get(
        "atr_value",
        trade.current_atr
    )

    trade.last_atr_bar_time = data.get(
        "last_atr_bar_time"
    )

    trade.last_stop_bar_time = data.get(
        "last_stop_bar_time"
    )

    trade.last_target_bar_time = data.get(
        "last_target_bar_time"
    )

    return trade


def save_state(
    active_trade,
    processed_signal_ids
):

    ensure_state_folder()

    state = {
        "active_trade": trade_to_dict(
            active_trade
        ),

        "processed_signal_ids": list(
            processed_signal_ids
        )
    }


    temporary_file = (
        STATE_FILE +
        ".tmp"
    )


    with open(
        temporary_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            state,
            file,
            indent=4
        )


    # Atomic-ish replacement.
    os.replace(
        temporary_file,
        STATE_FILE
    )


def load_state():

    ensure_state_folder()

    if not os.path.exists(
        STATE_FILE
    ):

        return {
            "active_trade": None,
            "processed_signal_ids": []
        }


    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            state = json.load(
                file
            )


        return {
            "active_trade":
                trade_from_dict(
                    state.get(
                        "active_trade"
                    )
                ),

            "processed_signal_ids":
                state.get(
                    "processed_signal_ids",
                    []
                )
        }


    except Exception as error:

        print(
            "\n===== STATE LOAD ERROR ====="
        )

        print(
            repr(error)
        )


        return {
            "active_trade": None,
            "processed_signal_ids": []
        }