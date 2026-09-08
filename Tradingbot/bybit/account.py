from bybit.client import session

def get_balance():

    wallet =  session.get_wallet_balance(
        accountType="UNIFIED"
    )

    return float(wallet["result"]["list"][0]["totalEquity"]
    )