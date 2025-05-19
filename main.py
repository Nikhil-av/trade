from flask import Flask, jsonify, request
import requests, pyotp
import time
from typing import Optional
from SmartApi.smartConnect import SmartConnect
import yfinance as yf

app = Flask(__name__)

ANGELONE_API_KEY = "ezWgejKX"
ANGELONE_CLIENT_CODE = "nikhil"
ANGELONE_ACCESS_TOKEN = "6ac39929-077b-49a1-bbac-516cfbb520f7"
ANGELONE_BASE_URL = "https://apiconnect.angelone.in"

HEADERS = {
    "X-PrivateKey": ANGELONE_API_KEY,
    "X-ClientLocalIP": "127.0.0.1",
    "X-ClientPublicIP": "127.0.0.1",
    "X-MACAddress": "00:00:00:00:00:00",
    "X-UserType": "USER",
    "Authorization": f"Bearer {ANGELONE_ACCESS_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_smartconnect_obj():
    import pyotp
    from SmartApi.smartConnect import SmartConnect
    api_key = "ezWgejKX"
    client_code = "AAAM735506"
    password = "1793"
    totp_secret = "FWONPNHOM6VGBYQEZ2GNTKAA5M"
    obj = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(totp_secret).now()
    data = obj.generateSession(client_code, password, totp)
    refreshToken = data['data']['refreshToken']
    obj.getfeedToken()
    obj.getProfile(refreshToken)
    return obj
obj=get_smartconnect_obj()
mode="FULL"
exchangeTokens= {
"BSE": [
"3045"
]
}
marketData=obj.getMarketData(mode, exchangeTokens)
print(marketData)
nifty_50_symbols = [
    "ADANIENT", "ADANIPORTS", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV",
    "BPCL", "BHARTIARTL", "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY", "EICHERMOT",
    "GRASIM", "HCLTECH", "HDFCBANK", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC",
    "INDUSINDBK", "INFY", "JSWSTEEL", "KOTAKBANK", "LT", "M&M", "MARUTI", "NTPC", "NESTLEIND",
    "ONGC", "POWERGRID", "RELIANCE", "SBIN", "SHRIRAMFIN", "SUNPHARMA", "TCS", "TATACONSUM",
    "TATAMOTORS", "TATASTEEL", "TECHM", "TITAN", "ULTRACEMCO", "UPL", "WIPRO", "LTIM", "BAJAJHLDNG"
]
nifty_100_symbols = [
    "ABB", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIENSOL", "AMBUJACEM", "APOLLOHOSP", "ASIANPAINT",
    "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BAJAJHLDNG", "BANDHANBNK", "BANKBARODA",
    "BEL", "BERGEPAINT", "BHARTIARTL", "BIOCON", "BOSCHLTD", "BPCL", "BRITANNIA", "CANBK", "CHOLAFIN",
    "CIPLA", "COALINDIA", "COLPAL", "DABUR", "DIVISLAB", "DLF", "DRREDDY", "EICHERMOT", "GAIL", "GODREJCP",
    "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK",
    "ICICIPRULI", "IDFCFIRSTB", "INDHOTEL", "INDIGO", "INDUSINDBK", "INFY", "IOC", "ITC", "JSWSTEEL",
    "JINDALSTEL", "KOTAKBANK", "LT", "LTIM", "M&M", "MARICO", "MARUTI", "MCDOWELL-N", "MOTHERSON",
    "NESTLEIND", "NTPC", "ONGC", "PAGEIND", "PAYTM", "PEL", "PETRONET", "PIDILITIND", "PNB", "POWERGRID",
    "RECLTD", "RELIANCE", "SAIL", "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SRF", "SUNPHARMA",
    "TATACHEM", "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM",
    "TRENT", "TVSMOTOR", "UBL", "ULTRACEMCO", "UPL", "VEDL", "VOLTAS", "WIPRO", "ZEEL"
]
nifty_smallcap_100_symbols = [
    "AAVAS", "AEGISCHEM", "AFFLE", "AMARAJABAT", "AMBER", "ANGELONE", "ANURAS", "APARINDS", "BLS", "BSE",
    "BALAMINES", "BALRAMCHIN", "BIKAJI", "BIRLACORPN", "BSOFT", "CESC", "CIEINDIA", "CAMPUS", "CANFINHOME", "CEATLTD",
    "CENTRALBK", "CDSL", "CENTURYTEX", "CHAMBLFERT", "CUB", "COCHINSHIP", "CAMS", "CREDITACC", "CYIENT", "DATAPATTNS",
    "DEEPAKFERT", "EASEMYTRIP", "ELGIEQUIP", "EQUITASBNK", "EXIDEIND", "FINCABLES", "FSL", "GLENMARK", "MEDANTA", "GRANULES",
    "GRAPHITE", "GNFC", "HFCL", "HAPPSTMNDS", "HBLPOWER", "IDFC", "IDFCFIRSTB", "IIFL", "IIFLWAM", "INDIAMART",
    "IRCON", "JINDALSAW", "JUBLINGREA", "JUSTDIAL", "KARURVYSYA", "KEC", "KFINTECH", "KIRLOSENG", "LAXMIMACH", "LATENTVIEW",
    "LXCHEM", "MGL", "MANAPPURAM", "MRPL", "MEDPLUS", "METROPOLIS", "MINDACORP", "MOTILALOFS", "NATCOPHARM", "NAVINFLUOR",
    "NCC", "NEULANDLAB", "NH", "NLCINDIA", "PNBHOUSING", "PERSISTENT", "PRINCEPIPE", "RADICO", "RAILTEL", "RBLBANK",
    "RECLTD", "REDINGTON", "SAREGAMA", "SHILPAMED", "SHRIRAMFIN", "SOBHA", "SPARC", "SPANDANA", "SYNGENE", "TATACOMM",
    "TATVA", "TEJASNET", "TRIDENT", "TRITURBINE", "TTKPRESTIG", "UJJIVANSFB", "VGUARD", "VSTIND", "WELCORP", "ZENSARTECH"
]

url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
data = requests.get(url).json()
bse_stocks = [item for item in data if item.get('exch_seg') == 'BSE']
nifty_50_array = []
nifty_100_array = []
small_cap_100_array = []
for symb in nifty_50_symbols:
    stocks = [item for item in bse_stocks if item.get('symbol') == symb]
    if len(stocks) == 1:
        nifty_50_array.append(stocks[0])
for symb in nifty_100_symbols:
    if symb not in nifty_50_symbols:
        stocks = [item for item in bse_stocks if item.get('symbol') == symb]
        if len(stocks) >= 1:
            nifty_100_array.append(stocks[0])
for symb in nifty_smallcap_100_symbols:
    stocks = [item for item in bse_stocks if item.get('symbol') == symb]
    if len(stocks) >= 1:
        small_cap_100_array.append(stocks[0])
print(len(nifty_50_array), len(nifty_100_array), len(small_cap_100_array))

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def fetch_market_data_bulk(obj, stocks, mode="FULL", exchange="BSE", batch_size=25, sleep_time=4):
    symboltoken_to_stock = {stock['token']: stock for stock in stocks}
    tokens = [stock['token'] for stock in stocks]
    all_market_data = {}
    for token_batch in batch(tokens, batch_size):
        exchangeTokens = {exchange: token_batch}
        marketData = obj.getMarketData(mode, exchangeTokens)
        if marketData['status'] and 'data' in marketData and 'fetched' in marketData['data']:
            for item in marketData['data']['fetched']:
                all_market_data[item['symbolToken']] = item
        time.sleep(sleep_time)
    return all_market_data, symboltoken_to_stock

@app.route("/nifty50", methods=["GET"])
def trade_nifty_50_stocks():
    obj = get_smartconnect_obj()
    print("in nifty 50")
    gt_5, gt_4, gt_3, gt_2_5, gt_2 = [], [], [], [], []
    tradable_stocks = []
    try:
        market_data, token_map = fetch_market_data_bulk(obj, nifty_50_array)
        for token, data in market_data.items():
            close_price = data.get('ltp')
            open_price = data.get('open')
            if close_price is not None and open_price is not None:
                percent_change = ((close_price - open_price) / open_price) * 100
                if close_price < 2500:
                    stock = token_map[token]
                    if percent_change > 5:
                        gt_5.append(stock)
                    elif percent_change > 4:
                        gt_4.append(stock)
                    elif percent_change > 3:
                        gt_3.append(stock)
                    elif percent_change > 2.5:
                        gt_2_5.append(stock)
                    elif percent_change > 2:
                        gt_2.append(stock)
        tradable_stocks = gt_5
        if len(tradable_stocks) <= 5:
            tradable_stocks += gt_4
        if len(tradable_stocks) <= 5:
            tradable_stocks += gt_3
        if len(tradable_stocks) <= 5:
            tradable_stocks += gt_2_5
        if len(tradable_stocks) <= 5:
            tradable_stocks += gt_2
        for trade_stock in tradable_stocks:
            token = trade_stock['token']
            data = market_data.get(token, {})
            close_price = data.get('close', 1)
            if close_price > 500:
                quantity = 1
            else:
                quantity = int(500 // close_price)
                if quantity < 1:
                    quantity = 1
            orderparams = {
                "variety": "NORMAL",
                "tradingsymbol": trade_stock['symbol'],
                "symboltoken": trade_stock['token'],
                "transactiontype": "BUY",
                "exchange": "BSE",
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": str(quantity)
            }
            orderId = obj.placeOrder(orderparams)
            print(orderId)
        return jsonify({
            "tradable_stocks": tradable_stocks
        })
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route("/nifty100", methods=["GET"])
def trade_nifty_100_stocks():
    obj = get_smartconnect_obj()
    gt_5, gt_4, gt_3, gt_2_5 = [], [], [], []
    tradable_stocks = []
    print("in nifty 100")
    try:
        market_data, token_map = fetch_market_data_bulk(obj, nifty_100_array)
        for token, data in market_data.items():
            close_price = data.get('ltp')
            open_price = data.get('open')
            if close_price is not None and open_price is not None:
                percent_change = ((close_price - open_price) / open_price) * 100
                if close_price < 2500:
                    stock = token_map[token]
                    if percent_change > 5:
                        gt_5.append(stock)
                    elif percent_change > 4:
                        gt_4.append(stock)
                    elif percent_change > 3:
                        gt_3.append(stock)
                    elif percent_change > 2.5:
                        gt_2_5.append(stock)
        tradable_stocks = gt_5
        if len(tradable_stocks) <= 5:
            tradable_stocks += gt_4
        if len(tradable_stocks) <= 5:
            tradable_stocks += gt_3
        if len(tradable_stocks) <= 5:
            tradable_stocks += gt_2_5
        for trade_stock in tradable_stocks:
            token = trade_stock['token']
            data = market_data.get(token, {})
            close_price = data.get('close', 1)
            if close_price > 500:
                quantity = 1
            else:
                quantity = int(500 // close_price)
                if quantity < 1:
                    quantity = 1
            orderparams = {
                "variety": "NORMAL",
                "tradingsymbol": trade_stock['symbol'],
                "symboltoken": trade_stock['token'],
                "transactiontype": "BUY",
                "exchange": "BSE",
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": str(quantity)
            }
            orderId = obj.placeOrder(orderparams)
            print(orderId)
        return jsonify({
            "tradable_stocks": tradable_stocks
        })
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route("/smallcap", methods=["GET"])
def trade_smallcap_stocks():
    obj = get_smartconnect_obj()
    gt_5, gt_4, gt_3 = [], [], []
    tradable_stocks = []
    try:
        market_data, token_map = fetch_market_data_bulk(obj, small_cap_100_array)
        for token, data in market_data.items():
            close_price = data.get('ltp')
            open_price = data.get('open')
            if close_price is not None and open_price is not None:
                percent_change = ((close_price - open_price) / open_price) * 100
                if close_price < 2500:
                    stock = token_map[token]
                    if percent_change > 5:
                        gt_5.append(stock)
                    elif percent_change > 4:
                        gt_4.append(stock)
                    elif percent_change > 3:
                        gt_3.append(stock)
        tradable_stocks = gt_5
        if len(tradable_stocks) <= 5:
            tradable_stocks += gt_4
        if len(tradable_stocks) <= 5:
            tradable_stocks += gt_3
        for trade_stock in tradable_stocks:
            token = trade_stock['token']
            data = market_data.get(token, {})
            close_price = data.get('close', 1)
            if close_price > 500:
                quantity = 1
            else:
                quantity = int(500 // close_price)
                if quantity < 1:
                    quantity = 1
            orderparams = {
                "variety": "NORMAL",
                "tradingsymbol": trade_stock['symbol'],
                "symboltoken": trade_stock['token'],
                "transactiontype": "BUY",
                "exchange": "BSE",
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": str(quantity)
            }
            orderId = obj.placeOrder(orderparams)
            print(orderId)
        return jsonify({
            "tradable_stocks": tradable_stocks
        })
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route("/sell", methods=["GET"])
def sell():
    obj = get_smartconnect_obj()
    holdings = obj.holding()["data"]
    for stock in holdings:
        ltp = stock["ltp"]
        close = stock["close"]
        quantity = stock["quantity"]
        symbol = stock["tradingsymbol"]
        exchange = stock["exchange"]
        token = stock["symboltoken"]

        if ltp < close:
            print(f"Selling {symbol}: LTP ({ltp}) < Close ({close})")
            sell_order = obj.placeOrder({
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": token,
                "transactiontype": "SELL",
                "exchange": exchange,
                "ordertype": "MARKET",
                "producttype": "DELIVERY",
                "duration": "DAY",
                "price": 0.0,
                "squareoff": "0",
                "stoploss": "0",
                "quantity": quantity
            })
            print("Sell Order Response:", sell_order)
if __name__ == "__main__":
    app.run(debug=True)

