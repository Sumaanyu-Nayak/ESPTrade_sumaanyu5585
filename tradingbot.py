from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Trading variables
cash = 10000  # Initial cash
holdings = 0  # Stocks held
trade_log = []

def process_data(data):
    df = pd.DataFrame(data).T.rename(columns={
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close",
        "5. volume": "volume"
    }).astype(float)
    
    # Add EMA for trading strategy
    df["short_ema"] = df["close"].ewm(span=12, adjust=False).mean()
    df["long_ema"] = df["close"].ewm(span=26, adjust=False).mean()
    return df

def execute_trades(data):
    global cash, holdings, trade_log
    last_row = data.iloc[-1]
    
    if last_row["short_ema"] > last_row["long_ema"] and cash > last_row["close"]:
        # Buy signal
        holdings += 1
        cash -= last_row["close"]
        trade_log.append(f"BUY at {last_row['close']}")
    elif last_row["short_ema"] < last_row["long_ema"] and holdings > 0:
        # Sell signal
        cash += last_row["close"]
        holdings -= 1
        trade_log.append(f"SELL at {last_row['close']}")
    
    # Check if there is at least one trade in the trade_log
    last_trade = trade_log[-1] if trade_log else "No trades executed yet."
    
    return {"cash": cash, "holdings": holdings, "last_trade": last_trade}


@app.route('/', methods=['GET'])
def welcome():
    return "Welcome to the trading bot!"

@app.route('/data-new', methods=['POST'])
def receive_data_new():
    json_data = request.get_json()
    print(json_data)

@app.route('/data', methods=['POST'])
def receive_data():
    json_data = request.get_json()
    print(json_data)
    if "Time Series (1min)" in json_data:
        print("inside")
        data = process_data(json_data["Time Series (1min)"])
        result = execute_trades(data)
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid data format"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3300)
