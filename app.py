from flask import Flask, render_template, request, jsonify
import yfinance as yf
import random
import math

app = Flask(__name__)

def simulate_sync(symbol, years, sims):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="max", auto_adjust=True)
        if hist.empty or len(hist) < 2:
            return {"error": "無法取得足夠歷史資料"}
        col = 'Close' if 'Close' in hist.columns else hist.columns[0]
        prices = list(hist[col])
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        if not returns:
            return {"error": "無法計算報酬率"}
        mean_r = sum(returns) / len(returns)
        var = sum((r - mean_r)**2 for r in returns) / (len(returns)-1)
        mu = mean_r * 252
        sigma = math.sqrt(var) * math.sqrt(252)
        S0 = prices[-1]
        N = int(years) * 252
        dt = 1/252.0
        sims_list = []
        for _ in range(int(sims)):
            path = [S0]
            for _ in range(N):
                z = random.gauss(0, 1)
                path.append(path[-1] * math.exp((mu - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * z))
            sims_list.append(path)
        expected = round(sum(p[-1] for p in sims_list) / len(sims_list), 2)
        return {"expected_price": expected, "simulations": sims_list[:20]}
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stock_sync", methods=["POST"])
def stock_sync():
    data = request.get_json()
    return jsonify(simulate_sync(data.get("symbol"), data.get("years"), data.get("simulations")))

if __name__ == "__main__":
    app.run(debug=True)
