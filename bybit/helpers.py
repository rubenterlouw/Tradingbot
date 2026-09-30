def normalize_symbol(tv_symbol):

    symbol = tv_symbol

    if ":" in symbol:
        symbol = symbol.split(":")[1]

    if symbol.endswith(".P"):
        symbol = symbol.replace(".P", "")

    return symbol 

