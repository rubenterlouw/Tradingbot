from flask import Flask, request, jsonify
import threading

from config import WEBHOOK_SECRET

from models.trade import Trade

from engine.trade_manager import TradeManager
from engine.monitor import TradeMonitor

from bybit.helpers import normalize_symbol


app = Flask(__name__)


# =========================================================
# GLOBAL MANAGER / MONITOR
# =========================================================

trade_manager = TradeManager()

monitor = TradeMonitor(
    trade_manager
)


# =========================================================
# WEBHOOK
# =========================================================

@app.route(
    "/webhook",
    methods=["POST"]
)
def webhook():

    try:

        # -------------------------------------------------
        # READ JSON
        # -------------------------------------------------

        data = request.get_json(
            silent=True
        )


        if data is None:

            return jsonify(
                {
                    "status": "error",
                    "message": "Invalid JSON"
                }
            ), 400


        print(
            "\n===== ALERT RECEIVED ====="
        )

        print(
            data
        )


        # -------------------------------------------------
        # CHECK SECRET
        # -------------------------------------------------

        if data.get(
            "secret"
        ) != WEBHOOK_SECRET:

            print(
                "\n===== INVALID SECRET ====="
            )

            return jsonify(
                {
                    "status": "error",
                    "message": "Invalid secret"
                }
            ), 403


        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        required_fields = [
            "symbol",
            "direction",
            "entry_price",
            "stoploss",
            "positionsize",
            "first_target_ONOFF",
            "first_target",
            "first_target_close_perc",
            "exit_options",
            "stop_static_trail",
            "trail_distance",
            "timeframe",
            "bar_time",
            "signal_id"
        ]


        missing_fields = []


        for field in required_fields:

            if field not in data:

                missing_fields.append(
                    field
                )


        if missing_fields:

            print(
                "\n===== MISSING FIELDS ====="
            )

            print(
                missing_fields
            )


            return jsonify(
                {
                    "status": "error",
                    "message": "Missing fields",
                    "fields": missing_fields
                }
            ), 400


        # -------------------------------------------------
        # SIGNAL ID
        # -------------------------------------------------

        signal_id = str(
            data["signal_id"]
        )


        # -------------------------------------------------
        # DUPLICATE PROTECTION
        # -------------------------------------------------

        if trade_manager.is_duplicate_signal(
            signal_id
        ):

            print(
                "\n===== DUPLICATE WEBHOOK IGNORED ====="
            )

            print(
                signal_id
            )


            return jsonify(
                {
                    "status": "duplicate_ignored",
                    "signal_id": signal_id
                }
            ), 200


        # -------------------------------------------------
        # NORMALIZE SYMBOL
        # -------------------------------------------------

        bybit_symbol = normalize_symbol(
            data["symbol"]
        )


        # -------------------------------------------------
        # CURRENT ATR
        # -------------------------------------------------

        current_atr = data.get(
            "current_atr"
        )


        if current_atr is not None:

            current_atr = float(
                current_atr
            )


        # -------------------------------------------------
        # FIRST TARGET
        # -------------------------------------------------

        first_target = data.get(
            "first_target"
        )


        if first_target is not None:

            first_target = float(
                first_target
            )


        # -------------------------------------------------
        # CREATE TRADE OBJECT
        # -------------------------------------------------

        trade = Trade(

            symbol=bybit_symbol,

            direction=str(
                data["direction"]
            ).upper(),

            entry_price=float(
                data["entry_price"]
            ),

            stop_loss=float(
                data["stoploss"]
            ),

            position_size=float(
                data["positionsize"]
            ),

            first_target_enabled=bool(
                data["first_target_ONOFF"]
            ),

            first_target=first_target,

            first_target_close_perc=float(
                data["first_target_close_perc"]
            ),

            exit_option=str(
                data["exit_options"]
            ),

            stop_static_trail=data[
                "stop_static_trail"
            ],

            trail_distance=float(
                data["trail_distance"]
            ),

            current_atr=current_atr,

            timeframe=str(
                data["timeframe"]
            ),

            signal_id=signal_id,

            bar_time=int(
                data["bar_time"]
            ),

            stoploss_intra_closed=bool(
                data.get(
                    "stoploss_intra_closed",
                    True
                )
            ),

            first_target_intra_closed=bool(
                data.get(
                    "first_target_intra_closed",
                    True
                )
            ),

            trail_intra_closed=bool(
                data.get(
                    "trail_intra_closed",
                    True
                )
            )
        )


        # -------------------------------------------------
        # START TRADE
        # -------------------------------------------------

        success = (
            trade_manager.start_trade(
                trade
            )
        )


        if not success:

            print(
                "\n===== TRADE NOT OPENED ====="
            )


            return jsonify(
                {
                    "status": "error",
                    "message": "Trade was not opened",
                    "signal_id": signal_id
                }
            ), 400


        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        print(
            "\n===== WEBHOOK COMPLETE ====="
        )


        return jsonify(
            {
                "status": "success",
                "symbol": bybit_symbol,
                "direction": trade.direction,
                "signal_id": signal_id
            }
        ), 200


    # =========================================================
    # WEBHOOK ERROR
    # =========================================================

    except Exception as error:

        print(
            "\n===== WEBHOOK ERROR ====="
        )

        print(
            repr(error)
        )


        return jsonify(
            {
                "status": "error",
                "message": str(error)
            }
        ), 500


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    monitor_thread = threading.Thread(
        target=monitor.start,
        daemon=True
    )

    monitor_thread.start()


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )