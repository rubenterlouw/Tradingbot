from queue import Queue, Full
from threading import Thread, Lock


# =========================================================
# PTS EXECUTION WORKER
# =========================================================

class ExecutionWorker:

    def __init__(
        self,
        trade_manager
    ):

        self.trade_manager = (
            trade_manager
        )

        # PTS only handles one active trade at a time,
        # but we allow a few pending messages.
        self.queue = Queue(
            maxsize=10
        )

        self.started = False

        # Signal IDs which have been accepted by Flask
        # but are not yet completely processed.
        self.pending_signal_ids = set()

        self.pending_lock = Lock()

    # =====================================================
    # START WORKER
    # =====================================================

    def start(self):

        if self.started:
            return

        self.started = True

        thread = Thread(
            target=self._worker_loop,
            daemon=True
        )

        thread.start()

        print(
            "\n===== PTS EXECUTION WORKER STARTED ====="
        )

    # =====================================================
    # CHECK PENDING SIGNAL
    # =====================================================

    def is_pending(
        self,
        signal_id
    ):

        with self.pending_lock:

            return (
                signal_id
                in self.pending_signal_ids
            )

    # =====================================================
    # QUEUE TRADE
    # =====================================================

    def queue_trade(
        self,
        trade
    ):

        signal_id = str(
            trade.signal_id
        )

        # -------------------------------------------------
        # RESERVE SIGNAL ID FIRST
        # -------------------------------------------------

        with self.pending_lock:

            if (
                signal_id
                in self.pending_signal_ids
            ):

                return False

            self.pending_signal_ids.add(
                signal_id
            )

        # -------------------------------------------------
        # ADD TO QUEUE
        # -------------------------------------------------

        try:

            self.queue.put_nowait(
                trade
            )

        except Full:

            with self.pending_lock:

                self.pending_signal_ids.discard(
                    signal_id
                )

            return False

        print(
            "\n===== PTS TRADE QUEUED ====="
        )

        print(
            f"Signal ID: {signal_id}"
        )

        print(
            f"Symbol: {trade.symbol}"
        )

        print(
            f"Direction: {trade.direction}"
        )

        return True

    # =====================================================
    # WORKER LOOP
    # =====================================================

    def _worker_loop(self):

        while True:

            trade = (
                self.queue.get()
            )

            signal_id = str(
                trade.signal_id
            )

            try:

                print(
                    "\n"
                    "========================================"
                )

                print(
                    "       PTS BACKGROUND EXECUTION"
                )

                print(
                    "========================================"
                )

                print(
                    f"Signal ID: {signal_id}"
                )

                print(
                    f"Symbol: {trade.symbol}"
                )

                print(
                    f"Direction: {trade.direction}"
                )

                # -----------------------------------------
                # FINAL DUPLICATE CHECK
                # -----------------------------------------

                if (
                    self.trade_manager
                    .is_duplicate_signal(
                        signal_id
                    )
                ):

                    print(
                        "\n===== DUPLICATE TRADE SKIPPED ====="
                    )

                    continue

                # -----------------------------------------
                # START TRADE
                # -----------------------------------------

                success = (
                    self.trade_manager.start_trade(
                        trade
                    )
                )

                if success:

                    print(
                        "\n"
                        "===== PTS BACKGROUND TRADE STARTED ====="
                    )

                else:

                    print(
                        "\n"
                        "===== PTS BACKGROUND TRADE REJECTED ====="
                    )

            except Exception as error:

                print(
                    "\n===== PTS EXECUTION WORKER ERROR ====="
                )

                print(
                    repr(error)
                )

            finally:

                with self.pending_lock:

                    self.pending_signal_ids.discard(
                        signal_id
                    )

                self.queue.task_done()