from flask import Flask, jsonify
import requests

app = Flask(__name__)

PROXY_BASE_URL = "https://chilly-baboons-rule.loca.lt"

@app.route("/")
def home():
    return jsonify({"status": "NSE Signal API Running"})

@app.route("/besttrade")
def get_best_trade():
    try:
        spot = get_spot_price()
        option_chain = get_option_chain()

        best = None

        for item in option_chain:
            strike = item["strikePrice"]
            ce = item.get("CE", {})
            pe = item.get("PE", {})

            # Entry decision based on trend
            if spot > ce.get("strikePrice", 0):  # Spot is bullish, check CE
                if is_trade_valid(ce, spot, "CE"):
                    best = format_trade("CE", ce)
                    break
            elif spot < pe.get("strikePrice", 0):  # Spot is bearish, check PE
                if is_trade_valid(pe, spot, "PE"):
                    best = format_trade("PE", pe)
                    break

        if best:
            return jsonify(best)
        else:
            return jsonify({"message": "No strong trade found. Indicators not aligned."})
    except Exception as e:
        return jsonify({"error": str(e)})

def get_spot_price():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY 50"
    headers = {"User-Agent": "Mozilla/5.0"}
    data = requests.get(url, headers=headers).json()
    return float(data["data"][0]["last"])

def get_option_chain():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {"User-Agent": "Mozilla/5.0"}
    data = requests.get(url, headers=headers).json()
    return data["filtered"]["data"]

def is_trade_valid(option, spot, type):
    ltp = option.get("lastPrice", 0)
    volume = option.get("totalTradedVolume", 0)
    oi = option.get("openInterest", 0)
    change_oi = option.get("changeinOpenInterest", 0)
    iv = option.get("impliedVolatility", 0)

    # STRATEGY FILTERS (institution-style logic)
    if ltp < 1 or volume < 50000:
        return False  # illiquid

    if type == "CE" and spot < option.get("strikePrice", 0):
        return False
    if type == "PE" and spot > option.get("strikePrice", 0):
        return False

    if change_oi < 0 or iv == 0:
        return False  # no momentum

    return True  # passed all filters

def format_trade(type, option):
    ltp = option["lastPrice"]
    return {
        "symbol": "NIFTY",
        "type": type,
        "strike": option["strikePrice"],
        "ltp": ltp,
        "entry": ltp,
        "sl": round(ltp * 0.92, 2),
        "target": round(ltp * 1.12, 2),
        "volume": option["totalTradedVolume"]
    }

if __name__ == "__main__":
    app.run(debug=True)
