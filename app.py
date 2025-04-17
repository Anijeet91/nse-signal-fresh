from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route("/besttrade")
def best_trade():
    # Simulated spot price
    spot_price = 22590

    # Sample option chain (simulated)
    option_chain = [
        {"strike": 22500, "CE": {"volume": 10500, "lastPrice": 96}, "PE": {"volume": 8500, "lastPrice": 70}},
        {"strike": 22550, "CE": {"volume": 15200, "lastPrice": 78.4}, "PE": {"volume": 6300, "lastPrice": 94}},
        {"strike": 22600, "CE": {"volume": 18800, "lastPrice": 60}, "PE": {"volume": 7200, "lastPrice": 110}},
        {"strike": 22650, "CE": {"volume": 9700, "lastPrice": 48}, "PE": {"volume": 9300, "lastPrice": 128}},
    ]

    # Determine ITM CE (strike just below spot)
    itm_ce_strike = max([o["strike"] for o in option_chain if o["strike"] < spot_price])

    # Get CE info
    selected = next((o for o in option_chain if o["strike"] == itm_ce_strike), None)
    if not selected:
        return jsonify({"error": "No suitable option found"})

    ce_data = selected["CE"]

    # Simulated indicators
    macd_bullish = random.choice([True, False])
    rsi = random.randint(40, 65)
    vwap_confirmation = random.choice([True, False])

    # Trade decision logic
    if macd_bullish and rsi < 60 and vwap_confirmation:
        return jsonify({
            "symbol": "NIFTY",
            "type": "CE",
            "strike": itm_ce_strike,
            "ltp": ce_data["lastPrice"],
            "entry": ce_data["lastPrice"],
            "sl": round(ce_data["lastPrice"] * 0.9, 2),
            "target": round(ce_data["lastPrice"] * 1.2, 2),
            "volume": ce_data["volume"],
            "indicators": {
                "MACD": macd_bullish,
                "RSI": rsi,
                "VWAP": vwap_confirmation
            }
        })

    else:
        return jsonify({"message": "No strong trade found. Indicators not aligned."})

# Run on correct port and IP for Render
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
