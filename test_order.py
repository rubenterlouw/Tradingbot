from bybit.orders import place_market_order

result = place_market_order(
    "BTCUSDT",
    "Buy",
    0.001
)

print(result)