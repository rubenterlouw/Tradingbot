import time

from threading import Lock

from models.trade import Trade

from bybit.market import (
    get_last_price,
    get_recent_klines,
    get_latest_closed_candle
)

from bybit.orders import (
    place_market_order,
    close_partial_position,
    close_position
)

from bybit.positions import (
    get_position_size
)

from engine.state_store import (
    save_state,
    load_state
)


class TradeManager:

    # =========================================================
    # INITIALIZE
    # =========================================================

    def __init__(self):

        self.active_trade = None
        self.lock = Lock()
        self.processed_signal_ids = set()

        self.restore_state()


    # =========================================================
    # SAVE STATE
    # =========================================================

    def save_current_state(self):

        try:

            save_state(
                self.active_trade,
                self.processed_signal_ids
            )

        except Exception as error:

            print(
                "\n===== STATE SAVE ERROR ====="
            )

            print(
                repr(error)
            )


    # =========================================================
    # RESTORE STATE
    # =========================================================

    def restore_state(self):

        state = load_state()

        self.processed_signal_ids = set(
            state["processed_signal_ids"]
        )

        saved_trade = state["active_trade"]

        if saved_trade is None:

            print(
                "\n===== NO SAVED ACTIVE TRADE ====="
            )

            return


        print(
            "\n===== SAVED TRADE FOUND ====="
        )

        print(
            f"Symbol: {saved_trade.symbol}"
        )

        print(
            f"Direction: {saved_trade.direction}"
        )


        actual_position = get_position_size(
            saved_trade.symbol,
            saved_trade.direction
        )


        if actual_position is None:

            print(
                "\n===== RECOVERY POSITION CHECK FAILED ====="
            )

            print(
                "Keeping saved trade active for safety."
            )

            self.active_trade = saved_trade

            return


        if actual_position > 0:

            saved_trade.remaining_position = (
                actual_position
            )

            saved_trade.status = "OPEN"

            self.active_trade = saved_trade


            print(
                "\n===== TRADE RECOVERED ====="
            )

            print(
                f"Actual position: {actual_position}"
            )

            print(
                f"Current stop: {saved_trade.current_stop}"
            )

            print(
                f"First target hit: "
                f"{saved_trade.first_target_hit}"
            )


            self.save_current_state()

            return


        print(
            "\n===== SAVED TRADE NO LONGER EXISTS ====="
        )

        self.active_trade = None

        self.save_current_state()


    # =========================================================
    # DUPLICATE SIGNAL
    # =========================================================

    def is_duplicate_signal(
        self,
        signal_id
    ):

        return (
            signal_id
            in
            self.processed_signal_ids
        )


    # =========================================================
    # REMEMBER SIGNAL
    # =========================================================

    def remember_signal(
        self,
        signal_id
    ):

        self.processed_signal_ids.add(
            signal_id
        )


        if len(
            self.processed_signal_ids
        ) > 1000:

            self.processed_signal_ids = set(
                list(
                    self.processed_signal_ids
                )[-1000:]
            )


        self.save_current_state()


    # =========================================================
    # START TRADE
    # =========================================================

    def start_trade(
        self,
        trade: Trade
    ):

        with self.lock:

            if self.is_duplicate_signal(
                trade.signal_id
            ):

                print(
                    "\n===== DUPLICATE SIGNAL IGNORED ====="
                )

                print(
                    trade.signal_id
                )

                return False


            if self.active_trade is not None:

                print(
                    "\n===== TRADE ALREADY ACTIVE ====="
                )

                return False


            if trade.direction == "LONG":

                open_side = "Buy"

            elif trade.direction == "SHORT":

                open_side = "Sell"

            else:

                print(
                    "\n===== INVALID DIRECTION ====="
                )

                return False


            self.active_trade = trade


            result = place_market_order(
                symbol=trade.symbol,
                side=open_side,
                qty=trade.position_size
            )


            if not result["success"]:

                print(
                    "\n===== TRADE OPEN FAILED ====="
                )

                print(
                    result["error"]
                )

                self.active_trade = None

                return False


            print(
                "\n===== OPEN ORDER ACCEPTED ====="
            )

            print(
                f"Symbol: {trade.symbol}"
            )

            print(
                f"Direction: {trade.direction}"
            )

            print(
                f"Requested quantity: "
                f"{trade.position_size}"
            )


            # -------------------------------------------------
            # VERIFY POSITION
            # -------------------------------------------------

            actual_position = None


            for attempt in range(10):

                actual_position = (
                    get_position_size(
                        trade.symbol,
                        trade.direction
                    )
                )


                if (
                    actual_position is not None
                    and
                    actual_position > 0
                ):

                    break


                time.sleep(
                    0.25
                )


            if actual_position is None:

                print(
                    "\n===== ENTRY VERIFICATION FAILED ====="
                )

                print(
                    "Order accepted but position "
                    "verification failed."
                )

                print(
                    "Keeping trade active for safety."
                )


                self.remember_signal(
                    trade.signal_id
                )

                self.save_current_state()

                return True


            if actual_position <= 0:

                print(
                    "\n===== ENTRY POSITION NOT FOUND ====="
                )

                self.active_trade = None

                return False


            trade.remaining_position = (
                actual_position
            )


            self.remember_signal(
                trade.signal_id
            )

            self.save_current_state()


            print(
                "\n===== POSITION CONFIRMED ====="
            )

            print(
                f"Actual position: "
                f"{actual_position}"
            )

            print(
                f"Initial stop: "
                f"{trade.current_stop}"
            )

            print(
                f"Exit method: "
                f"{trade.exit_option}"
            )

            print(
                f"Static/trailing: "
                f"{trade.stop_static_trail}"
            )


            return True


    # =========================================================
    # MAIN MONITOR CHECK
    # =========================================================

    def check_price(self):

        with self.lock:

            trade = self.active_trade


            if trade is None:
                return


            if trade.status == "CLOSED":

                self.active_trade = None

                self.save_current_state()

                return


            price = get_last_price(
                trade.symbol
            )


            if price is None:
                return


            print(
                f"Current {trade.symbol}: "
                f"{price}"
            )


            self.update_price_extremes(
                price
            )


            if self.is_atr_method():

                self.update_atr()


            self.update_stop()


            if self.check_stop_loss(
                price
            ):

                return


            self.check_first_target(
                price
            )


    # =========================================================
    # HIGHEST / LOWEST
    # =========================================================

    def update_price_extremes(
        self,
        price
    ):

        trade = self.active_trade


        if trade is None:
            return


        changed = False


        if trade.direction == "LONG":

            if price > trade.highest_price:

                trade.highest_price = price

                changed = True

                print(
                    f"New highest: "
                    f"{trade.highest_price}"
                )


            if price < trade.lowest_price:

                trade.lowest_price = price

                changed = True


        elif trade.direction == "SHORT":

            if price < trade.lowest_price:

                trade.lowest_price = price

                changed = True

                print(
                    f"New lowest: "
                    f"{trade.lowest_price}"
                )


            if price > trade.highest_price:

                trade.highest_price = price

                changed = True


        if changed:

            self.save_current_state()


    # =========================================================
    # EXIT METHOD
    # =========================================================

    def get_exit_method(self):

        trade = self.active_trade


        if trade is None:
            return ""


        return str(
            trade.exit_option
        ).strip().lower()


    def is_percentage_method(self):

        return (
            "percentage"
            in
            self.get_exit_method()
        )


    def is_atr_method(self):

        return (
            "atr"
            in
            self.get_exit_method()
        )


    def is_swing_method(self):

        return (
            "swing"
            in
            self.get_exit_method()
        )


    # =========================================================
    # STATIC VS TRAILING
    # =========================================================

    def is_trailing_mode(self):

        trade = self.active_trade


        if trade is None:
            return False


        value = (
            trade.stop_static_trail
        )


        if isinstance(
            value,
            bool
        ):

            return value


        if isinstance(
            value,
            (int, float)
        ):

            return value != 0


        text = str(
            value
        ).strip().lower()


        if text in {
            "true",
            "1",
            "trail",
            "trailing",
            "trail stop",
            "trailstop"
        }:

            return True


        if text in {
            "false",
            "0",
            "stop",
            "stop loss",
            "stoploss",
            "static",
            "static stop"
        }:

            return False


        print(
            "\n===== UNKNOWN STOP MODE ====="
        )

        print(
            value
        )


        return False


    # =========================================================
    # UPDATE STOP
    # =========================================================

    def update_stop(self):

        trade = self.active_trade


        if trade is None:
            return


        if not self.is_trailing_mode():

            return


        if self.is_percentage_method():

            self.update_percentage_trail()

            return


        if self.is_atr_method():

            self.update_atr_trail()

            return


        if self.is_swing_method():

            return


    # =========================================================
    # PERCENTAGE TRAIL
    # =========================================================

    def update_percentage_trail(self):

        trade = self.active_trade


        if trade is None:
            return


        if trade.trail_distance is None:
            return


        if trade.trail_distance <= 0:
            return


        distance = (
            trade.trail_distance /
            100
        )


        if trade.direction == "LONG":

            new_stop = (
                trade.highest_price *
                (1 - distance)
            )


            if new_stop > trade.current_stop:

                old_stop = (
                    trade.current_stop
                )

                trade.current_stop = (
                    new_stop
                )


                print(
                    "\n===== PERCENTAGE TRAIL LONG ====="
                )

                print(
                    f"Highest: "
                    f"{trade.highest_price}"
                )

                print(
                    f"Distance: "
                    f"{trade.trail_distance}%"
                )

                print(
                    f"Old stop: "
                    f"{old_stop}"
                )

                print(
                    f"New stop: "
                    f"{trade.current_stop}"
                )


                self.save_current_state()


        elif trade.direction == "SHORT":

            new_stop = (
                trade.lowest_price *
                (1 + distance)
            )


            if new_stop < trade.current_stop:

                old_stop = (
                    trade.current_stop
                )

                trade.current_stop = (
                    new_stop
                )


                print(
                    "\n===== PERCENTAGE TRAIL SHORT ====="
                )

                print(
                    f"Lowest: "
                    f"{trade.lowest_price}"
                )

                print(
                    f"Distance: "
                    f"{trade.trail_distance}%"
                )

                print(
                    f"Old stop: "
                    f"{old_stop}"
                )

                print(
                    f"New stop: "
                    f"{trade.current_stop}"
                )


                self.save_current_state()


    # =========================================================
    # UPDATE ATR
    # =========================================================

    def update_atr(self):

        trade = self.active_trade


        if trade is None:
            return


        if trade.atr_value is None:
            return


        atr_length = int(
            trade.trail_distance
        )


        if atr_length <= 0:
            return


        candles = get_recent_klines(
            symbol=trade.symbol,
            interval=trade.timeframe,
            limit=50
        )


        if candles is None:
            return


        closed_candles = (
            candles[:-1]
        )


        if len(
            closed_candles
        ) < 2:

            return


        for index in range(
            1,
            len(closed_candles)
        ):

            candle = (
                closed_candles[index]
            )

            previous = (
                closed_candles[
                    index - 1
                ]
            )


            bar_time = (
                candle["start_time"]
            )


            if (
                trade.last_atr_bar_time
                is not None
                and
                bar_time
                <=
                trade.last_atr_bar_time
            ):

                continue


            high = candle["high"]

            low = candle["low"]

            previous_close = (
                previous["close"]
            )


            true_range = max(
                high - low,

                abs(
                    high -
                    previous_close
                ),

                abs(
                    low -
                    previous_close
                )
            )


            trade.atr_value = (
                (
                    trade.atr_value *
                    (
                        atr_length - 1
                    )
                )
                +
                true_range
            ) / atr_length


            trade.last_atr_bar_time = (
                bar_time
            )


            print(
                "\n===== ATR UPDATED ====="
            )

            print(
                f"ATR length: "
                f"{atr_length}"
            )

            print(
                f"True range: "
                f"{true_range}"
            )

            print(
                f"ATR: "
                f"{trade.atr_value}"
            )


            self.save_current_state()


    # =========================================================
    # ATR TRAIL
    # =========================================================

    def update_atr_trail(self):

        trade = self.active_trade


        if trade is None:
            return


        if trade.atr_value is None:
            return


        if trade.atr_value <= 0:
            return


        if trade.direction == "LONG":

            new_stop = (
                trade.highest_price -
                trade.atr_value
            )


            if new_stop > trade.current_stop:

                old_stop = (
                    trade.current_stop
                )

                trade.current_stop = (
                    new_stop
                )


                print(
                    "\n===== ATR TRAIL LONG ====="
                )

                print(
                    f"Highest: "
                    f"{trade.highest_price}"
                )

                print(
                    f"ATR: "
                    f"{trade.atr_value}"
                )

                print(
                    f"Old stop: "
                    f"{old_stop}"
                )

                print(
                    f"New stop: "
                    f"{trade.current_stop}"
                )


                self.save_current_state()


        elif trade.direction == "SHORT":

            new_stop = (
                trade.lowest_price +
                trade.atr_value
            )


            if new_stop < trade.current_stop:

                old_stop = (
                    trade.current_stop
                )

                trade.current_stop = (
                    new_stop
                )


                print(
                    "\n===== ATR TRAIL SHORT ====="
                )

                print(
                    f"Lowest: "
                    f"{trade.lowest_price}"
                )

                print(
                    f"ATR: "
                    f"{trade.atr_value}"
                )

                print(
                    f"Old stop: "
                    f"{old_stop}"
                )

                print(
                    f"New stop: "
                    f"{trade.current_stop}"
                )


                self.save_current_state()


    # =========================================================
    # STOP TRIGGER MODE
    # =========================================================

    def stop_uses_intrabar(self):

        trade = self.active_trade


        if trade is None:
            return True


        if self.is_trailing_mode():

            return bool(
                trade.trail_intra_closed
            )


        return bool(
            trade.stoploss_intra_closed
        )


    # =========================================================
    # GET STOP CHECK PRICE
    # =========================================================

    def get_stop_check_price(
        self,
        live_price
    ):

        trade = self.active_trade


        if trade is None:
            return None


        if self.stop_uses_intrabar():

            return live_price


        candle = get_latest_closed_candle(
            symbol=trade.symbol,
            interval=trade.timeframe
        )


        if candle is None:
            return None


        bar_time = (
            candle["start_time"]
        )


        if (
            bar_time
            <=
            trade.bar_time
        ):

            return None


        if (
            trade.last_stop_bar_time
            ==
            bar_time
        ):

            return None


        trade.last_stop_bar_time = (
            bar_time
        )


        self.save_current_state()


        print(
            "\n===== STOP BAR CLOSED ====="
        )

        print(
            f"Bar: {bar_time}"
        )

        print(
            f"Close: "
            f"{candle['close']}"
        )


        return candle["close"]


    # =========================================================
    # STOP LOSS
    # =========================================================

    def check_stop_loss(
        self,
        live_price
    ):

        trade = self.active_trade


        if trade is None:
            return False


        actual_position = (
            get_position_size(
                trade.symbol,
                trade.direction
            )
        )


        if actual_position is None:

            print(
                "\n===== POSITION CHECK FAILED ====="
            )

            return False


        if actual_position <= 0:

            print(
                "\n===== NO POSITION FOUND ON BYBIT ====="
            )

            self.close_trade_locally()

            return True


        trade.remaining_position = (
            actual_position
        )


        check_price = (
            self.get_stop_check_price(
                live_price
            )
        )


        if check_price is None:
            return False


        if trade.direction == "LONG":

            if (
                check_price >
                trade.current_stop
            ):

                return False


            close_side = "Sell"


        elif trade.direction == "SHORT":

            if (
                check_price <
                trade.current_stop
            ):

                return False


            close_side = "Buy"


        else:

            return False


        print(
            f"\n===== STOP HIT "
            f"{trade.direction} ====="
        )

        print(
            f"Check price: "
            f"{check_price}"
        )

        print(
            f"Stop: "
            f"{trade.current_stop}"
        )

        print(
            f"Actual position: "
            f"{actual_position}"
        )


        result = close_position(
            symbol=trade.symbol,
            side=close_side,
            qty=actual_position
        )


        if not result["success"]:

            print(
                "\n===== STOP CLOSE FAILED ====="
            )

            print(
                result["error"]
            )

            return False


        print(
            "\n===== STOP LOSS EXECUTED ====="
        )


        self.close_trade_locally()

        return True


    # =========================================================
    # TARGET CHECK PRICE
    # =========================================================

    def get_target_check_price(
        self,
        live_price
    ):

        trade = self.active_trade


        if trade is None:
            return None


        if (
            trade.first_target_intra_closed
        ):

            return live_price


        candle = get_latest_closed_candle(
            symbol=trade.symbol,
            interval=trade.timeframe
        )


        if candle is None:
            return None


        bar_time = (
            candle["start_time"]
        )


        if (
            bar_time
            <=
            trade.bar_time
        ):

            return None


        if (
            trade.last_target_bar_time
            ==
            bar_time
        ):

            return None


        trade.last_target_bar_time = (
            bar_time
        )


        self.save_current_state()


        print(
            "\n===== TARGET BAR CLOSED ====="
        )

        print(
            f"Bar: "
            f"{bar_time}"
        )

        print(
            f"Close: "
            f"{candle['close']}"
        )


        return candle["close"]


    # =========================================================
    # FIRST TARGET
    # =========================================================

    def check_first_target(
        self,
        live_price
    ):

        trade = self.active_trade


        if trade is None:
            return


        if not trade.first_target_enabled:
            return


        if trade.first_target is None:
            return


        if trade.first_target_hit:
            return


        check_price = (
            self.get_target_check_price(
                live_price
            )
        )


        if check_price is None:
            return


        if trade.direction == "LONG":

            if (
                check_price <
                trade.first_target
            ):

                return


            close_side = "Sell"


        elif trade.direction == "SHORT":

            if (
                check_price >
                trade.first_target
            ):

                return


            close_side = "Buy"


        else:

            return


        print(
            f"\n===== FIRST TARGET HIT "
            f"{trade.direction} ====="
        )

        print(
            f"Check price: "
            f"{check_price}"
        )

        print(
            f"Target: "
            f"{trade.first_target}"
        )


        actual_position = (
            get_position_size(
                trade.symbol,
                trade.direction
            )
        )


        if actual_position is None:

            print(
                "\n===== POSITION CHECK FAILED ====="
            )

            return


        if actual_position <= 0:

            print(
                "\n===== NO POSITION FOUND ON BYBIT ====="
            )

            self.close_trade_locally()

            return


        closed_amount = (
            trade.position_size *
            trade.first_target_close_perc /
            100
        )


        closed_amount = min(
            closed_amount,
            actual_position
        )


        if closed_amount <= 0:

            print(
                "\n===== NOTHING TO PARTIALLY CLOSE ====="
            )

            trade.first_target_hit = True

            self.save_current_state()

            return


        result = close_partial_position(
            symbol=trade.symbol,
            side=close_side,
            qty=closed_amount
        )


        # -------------------------------------------------
        # FAILED PARTIAL CLOSE
        # -------------------------------------------------

        if not result["success"]:

            error = result.get(
                "error"
            )


            print(
                "\n===== PARTIAL CLOSE FAILED ====="
            )

            print(
                error
            )


            error_text = str(
                error
            ).lower()


            # ---------------------------------------------
            # TOO SMALL FOR EXCHANGE
            # ---------------------------------------------

            if (
                "invalid partial close quantity"
                in error_text
            ):

                print(
                    "\n===== FIRST TARGET TOO SMALL FOR EXCHANGE ====="
                )

                print(
                    "Target marked as handled."
                )

                print(
                    "Remaining position will continue "
                    "to be managed by the stop/trail."
                )


                trade.first_target_hit = True

                trade.remaining_position = (
                    actual_position
                )


                self.save_current_state()


            return


        # -------------------------------------------------
        # PARTIAL CLOSE SUCCESS
        # -------------------------------------------------

        trade.first_target_hit = True


        print(
            "\n===== PARTIAL CLOSE EXECUTED ====="
        )

        print(
            f"Requested close: "
            f"{closed_amount}"
        )


        actual_after = (
            get_position_size(
                trade.symbol,
                trade.direction
            )
        )


        if actual_after is None:

            print(
                "\n===== POSITION RESYNC FAILED ====="
            )

            self.save_current_state()

            return


        trade.remaining_position = (
            actual_after
        )


        print(
            f"Remaining: "
            f"{actual_after}"
        )


        self.save_current_state()


        if actual_after <= 0:

            self.close_trade_locally()


    # =========================================================
    # CLOSE LOCAL TRADE
    # =========================================================

    def close_trade_locally(self):

        trade = self.active_trade


        if trade is None:
            return


        trade.remaining_position = 0

        trade.status = "CLOSED"


        print(
            "\n===== TRADE CLOSED LOCALLY ====="
        )


        self.active_trade = None


        self.save_current_state()                                        