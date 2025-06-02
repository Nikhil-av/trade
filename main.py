from flask import Flask, jsonify, request
import requests, pyotp
import time
from typing import Optional
from SmartApi.smartConnect import SmartConnect
import yfinance as yf
import datetime
import threading
import numpy as np
import pandas as pd

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

def get_last_trading_day():
    """
    Returns (fromdate, todate) as strings in 'YYYY-MM-DD HH:MM' format for the last trading day (skipping weekends).
    """
    today = datetime.date.today()
    # If today is Monday, last trading day is Friday
    if today.weekday() == 0:
        last_trading_day = today - datetime.timedelta(days=3)
    # If today is Sunday, last trading day is Friday
    elif today.weekday() == 6:
        last_trading_day = today - datetime.timedelta(days=2)
    # If today is Saturday, last trading day is Friday
    elif today.weekday() == 5:
        last_trading_day = today - datetime.timedelta(days=1)
    else:
        last_trading_day = today - datetime.timedelta(days=1)
    # Market open and close times for daily candle (09:00 to 15:30)
    fromdate = last_trading_day.strftime("%Y-%m-%d") + " 09:00"
    todate = last_trading_day.strftime("%Y-%m-%d") + " 15:30"
    return fromdate, todate

def fetch_candle_data_bulk(obj, stocks, interval="ONE_DAY", exchange="BSE", batch_size=10, sleep_time=5, num_candles=90):
    """
    Fetches candle data for a list of stocks in batches using obj.getCandleData.
    Returns a dict mapping token to a list of last N candle dicts (open, high, low, close).
    """
    symboltoken_to_stock = {stock['token']: stock for stock in stocks}
    tokens = [stock['token'] for stock in stocks]
    all_candle_data = {}
    today = datetime.date.today()
    # Find last trading day
    if today.weekday() == 0:
        last_trading_day = today - datetime.timedelta(days=3)
    elif today.weekday() == 6:
        last_trading_day = today - datetime.timedelta(days=2)
    elif today.weekday() == 5:
        last_trading_day = today - datetime.timedelta(days=1)
    else:
        last_trading_day = today - datetime.timedelta(days=1)
    # Go back 40 days to ensure we get 30 trading days (skip weekends/holidays)
    fromdate = (last_trading_day - datetime.timedelta(days=90)).strftime("%Y-%m-%d") + " 09:00"
    todate = last_trading_day.strftime("%Y-%m-%d") + " 15:30"
    for token_batch in batch(tokens, batch_size):
        for token in token_batch:
            try:
                params = {
                    "exchange": exchange,
                    "symboltoken": token,
                    "interval": interval,
                    "fromdate": fromdate,
                    "todate": todate
                }
                candle_resp = obj.getCandleData(params)
                if candle_resp.get("status") and candle_resp.get("data"):
                    # Each item: [timestamp, open, high, low, close, volume]
                    candles = [
                        {
                            "open": c[1],
                            "high": c[2],
                            "low": c[3],
                            "close": c[4]
                        }
                        for c in candle_resp["data"][-num_candles:]
                    ]
                    all_candle_data[token] = candles
            except Exception as e:
                continue
        time.sleep(sleep_time)
    return all_candle_data, symboltoken_to_stock

def detect_candlestick_patterns(candles):
    """
    Detects major candlestick patterns from a list of candles (up to 30).
    Returns a list of pattern names detected for the last candle.
    """
    patterns = []
    if not candles or len(candles) == 0:
        return patterns

    # Single-candle patterns (use last candle)
    last = candles[-1]
    open_ = last.get('open')
    high = last.get('high')
    low = last.get('low')
    close = last.get('close')
    if None in (open_, high, low, close):
        return patterns

    body = abs(close - open_)
    candle_range = high - low
    upper_shadow = high - max(open_, close)
    lower_shadow = min(open_, close) - low

    # Bullish Engulfing (needs previous candle)
    if len(candles) >= 2:
        prev = candles[-2]
        prev_open = prev.get('open')
        prev_close = prev.get('close')
        if prev_open is not None and prev_close is not None:
            if prev_close < prev_open and close > open_ and close > prev_open and open_ < prev_close:
                patterns.append("Bullish Engulfing")
            if prev_close > prev_open and close < open_ and close < prev_open and open_ > prev_close:
                patterns.append("Bearish Engulfing")
        # Piercing Line (bullish reversal)
        if prev_close < prev_open and close > open_ and open_ < prev_close and close > ((prev_open + prev_close) / 2):
            patterns.append("Piercing Line")
        # Bullish Harami
        if prev_close < prev_open and close > open_ and open_ > prev_close and close < prev_open:
            patterns.append("Bullish Harami")
        # Inverted Hammer (single candle, but often checked after a downtrend)
        if body < 0.3 * candle_range and upper_shadow > 2 * body and lower_shadow < 0.2 * candle_range:
            patterns.append("Inverted Hammer")

    # Three White Soldiers (needs 3 candles)
    if len(candles) >= 3:
        c1, c2, c3 = candles[-3], candles[-2], candles[-1]
        if (
            c1.get('close') > c1.get('open') and
            c2.get('close') > c2.get('open') and
            c3.get('close') > c3.get('open') and
            c2.get('open') > c1.get('open') and
            c3.get('open') > c2.get('open') and
            c2.get('close') > c1.get('close') and
            c3.get('close') > c2.get('close')
        ):
            patterns.append("Three White Soldiers")
        # Morning Star
        if (
            c1.get('close') < c1.get('open') and
            abs(c2.get('close') - c2.get('open')) < 0.5 * abs(c1.get('close') - c1.get('open')) and
            c3.get('close') > c3.get('open') and
            c3.get('close') > ((c1.get('open') + c1.get('close')) / 2)
        ):
            patterns.append("Morning Star")
        # Rising Three Methods (bullish continuation)
        if (
            c1.get('close') > c1.get('open') and
            all(c.get('close') < c.get('open') for c in candles[-4:-1]) and
            candles[-4].get('close') > candles[-3].get('close') and
            c3.get('close') > c1.get('close')
        ):
            patterns.append("Rising Three Methods")

    # Hammer (single candle)
    if body < 0.3 * candle_range and lower_shadow > 2 * body and upper_shadow < 0.2 * candle_range:
        patterns.append("Hammer")
    # Dragonfly Doji
    if body < 0.1 * candle_range and abs(open_ - low) < 0.05 * candle_range and abs(close - low) < 0.05 * candle_range:
        patterns.append("Dragonfly Doji")
    # Doji
    if body < 0.1 * candle_range:
        patterns.append("Doji")

    return patterns

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

def detect_candlestick_patterns(candles):
    """
    Detects major candlestick patterns from a list of candles.
    Each candle is a dict with open, high, low, close.
    Returns a list of pattern names detected for the last candle.
    """
    patterns = []
    if not candles or len(candles) == 0:
        return patterns

    # Single-candle patterns (use last candle)
    last = candles[-1]
    open_ = last.get('open')
    high = last.get('high')
    low = last.get('low')
    close = last.get('close')
    if None in (open_, high, low, close):
        return patterns

    body = abs(close - open_)
    candle_range = high - low
    upper_shadow = high - max(open_, close)
    lower_shadow = min(open_, close) - low

    # Bullish Engulfing (needs previous candle)
    if len(candles) >= 2:
        prev = candles[-2]
        prev_open = prev.get('open')
        prev_close = prev.get('close')
        if prev_open is not None and prev_close is not None:
            if prev_close < prev_open and close > open_ and close > prev_open and open_ < prev_close:
                patterns.append("Bullish Engulfing")
            if prev_close > prev_open and close < open_ and close < prev_open and open_ > prev_close:
                patterns.append("Bearish Engulfing")
        # Piercing Line (bullish reversal)
        if prev_close < prev_open and close > open_ and open_ < prev_close and close > ((prev_open + prev_close) / 2):
            patterns.append("Piercing Line")
        # Bullish Harami
        if prev_close < prev_open and close > open_ and open_ > prev_close and close < prev_open:
            patterns.append("Bullish Harami")
        # Inverted Hammer (single candle, but often checked after a downtrend)
        if body < 0.3 * candle_range and upper_shadow > 2 * body and lower_shadow < 0.2 * candle_range:
            patterns.append("Inverted Hammer")

    # Three White Soldiers (needs 3 candles)
    if len(candles) >= 3:
        c1, c2, c3 = candles[-3], candles[-2], candles[-1]
        if (
            c1.get('close') > c1.get('open') and
            c2.get('close') > c2.get('open') and
            c3.get('close') > c3.get('open') and
            c2.get('open') > c1.get('open') and
            c3.get('open') > c2.get('open') and
            c2.get('close') > c1.get('close') and
            c3.get('close') > c2.get('close')
        ):
            patterns.append("Three White Soldiers")
        # Morning Star
        if (
            c1.get('close') < c1.get('open') and
            abs(c2.get('close') - c2.get('open')) < 0.5 * abs(c1.get('close') - c1.get('open')) and
            c3.get('close') > c3.get('open') and
            c3.get('close') > ((c1.get('open') + c1.get('close')) / 2)
        ):
            patterns.append("Morning Star")
        # Rising Three Methods (bullish continuation)
        if (
            c1.get('close') > c1.get('open') and
            all(c.get('close') < c.get('open') for c in candles[-4:-1]) and
            candles[-4].get('close') > candles[-3].get('close') and
            c3.get('close') > c1.get('close')
        ):
            patterns.append("Rising Three Methods")

    # Hammer (single candle)
    if body < 0.3 * candle_range and lower_shadow > 2 * body and upper_shadow < 0.2 * candle_range:
        patterns.append("Hammer")
    # Dragonfly Doji
    if body < 0.1 * candle_range and abs(open_ - low) < 0.05 * candle_range and abs(close - low) < 0.05 * candle_range:
        patterns.append("Dragonfly Doji")
    # Doji
    if body < 0.1 * candle_range:
        patterns.append("Doji")

    return patterns

# @app.route("/nifty100/candlestick-patterns", methods=["GET"])
# def get_nifty100_candlestick_patterns():
#     import pandas as pd
#     obj = get_smartconnect_obj()
#     try:
#         # Fetch last 30 candles for each stock to cover all patterns and indicators
#         candle_data, token_map = fetch_candle_data_bulk(obj, nifty_100_array, num_candles=30)
#         result = []
#         bullish_patterns = {
#             "Bullish Engulfing",
#             "Hammer",
#             "Morning Star",
#             "Piercing Line",
#             "Bullish Harami",
#             "Inverted Hammer",
#             "Three White Soldiers",
#             "Dragonfly Doji",
#             "Rising Three Methods"
#         }
#         for token, candles in candle_data.items():
#             patterns = detect_candlestick_patterns(candles)
#             positive = [p for p in patterns if p in bullish_patterns]
#             closes = [c['close'] for c in candles]
#             volumes = [c.get('volume', 0) for c in candles]
#             rsi = calculate_rsi(closes)
#             macd, macd_signal = calculate_macd(closes)
#             ema = calculate_ema(closes)
#             bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(closes)
#             atr = calculate_atr(candles)
#             last_volume = volumes[-1] if volumes else None
#             stock = token_map[token]
#             result.append({
#                 "symbol": stock["symbol"],
#                 "token": stock["token"],
#                 "patterns": positive,
#                 "rsi": rsi,
#                 "macd": macd,
#                 "macd_signal": macd_signal,
#                 "ema": ema,
#                 "bollinger_upper": bb_upper,
#                 "bollinger_mid": bb_mid,
#                 "bollinger_lower": bb_lower,
#                 "atr": atr,
#                 "volume": last_volume
#             })
#         return jsonify({"candlestick_patterns": result})
#     except Exception as e:
#         return jsonify({"detail": str(e)}), 500


def calculate_rsi(closes, period=14):
    closes = np.array(closes)
    if len(closes) < period + 1:
        return None
    deltas = np.diff(closes)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - 100 / (1 + rs)
    for i in range(period, len(closes) - 1):
        delta = deltas[i]
        if delta > 0:
            upval = delta
            downval = 0
        else:
            upval = 0
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi = 100 - 100 / (1 + rs)
    return round(rsi, 2)

def calculate_macd(closes, fast=12, slow=26, signal=9):
    closes = np.array(closes)
    if len(closes) < slow + signal:
        return None, None
    ema_fast = pd.Series(closes).ewm(span=fast, adjust=False).mean()
    ema_slow = pd.Series(closes).ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return round(macd_line.iloc[-1], 2), round(signal_line.iloc[-1], 2)

def calculate_ema(closes, period=20):
    closes = np.array(closes)
    if len(closes) < period:
        return None
    ema = pd.Series(closes).ewm(span=period, adjust=False).mean()
    return round(ema.iloc[-1], 2)

def calculate_bollinger_bands(closes, period=20, num_std=2):
    closes = np.array(closes)
    if len(closes) < period:
        return None, None, None
    series = pd.Series(closes)
    sma = series.rolling(window=period).mean().iloc[-1]
    std = series.rolling(window=period).std().iloc[-1]
    upper = sma + num_std * std
    lower = sma - num_std * std
    return round(upper, 2), round(sma, 2), round(lower, 2)

def calculate_atr(candles, period=14):
    if len(candles) < period + 1:
        return None
    trs = []
    for i in range(1, len(candles)):
        high = candles[i]['high']
        low = candles[i]['low']
        prev_close = candles[i-1]['close']
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    atr = np.mean(trs[-period:])
    return round(atr, 2)

@app.route("/nifty100/tech", methods=["GET"])
def get_nifty100_candlestick_patterns():
    obj = get_smartconnect_obj()
    try:
        # Fetch last 30 candles for each stock to cover all patterns and indicators
        candle_data, token_map = fetch_candle_data_bulk(obj, nifty_100_array, num_candles=90)
        result = []
        bullish_patterns = {
            "Bullish Engulfing",
            "Hammer",
            "Morning Star",
            "Piercing Line",
            "Bullish Harami",
            "Inverted Hammer",
            "Three White Soldiers",
            "Dragonfly Doji",
            "Rising Three Methods"
        }
        for token, candles in candle_data.items():
            patterns = detect_candlestick_patterns(candles)
            positive = [p for p in patterns if p in bullish_patterns]
            closes = [c['close'] for c in candles]
            volumes = [c.get('volume', 0) for c in candles]
            rsi = calculate_rsi(closes)
            macd, macd_signal = calculate_macd(closes)
            ema = calculate_ema(closes)
            bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(closes)
            atr = calculate_atr(candles)
            last_volume = volumes[-1] if volumes else None
            stock = token_map[token]
            result.append({
                "symbol": stock["symbol"],
                "token": stock["token"],
                "patterns": positive,
                "rsi": rsi,
                "macd": macd,
                "macd_signal": macd_signal,
                "ema": ema,
                "bollinger_upper": bb_upper,
                "bollinger_mid": bb_mid,
                "bollinger_lower": bb_lower,
                "atr": atr,
                "volume": last_volume
            })
        return jsonify({"candlestick_patterns": result})
    except Exception as e:
        return jsonify({"detail": str(e)}), 500



@app.route("/nifty50/tech", methods=["GET"])
def get_nifty50_candlestick_patterns():
    obj = get_smartconnect_obj()
    try:
        # Fetch last 30 candles for each stock to cover all patterns and indicators
        candle_data, token_map = fetch_candle_data_bulk(obj, nifty_50_array, num_candles=90)
        result = []
        bullish_patterns = {
            "Bullish Engulfing",
            "Hammer",
            "Morning Star",
            "Piercing Line",
            "Bullish Harami",
            "Inverted Hammer",
            "Three White Soldiers",
            "Dragonfly Doji",
            "Rising Three Methods"
        }
        for token, candles in candle_data.items():
            patterns = detect_candlestick_patterns(candles)
            positive = [p for p in patterns if p in bullish_patterns]
            closes = [c['close'] for c in candles]
            volumes = [c.get('volume', 0) for c in candles]
            rsi = calculate_rsi(closes)
            macd, macd_signal = calculate_macd(closes)
            ema = calculate_ema(closes)
            bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(closes)
            atr = calculate_atr(candles)
            last_volume = volumes[-1] if volumes else None
            stock = token_map[token]
            result.append({
                "symbol": stock["symbol"],
                "token": stock["token"],
                "patterns": positive,
                "rsi": rsi,
                "macd": macd,
                "macd_signal": macd_signal,
                "ema": ema,
                "bollinger_upper": bb_upper,
                "bollinger_mid": bb_mid,
                "bollinger_lower": bb_lower,
                "atr": atr,
                "volume": last_volume
            })
        return jsonify({"candlestick_patterns": result})
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route("/smallcap/tech", methods=["GET"])
def get_small_candlestick_patterns():
    obj = get_smartconnect_obj()
    try:
        # Fetch last 30 candles for each stock to cover all patterns and indicators
        candle_data, token_map = fetch_candle_data_bulk(obj, small_cap_100_array, num_candles=90)
        result = []
        bullish_patterns = {
            "Bullish Engulfing",
            "Hammer",
            "Morning Star",
            "Piercing Line",
            "Bullish Harami",
            "Inverted Hammer",
            "Three White Soldiers",
            "Dragonfly Doji",
            "Rising Three Methods"
        }
        for token, candles in candle_data.items():
            patterns = detect_candlestick_patterns(candles)
            positive = [p for p in patterns if p in bullish_patterns]
            closes = [c['close'] for c in candles]
            volumes = [c.get('volume', 0) for c in candles]
            rsi = calculate_rsi(closes)
            macd, macd_signal = calculate_macd(closes)
            ema = calculate_ema(closes)
            bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(closes)
            atr = calculate_atr(candles)
            last_volume = volumes[-1] if volumes else None
            stock = token_map[token]
            result.append({
                "symbol": stock["symbol"],
                "token": stock["token"],
                "patterns": positive,
                "rsi": rsi,
                "macd": macd,
                "macd_signal": macd_signal,
                "ema": ema,
                "bollinger_upper": bb_upper,
                "bollinger_mid": bb_mid,
                "bollinger_lower": bb_lower,
                "atr": atr,
                "volume": last_volume
            })
        return jsonify({"candlestick_patterns": result})
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)