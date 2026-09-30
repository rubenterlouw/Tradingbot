import time
import traceback


class TradeMonitor:

    def __init__(
        self,
        trade_manager
    ):

        self.trade_manager = (
            trade_manager
        )

        self.running = False


    def start(self):

        print(
            "\n===== MONITOR STARTED ====="
        )

        self.running = True


        while self.running:

            try:

                if (
                    self.trade_manager
                    .active_trade
                    is not None
                ):

                    self.trade_manager.check_price()


            except Exception as error:

                print(
                    "\n===== MONITOR ERROR ====="
                )

                print(
                    repr(error)
                )

                traceback.print_exc()


            # Even if one iteration fails,
            # monitor continues running.

            time.sleep(1)


    def stop(self):

        self.running = False