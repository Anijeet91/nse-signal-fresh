from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# Set your public proxy URL here (LocalTunnel)
PROXY_BASE_URL = "https://three-weeks-lie.loca.lt"

@app.route("/besttrade")
def best_trade():
    try:
        # Fetch spot price
        spot_res = requests.get(f"{PROXY_BASE_URL}/index-price?symbol=NIFTY", timeout=10)
        spot_data = spot_res.json()
        spot_price = spot_data.get("price")

        # Fetch option chain
        chain_res = requests.get(f"{PROXY_BASE_URL}/option-chain?symbol=NIFTY", timeout=10)
        chain_data = chain_res.json()

        option_chain = chain_data['filtered']['data']

        # Find nearest ITM CE below spot
        itm_ce = None
        for item in option_chain:
            if item['strikePrice'] < spot_price and 'CE' in item:
                itm_ce = item
        if not itm_ce:
            return jsonify({"error": "No ITM CE found"})

        strike = itm_ce["strikePrice"]
        ce_data = itm_ce["CE"]
        ltp = ce_data["lastPrice"]
        volume = ce_data["totalTradedVolume"]

        # Simplified indicator logic (mock for now)
        if volume > 10000:
            return jsonify({
                "symbol": "NIFTY",
                "type": "CE",
                "strike": strike,
                "ltp": ltp,
                "entry": ltp,
                "sl": round(ltp * 0.9, 2),
                "target": round(ltp * 1.2, 2),
                "volume": volume
            })
        else:
            return jsonify({"message": "Volume too low for signal"})

    except Exception as e:
        return jsonify({"error": str(e)})

# Required for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
