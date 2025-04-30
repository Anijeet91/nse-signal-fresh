from flask import Flask, jsonify
import requests

app = Flask(__name__)

# --- Config ---
INDEX = "NIFTY"
SPOT_URL = f"https://www.nseindia.com/api/equity-stockIndices?index=NIFTY 50"
CHAIN_URL = f"https://www.nseindia.com/api/option-chain-indices?symbol={INDEX}"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

def get_spot_price():
    response = requests.get(SPOT_URL, headers=HEADERS, timeout=10)
    data = response.json()
    return float(data["data"][0]["last"])

def get_option_chain():
    response = requests.get(CHAIN_URL, headers=HEADERS, timeout=10)
    return response.json()

def calculate_trade():
    try:
        spot = get_spot_price()
        data = get_option_chain()
        option_data = data["filtered"]["data"]
        best_trade = None

        for item in option_data:
            strike = item["strikePrice"]
            ce = item.get("CE", {})
            pe = item.get("PE", {})

            # Check proximity (ATM or ITM)
            if abs(strike - spot) <= 50:
                for opt_type, opt_data in [("CE", ce), ("PE", pe)]:
                    try:
                        ltp = float(opt_data["lastPrice"])
                        volume = int(opt_data["totalTradedVolume"])
                        oi = int(opt_data["openInterest"])
                        change = float(opt_data["changeinOpenInterest"])

                        # Light indicator filter (momentum bias)
                        if ltp > 1 and volume > 100000 and abs(change) > 1000:
                            score = volume + abs(change)
                            if not best_trade or score > best_trade["score"]:
                                best_trade = {
                                    "symbol": INDEX,
                                    "strike": strike,
                                    "type": opt_type,
                                    "ltp": ltp,
                                    "entry": round(ltp, 1),
                                    "sl": round(ltp * 0.9, 1),
                                    "target": round(ltp * 1.2, 1),
                                    "volume": volume,
                                    "score": score
                                }
                    except Exception:
                        continue

        if best_trade:
            best_trade.pop("score")
            return jsonify(best_trade)
        else:
            return jsonify({"message": "No strong trade found. Indicators not aligned."})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/")
def home():
    return jsonify({"status": "NSE Signal API Running"})

@app.route("/besttrade")
def best_trade():
    return calculate_trade()

if __name__ == "__main__":
    app.run(debug=False, port=5000)
