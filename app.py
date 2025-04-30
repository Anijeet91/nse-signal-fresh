from flask import Flask, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://www.nseindia.com'
}

@app.route('/')
def index():
    return jsonify({"status": "NSE Signal API Running"})

@app.route('/price')
def get_price():
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        spot_price = data["records"]["underlyingValue"]
        return jsonify({"price": spot_price, "symbol": "NIFTY"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/raw')
def get_raw():
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.json()
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/besttrade')
def get_best_trade():
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        spot = data["records"]["underlyingValue"]
        all_data = data["filtered"]["data"]

        # Filter strike nearest ITM CE and PE
        best_ce = None
        best_pe = None
        max_vol_ce = 0
        max_vol_pe = 0

        for item in all_data:
            strike = item["strikePrice"]
            if "CE" in item and item["CE"]:
                vol = item["CE"].get("totalTradedVolume", 0)
                if spot >= strike and vol > max_vol_ce:
                    max_vol_ce = vol
                    best_ce = {
                        "symbol": "NIFTY",
                        "type": "CE",
                        "strike": strike,
                        "ltp": item["CE"].get("lastPrice", 0),
                        "volume": vol
                    }

            if "PE" in item and item["PE"]:
                vol = item["PE"].get("totalTradedVolume", 0)
                if spot <= strike and vol > max_vol_pe:
                    max_vol_pe = vol
                    best_pe = {
                        "symbol": "NIFTY",
                        "type": "PE",
                        "strike": strike,
                        "ltp": item["PE"].get("lastPrice", 0),
                        "volume": vol
                    }

        if not best_ce and not best_pe:
            return jsonify({"message": "No strong trade found"})

        # Pick stronger signal
        best = best_ce if max_vol_ce > max_vol_pe else best_pe
        best["entry"] = best["ltp"]
        best["target"] = round(best["ltp"] * 1.2, 2)
        best["sl"] = round(best["ltp"] * 0.9, 2)

        return jsonify(best)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
