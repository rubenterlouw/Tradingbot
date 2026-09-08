from pybit.unified_trading import HTTP

from config import(
    BYBIT_API_KEY_DEMO,
    BYBIT_API_SECRET_DEMO,
    USE_DEMO
)

session = HTTP(
    demo = USE_DEMO,
    api_key = BYBIT_API_KEY_DEMO,
    api_secret = BYBIT_API_SECRET_DEMO
)