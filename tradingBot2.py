# from flask import Flask, request, jsonify
# import pandas as pd
# import numpy as np
# import sqlite3
# from datetime import datetime

# app = Flask(__name__)
# DB_PATH = 'trades.db'

# # Initialize SQLite Database
# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     # Create table if it doesn't exist
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS trades (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             timestamp TEXT,
#             signal TEXT,
#             reason TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()

# # Save trade to SQLite
# def save_trade(signal, reason):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     timestamp = datetime.utcnow().isoformat()  # UTC timestamp
#     cursor.execute('INSERT INTO trades (timestamp, signal, reason) VALUES (?, ?, ?)', (timestamp, signal, reason))
#     conn.commit()
#     conn.close()

# # Get all trades from SQLite
# def get_all_trades():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC')
#     trades = cursor.fetchall()
#     conn.close()
#     return trades

# # Endpoint to process data
# @app.route('/process-data', methods=['POST'])
# def process_data():
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Invalid data"}), 400

#     # Convert data to DataFrame
#     df = pd.DataFrame(data)
#     df['close'] = pd.to_numeric(df['close'])

#     # Calculate EMAs
#     df['short_ema'] = df['close'].ewm(span=12, adjust=False).mean()
#     df['long_ema'] = df['close'].ewm(span=26, adjust=False).mean()

#     # Determine signal
#     last_row = df.iloc[-1]
#     signal = "HOLD"
#     reason = "No significant EMA crossover"

#     if last_row['short_ema'] > last_row['long_ema']:
#         signal = "BUY"
#         reason = "Short EMA crossed above Long EMA"
#     elif last_row['short_ema'] < last_row['long_ema']:
#         signal = "SELL"
#         reason = "Short EMA crossed below Long EMA"

#     # Log the trade decision in SQLite
#     save_trade(signal, reason)

#     return jsonify({"signal": signal, "reason": reason})

# # Endpoint to retrieve all trades
# @app.route('/get-trades', methods=['GET'])
# def get_trades():
#     trades = get_all_trades()
#     return jsonify([
#         {"id": t[0], "timestamp": t[1], "signal": t[2], "reason": t[3]} for t in trades
#     ])

# if __name__ == '__main__':
#     init_db()  # Initialize the database
#     app.run(host='0.0.0.0', port=3300)


from flask import Flask, request, jsonify
import pandas as pd
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_PATH = 'trades.db'

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            signal TEXT,
            reason TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Save trade to SQLite
def save_trade(signal, reason):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat()  # UTC timestamp
    cursor.execute('INSERT INTO trades (timestamp, signal, reason) VALUES (?, ?, ?)', (timestamp, signal, reason))
    conn.commit()
    conn.close()

# Get all trades from SQLite
def get_all_trades():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC')
    trades = cursor.fetchall()
    conn.close()
    return trades

# Transform nested JSON into a DataFrame
def transform_data(json_data):
    time_series = json_data.get("Time Series (1min)", {})
    if not time_series:
        return pd.DataFrame()  # Return an empty DataFrame if no data is found

    # Convert time-series data into a DataFrame
    records = []
    for timestamp, values in time_series.items():
        record = {
            "timestamp": timestamp,
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"]),
        }
        records.append(record)

    df = pd.DataFrame(records)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    return df

# Endpoint to process data
@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    df = transform_data(data)
    if df.empty:
        return jsonify({"error": "No valid time-series data"}), 400

    # Calculate EMAs
    df['short_ema'] = df['close'].ewm(span=12, adjust=False).mean()
    df['long_ema'] = df['close'].ewm(span=26, adjust=False).mean()

    # Determine signal based on the latest record
    last_row = df.iloc[-1]
    signal = "HOLD"
    reason = "No significant EMA crossover"

    if last_row['short_ema'] > last_row['long_ema']:
        signal = "BUY"
        reason = "Short EMA crossed above Long EMA"
    elif last_row['short_ema'] < last_row['long_ema']:
        signal = "SELL"
        reason = "Short EMA crossed below Long EMA"

    # Log the trade decision in SQLite
    save_trade(signal, reason)

    return jsonify({"signal": signal, "reason": reason})

# Endpoint to retrieve all trades
@app.route('/get-trades', methods=['GET'])
def get_trades():
    trades = get_all_trades()
    return jsonify([
        {"id": t[0], "timestamp": t[1], "signal": t[2], "reason": t[3]} for t in trades
    ])

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(host='0.0.0.0', port=3300)
