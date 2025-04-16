from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/besttrade")
def best_trade():
    # mock data for now
    return jsonify({
        "symbol": "NIFTY",
        "type": "CE",
        "strike": 22600,
        "ltp": 78.4,
        "entry": 78.4,
        "sl": 70.4,
        "target": 94.4
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
