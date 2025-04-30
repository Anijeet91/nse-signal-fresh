from flask import Flask, jsonify
import cloudscraper

app = Flask(__name__)
scraper = cloudscraper.create_scraper()  # handles headers + cookies

@app.route('/')
def home():
    return jsonify({"status": "NSE Signal API Running"})

@app.route('/besttrade')
def best_trade():
    try:
        # 1. Fetch Spot Price
        spot_url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY 50"
        spot_data = scraper.get(spot_url).json()
        price = spot_data['data'][0]['lastPrice']

        # 2. Compute Strike
        strike = int(round(price / 50) * 50)

        # 3. Fetch Option Chain
        option_url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        option_data = scraper.get(option_url).json()
        options = option_data['filtered']['data']

        # 4. Pick Option
        selected = None
        for row in options:
            if row['strikePrice'] == strike:
                ce = row.get('CE')
                if ce and ce.get('lastPrice') and ce.get('totalTradedVolume'):
                    entry = ce['lastPrice']
                    volume = ce['totalTradedVolume']
                    sl = round(entry * 0.9, 2)
                    target = round(entry * 1.2, 2)

                    selected = {
                        "symbol": "NIFTY",
                        "type": "CE",
                        "strike": strike,
                        "ltp": entry,
                        "entry": entry,
                        "sl": sl,
                        "target": target,
                        "volume": volume
                    }
                break

        if selected:
            return jsonify(selected)
        else:
            return jsonify({"message": "No strong trade found."})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
