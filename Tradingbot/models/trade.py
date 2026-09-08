from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Trade:

    # =========================================================
    # TRADINGVIEW DATA
    # =========================================================

    symbol: str
    direction: str

    entry_price: float
    stop_loss: float
    position_size: float

    first_target_enabled: bool
    first_target: Optional[float]
    first_target_close_perc: float

    exit_option: str
    stop_static_trail: object
    trail_distance: float

    current_atr: Optional[float]

    timeframe: str
    signal_id: str
    bar_time: int

    stoploss_intra_closed: bool = True
    first_target_intra_closed: bool = True
    trail_intra_closed: bool = True


    # =========================================================
    # DYNAMIC TRADE STATE
    # =========================================================

    current_stop: float = field(
        init=False
    )

    highest_price: float = field(
        init=False
    )

    lowest_price: float = field(
        init=False
    )

    remaining_position: float = field(
        init=False
    )

    first_target_hit: bool = field(
        default=False,
        init=False
    )

    status: str = field(
        default="OPEN",
        init=False
    )


    # =========================================================
    # ATR STATE
    # =========================================================

    atr_value: Optional[float] = field(
        init=False
    )

    last_atr_bar_time: Optional[int] = field(
        init=False
    )


    # =========================================================
    # BAR-CLOSE STATE
    # =========================================================

    last_stop_bar_time: Optional[int] = field(
        default=None,
        init=False
    )

    last_target_bar_time: Optional[int] = field(
        default=None,
        init=False
    )


    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __post_init__(self):

        self.direction = (
            self.direction.upper()
        )


        self.current_stop = (
            self.stop_loss
        )


        self.highest_price = (
            self.entry_price
        )


        self.lowest_price = (
            self.entry_price
        )


        self.remaining_position = (
            self.position_size
        )


        self.atr_value = (
            self.current_atr
        )


        # current_atr came from TradingView
        # on this bar.

        self.last_atr_bar_time = (
            self.bar_time
        )