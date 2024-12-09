from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from ESP32
DB_PATH = 'trades.db'

# Simulation Variables
CASH = 10000.00  # Starting cash balance
HOLDINGS = 0  # Number of shares owned


# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            signal TEXT,
            reason TEXT,
            stock_price REAL,
            cash REAL,
            holdings INTEGER
        )
    ''')
    conn.commit()
    conn.close()


# Save trade to SQLite
def save_trade(signal, reason, stock_price, cash, holdings):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat()  # UTC timestamp
    cursor.execute('''
        INSERT INTO trades (timestamp, signal, reason, stock_price, cash, holdings)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, signal, reason, stock_price, cash, holdings))
    conn.commit()
    conn.close()


# Transform JSON to DataFrame
def transform_data(json_data):
    time_series = json_data.get("Time Series (1min)", {})
    if not time_series:
        return pd.DataFrame()  # Return empty DataFrame if no data

    records = []
    for timestamp, values in time_series.items():
        record = {
            "timestamp": timestamp,
            "close": float(values["4. close"])
        }
        records.append(record)

    df = pd.DataFrame(records)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    return df


# Process incoming data and make a trade decision
@app.route('/process-data', methods=['POST'])
def process_data():
    global CASH, HOLDINGS
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    df = transform_data(data)
    if df.empty:
        return jsonify({"error": "No valid time-series data"}), 400

    # Calculate EMAs
    df['short_ema'] = df['close'].ewm(span=12, adjust=False).mean()
    df['long_ema'] = df['close'].ewm(span=26, adjust=False).mean()

    # Determine trading signal
    last_row = df.iloc[-1]
    stock_price = last_row['close']
    signal = "HOLD"
    reason = "No significant EMA crossover"

    if last_row['short_ema'] > last_row['long_ema']:
        signal = "BUY"
        reason = "Short EMA crossed above Long EMA"
    elif last_row['short_ema'] < last_row['long_ema']:
        signal = "SELL"
        reason = "Short EMA crossed below Long EMA"

    # Execute trade simulation
    if signal == "BUY" and CASH >= stock_price:
        HOLDINGS += 1
        CASH -= stock_price
    elif signal == "SELL" and HOLDINGS > 0:
        HOLDINGS -= 1
        CASH += stock_price

    # Save the trade
    save_trade(signal, reason, stock_price, CASH, HOLDINGS)

    return jsonify({
        "signal": signal,
        "reason": reason,
        "stock_price": stock_price,
        "cash": CASH,
        "holdings": HOLDINGS
    })


# Retrieve all trades
@app.route('/get-trades', methods=['GET'])
def get_trades():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC')
    trades = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "id": t[0],
            "timestamp": t[1],
            "signal": t[2],
            "reason": t[3],
            "stock_price": t[4],
            "cash": t[5],
            "holdings": t[6]
        } for t in trades
    ])


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3300)
